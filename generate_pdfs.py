# -*- coding: utf-8 -*-
"""
考研英语词汇 PDF 生成器
使用 reportlab 生成四级分级词汇 PDF
输出目录: /root/考研网站/pdfs/english/
"""
import os
import json
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = '/root/考研网站'
PDF_DIR = os.path.join(BASE_DIR, 'pdfs', 'english')
DATA_DIR = os.path.join(BASE_DIR, 'data', 'english')

# 注册中文字体
def register_chinese_font():
    try:
        # 尝试注册系统中的中文字体
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
        ]
        for path in font_paths:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont('ChineseFont', path))
                return 'ChineseFont'
        return 'Helvetica'
    except Exception:
        return 'Helvetica'

FONT_NAME = register_chinese_font()

LEVEL_NAMES = {
    1: 'Lv1 绿色基础词',
    2: 'Lv2 黄色进阶词',
    3: 'Lv3 橙色高频词',
    4: 'Lv4 红色认知词',
}

LEVEL_COLORS = {
    1: colors.HexColor('#27ae60'),  # 绿色
    2: colors.HexColor('#f1c40f'),  # 黄色
    3: colors.HexColor('#e67e22'),  # 橙色
    4: colors.HexColor('#e74c3c'),  # 红色
}

def load_words(level):
    """加载指定级别的词汇"""
    file_path = os.path.join(DATA_DIR, f'level{level}.json')
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_pdf(level):
    """为指定级别生成 PDF"""
    words = load_words(level)
    if not words:
        print(f"[WARN] Level {level} 没有词汇数据，跳过")
        return False

    os.makedirs(PDF_DIR, exist_ok=True)
    pdf_path = os.path.join(PDF_DIR, f'level{level}.pdf')

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName=FONT_NAME,
        fontSize=18,
        leading=24,
        alignment=1,  # 居中
        textColor=LEVEL_COLORS[level],
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontName=FONT_NAME,
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
    )
    header_style = ParagraphStyle(
        'Header',
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#333333'),
    )

    story = []

    # 标题
    story.append(Paragraph(f'考研英语词汇', title_style))
    story.append(Paragraph(f'{LEVEL_NAMES[level]} — 共 {len(words)} 词', subtitle_style))
    story.append(Spacer(1, 0.3*cm))

    # 词汇表格
    table_data = [['序号', '单词', '音标', '词性', '中文释义']]
    for i, w in enumerate(words, 1):
        row = [
            str(i),
            Paragraph(f"<b>{w.get('word','')}</b>", header_style),
            w.get('pronunciation', ''),
            w.get('part_of_speech', ''),
            Paragraph(w.get('meaning', ''), header_style),
        ]
        table_data.append(row)

    # 表格样式
    col_widths = [1.5*cm, 4*cm, 4.5*cm, 2*cm, 5.5*cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # 表头颜色
    level_color = LEVEL_COLORS[level]
    table_style = TableStyle([
        # 表头
        ('BACKGROUND', (0, 0), (-1, 0), level_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOLD', (0, 0), (-1, 0), True),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # 数据行
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # 序号居中
        ('ALIGN', (2, 1), (-1, -1), 'LEFT'),    # 其他左对齐
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f6fa')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    table.setStyle(table_style)
    story.append(table)

    # 页脚
    story.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        fontName=FONT_NAME,
        fontSize=8,
        alignment=1,
        textColor=colors.HexColor('#999999'),
    )
    story.append(Paragraph(f'考研英语词汇 · {LEVEL_NAMES[level]} · Generated by Flask App', footer_style))

    doc.build(story)
    print(f"[OK] PDF已生成: {pdf_path}")
    # 同时生成中文命名副本
    chinese_names = {
        1: 'Lv1绿色基础词.pdf',
        2: 'Lv2黄色进阶词.pdf',
        3: 'Lv3橙色高频词.pdf',
        4: 'Lv4红色认知词.pdf',
    }
    chinese_path = os.path.join(PDF_DIR, chinese_names[level])
    shutil.copy2(pdf_path, chinese_path)
    print(f"[OK] 中文命名副本: {chinese_path}")
    return True

def main():
    print("=" * 50)
    print("考研英语词汇 PDF 生成器")
    print(f"输出目录: {PDF_DIR}")
    print("=" * 50)

    os.makedirs(PDF_DIR, exist_ok=True)

    success_count = 0
    for level in [1, 2, 3, 4]:
        print(f"\n正在处理 Level {level} ({LEVEL_NAMES[level]})...")
        if create_pdf(level):
            success_count += 1

    print(f"\n{'=' * 50}")
    print(f"完成！成功生成 {success_count}/4 个 PDF 文件")
    print(f"PDF保存位置: {PDF_DIR}")
    print("=" * 50)

if __name__ == '__main__':
    main()
