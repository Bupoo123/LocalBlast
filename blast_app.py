#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalBlast - 本地化BLAST程序
用于执行blastn比对并生成HTML结果页面
支持本地DNA序列比对，无需连接NCBI服务器
"""

import os
import json
import subprocess
import tempfile
import shutil
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# 加载物种数据库
SPECIES_DB_FILE = 'species_db.json'
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

def generate_html_result(query_sequence, subject_info, blast_results):
    """生成HTML结果页面"""
    query_length = len(query_sequence)
    subject_length = subject_info.get('length', 0)
    subject_id = f"lcl|Query_{subject_info.get('id', 0)} (dna)"
    
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
      max-width: 1400px;
      border: 1px solid #d0d0d0;
      border-radius: 2px;
      padding: 12px 16px 20px;
    }}
    .summary-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 12px;
    }}
    .summary-table td {{
      padding: 4px 6px;
      vertical-align: middle;
    }}
    .summary-table td.label {{
      width: 120px;
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
      border-bottom: 1px solid #ccc;
      margin: 0 -16px 0;
      padding: 0 16px;
      display: flex;
      gap: 8px;
    }}
    .tab {{
      padding: 8px 14px;
      border: 1px solid #ccc;
      border-bottom: none;
      border-radius: 4px 4px 0 0;
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
      border-bottom: 1px solid #ffffff;
      border-radius: 4px 4px 0 0;
    }}
    .main-panel {{
      border-top: none;
      margin-top: 0;
    }}
    .section-header {{
      margin-top: 12px;
      background: #4a9bc7;
      border: 1px solid #3a7ba5;
      padding: 6px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 14px;
      font-weight: bold;
      color: #ffffff;
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
      color: #ffffff;
    }}
    .section-header-right a {{
      color: #ffffff;
      text-decoration: underline;
    }}
    .dropdown-label {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: default;
      color: #ffffff;
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
      color: #4a9bc7;
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
      gap: 6px;
      background: #f7f9fb;
      font-size: 13px;
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
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    table.result-table th {{
      background: #f4f6fb;
      font-weight: bold;
      color: #333;
      position: relative;
    }}
    table.result-table th::after {{
      content: "▼";
      font-size: 9px;
      margin-left: 4px;
      opacity: 0.5;
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
      text-align: right;
    }}
    table.result-table .col-evalue {{
      width: 80px;
      text-align: left;
    }}
    table.result-table .col-accession {{
      width: 110px;
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
      <td class="label">Subject ID</td>
      <td class="value">{subject_id}</td>
    </tr>
    <tr>
      <td class="label">Subject Descr</td>
      <td class="value">{subject_info.get('name', 'None')}</td>
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
        <a href="#">Graphics</a>
        <a href="#">MSA Viewer</a>
      </div>
    </div>

    <div class="select-all-row">
      <input type="checkbox" checked>
      <span>select all</span>
      <span class="count">{len(blast_results)} sequences selected</span>
    </div>

    <div class="result-table-wrapper">
      <table class="result-table">
        <thead>
        <tr>
          <th class="col-checkbox"></th>
          <th class="col-description">Description</th>
          <th class="col-scientific">Scientific Name</th>
          <th class="col-small">Max Score</th>
          <th class="col-small">Total Score</th>
          <th class="col-small">Query Cover</th>
          <th class="col-evalue">E value</th>
          <th class="col-small">Per. Ident</th>
          <th class="col-small">Acc. Len</th>
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
            <a href="#" class="link-blue">{subject_info.get('name', 'None provided')}</a>
          </td>
          <td class="col-scientific"></td>
          <td class="col-small">{int(result['bitscore'])}</td>
          <td class="col-small">{int(result['bitscore'])}</td>
          <td class="col-small">{query_cover}%</td>
          <td class="col-evalue">{evalue_str}</td>
          <td class="col-small value-highlight">{result['identity']:.2f}%</td>
          <td class="col-small">{subject_length}</td>
          <td class="col-accession">Query_{subject_info.get('id', 0)}</td>
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

@app.route('/')
def index():
    """主页面"""
    return render_template('blast_input.html', species_list=SPECIES_DB)

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
    
    if not species_id:
        return jsonify({'error': '请选择物种'}), 400
    
    # 查找物种信息
    subject_info = None
    for species in SPECIES_DB:
        if species['id'] == species_id:
            subject_info = species
            break
    
    if not subject_info:
        return jsonify({'error': '未找到指定的物种'}), 404
    
    # 检查BLAST是否安装
    if not check_blast_installed():
        return jsonify({'error': 'BLAST+未安装，请先安装BLAST+工具'}), 500
    
    try:
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
    
    except Exception as e:
        return jsonify({'error': f'BLAST执行失败: {str(e)}'}), 500

if __name__ == '__main__':
    load_species_db()
    print("=" * 50)
    print("LocalBlast - 本地化BLAST序列比对工具")
    print("=" * 50)
    print("服务已启动，访问 http://localhost:5001 使用BLAST工具")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)



