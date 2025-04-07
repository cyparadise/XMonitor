# XMonitor - 加密货币项目推文监控与AI分析系统

![XMonitor Logo](static/img/logo.png)

XMonitor是一个专为加密货币爱好者和投资者设计的工具，它可以自动监控Twitter上特定加密货币项目的最新推文，并使用人工智能(AI)分析这些推文对币价的潜在影响。

## 主要功能

- **推文监控**：实时监控指定Twitter账号的新推文
- **AI分析**：使用大型语言模型API(OpenAI/Claude/Deepseek)分析推文内容
- **市场影响评估**：评估推文对代币价格的潜在影响
- **即时通知**：通过Telegram Bot发送重要推文的分析结果
- **历史数据查询**：查看和搜索历史推文及其分析结果
- **多项目管理**：支持监控多个加密货币项目

## 技术栈

- **后端**：Python + Flask
- **数据库**：MongoDB
- **通知**：Telegram Bot API
- **AI分析**：支持多种AI提供商(OpenAI, Anthropic Claude, Deepseek)
- **推文获取**：IFTTT (Twitter + Webhooks)
- **部署**：Ubuntu/Debian Linux服务器

## 系统截图

![主页截图](static/img/screenshot-home.png)
![项目管理截图](static/img/screenshot-projects.png)
![推文分析截图](static/img/screenshot-tweets.png)

## 快速开始

详细的安装和部署指南可以在[INSTALLATION.md](INSTALLATION.md)文件中找到。

### 基本步骤

1. 克隆代码库
2. 运行自动安装脚本
   ```bash
   sudo bash scripts/setup_server.sh
   ```
3. 配置环境变量(API密钥等)
4. 启动服务
   ```bash
   sudo systemctl start xmonitor
   ```
5. 添加监控项目
   ```bash
   python src/scripts/manage_projects.py add --name "Bitcoin" --token-symbol "BTC" --twitter-username "bitcoin"
   ```

## 系统架构

XMonitor系统采用模块化设计，主要包含以下组件：

1. **Flask Web服务**：提供API和Web界面
2. **MongoDB数据库**：存储项目和推文数据
3. **AI分析模块**：连接多种AI API进行推文分析
4. **Telegram通知模块**：发送分析结果通知
5. **IFTTT Webhook**：接收Twitter推文更新

## 贡献

欢迎提交问题报告和改进建议！如果你想贡献代码，请先创建一个Issue描述你的想法。

## 授权协议

MIT License - 详见[LICENSE](LICENSE)文件

## 联系方式

如有任何问题或建议，请通过以下方式联系：

- Email: your.email@example.com
- Twitter: [@YourHandle](https://twitter.com/YourHandle)

---

**免责声明**：XMonitor不提供投资建议。所有AI分析结果仅供参考，投资决策需用户自行判断并承担风险。 