# 使用完整的Windows Server 2022作为基础镜像
FROM mcr.microsoft.com/windows/server:ltsc2022

# 设置维护者信息
LABEL maintainer="SimpleBlog Admin"

# 设置工作目录
WORKDIR /app

# 设置环境变量 - Python不生成.pyc文件，且输出不缓冲
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 下载并安装Python（使用PowerShell）
RUN powershell -Command \
    $ProgressPreference = 'SilentlyContinue'; \
    Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe'; \
    Start-Process -FilePath 'python-installer.exe' -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_test=0' -Wait; \
    Remove-Item 'python-installer.exe' -Force

# 刷新环境变量
RUN powershell -Command \
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User'); \
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name 'Path' -Value $env:Path

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN powershell -Command \
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User'); \
    python -m pip install --upgrade pip; \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器
COPY . .

# 创建必要的目录
RUN powershell -Command \
    if (-not (Test-Path 'markdown_posts')) { New-Item -ItemType Directory -Path 'markdown_posts' }; \
    if (-not (Test-Path 'instance')) { New-Item -ItemType Directory -Path 'instance' }

# 设置环境变量（可通过docker run -e覆盖）
ENV DATABASE_URI=sqlite:///blog.db
ENV OPERATION_PASSWORD=change_this_password
ENV SECRET_KEY=generate_a_random_secret_key_here
ENV UPLOAD_FOLDER=markdown_posts

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD powershell -Command \
    try { \
        $response = Invoke-WebRequest -Uri 'http://localhost:80/' -UseBasicParsing -TimeoutSec 5; \
        if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } \
    } catch { exit 1 }

# 启动应用
CMD ["python", "app.py"]
