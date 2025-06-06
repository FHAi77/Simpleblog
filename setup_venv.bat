@echo off
echo 正在创建Python虚拟环境...

REM 尝试使用python命令创建虚拟环境
python -m venv venv
if %errorlevel% neq 0 (
    echo python命令失败，尝试使用python3...
    python3 -m venv venv
    if %errorlevel% neq 0 (
        echo python3命令也失败，尝试使用py...
        py -m venv venv
        if %errorlevel% neq 0 (
            echo 无法自动创建虚拟环境。
            echo 请手动执行以下命令创建虚拟环境：
            echo python -m venv venv
            echo 或
            echo python3 -m venv venv
            echo 或
            echo py -m venv venv
            exit /b 1
        )
    )
)

echo 虚拟环境创建成功！

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

echo 设置完成！
echo 要激活虚拟环境，请运行：venv\Scripts\activate.bat