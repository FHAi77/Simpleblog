# 个人博客系统

## 功能特点
- 使用 Markdown 格式撰写博客文章
- SQLite 数据库存储
- 支持文章上传
- 首页展示最近文章
- 分页显示
- SEO 友好

## 如何运行此程序

要成功运行此博客系统，您需要遵循以下步骤：

**1. 安装 Python:**
   - 确保您的计算机上安装了 Python (版本 3.x 或更高版本)。
   - 您可以从 [Python 官网](https://www.python.org/downloads/) 下载并安装。
   - (可选) 对于中国大陆用户，为了加快后续步骤中依赖包的下载速度，建议配置 pip 使用国内镜像源。打开命令行并运行：
     ```bash
     pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
     ```

**2. 克隆代码库:**
   - 如果您还没有项目的代码，请先克隆代码库：
     ```bash
     git clone https://github.com/dazhongqi789/Simpleblog.git
     cd Simpleblog
     ```

**3. 创建并激活虚拟环境:**
   - 在项目根目录下，创建一个 Python 虚拟环境。这有助于隔离项目依赖。
     ```bash
     python -m venv venv
     ```
   - 激活虚拟环境：
     - Windows: `venv\Scriptsctivate`
     - macOS/Linux: `source venv/bin/activate`
   - 激活成功后，命令行提示符前通常会显示 `(venv)`。

**4. 安装项目依赖:**
   - 确保虚拟环境已激活，然后使用 `requirements.txt` 文件安装所有必需的 Python 包：
     ```bash
     pip install -r requirements.txt
     ```

**5. 配置环境变量:**
   - 项目使用 `.env` 文件来管理敏感配置（例如操作密码）。
   - 复制项目中的 `.env.example` 文件并将其重命名为 `.env`。
     ```bash
     # 在 Windows 命令提示符中
     copy .env.example .env
     # 或在 PowerShell 或 macOS/Linux 终端中
     # cp .env.example .env
     ```
   - 打开 `.env` 文件，并根据您的需求修改其中的配置项，特别是 `OPERATION_PASSWORD`，它用于文章的上传和删除。

**6. 初始化数据库并运行程序:**
   - 运行主应用程序脚本 `app.py`。这将初始化数据库（如果尚未创建）并启动开发服务器：
     ```bash
     python app.py
     ```

**7. 访问应用:**
   - 程序默认在本地的 80 端口运行。
   - 打开您的网页浏览器，访问 `http://127.0.0.1` 或 `http://localhost` (如果80端口被占用，请根据 `app.py` 中的配置或命令行输出确认实际端口和IP地址)。

---

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

5. 访问当前的ip地址即可（默认运行的端口是80）

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


## 环境配置

### 环境变量

项目使用 `.env` 文件管理配置。请按照以下步骤配置：

1. 复制 `.env.example` 为 `.env`
2. 修改 `.env` 中的配置项：


### 注意事项

- 不要将 `.env` 文件提交到版本控制
- `OPERATION_PASSWORD` 用于文章的上传和删除
- `SECRET_KEY` 暂时未使用

### 依赖安装

```bash
pip install python-dotenv