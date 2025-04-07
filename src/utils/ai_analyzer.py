#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import requests
from dotenv import load_dotenv
import anthropic
import openai

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# AI提供商配置
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai').lower()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-0125-preview')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

def analyze_tweet(tweet_text, token_symbol):
    """
    使用AI分析推文内容，评估对币价的潜在影响
    
    参数:
        tweet_text (str): 推文内容
        token_symbol (str): 代币符号，如BTC、ETH等
        
    返回:
        dict: 分析结果，包含影响等级、预期波动等信息
    """
    try:
        # 构建prompt
        prompt = f"""
你是一个加密货币市场分析师，请根据[推文内容]，评估其对代币 [{token_symbol}] 价格的潜在影响:

评估依据包括：
1. 是否涉及合作伙伴关系、监管批准、技术突破等关键事件
2. 市场情绪关键词（如"重大进展""首次""唯一"等）
3. 对比历史事件：历史上有无类似事件，以及当时对应代币价格的市场反应
4. 使用加密货币行业专用情感词典

推文内容: {tweet_text}

输出格式：
   1. 简短总结事件类型
   2. 影响等级（按以下等级分类）：
- Extremely Bullish（重大利好）
- Bullish（利好）
- Non-Significant（无显著影响）
- Bearish（利空）
- Extremely Bearish（重大利空）
   3. 预期波动：±百分比范围
   4. 关键因素：列举3个影响点
   5. 历史参照：历史类似事件发生后，当时对应代币价格的市场反应

请以JSON格式输出，包含以下字段：event_type, impact_level, expected_volatility, key_factors (数组), historical_reference
"""
        
        # 根据配置的AI提供商调用相应的API
        response_content = None
        
        if AI_PROVIDER == 'openai':
            response_content = analyze_with_openai(prompt)
        elif AI_PROVIDER == 'anthropic':
            response_content = analyze_with_anthropic(prompt)
        elif AI_PROVIDER == 'deepseek':
            response_content = analyze_with_deepseek(prompt)
        else:
            logger.error(f"未知的AI提供商: {AI_PROVIDER}")
            return default_analysis_result(token_symbol)
        
        # 解析JSON结果
        try:
            # 尝试直接解析JSON
            result = json.loads(response_content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试从文本中提取JSON部分
            try:
                json_str = extract_json_from_text(response_content)
                result = json.loads(json_str)
            except:
                logger.error("无法解析AI响应为JSON格式")
                return default_analysis_result(token_symbol)
        
        # 验证结果格式
        required_fields = ['event_type', 'impact_level', 'expected_volatility', 'key_factors', 'historical_reference']
        for field in required_fields:
            if field not in result:
                logger.warning(f"AI响应中缺少必要字段: {field}")
                result[field] = "未提供" if field != 'key_factors' else []
        
        return result
        
    except Exception as e:
        logger.error(f"分析推文时出错: {str(e)}")
        return default_analysis_result(token_symbol)

def analyze_with_openai(prompt):
    """使用OpenAI API分析推文"""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的加密货币市场分析师，请以JSON格式输出分析结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API调用失败: {str(e)}")
        raise

def analyze_with_anthropic(prompt):
    """使用Anthropic Claude API分析推文"""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            system="你是一个专业的加密货币市场分析师，请以JSON格式输出分析结果。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Anthropic API调用失败: {str(e)}")
        raise

def analyze_with_deepseek(prompt):
    """使用Deepseek API分析推文"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业的加密货币市场分析师，请以JSON格式输出分析结果。"},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        response_json = response.json()
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        else:
            logger.error(f"Deepseek API响应格式异常: {response_json}")
            raise Exception("Deepseek API响应格式异常")
    except Exception as e:
        logger.error(f"Deepseek API调用失败: {str(e)}")
        raise

def extract_json_from_text(text):
    """从文本中提取JSON部分"""
    # 尝试查找花括号位置
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx >= 0 and end_idx >= 0:
        return text[start_idx:end_idx+1]
    else:
        raise ValueError("无法在文本中找到JSON")
    
def default_analysis_result(token_symbol):
    """默认的分析结果，当AI分析失败时使用"""
    return {
        "event_type": "未能分析事件类型",
        "impact_level": "Non-Significant",
        "expected_volatility": "±0-1%",
        "key_factors": [
            "AI分析失败，无法提供关键因素",
            "请手动查看推文内容",
            "考虑检查AI API配置"
        ],
        "historical_reference": "未能提供历史参照"
    } 