#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import requests
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# Telegram Bot配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_notification(message, parse_mode="HTML"):
    """
    发送Telegram通知
    
    参数:
        message (str): 要发送的消息内容，支持HTML或Markdown格式
        parse_mode (str): 解析模式，"HTML"或"MarkdownV2"
    
    返回:
        bool: 发送是否成功
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram配置不完整，无法发送通知")
        return False
    
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, data=data)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('ok'):
            logger.info("通知发送成功")
            return True
        else:
            logger.error(f"通知发送失败: {response_json}")
            return False
            
    except Exception as e:
        logger.error(f"发送Telegram通知时出错: {str(e)}")
        return False

def send_notification_with_buttons(message, buttons=None, parse_mode="HTML"):
    """
    发送带有内联按钮的Telegram通知
    
    参数:
        message (str): 要发送的消息内容，支持HTML或Markdown格式
        buttons (list): 按钮列表，格式为[{"text": "按钮文本", "url": "按钮链接"}]
        parse_mode (str): 解析模式，"HTML"或"MarkdownV2"
    
    返回:
        bool: 发送是否成功
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram配置不完整，无法发送通知")
        return False
    
    if not buttons:
        return send_notification(message, parse_mode)
    
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        
        # 创建内联键盘标记
        inline_keyboard = []
        row = []
        for i, button in enumerate(buttons):
            row.append({
                "text": button["text"],
                "url": button["url"]
            })
            
            # 每行最多放置2个按钮
            if (i + 1) % 2 == 0 or i == len(buttons) - 1:
                inline_keyboard.append(row)
                row = []
        
        reply_markup = {
            "inline_keyboard": inline_keyboard
        }
        
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
            "reply_markup": json.dumps(reply_markup)
        }
        
        response = requests.post(url, data=data)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('ok'):
            logger.info("带按钮的通知发送成功")
            return True
        else:
            logger.error(f"带按钮的通知发送失败: {response_json}")
            return False
            
    except Exception as e:
        logger.error(f"发送带按钮的Telegram通知时出错: {str(e)}")
        return False

def test_telegram_connection():
    """
    测试Telegram Bot连接是否正常
    
    返回:
        bool: 连接是否正常
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("缺少Telegram Bot Token，无法测试连接")
        return False
    
    try:
        url = f"{TELEGRAM_API_URL}/getMe"
        response = requests.get(url)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('ok'):
            bot_username = response_json.get('result', {}).get('username')
            logger.info(f"Telegram Bot连接正常，Bot用户名: {bot_username}")
            return True
        else:
            logger.error(f"Telegram Bot连接测试失败: {response_json}")
            return False
    
    except Exception as e:
        logger.error(f"测试Telegram连接时出错: {str(e)}")
        return False

# 发送错误通知
def send_error_notification(error_message):
    """
    发送错误通知到Telegram
    
    参数:
        error_message (str): 错误消息
    
    返回:
        bool: 发送是否成功
    """
    message = f"⚠️ <b>XMonitor系统错误</b>\n\n<pre>{error_message}</pre>"
    return send_notification(message) 