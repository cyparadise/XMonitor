# XMonitor 安装和部署指南

本文档提供了完整的XMonitor系统安装和部署步骤，即使您没有Linux经验也能轻松完成。

## 目录

1. [系统要求](#系统要求)
2. [获取代码](#获取代码)
3. [服务器环境设置](#服务器环境设置)
4. [配置环境变量](#配置环境变量)
5. [获取API密钥](#获取API密钥)
   - [OpenAI API](#openai-api)
   - [Telegram Bot API](#telegram-bot-api)
   - [Anthropic Claude API](#anthropic-claude-api)
   - [Deepseek API](#deepseek-api)
6. [设置IFTTT与Twitter](#设置ifttt与twitter)
7. [项目管理](#项目管理)
8. [启动服务](#启动服务)
9. [查询历史数据](#查询历史数据)
10. [故障排除](#故障排除)

## 系统要求

- Ubuntu 20.04 LTS或Debian 11或更新版本
- 至少1GB RAM
- 至少20GB磁盘空间
- Python 3.8或更高版本
- MongoDB 4.4或更高版本

## 获取代码

1. 连接到您的服务器：

```bash
ssh username@your_server_ip
```

2. 安装Git：

```bash
sudo apt-get update
sudo apt-get install -y git
```

3. 克隆项目代码：

```bash
git clone https://github.com/yourusername/xmonitor.git
cd xmonitor
```

如果您没有GitHub仓库，可以直接上传项目文件到服务器，或者手动创建所需文件。

## 服务器环境设置

我们提供了一个自动安装脚本，可以帮助您快速设置所有必要的组件：

```bash
# 给脚本添加执行权限
chmod +x scripts/setup_server.sh

# 运行安装脚本
sudo bash scripts/setup_server.sh
```

该脚本会自动执行以下操作：
- 安装所需的系统依赖
- 设置MongoDB数据库
- 创建Python虚拟环境
- 安装Python依赖
- 创建日志目录
- 设置系统服务

## 配置环境变量

安装脚本会自动创建`.env`文件，但您需要编辑该文件并填入您的API密钥和配置信息：

```bash
nano .env
```

需要配置以下参数：

- `MONGO_URI`: MongoDB连接URI (默认值通常可用)
- `MONGO_DB_NAME`: MongoDB数据库名称 (默认值: xmonitor)
- `TELEGRAM_BOT_TOKEN`: Telegram机器人令牌
- `TELEGRAM_CHAT_ID`: Telegram聊天ID
- `AI_PROVIDER`: 选择使用的AI提供商 (openai, anthropic, 或 deepseek)
- `OPENAI_API_KEY`: OpenAI API密钥
- `ANTHROPIC_API_KEY`: Anthropic API密钥
- `DEEPSEEK_API_KEY`: Deepseek API密钥
- `WEBHOOK_SECRET`: Webhook安全密钥，用于验证请求

保存文件：按`Ctrl+X`，然后按`Y`确认，再按`Enter`。

## 获取API密钥

### OpenAI API

1. 访问 [OpenAI API](https://platform.openai.com/signup) 并注册账号
2. 登录后，点击右上角的个人资料，选择"View API keys"
3. 点击"Create new secret key"创建新的API密钥
4. 复制生成的密钥，将其添加到`.env`文件的`OPENAI_API_KEY`字段

### Telegram Bot API

1. 在Telegram中搜索 [@BotFather](https://t.me/BotFather) 并开始对话
2. 发送命令 `/newbot` 创建新机器人
3. 按照提示设置机器人名称和用户名
4. 创建成功后，您将收到API令牌，格式类似：`123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
5. 将此令牌添加到`.env`文件的`TELEGRAM_BOT_TOKEN`字段

**获取聊天ID：**

1. 在Telegram中搜索您刚创建的机器人并开始对话
2. 发送任意消息给机器人
3. 访问以下URL（替换`YOUR_BOT_TOKEN`为您的机器人令牌）：
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. 在响应JSON中找到 `"chat": {"id": 123456789,` 部分，这个数字就是您的聊天ID
5. 将此ID添加到`.env`文件的`TELEGRAM_CHAT_ID`字段

### Anthropic Claude API

1. 访问 [Anthropic Console](https://console.anthropic.com/) 并注册账号
2. 登录后，导航到API Keys部分
3. 点击"Create API Key"按钮
4. 为您的密钥命名并创建
5. 复制生成的密钥，将其添加到`.env`文件的`ANTHROPIC_API_KEY`字段

### Deepseek API

1. 访问 [Deepseek](https://platform.deepseek.com/) 并注册账号
2. 登录后，导航到API部分
3. 创建新的API密钥
4. 复制生成的密钥，将其添加到`.env`文件的`DEEPSEEK_API_KEY`字段

## 设置IFTTT与Twitter

由于Twitter API现在需要付费，我们使用IFTTT来监控Twitter账号并触发Webhook：

1. 注册 [IFTTT](https://ifttt.com/) 账号
2. 点击"Create"创建新的Applet
3. 点击"Add"添加触发条件，选择"Twitter"
4. 选择"New tweet by a specific user"
5. 输入要监控的Twitter用户名（不带@）
6. 点击"Create trigger"
7. 点击"Add"添加操作，选择"Webhooks"
8. 选择"Make a web request"
9. 配置以下信息：
   - URL: `http://your_server_ip:5000/api/webhook/tweet`
   - Method: `POST`
   - Content Type: `application/json`
   - Body: 
     ```json
     {
       "text": "{{Text}}",
       "id_str": "{{TweetId}}",
       "user": {
         "screen_name": "{{UserName}}"
       }
     }
     ```
   - Headers (添加此头信息):
     ```
     X-Webhook-Secret: your_webhook_secret_here
     ```

10. 点击"Create action"
11. 点击"Continue"，然后点击"Finish"

重复上述步骤为每个要监控的Twitter账号创建Applet。

## 项目管理

添加要监控的加密货币项目：

```bash
# 切换到项目目录
cd /path/to/xmonitor

# 激活虚拟环境
source venv/bin/activate

# 添加项目
python src/scripts/manage_projects.py add --name "Bitcoin" --token-symbol "BTC" --twitter-username "bitcoin" --description "比特币官方账号"
```

列出所有项目：

```bash
python src/scripts/manage_projects.py list
```

更新项目信息：

```bash
python src/scripts/manage_projects.py update --id "project_id_here" --name "New Name" --active true
```

删除项目：

```bash
python src/scripts/manage_projects.py delete --id "project_id_here"
```

## 启动服务

使用systemd启动服务：

```bash
# 启动服务
sudo systemctl start xmonitor

# 设置开机自启
sudo systemctl enable xmonitor

# 查看服务状态
sudo systemctl status xmonitor
```

查看日志：

```bash
# 实时查看日志
journalctl -u xmonitor -f

# 查看特定日期的日志
journalctl -u xmonitor --since "2023-12-01" --until "2023-12-02"
```

## 查询历史数据

查询最近的推文：

```bash
# 切换到项目目录
cd /path/to/xmonitor

# 激活虚拟环境
source venv/bin/activate

# 查询最近10条推文
python src/scripts/query_tweets.py recent --limit 10
```

查询特定项目的推文：

```bash
python src/scripts/query_tweets.py project --project-id "project_id_here" --limit 20
```

查询特定影响等级的推文：

```bash
python src/scripts/query_tweets.py impact --impact-level "Extremely Bullish" --limit 20
```

导出推文数据：

```bash
python src/scripts/query_tweets.py export --output "tweets_export.json" --limit 100
```

## 故障排除

### MongoDB连接问题

如果遇到MongoDB连接问题：

```bash
# 检查MongoDB服务状态
sudo systemctl status mongodb

# 如果服务未运行，启动服务
sudo systemctl start mongodb

# 如果需要，设置开机自启
sudo systemctl enable mongodb
```

### API请求失败

如果AI分析请求失败：

1. 检查您的API密钥是否正确
2. 检查API提供商服务是否正常
3. 检查网络连接
4. 查看日志文件以获取详细错误信息：
   ```bash
   cat logs/xmonitor.log
   ```

### Webhook未触发

如果IFTTT Webhook未触发：

1. 确保您的服务器端口（默认5000）已在防火墙中开放
2. 确保IFTTT Applet已启用
3. 检查Webhook URL是否正确
4. 确保X-Webhook-Secret头信息与.env文件中的WEBHOOK_SECRET匹配

### 服务无法启动

如果服务无法启动：

```bash
# 查看详细错误
journalctl -u xmonitor -e

# 手动运行启动脚本以查看详细输出
cd /path/to/xmonitor
bash scripts/start_production.sh
```

---

如果您遇到任何其他问题，请查阅日志文件或联系支持。 