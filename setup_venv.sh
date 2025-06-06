#!/bin/bash

echo "正在创建Python虚拟环境..."

# 尝试使用python命令创建虚拟环境
python -m venv venv 2>/dev/null
if [ $? -ne 0 ]; then
    echo "python命令失败，尝试使用python3..."
    python3 -m venv venv 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "无法自动创建虚拟环境。"
        echo "请手动执行以下命令创建虚拟环境："
        echo "python -m venv venv"
        echo "或"
        echo "python3 -m venv venv"
        exit 1
    fi
fi

echo "虚拟环境创建成功！"

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt

echo "设置完成！"
echo "要激活虚拟环境，请运行：source venv/bin/activate"