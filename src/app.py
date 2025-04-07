#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import pymongo
from bson import ObjectId

# 导入项目内部模块
from models.tweet import Tweet
from models.project import Project
from utils.ai_analyzer import analyze_tweet
from utils.telegram_bot import send_notification
from utils.notification_formatter import format_notification

# 加载环境变量
load_dotenv()

# 配置日志
log_dir = os.path.dirname(os.getenv('LOG_FILE', 'logs/xmonitor.log'))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/xmonitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
CORS(app)

# 连接MongoDB
try:
    mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
    db = mongo_client[os.getenv('MONGO_DB_NAME', 'xmonitor')]
    logger.info("成功连接到MongoDB")
except Exception as e:
    logger.error(f"MongoDB连接失败: {str(e)}")
    db = None

# 路由：主页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：项目管理页面
@app.route('/projects')
def projects_page():
    projects = list(db.projects.find())
    for project in projects:
        project['_id'] = str(project['_id'])
    return render_template('projects.html', projects=projects)

# 路由：查看历史推文页面
@app.route('/tweets')
def tweets_page():
    project_id = request.args.get('project_id')
    query = {'project_id': project_id} if project_id else {}
    tweets = list(db.tweets.find(query).sort('created_at', -1).limit(100))
    for tweet in tweets:
        tweet['_id'] = str(tweet['_id'])
    projects = list(db.projects.find())
    for project in projects:
        project['_id'] = str(project['_id'])
    return render_template('tweets.html', tweets=tweets, projects=projects, selected_project=project_id)

# API路由：接收推文webhook
@app.route('/api/webhook/tweet', methods=['POST'])
def receive_tweet():
    # 验证Webhook密钥
    secret = request.headers.get('X-Webhook-Secret')
    if secret != os.getenv('WEBHOOK_SECRET'):
        logger.warning(f"接收到无效的Webhook请求，验证失败")
        return jsonify({'status': 'error', 'message': '验证失败'}), 401
    
    try:
        data = request.json
        logger.info(f"接收到新推文: {data.get('text', '')[:50]}...")
        
        # 提取所需信息
        tweet_id = data.get('id_str') or data.get('id')
        project_id = data.get('project_id')
        twitter_username = data.get('user', {}).get('screen_name')
        token_symbol = None
        
        # 查找关联的项目
        if project_id:
            project = db.projects.find_one({'_id': ObjectId(project_id)})
        else:
            project = db.projects.find_one({'twitter_username': twitter_username})
        
        if not project:
            logger.warning(f"找不到匹配的项目: {twitter_username}")
            return jsonify({'status': 'error', 'message': '找不到匹配的项目'}), 404
        
        token_symbol = project.get('token_symbol')
        project_id = str(project['_id'])
        
        # 分析推文内容
        tweet_text = data.get('text', '')
        analysis_result = analyze_tweet(tweet_text, token_symbol)
        
        # 保存到数据库
        tweet_data = {
            'tweet_id': tweet_id,
            'project_id': project_id,
            'twitter_username': twitter_username,
            'token_symbol': token_symbol,
            'text': tweet_text,
            'created_at': datetime.utcnow(),
            'analysis': analysis_result
        }
        
        inserted_id = db.tweets.insert_one(tweet_data).inserted_id
        logger.info(f"推文已保存到数据库，ID: {inserted_id}")
        
        # 根据分析结果决定是否发送通知
        impact_level = analysis_result.get('impact_level', 'Non-Significant')
        if impact_level in ['Extremely Bullish', 'Bullish', 'Extremely Bearish', 'Bearish']:
            # 格式化并发送通知
            notification_text = format_notification(tweet_data)
            send_notification(notification_text)
            logger.info(f"已发送通知，影响级别: {impact_level}")
        
        return jsonify({'status': 'success', 'message': '推文已处理', 'tweet_id': str(inserted_id)}), 200
    
    except Exception as e:
        logger.error(f"处理推文时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'处理失败: {str(e)}'}), 500

# API路由：添加项目
@app.route('/api/projects', methods=['POST'])
def add_project():
    try:
        data = request.json
        required_fields = ['name', 'token_symbol', 'twitter_username']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'缺少必填字段: {field}'}), 400
        
        project_data = {
            'name': data['name'],
            'token_symbol': data['token_symbol'],
            'twitter_username': data['twitter_username'],
            'description': data.get('description', ''),
            'created_at': datetime.utcnow(),
            'active': True
        }
        
        inserted_id = db.projects.insert_one(project_data).inserted_id
        logger.info(f"已添加新项目: {data['name']}, ID: {inserted_id}")
        
        return jsonify({
            'status': 'success', 
            'message': '项目已添加', 
            'project_id': str(inserted_id)
        }), 201
    
    except Exception as e:
        logger.error(f"添加项目时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'添加失败: {str(e)}'}), 500

# API路由：获取所有项目
@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        projects = list(db.projects.find())
        for project in projects:
            project['_id'] = str(project['_id'])
        
        return jsonify({
            'status': 'success',
            'projects': projects
        }), 200
    
    except Exception as e:
        logger.error(f"获取项目列表时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

# API路由：更新项目
@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        data = request.json
        update_data = {}
        
        allowed_fields = ['name', 'token_symbol', 'twitter_username', 'description', 'active']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
                
        if not update_data:
            return jsonify({'status': 'error', 'message': '没有提供可更新的字段'}), 400
        
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'status': 'error', 'message': '项目不存在'}), 404
            
        logger.info(f"已更新项目, ID: {project_id}")
        
        return jsonify({
            'status': 'success',
            'message': '项目已更新'
        }), 200
    
    except Exception as e:
        logger.error(f"更新项目时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'更新失败: {str(e)}'}), 500

# API路由：删除项目
@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        result = db.projects.delete_one({'_id': ObjectId(project_id)})
        
        if result.deleted_count == 0:
            return jsonify({'status': 'error', 'message': '项目不存在'}), 404
            
        logger.info(f"已删除项目, ID: {project_id}")
        
        return jsonify({
            'status': 'success',
            'message': '项目已删除'
        }), 200
    
    except Exception as e:
        logger.error(f"删除项目时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'}), 500

# API路由：获取推文历史
@app.route('/api/tweets', methods=['GET'])
def get_tweets():
    try:
        project_id = request.args.get('project_id')
        limit = int(request.args.get('limit', 100))
        
        query = {}
        if project_id:
            query['project_id'] = project_id
        
        tweets = list(db.tweets.find(query).sort('created_at', -1).limit(limit))
        for tweet in tweets:
            tweet['_id'] = str(tweet['_id'])
            tweet['created_at'] = tweet['created_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'tweets': tweets
        }), 200
    
    except Exception as e:
        logger.error(f"获取推文历史时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': f'获取失败: {str(e)}'}), 500

# 主函数
if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"启动XMonitor服务，端口: {port}, 调试模式: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug) 