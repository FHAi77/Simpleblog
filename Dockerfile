# 使用完整的 Windows Server Core 作为基础镜像
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# 设置工作目录 - 使用正斜杠避免转义问题
WORKDIR C:/app

# 使用 PowerShell 下载并安装 Python
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue';"]

# 创建临时目录并下载 Python
RUN New-Item -ItemType Directory -Force -Path C:/temp; \
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile "C:/temp/python-installer.exe" -UseBasicParsing

# 安装 Python
RUN Start-Process -Wait -FilePath "C:/temp/python-installer.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "TargetDir=C:/Python311"; \
    Remove-Item "C:/temp/python-installer.exe" -Force

# 设置 Python 环境变量
ENV PYTHONPATH=C:/Python311
ENV PATH="C:/Python311;C:/Python311/Scripts;${PATH}"

# 复制项目文件到容器中
COPY requirements.txt .
COPY app.py .
COPY models.py .
COPY .env.example .
COPY templates/ templates/
COPY static/ static/
COPY instance/ instance/

# 创建上传文件夹
RUN New-Item -ItemType Directory -Force -Path C:/app/markdown_posts

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制环境变量文件
RUN Copy-Item .env.example .env

# 暴露 80 端口
EXPOSE 80

# 设置入口点，初始化数据库并运行应用
CMD ["python", "app.py"]
