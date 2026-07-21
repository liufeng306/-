# -*- coding: utf-8 -*-
"""
考研网站 Flask 服务器
绑定: 0.0.0.0:80
"""
from flask import Flask, render_template, send_file, jsonify, request
import os
import json
import urllib.request
import urllib.error

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_BASE = os.path.join(BASE_DIR, 'pdfs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SUBJECTS_DIR = os.path.join(BASE_DIR, 'subjects')

# ─── 辅助函数 ────────────────────────────────────────────────────────────────
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def list_pdfs(subject):
    """列出某科目的PDF文件，按年份分组"""
    subject_dir = os.path.join(PDF_BASE, subject)
    if not os.path.exists(subject_dir):
        return []
    import re
    files_by_year = {}
    for f in sorted(os.listdir(subject_dir)):
        if f.endswith('.pdf'):
            size = os.path.getsize(os.path.join(subject_dir, f))
            size_str = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.0f}KB"
            # 提取年份：匹配前4位数字
            m = re.match(r'^(\d{4})', f)
            year = m.group(1) if m else '其他'
            if year not in files_by_year:
                files_by_year[year] = []
            files_by_year[year].append({'name': f, 'size': size_str})
    # 按年份降序排列
    sorted_years = sorted(files_by_year.keys(), key=lambda x: (x == '其他', x), reverse=True)
    return [{'year': y, 'files': files_by_year[y]} for y in sorted_years]

def filter_videos(subject):
    """从links.json中筛选某科目的视频"""
    all_links = load_json('links.json')
    return [v for v in all_links if v.get('subject') == subject]

# ─── 首页 ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─── 英语页面 ───────────────────────────────────────────────────────────────
@app.route('/english')
def english():
    videos = filter_videos('english')
    groups = {}
    for v in videos:
        t = v.get('teacher', '其他')
        groups.setdefault(t, []).append(v)
    # 历史目录包含英语一和来源未核验文件，不向英语二学习路径公开。
    pdfs = []
    return render_template('english.html', videos=videos, video_groups=groups, pdfs=pdfs)

@app.route('/english/level/<int:level>')
def english_level(level):
    vocab_file = os.path.join(DATA_DIR, 'english', f'level{level}.json')
    words = []
    if os.path.exists(vocab_file):
        with open(vocab_file, 'r', encoding='utf-8') as f:
            words = json.load(f)
    return render_template('english_level.html', level=level, words=words)

@app.route('/english/level/<int:level>/download')
def download_level_pdf(level):
    pdf_file = os.path.join(PDF_BASE, 'english', f'level{level}.pdf')
    if os.path.exists(pdf_file):
        return send_file(pdf_file, as_attachment=True,
                        download_name=f'考研英语词汇 Level{level}.pdf')
    return "PDF未生成，请先运行 generate_pdfs.py", 404

# ─── 数学页面 ───────────────────────────────────────────────────────────────
@app.route('/math')
def math():
    videos = filter_videos('math')
    # 按老师分组
    groups = {}
    for v in videos:
        t = v.get('teacher', '其他')
        groups.setdefault(t, []).append(v)
    # 服务器历史目录含数学一文件，085801 仅允许审核后的数学二题目进入题库。
    pdfs = []
    return render_template('math.html', videos=videos, video_groups=groups, pdfs=pdfs)

@app.route('/math/topic/<topic>')
def math_topic(topic):
    data_file = os.path.join(SUBJECTS_DIR, 'math', f'{topic}.json')
    content = {}
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
    return render_template('math_topic.html', topic=topic, content=content)

# ─── 政治页面 ───────────────────────────────────────────────────────────────
@app.route('/politics')
def politics():
    videos = filter_videos('politics')
    groups = {}
    for v in videos:
        t = v.get('teacher', '其他')
        groups.setdefault(t, []).append(v)
    # 未标注版权与年份来源的 PDF 不作为公开题库内容。
    pdfs = []
    return render_template('politics.html', videos=videos, video_groups=groups, pdfs=pdfs)

# ─── 专业课页面 ──────────────────────────────────────────────────────────────
@app.route('/major')
def major():
    all_links = load_json('links.json')
    videos = [v for v in all_links if v.get('subject') in ('major', 'electronics', 'analog', 'digital')]
    # 去重：按url保留唯一视频
    seen_urls = set()
    unique_videos = []
    for v in videos:
        url = v.get('url', '')
        if url not in seen_urls:
            seen_urls.add(url)
            unique_videos.append(v)
    videos = unique_videos
    # 按老师分组
    groups = {}
    for v in videos:
        t = v.get('teacher', '其他')
        groups.setdefault(t, []).append(v)
    pdfs = list_pdfs('817')
    # 加载外部链接
    all_external = load_json('external_links.json')
    school_links = [l for l in all_external if l.get('category') in ('school', 'official')]
    major_links = [l for l in all_external if l.get('category') in ('school_major', 'info')]
    outline = load_json('major_817.json')
    return render_template('major.html', videos=videos, video_groups=groups, pdfs=pdfs,
                           school_links=school_links, major_links=major_links, outline=outline)

# ─── 词汇页面 ───────────────────────────────────────────────────────────────
@app.route('/vocabulary')
def vocabulary():
    """默认跳转 Lv1 高频词汇"""
    return vocabulary_level(1)

@app.route('/vocabulary/<int:level>')
def vocabulary_level(level):
    """按等级显示词汇，Lv1=高频, Lv2=中高频, Lv3=中频, Lv4=低频，不分页"""
    vocab_data = load_json('english_vocabulary.json')
    all_words = vocab_data.get('words', []) if isinstance(vocab_data, dict) else vocab_data
    metadata = vocab_data.get('metadata', {}) if isinstance(vocab_data, dict) else {}

    # 按等级筛选
    if level not in (1, 2, 3, 4):
        level = 1
    level_words = [w for w in all_words if w.get('level') == level]

    return render_template('vocabulary.html', words=level_words, metadata=metadata,
                          current_level=level, total_words=len(level_words))

# ─── 计划页面 ───────────────────────────────────────────────────────────────
@app.route('/plan')
def plan():
    plan_data = load_json('exam_plan.json')
    return render_template('plan.html', plan=plan_data)

# ─── AI助手页面 ─────────────────────────────────────────────────────────────
@app.route('/ai')
def ai():
    return render_template('ai.html')

# ─── AI对话API ──────────────────────────────────────────────────────────────
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """连接OpenClaw AI（OpenAI兼容端点）进行对话"""
    try:
        data = request.get_json(silent=True) or {}
        message = str(data.get('message', '')).strip()
        history = data.get('history', [])
        
        if not message or len(message) > 1200:
            return jsonify({'error': '消息不能为空'})
        if not isinstance(history, list):
            history = []
        
        # OpenClaw Gateway - OpenAI 兼容端点
        gateway_url = 'http://127.0.0.1:19440/v1/chat/completions'
        token = os.environ.get('OPENCLAW_API_TOKEN')
        if not token:
            return jsonify({'error': 'AI 服务暂未配置，请联系管理员。'}), 503
        
        # 构造消息列表（带上下文）
        messages = [
            {
                'role': 'system',
                'content': '你是东北石油大学085801电气工程专硕的学习助教。用中文、分点、简明回答。默认科目为政治、英语二、数学二、817电子技术基础（模电+数电）。招生政策、日期、分数线和真题来源不确定时，明确说明需以东北石油大学和研招网官方公告为准；不得编造真题、官方数据或“必考”结论。'
            }
        ]
        # 追加历史（仅保留最近6条以避免token超限）
        for h in history[-6:]:
            if isinstance(h, dict) and h.get('role') in ('user', 'assistant') and h.get('content'):
                messages.append({'role': h['role'], 'content': str(h['content'])[:1200]})
        # 当前问题
        messages.append({'role': 'user', 'content': message})
        
        # 构建请求（model: openclaw/shenma_meishu 路由到具体agent）
        req_data = json.dumps({
            'model': 'openclaw/shenma_meishu',
            'messages': messages,
            'stream': False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            gateway_url,
            data=req_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            # OpenAI 格式：choices[0].message.content
            content = ''
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
            if not content:
                content = result.get('message') or '（AI 未返回内容）'
            return jsonify({'response': content})
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return jsonify({'error': f'HTTP错误: {e.code}', 'detail': error_body[:500]}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── PDF 下载路由 ───────────────────────────────────────────────────────────
@app.route('/pdfs/english/<path:filename>')
def serve_pdf_english(filename):
    return send_file(os.path.join(PDF_BASE, 'english', filename))

@app.route('/pdfs/math/<path:filename>')
def serve_pdf_math(filename):
    return send_file(os.path.join(PDF_BASE, 'math', filename))

@app.route('/pdfs/politics/<path:filename>')
def serve_pdf_politics(filename):
    return send_file(os.path.join(PDF_BASE, 'politics', filename))

@app.route('/pdfs/major/<path:filename>')
def serve_pdf_major(filename):
    return send_file(os.path.join(PDF_BASE, '817', filename))

# ─── 健康检查 ───────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({'status': 'running', 'version': '1.1.0'})

if __name__ == '__main__':
    print("=" * 50)
    print("考研网站服务器启动中...")
    print("访问地址: http://0.0.0.0:80")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
