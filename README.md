# 考研复习网站

在线考研复习平台，提供英语词汇、数学、政治、专业课等学习资源。

## 🚀 快速启动

```bash
cd /root/考研网站
bash start.sh
```

或手动启动：

```bash
cd /root/考研网站
pip3 install flask reportlab fpdf2 -q --break-system-packages
python3 generate_pdfs.py          # 首次生成词汇PDF
nohup python3 app.py > server.log 2>&1 &
```

## 🌐 访问地址

启动后访问：

- **本机**: http://localhost:5000
- **局域网**: http://`<本机IP>`:5000

查看本机 IP：
```bash
hostname -I | awk '{print $1}'
```

## 📁 目录结构

```
/root/考研网站/
├── app.py                  # Flask 主服务器
├── generate_pdfs.py        # 英语词汇 PDF 生成器
├── start.sh                # 一键启动脚本
├── README.md               # 本文档
├── templates/              # HTML 模板
├── data/                   # 词汇数据（JSON）
│   └── english/
│       ├── level1.json     # CET-4 词汇
│       ├── level2.json     # CET-6 词汇
│       ├── level3.json     # TEM-4 词汇
│       └── level4.json     # TEM-8 词汇
├── pdfs/                   # 生成的 PDF 文件
│   └── english/
│       ├── level1.pdf
│       ├── level2.pdf
│       ├── level3.pdf
│       └── level4.pdf
├── subjects/               # 各科目资料
│   ├── english/
│   ├── math/
│   ├── politics/
│   └── 专业课/
├── css/
└── js/
```

## 📚 功能模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | 网站首页 |
| 英语词汇 | `/english` | 四级分级词汇学习 |
| 数学 | `/math` | 高数/线代/概率论 |
| 政治 | `/politics` | 马原/毛中特/史纲/思修 |
| 专业课 | `/major` | 408计算机/自命题 |

## 🔧 常用操作

### 重启服务器
```bash
pkill -f "python3 app.py" && nohup python3 /root/考研网站/app.py > /root/考研网站/server.log 2>&1 &
```

### 查看日志
```bash
tail -f /root/考研网站/server.log
```

### 重新生成 PDF
```bash
python3 /root/考研网站/generate_pdfs.py
```

### 检查服务器状态
```bash
curl http://localhost:5000/health
```

## ⚙️ 技术栈

- **后端**: Flask (Python)
- **PDF生成**: ReportLab
- **数据**: JSON 文件存储
- **绑定地址**: 0.0.0.0:5000（支持局域网访问）

## 📝 注意事项

- 服务器默认绑定 `0.0.0.0:5000`，可直接从局域网访问
- PDF 首次访问时如不存在，会提示运行 `generate_pdfs.py`
- 防火墙需开放 5000 端口：`ufw allow 5000`
