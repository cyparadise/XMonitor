#!/bin/bash

# XMonitor服务器环境设置脚本
# 这个脚本会自动安装所有必要的依赖，并配置服务器环境

# 打印彩色信息函数
print_info() {
    echo -e "\e[1;34m[信息]\e[0m $1"
}

print_success() {
    echo -e "\e[1;32m[成功]\e[0m $1"
}

print_warning() {
    echo -e "\e[1;33m[警告]\e[0m $1"
}

print_error() {
    echo -e "\e[1;31m[错误]\e[0m $1"
}

# 确保脚本以root权限运行
if [[ $EUID -ne 0 ]]; then
   print_error "此脚本需要以root权限运行，请使用sudo执行"
   echo "例如: sudo bash setup_server.sh"
   exit 1
fi

# 获取当前目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

print_info "开始设置XMonitor服务器环境..."
print_info "项目目录: $PROJECT_DIR"

# 更新包列表
print_info "更新包列表..."
apt-get update

# 安装基本工具
print_info "安装基本工具..."
apt-get install -y build-essential git curl wget python3 python3-pip python3-dev python3-venv mongodb

# 检查MongoDB安装
print_info "检查MongoDB服务状态..."
systemctl status mongodb
if [ $? -ne 0 ]; then
    print_warning "MongoDB服务未启动，正在启动..."
    systemctl start mongodb
    systemctl enable mongodb
    if [ $? -ne 0 ]; then
        print_error "MongoDB启动失败，请手动检查并启动MongoDB服务"
        print_info "您可以使用以下命令: sudo systemctl start mongodb"
    else
        print_success "MongoDB服务已启动并设置为开机自启"
    fi
else
    print_success "MongoDB服务已经在运行"
fi

# 创建Python虚拟环境
print_info "创建Python虚拟环境..."
if [ ! -d "$PROJECT_DIR/venv" ]; then
    python3 -m venv "$PROJECT_DIR/venv"
    print_success "Python虚拟环境创建成功"
else
    print_warning "Python虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境并安装依赖
print_info "安装Python依赖..."
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    print_error "安装Python依赖失败，请检查requirements.txt文件是否存在或有错误"
else
    print_success "Python依赖安装成功"
fi

# 创建日志目录
print_info "创建日志目录..."
mkdir -p "$PROJECT_DIR/logs"
chmod 755 "$PROJECT_DIR/logs"
print_success "日志目录创建成功"

# 确保脚本可执行
print_info "设置脚本权限..."
chmod +x "$PROJECT_DIR/scripts/start_production.sh"
chmod +x "$PROJECT_DIR/src/scripts/manage_projects.py"
chmod +x "$PROJECT_DIR/src/scripts/query_tweets.py"
print_success "脚本权限设置成功"

# 检查环境配置文件
print_info "检查环境配置文件..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        print_warning "已创建.env文件，请编辑并填入您的实际配置信息"
        print_info "使用命令: nano $PROJECT_DIR/.env"
    else
        print_error "找不到.env.example文件，请手动创建.env文件"
    fi
else
    print_warning ".env文件已存在，请确保配置正确"
fi

# 创建systemd服务文件
print_info "创建systemd服务文件..."
cat > /etc/systemd/system/xmonitor.service << EOF
[Unit]
Description=XMonitor Crypto Twitter Monitoring Service
After=network.target mongodb.service

[Service]
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/scripts/start_production.sh
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=xmonitor

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
systemctl daemon-reload
print_success "systemd服务文件创建成功"

# 提供后续操作说明
print_success "环境设置完成！"
echo ""
echo "后续步骤:"
echo "1. 编辑.env文件，填入您的API密钥和配置信息:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. 启动XMonitor服务:"
echo "   sudo systemctl start xmonitor"
echo ""
echo "3. 设置服务开机自启:"
echo "   sudo systemctl enable xmonitor"
echo ""
echo "4. 查看服务状态:"
echo "   sudo systemctl status xmonitor"
echo ""
echo "5. 查看日志:"
echo "   journalctl -u xmonitor -f"
echo ""
echo "6. 添加监控项目:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python src/scripts/manage_projects.py add --name '项目名称' --token-symbol 'BTC' --twitter-username 'bitcoin'"
echo ""
print_info "如有任何问题，请参阅README.md或INSTALLATION.md文件" 