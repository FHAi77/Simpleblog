# 个人博客系统

## 功能特点
- 使用 Markdown 格式撰写博客文章
- SQLite 数据库存储
- 支持文章上传
- 首页展示最近文章
- 分页显示
- SEO 友好

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/dazhongqi789/Simpleblog
cd Simpleblog
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库并运行
```bash
python app.py
```

5.访问当前的ip地址即可（默认运行的端口是80）

## 使用说明

1. 使用 Markdown 格式撰写博客文章
2. 点击首页右下角的上传文章按钮进行markdown文章上传

## Markdown 文件格式
文章 Markdown 文件需包含 YAML 前置元数据：
```markdown
---
title: 文章标题
tags: python, web
---

文章正文内容...
