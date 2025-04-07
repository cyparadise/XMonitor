#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

# 影响等级对应的颜色标签
IMPACT_LEVEL_COLORS = {
    "Extremely Bullish": "🟢 极度看涨",
    "Bullish": "🟢 看涨",
    "Non-Significant": "⚪ 无显著影响",
    "Bearish": "🔴 看跌",
    "Extremely Bearish": "🔴 极度看跌"
}

def format_notification(tweet_data):
    """
    格式化推文分析结果为Telegram富文本消息
    
    参数:
        tweet_data (dict): 包含推文和分析结果的字典
    
    返回:
        str: 格式化后的Telegram富文本消息
    """
    try:
        # 提取推文和分析数据
        token_symbol = tweet_data.get('token_symbol', '未知代币')
        twitter_username = tweet_data.get('twitter_username', '未知账号')
        text = tweet_data.get('text', '无推文内容')
        analysis = tweet_data.get('analysis', {})
        
        # 提取分析结果
        event_type = analysis.get('event_type', '未知事件')
        impact_level = analysis.get('impact_level', 'Non-Significant')
        expected_volatility = analysis.get('expected_volatility', '±0-1%')
        key_factors = analysis.get('key_factors', [])
        historical_reference = analysis.get('historical_reference', '无历史参照')
        
        # 格式化为HTML
        formatted_message = f"""
📊 <b>{token_symbol} 市场预警</b>

<b>Twitter账号:</b> @{twitter_username}
<b>事件类型:</b> {event_type}
<b>影响等级:</b> {IMPACT_LEVEL_COLORS.get(impact_level, impact_level)}
<b>预期波动:</b> {expected_volatility} (24H)

<b>推文内容:</b>
<i>{text[:200]}{'...' if len(text) > 200 else ''}</i>

<b>关键因素:</b>
"""
        
        # 添加关键因素列表
        for i, factor in enumerate(key_factors[:3], 1):
            formatted_message += f"{i}. {factor}\n"
        
        # 添加历史参照
        formatted_message += f"\n<b>历史参照:</b>\n{historical_reference}"
        
        # 添加时间戳
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message += f"\n\n<i>分析时间: {now} UTC</i>"
        
        # 添加查看链接
        tweet_id = tweet_data.get('tweet_id')
        if tweet_id:
            formatted_message += f"\n\n<a href='https://twitter.com/{twitter_username}/status/{tweet_id}'>查看原文</a>"
        
        return formatted_message
        
    except Exception as e:
        logger.error(f"格式化通知消息时出错: {str(e)}")
        # 返回简单的错误消息
        return f"⚠️ {tweet_data.get('token_symbol', '未知代币')} 有新推文，但格式化通知失败。"

def format_notification_with_buttons(tweet_data, trading_pairs=None):
    """
    格式化推文分析结果为带交易按钮的Telegram富文本消息
    
    参数:
        tweet_data (dict): 包含推文和分析结果的字典
        trading_pairs (list): 交易对列表，格式为[{"text": "交易对名称", "url": "交易链接"}]
    
    返回:
        tuple: (formatted_message, buttons)，格式化后的消息和按钮列表
    """
    formatted_message = format_notification(tweet_data)
    
    # 创建按钮
    buttons = []
    
    # 添加查看原文按钮
    tweet_id = tweet_data.get('tweet_id')
    twitter_username = tweet_data.get('twitter_username')
    if tweet_id and twitter_username:
        buttons.append({
            "text": "查看原文",
            "url": f"https://twitter.com/{twitter_username}/status/{tweet_id}"
        })
    
    # 添加交易对按钮
    token_symbol = tweet_data.get('token_symbol', '')
    if not trading_pairs and token_symbol:
        # 默认添加几个常用交易所
        buttons.extend([
            {
                "text": f"{token_symbol}/USDT Binance",
                "url": f"https://www.binance.com/zh-CN/trade/{token_symbol}_USDT"
            },
            {
                "text": f"{token_symbol}/USDT OKX",
                "url": f"https://www.okx.com/trade-spot/{token_symbol.lower()}-usdt"
            }
        ])
    elif trading_pairs:
        buttons.extend(trading_pairs)
    
    return formatted_message, buttons 