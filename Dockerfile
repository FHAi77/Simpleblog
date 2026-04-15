# escape=`

# 使用完整的Windows Server 2022作为基础镜像
FROM mcr.microsoft.com/windows/server:ltsc2022

# 设置默认shell为PowerShell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# 设置工作目录
WORKDIR /app

# 设置Python版本
ENV PYTHON_VERSION=3.11.8

# 下载并安装Python
RUN Invoke-WebRequest -Uri "https://www.python.org/ftp/python/$($env:PYTHON_VERSION)/python-$($env:PYTHON_VERSION)-amd64.exe" -OutFile 'python-installer.exe'; `
    Start-Process -FilePath 'python-installer.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait; `
    Remove-Item -Path 'python-installer.exe' -Force;

# 重新加载环境变量并验证Python安装
RUN $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User'); `
    python --version; `
    pip --version;

# 复制requirements.txt并安装依赖
COPY requirements.txt .

RUN $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User'); `
    pip install --no-cache-dir -r requirements.txt;

# 复制应用程序代码
COPY . .

# 创建必要的目录
RUN if (!(Test-Path -Path 'markdown_posts')) { New-Item -ItemType Directory -Path 'markdown_posts' }; `
    if (!(Test-Path -Path 'instance')) { New-Item -ItemType Directory -Path 'instance' };

# 初始化数据库
RUN $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User'); `
    python -c 'from app import app, db; app.app_context().push(); db.create_all()';

# 暴露Flask默认端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 创建启动脚本
RUN @'
$env:PATH = [Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User')
python -m flask run --host=0.0.0.0 --port=5000
'@ | Out-File -FilePath 'start.ps1' -Encoding ascii;

# 启动应用
CMD ["powershell", "-ExecutionPolicy", "Bypass", "-File", "start.ps1"]
