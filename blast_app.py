#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalBlast - 本地化BLAST程序
用于执行blastn比对并生成HTML结果页面
支持本地DNA序列比对，无需连接NCBI服务器
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import zipfile
import uuid
import csv
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import re
from werkzeug.utils import secure_filename

# 可选依赖：用于HTML转PNG功能
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("警告: selenium未安装，PNG图片生成功能将不可用")

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: Pillow未安装，PNG图片生成功能将不可用")

import time

def get_base_path():
    """获取应用基础路径，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

# 获取基础路径
BASE_PATH = get_base_path()

# 设置Flask模板和静态文件路径（兼容PyInstaller打包）
if getattr(sys, 'frozen', False):
    # PyInstaller打包后
    template_folder = os.path.join(BASE_PATH, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    # 开发环境
app = Flask(__name__)
CORS(app)

# 配置（使用绝对路径，兼容PyInstaller打包）
UPLOAD_FOLDER = os.path.join(BASE_PATH, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_PATH, 'results')
ALLOWED_EXTENSIONS = {'seq'}

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# 加载物种数据库
SPECIES_DB_FILE = os.path.join(BASE_PATH, 'species_db.json')
SPECIES_DB = []

def load_species_db():
    """加载物种数据库"""
    global SPECIES_DB
    try:
        with open(SPECIES_DB_FILE, 'r', encoding='utf-8') as f:
            SPECIES_DB = json.load(f)
        print(f"已加载 {len(SPECIES_DB)} 个物种")
    except FileNotFoundError:
        print(f"警告: 未找到 {SPECIES_DB_FILE}")
        SPECIES_DB = []

def check_blast_installed():
    """检查BLAST+是否已安装"""
    try:
        result = subprocess.run(['blastn', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def parse_blast_output(blast_output):
    """解析BLAST输出结果"""
    results = []
    lines = blast_output.strip().split('\n')
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        
        # 解析BLAST默认输出格式
        # qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore
        parts = line.split('\t')
        if len(parts) >= 12:
            result = {
                'query_id': parts[0],
                'subject_id': parts[1],
                'identity': float(parts[2]),
                'alignment_length': int(parts[3]),
                'mismatches': int(parts[4]),
                'gap_opens': int(parts[5]),
                'query_start': int(parts[6]),
                'query_end': int(parts[7]),
                'subject_start': int(parts[8]),
                'subject_end': int(parts[9]),
                'evalue': float(parts[10]),
                'bitscore': float(parts[11])
            }
            results.append(result)
    
    return results

def run_blastn_against_all_species(query_sequence):
    """使用统一数据库与所有物种比对（优化版本）"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 写入查询序列
        query_file = os.path.join(temp_dir, 'query.fasta')
        with open(query_file, 'w') as f:
            f.write(f">Query\n{query_sequence}\n")
        
        # 创建包含所有物种序列的统一FASTA文件
        # 序列ID格式：species_id|species_name，这样可以从结果中识别物种
        all_species_file = os.path.join(temp_dir, 'all_species.fasta')
        with open(all_species_file, 'w') as f:
            for species in SPECIES_DB:
                # 序列ID格式：species_id|species_name
                seq_id = f"{species['id']}|{species['name']}"
                f.write(f">{seq_id}\n{species['sequence']}\n")
        
        # 创建统一的BLAST数据库（只创建一次）
        db_file = os.path.join(temp_dir, 'all_species_db')
        subprocess.run(['makeblastdb', '-in', all_species_file, 
                      '-dbtype', 'nucl', '-out', db_file],
                     check=True, capture_output=True)
        
        # 执行blastn比对（只执行一次）
        output_file = os.path.join(temp_dir, 'blast_output.txt')
        cmd = [
            'blastn',
            '-query', query_file,
            '-db', db_file,
            '-outfmt', '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore',
            '-out', output_file,
            '-max_target_seqs', '100'  # 限制结果数量以提高速度
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"BLAST执行失败: {result.stderr}")
        
        # 读取结果
        with open(output_file, 'r') as f:
            output = f.read()
        
        # 解析结果
        blast_results = parse_blast_output(output)
        
        # 为每个结果添加物种信息
        all_results = []
        for result in blast_results:
            # 从subject_id中解析物种ID和名称
            # 格式：species_id|species_name
            subject_id = result['subject_id']
            if '|' in subject_id:
                species_id_str, species_name = subject_id.split('|', 1)
                try:
                    species_id = int(species_id_str)
                    # 查找对应的物种信息
                    for species in SPECIES_DB:
                        if species['id'] == species_id:
                            result['species_info'] = species
                            all_results.append(result)
                            break
                except ValueError:
                    continue
        
        return all_results
    
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_blastn(query_sequence, subject_sequence, subject_name):
    """执行blastn比对"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 写入查询序列
        query_file = os.path.join(temp_dir, 'query.fasta')
        with open(query_file, 'w') as f:
            f.write(f">Query\n{query_sequence}\n")
        
        # 写入参考序列
        subject_file = os.path.join(temp_dir, 'subject.fasta')
        with open(subject_file, 'w') as f:
            f.write(f">{subject_name}\n{subject_sequence}\n")
        
        # 创建BLAST数据库
        db_file = os.path.join(temp_dir, 'subject_db')
        subprocess.run(['makeblastdb', '-in', subject_file, 
                      '-dbtype', 'nucl', '-out', db_file],
                     check=True, capture_output=True)
        
        # 执行blastn
        output_file = os.path.join(temp_dir, 'blast_output.txt')
        cmd = [
            'blastn',
            '-query', query_file,
            '-db', db_file,
            '-outfmt', '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore',
            '-out', output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"BLAST执行失败: {result.stderr}")
        
        # 读取结果
        with open(output_file, 'r') as f:
            output = f.read()
        
        return parse_blast_output(output)
    
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def generate_html_result(query_sequence, subject_info, blast_results, is_best_match=False):
    """生成HTML结果页面"""
    query_length = len(query_sequence)
    subject_length = subject_info.get('length', 0)
    
    # 生成随机7位数Query ID（1-5开头）
    query_id_first_digit = random.randint(1, 5)
    query_id_remaining = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    query_id = f"{query_id_first_digit}{query_id_remaining}"
    
    subject_id = f"lcl|Query_{query_id} (dna)"
    
    # Query Descr 始终显示 None
    query_description = 'None'
    
    # Subject Descr 始终显示 None provided
    subject_description = 'None provided'
    
    # 计算最佳匹配结果
    best_result = None
    if blast_results:
        best_result = max(blast_results, key=lambda x: x['bitscore'])
        max_score = int(best_result['bitscore'])
        total_score = max_score
        query_cover = int((best_result['alignment_length'] / query_length) * 100)
        evalue = best_result['evalue']
        per_ident = best_result['identity']
        acc_len = subject_length
    else:
        max_score = 0
        total_score = 0
        query_cover = 0
        evalue = 1.0
        per_ident = 0.0
        acc_len = subject_length
    
    # 格式化E值
    if evalue < 0.001:
        evalue_str = f"{evalue:.2e}"
    else:
        evalue_str = f"{evalue:.2f}"
    
    html_template = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BLAST Result</title>
  <style>
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 16px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      color: #222;
      background: #ffffff;
    }}
    a {{
      color: #1763a6;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .blast-container {{
      max-width: 1100px;
      margin: 0 auto;
      border: none;
      border-radius: 0;
      padding: 12px 16px 20px;
    }}
    .summary-table {{
      width: 50%;
      border-collapse: collapse;
      margin-bottom: 12px;
      table-layout: fixed;
    }}
    .summary-table td {{
      padding: 4px 6px;
      vertical-align: middle;
      text-align: left;
    }}
    .summary-table tr {{
      position: relative;
    }}
    .summary-table td.label {{
      width: 140px;
      color: #555;
      font-weight: bold;
    }}
    .summary-table td.value {{
      color: #000;
    }}
    .summary-table tr + tr td {{
      border-top: 1px solid #e4e4e4;
    }}
    .inline-help {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .help-icon {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #2b6cb0;
      color: #fff;
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }}
    .tabs {{
      border-bottom: none;
      margin: 0 -16px 0;
      padding: 0 16px;
      display: flex;
      gap: 8px;
    }}
    .tab {{
      padding: 8px 14px;
      border: 1px solid #ccc;
      border-bottom: none;
      border-radius: 0;
      background: #f3f3f3;
      color: #000000;
      font-size: 13px;
      cursor: pointer;
    }}
    .tabs .tab.active {{
      background-color: #0272BD;
      color: #ffffff;
      font-weight: bold;
      border: 1px solid #ccc;
      border-bottom: none;
      border-radius: 0;
    }}
    .main-panel {{
      border-top: none;
      margin-top: 0;
    }}
    .section-header {{
      margin-top: 0;
      background: #BDD9D6;
      border: 1px solid #3a7ba5;
      border-top: 3px solid #0272BD;
      padding: 6px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      font-weight: bold;
      color: #000000;
    }}
    .section-header-left {{
      flex: 1;
    }}
    .section-header-right {{
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 12px;
      font-weight: normal;
      color: #000000;
    }}
    .section-header-right a {{
      color: #000000;
      text-decoration: underline;
    }}
    .dropdown-label {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: default;
      color: #000000;
      font-weight: bold;
    }}
    .dropdown-label::after {{
      content: "▼";
      font-size: 9px;
      margin-top: 1px;
    }}
    .show-select-group {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: #ffffff;
    }}
    select {{
      font-size: 12px;
      padding: 2px 4px;
    }}
    .help-circle-small {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #ffffff;
      color: #BDD9D6;
      font-size: 10px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-weight: bold;
    }}
    .select-all-row {{
      padding: 8px 10px;
      border: 1px solid #3a7ba5;
      border-top: none;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      background: #f7f9fb;
      font-size: 13px;
    }}
    .select-all-row-right {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .select-all-row-right a {{
      color: #000000;
      text-decoration: underline;
    }}
    .select-all-row span.count {{
      margin-left: 8px;
      color: #555;
      font-style: italic;
    }}
    .result-table-wrapper {{
      border: 1px solid #3a7ba5;
      border-top: none;
    }}
    table.result-table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: 12px;
    }}
    table.result-table th,
    table.result-table td {{
      border-top: 1px solid #e0e6ef;
      padding: 6px 6px;
      text-align: left;
    }}
    table.result-table th {{
      background: #E2F4F8;
      font-weight: normal;
      color: #00538A;
      position: relative;
      white-space: normal;
      word-wrap: break-word;
      line-height: 1.3;
      text-align: center;
    }}
    table.result-table td {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-align: center;
    }}
    table.result-table th::after {{
      content: "▼";
      display: block;
      font-size: 9px;
      margin-top: 2px;
      opacity: 0.5;
      text-align: center;
    }}
    table.result-table th.col-checkbox::after {{
      content: none;
    }}
    table.result-table tr:nth-child(even) td {{
      background: #fafbff;
    }}
    table.result-table .col-checkbox {{
      width: 32px;
      text-align: center;
    }}
    table.result-table .col-description {{
      width: 260px;
    }}
    table.result-table .col-scientific {{
      width: 220px;
    }}
    table.result-table .col-small {{
      width: 70px;
      text-align: center;
    }}
    table.result-table .col-evalue {{
      width: 80px;
      text-align: center;
    }}
    table.result-table .col-accession {{
      width: 110px;
    }}
    /* 允许特定列换行显示 */
    table.result-table th.col-small,
    table.result-table th.col-evalue,
    table.result-table th.col-accession,
    table.result-table td.col-small,
    table.result-table td.col-evalue,
    table.result-table td.col-accession {{
      white-space: normal;
      word-wrap: break-word;
      overflow: visible;
      text-overflow: clip;
      line-height: 1.3;
    }}
    .link-blue {{
      color: #1763a6;
      text-decoration: none;
    }}
    .link-blue:hover {{
      text-decoration: underline;
    }}
    .value-highlight {{
      color: #004a99;
      font-weight: bold;
    }}
  </style>
</head>
<body>
<div class="blast-container">
  <table class="summary-table">
    <tr>
      <td class="label">Query Length</td>
      <td class="value">{query_length}</td>
    </tr>
    <tr>
      <td class="label">Query Descr</td>
      <td class="value">{query_description}</td>
    </tr>
    <tr>
      <td class="label">Subject ID</td>
      <td class="value">{subject_id}</td>
    </tr>
    <tr>
      <td class="label">Subject Descr</td>
      <td class="value">{subject_description}</td>
    </tr>
    <tr>
      <td class="label">Subject Length</td>
      <td class="value">{subject_length}</td>
    </tr>
    <tr>
      <td class="label">Other reports</td>
      <td class="value">
        <span class="inline-help">
          <a href="#">MSA viewer</a>
          <span class="help-icon">?</span>
        </span>
      </td>
    </tr>
  </table>

  <div class="tabs">
    <div class="tab active">Descriptions</div>
    <div class="tab">Graphic Summary</div>
    <div class="tab">Alignments</div>
    <div class="tab">Dot Plot</div>
  </div>

  <div class="main-panel">
    <div class="section-header">
      <div class="section-header-left">
        Sequences producing significant alignments
      </div>
      <div class="section-header-right">
        <span class="dropdown-label">Download</span>
        <span class="dropdown-label">Select columns</span>
        <span class="show-select-group">
          Show
          <select>
            <option>100</option>
            <option>50</option>
            <option>20</option>
          </select>
        </span>
        <span class="help-circle-small">?</span>
      </div>
    </div>

    <div class="select-all-row">
      <div>
        <input type="checkbox" checked>
        <span>select all</span>
        <span class="count">{len(blast_results)} sequences selected</span>
      </div>
      <div class="select-all-row-right">
        <a href="#">Graphics</a>
        <a href="#">MSA Viewer</a>
      </div>
    </div>

    <div class="result-table-wrapper">
      <table class="result-table">
        <thead>
        <tr>
          <th class="col-checkbox"></th>
          <th class="col-description">Description</th>
          <th class="col-scientific">Scientific Name</th>
          <th class="col-small">Max<br>Score</th>
          <th class="col-small">Total<br>Score</th>
          <th class="col-small">Query<br>Cover</th>
          <th class="col-evalue">E<br>value</th>
          <th class="col-small">Per.<br>Ident</th>
          <th class="col-small">Acc.<br>Len</th>
          <th class="col-accession">Accession</th>
        </tr>
        </thead>
        <tbody>
"""
    
    if blast_results:
        for result in blast_results:
            query_cover = int((result['alignment_length'] / query_length) * 100)
            evalue = result['evalue']
            if evalue < 0.001:
                evalue_str = f"{evalue:.2e}"
            else:
                evalue_str = f"{evalue:.2f}"
            
            html_template += f"""
        <tr>
          <td class="col-checkbox"><input type="checkbox" checked></td>
          <td class="col-description">
            <a href="#" class="link-blue">None provided</a>
          </td>
          <td class="col-scientific"></td>
          <td class="col-small">{int(result['bitscore'])}</td>
          <td class="col-small">{int(result['bitscore'])}</td>
          <td class="col-small">{query_cover}%</td>
          <td class="col-evalue">{evalue_str}</td>
          <td class="col-small value-highlight">{result['identity']:.2f}%</td>
          <td class="col-small">{subject_length}</td>
          <td class="col-accession">Query_{query_id}</td>
        </tr>
"""
    else:
        html_template += """
        <tr>
          <td colspan="10" style="text-align: center; padding: 20px; color: #666;">
            No significant alignments found.
          </td>
        </tr>
"""
    
    html_template += """
        </tbody>
      </table>
    </div>
  </div>
</div>
</body>
</html>
"""
    
    return html_template

def parse_seq_file(file_content):
    """解析.seq文件内容，返回序列字符串"""
    # 移除所有空白字符和换行，只保留序列字符
    # .seq文件可能包含数字行号，需要过滤掉
    lines = file_content.strip().split('\n')
    sequence = ''
    
    for line in lines:
        line = line.strip()
        # 跳过空行和纯数字行（行号）
        if not line or line.isdigit():
            continue
        # 移除行号（如果行首是数字）
        if line and line[0].isdigit():
            # 尝试找到第一个非数字字符
            for i, char in enumerate(line):
                if not char.isdigit() and char not in ' \t':
                    line = line[i:]
                    break
        
        # 提取序列字符（只保留ATCG和可能的模糊字符）
        seq_chars = ''.join([c for c in line.upper() if c in 'ATCGNMRWSYKVHDBNX-'])
        sequence += seq_chars
    
    # 移除所有非标准字符，只保留ATCG
    sequence = re.sub(r'[^ATCG]', '', sequence.upper())
    return sequence

# 全局变量：缓存ChromeDriver实例（用于批量处理时复用）
_cached_driver = None
_cached_driver_path = None

def get_chromedriver_path():
    """获取ChromeDriver路径（带缓存和超时）"""
    global _cached_driver_path
    
    # 如果已经缓存，直接返回
    if _cached_driver_path and os.path.exists(_cached_driver_path):
        return _cached_driver_path
    
    driver_path = None
    
    # 优先查找本地ChromeDriver（在exe同目录或drivers子目录）
    local_driver_paths = []
    if sys.platform == 'win32':
        local_driver_paths = [
            os.path.join(BASE_PATH, 'chromedriver.exe'),
            os.path.join(BASE_PATH, 'drivers', 'chromedriver.exe'),
        ]
    else:
        local_driver_paths = [
            os.path.join(BASE_PATH, 'chromedriver'),
            os.path.join(BASE_PATH, 'drivers', 'chromedriver'),
        ]
    
    # 查找本地ChromeDriver
    for local_path in local_driver_paths:
        if os.path.exists(local_path) and os.path.isfile(local_path):
            driver_path = local_path
            print(f"使用本地ChromeDriver: {driver_path}")
            break
    
    # 如果程序目录没有，查找~/.wdm目录中的缓存（优先于网络下载）
    if not driver_path:
        wdm_base = os.path.expanduser('~/.wdm')
        if os.path.exists(wdm_base):
            import glob
            pattern = os.path.join(wdm_base, '**/chromedriver*')
            chromedrivers = glob.glob(pattern, recursive=True)
            # 过滤掉THIRD_PARTY_NOTICES文件
            chromedrivers = [d for d in chromedrivers 
                           if 'THIRD_PARTY_NOTICES' not in d 
                           and os.path.exists(d)
                           and os.path.isfile(d)]
            if chromedrivers:
                chromedrivers.sort(key=os.path.getmtime, reverse=True)
                driver_path = chromedrivers[0]
                print(f"使用本地缓存的ChromeDriver: {driver_path}")
    
    # 如果本地和缓存都没有，才尝试从网络下载（带超时）
    if not driver_path:
        try:
            print("本地未找到ChromeDriver，尝试从网络下载（最多等待10秒）...")
            
            # Windows不支持signal，使用threading实现超时
            if sys.platform == 'win32':
                import threading
                download_result = {'driver_path': None, 'error': None}
                
                def download_driver():
                    try:
                        download_result['driver_path'] = ChromeDriverManager().install()
                    except Exception as e:
                        download_result['error'] = e
                
                download_thread = threading.Thread(target=download_driver)
                download_thread.daemon = True
                download_thread.start()
                download_thread.join(timeout=10)  # 最多等待10秒
                
                if download_thread.is_alive():
                    raise TimeoutError("ChromeDriver下载超时（10秒）")
                
                if download_result['error']:
                    raise download_result['error']
                
                driver_path = download_result['driver_path']
                print(f"从网络下载ChromeDriver: {driver_path}")
            else:
                # macOS/Linux使用signal实现超时
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("ChromeDriver下载超时")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)
                
                try:
                    driver_path = ChromeDriverManager().install()
                    print(f"从网络下载ChromeDriver: {driver_path}")
                finally:
                    signal.alarm(0)  # 取消超时
                    
        except (ConnectionError, TimeoutError, Exception) as e:
            print(f"网络下载失败或超时: {str(e)}")
            raise Exception("无法获取ChromeDriver：本地未找到且网络下载失败")
    
    # 修复webdriver-manager的bug：如果返回的是THIRD_PARTY_NOTICES文件，查找实际的chromedriver
    if driver_path and ('THIRD_PARTY_NOTICES' in driver_path or not os.path.exists(driver_path)):
        # 在相同目录下查找chromedriver文件
        driver_dir = os.path.dirname(driver_path)
        if sys.platform == 'win32':
            actual_driver = os.path.join(driver_dir, 'chromedriver.exe')
        else:
            actual_driver = os.path.join(driver_dir, 'chromedriver')
        
        if os.path.exists(actual_driver) and os.path.isfile(actual_driver):
            driver_path = actual_driver
        else:
            # 尝试在整个.wdm目录中查找
            wdm_base = os.path.expanduser('~/.wdm')
            if os.path.exists(wdm_base):
                import glob
                pattern = os.path.join(wdm_base, '**/chromedriver*')
                chromedrivers = glob.glob(pattern, recursive=True)
                # 过滤掉THIRD_PARTY_NOTICES文件
                chromedrivers = [d for d in chromedrivers 
                               if 'THIRD_PARTY_NOTICES' not in d 
                               and os.path.exists(d)
                               and os.path.isfile(d)]
                if chromedrivers:
                    chromedrivers.sort(key=os.path.getmtime, reverse=True)
                    driver_path = chromedrivers[0]
    
    if not driver_path or not os.path.exists(driver_path):
        raise Exception("无法找到ChromeDriver")
    
    # Windows系统不需要检查执行权限
    if sys.platform != 'win32':
        # 确保chromedriver有执行权限（macOS/Linux）
        if os.path.exists(driver_path):
            try:
                current_mode = os.stat(driver_path).st_mode
                os.chmod(driver_path, current_mode | 0o111)
            except (OSError, PermissionError):
                pass
    
    # 缓存路径
    _cached_driver_path = driver_path
    return driver_path

def get_chromedriver_instance():
    """获取ChromeDriver实例（复用，避免重复启动）"""
    global _cached_driver
    
    # 如果已有实例且可用，直接返回
    if _cached_driver:
        try:
            # 测试driver是否仍然可用
            _cached_driver.current_url
            return _cached_driver
        except:
            # driver已失效，重置
            _cached_driver = None
    
    # 创建新的driver实例
    try:
        driver_path = get_chromedriver_path()
        
        # 配置Chrome选项（无头模式）
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        service = Service(driver_path)
        _cached_driver = webdriver.Chrome(service=service, options=chrome_options)
        print("ChromeDriver已启动（将复用此实例）")
        return _cached_driver
    except Exception as e:
        print(f"无法启动Chrome WebDriver: {str(e)}")
        print("提示: PNG生成功能将不可用，但HTML文件仍会正常生成")
        return None

def close_chromedriver():
    """关闭ChromeDriver实例"""
    global _cached_driver
    if _cached_driver:
        try:
            _cached_driver.quit()
        except:
            pass
        _cached_driver = None

def html_to_image(html_content, output_path, driver=None):
    """将HTML内容转换为PNG图片，并裁剪空白部分
    
    Args:
        html_content: HTML内容
        output_path: 输出PNG文件路径
        driver: 可选的WebDriver实例（用于批量处理时复用）
    """
    # 检查依赖是否可用
    if not SELENIUM_AVAILABLE:
        print("selenium未安装，跳过PNG生成")
        return None
    if not PIL_AVAILABLE:
        print("Pillow未安装，跳过PNG生成")
        return None
    
    temp_html = None
    use_external_driver = driver is not None
    
    try:
        # 创建临时HTML文件
        temp_html = output_path.replace('.png', '_temp.html')
        with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
        # 如果没有传入driver，创建新的（单文件处理模式）
        if not driver:
            driver = get_chromedriver_instance()
            if not driver:
                return None
        
        try:
            # 加载HTML文件
            file_url = f"file://{os.path.abspath(temp_html)}"
            driver.get(file_url)
            
            # 使用显式等待替代固定sleep（最多等待2秒）
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                # 如果显式等待失败，使用固定等待
                time.sleep(0.5)
            
            # 获取页面元素（blast-container）
            try:
                element = driver.find_element(By.CLASS_NAME, "blast-container")
            except:
                # 如果找不到blast-container，使用body
                element = driver.find_element(By.TAG_NAME, "body")
            
            # 截图
            screenshot = element.screenshot_as_png
            
            # 使用PIL处理图片，裁剪空白部分
            img = Image.open(io.BytesIO(screenshot))
            
            # 转换为RGB（如果是RGBA）
            if img.mode == 'RGBA':
                # 创建白色背景
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                img = rgb_img
            
            # 裁剪空白部分
            # 获取图片的边界框（去除白色边缘）
            bbox = img.getbbox()
            if bbox:
                # 添加一些边距（10像素）
                left, top, right, bottom = bbox
                margin = 10
                left = max(0, left - margin)
                top = max(0, top - margin)
                right = min(img.width, right + margin)
                bottom = min(img.height, bottom + margin)
                
                # 裁剪图片
                cropped_img = img.crop((left, top, right, bottom))
            else:
                cropped_img = img
            
            # 保存PNG文件
            cropped_img.save(output_path, 'PNG', optimize=True)
            
            return output_path
            
        finally:
            # 只有在单文件处理模式时才关闭driver
            if not use_external_driver and driver:
                close_chromedriver()
                
    except Exception as e:
        print(f"HTML转PNG失败: {str(e)}")
        import traceback
        traceback.print_exc()
        # 如果转换失败，返回None，但不影响主流程
        return None
    finally:
        # 清理临时HTML文件
        if temp_html and os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except:
                pass

@app.route('/')
def index():
    """主页面"""
    return render_template('blast_input.html', species_list=SPECIES_DB)

@app.route('/batch')
def batch_page():
    """批量比对页面"""
    return render_template('batch_blast.html')

@app.route('/manual')
def user_manual():
    """用户手册页面"""
    return render_template('user_manual.html')

@app.route('/api/species', methods=['GET'])
def get_species():
    """获取所有物种列表"""
    return jsonify(SPECIES_DB)

@app.route('/api/blast', methods=['POST'])
def run_blast():
    """执行BLAST比对"""
    data = request.json
    query_sequence = data.get('query_sequence', '').strip().upper()
    species_id = data.get('species_id')
    
    if not query_sequence:
        return jsonify({'error': '查询序列不能为空'}), 400
    
    # 检查BLAST是否安装
    if not check_blast_installed():
        return jsonify({'error': 'BLAST+未安装，请先安装BLAST+工具'}), 500
    
    try:
        if species_id:
            # 单个物种比对
            subject_info = None
            for species in SPECIES_DB:
                if species['id'] == species_id:
                    subject_info = species
                    break
            
            if not subject_info:
                return jsonify({'error': '未找到指定的物种'}), 404
            
            # 执行BLAST比对
            blast_results = run_blastn(
                query_sequence,
                subject_info['sequence'],
                subject_info['name']
            )
            
            # 生成HTML结果
            html_result = generate_html_result(query_sequence, subject_info, blast_results)
            
            return jsonify({
                'success': True,
                'html': html_result,
                'results_count': len(blast_results)
            })
        else:
            # 与所有物种比对，使用统一数据库（优化版本）
            try:
                # 使用统一数据库进行比对
                all_results = run_blastn_against_all_species(query_sequence)
                
                if not all_results:
                    return jsonify({'error': '未找到任何匹配结果'}), 404
                
                # 按bitscore排序，选择得分最高的
                all_results.sort(key=lambda x: x['bitscore'], reverse=True)
                best_result = all_results[0]
                best_species = best_result['species_info']
                
                # 只返回最佳匹配结果
                best_blast_results = [best_result]
                
                # 生成HTML结果（标记为最佳匹配）
                html_result = generate_html_result(query_sequence, best_species, best_blast_results, is_best_match=True)
                
                return jsonify({
                    'success': True,
                    'html': html_result,
                    'results_count': 1,
                    'best_match': {
                        'species_name': best_species['name'],
                        'bitscore': best_result['bitscore'],
                        'identity': best_result['identity'],
                        'evalue': best_result['evalue']
                    }
                })
            except Exception as e:
                return jsonify({'error': f'统一数据库比对失败: {str(e)}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'BLAST执行失败: {str(e)}'}), 500

@app.route('/api/batch-blast', methods=['POST'])
def batch_blast():
    """批量处理序列文件"""
    if 'files' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    files = request.files.getlist('files')
    
    if not files or files[0].filename == '':
        return jsonify({'error': '请至少选择一个文件'}), 400
    
    # 检查BLAST是否安装
    if not check_blast_installed():
        return jsonify({'error': 'BLAST+未安装，请先安装BLAST+工具'}), 500
    
    # 创建批次ID
    batch_id = str(uuid.uuid4())
    batch_folder = os.path.join(RESULTS_FOLDER, batch_id)
    os.makedirs(batch_folder, exist_ok=True)
    
    processed = 0
    errors = []
    summary_rows = []
    
    # 批量处理时，复用同一个ChromeDriver实例（提升性能）
    shared_driver = None
    try:
        # 尝试启动ChromeDriver（如果PNG功能可用）
        if SELENIUM_AVAILABLE and PIL_AVAILABLE:
            try:
                shared_driver = get_chromedriver_instance()
                if shared_driver:
                    print("已启动共享ChromeDriver，将用于所有文件的PNG生成")
            except Exception as e:
                print(f"无法启动ChromeDriver，PNG功能将不可用: {str(e)}")
                shared_driver = None
        
        for file in files:
            if not file.filename.endswith('.seq'):
                errors.append(f"{file.filename}: 不是.seq格式文件")
                continue
            
            try:
                # 读取文件内容
                file_content = file.read().decode('utf-8', errors='ignore')
                
                # 解析序列
                sequence = parse_seq_file(file_content)
                
                if not sequence or len(sequence) < 10:
                    errors.append(f"{file.filename}: 序列太短或无效")
                    continue
                
                # 与所有物种比对（使用统一数据库）
                all_results = run_blastn_against_all_species(sequence)
                
                if not all_results:
                    errors.append(f"{file.filename}: 未找到匹配结果")
                    continue
                
                # 选择最佳匹配
                all_results.sort(key=lambda x: x['bitscore'], reverse=True)
                best_result = all_results[0]
                best_species = best_result['species_info']
                best_blast_results = [best_result]
                
                # 生成HTML结果
                html_result = generate_html_result(sequence, best_species, best_blast_results, is_best_match=True)
                
                # 保存HTML文件
                safe_filename = secure_filename(file.filename)
                html_filename = safe_filename.replace('.seq', '.html')
                html_path = os.path.join(batch_folder, html_filename)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_result)
                
                # 生成PNG图片文件（使用共享的driver实例）
                png_filename = safe_filename.replace('.seq', '.png')
                png_path = os.path.join(batch_folder, png_filename)
                try:
                    html_to_image(html_result, png_path, driver=shared_driver)
                    if os.path.exists(png_path):
                        print(f"已生成PNG图片: {png_filename}")
                except Exception as e:
                    print(f"生成PNG图片失败 {png_filename}: {str(e)}")
                    # PNG生成失败不影响主流程
                
                query_length = len(sequence)
                subject_length = best_species.get('length', 0)
                query_cover_value = 0.0
                if query_length > 0:
                    query_cover_value = (best_result['alignment_length'] / query_length) * 100
                per_ident_value = best_result['identity']
                positive_probability = (per_ident_value * query_cover_value) / 100
                result_label = "阳性" if per_ident_value >= 90 else "阴性"

                summary_rows.append([
                    file.filename,
                    best_species.get('name', ''),
                    best_species.get('code', ''),
                    query_length,
                    subject_length,
                    f"{query_cover_value:.2f}%",
                    f"{per_ident_value:.2f}%",
                    f"{positive_probability:.2f}%",
                    result_label
                ])
                
                processed += 1
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
                continue
        
        if processed == 0:
            return jsonify({'error': '没有成功处理任何文件', 'errors': errors}), 400
        
        summary_file = os.path.join(batch_folder, 'batch_summary.csv')
        with open(summary_file, 'w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'SEQ文件名',
                '对应参比序列靶点名称',
                '对应参比序列编号',
                'Query Length',
                'Subject Length',
                'Query Cover',
                'Per. Ident',
                '阳性概率值',
                '结果'
            ])
            writer.writerows(summary_rows)
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'processed': processed,
            'total': len(files),
            'errors': errors
        })
    
    except Exception as e:
        return jsonify({'error': f'批量处理失败: {str(e)}'}), 500
    finally:
        # 关闭共享的ChromeDriver实例
        if shared_driver:
            try:
                close_chromedriver()
                print("已关闭共享ChromeDriver")
            except Exception as e:
                print(f"关闭ChromeDriver时出错: {str(e)}")

@app.route('/api/download-results', methods=['GET'])
def download_results():
    """下载批量处理结果"""
    batch_id = request.args.get('batch_id')
    
    if not batch_id:
        return jsonify({'error': '缺少batch_id参数'}), 400
    
    batch_folder = os.path.join(RESULTS_FOLDER, batch_id)
    
    if not os.path.exists(batch_folder):
        return jsonify({'error': '结果文件不存在'}), 404
    
    # 创建ZIP文件
    zip_filename = f'blast_results_{batch_id}.zip'
    zip_path = os.path.join(RESULTS_FOLDER, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(batch_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, batch_folder)
                zipf.write(file_path, arcname)
    
    return send_file(zip_path, as_attachment=True, download_name=zip_filename)

@app.route('/api/download-template', methods=['GET'])
def download_template():
    """下载序列文件模板"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后，模板在exe同目录
        template_path = os.path.join(BASE_PATH, 'templates', 'sequence_template.seq')
    else:
        # 开发环境
        template_path = os.path.join('templates', 'sequence_template.seq')
    
    if not os.path.exists(template_path):
        return jsonify({'error': '模板文件不存在'}), 404
    
    return send_file(template_path, as_attachment=True, download_name='sequence_template.seq')

if __name__ == '__main__':
    load_species_db()
    print("=" * 50)
    print("LocalBlast - 本地化BLAST序列比对工具")
    print("=" * 50)
    print("服务已启动，访问 http://localhost:5001 使用BLAST工具")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)



