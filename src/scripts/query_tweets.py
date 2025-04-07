#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.tweet import Tweet
from src.models.project import Project

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def format_impact_level(impact_level):
    """格式化影响等级，添加表情符号"""
    if impact_level == "Extremely Bullish":
        return "🟢🟢 极度看涨"
    elif impact_level == "Bullish":
        return "🟢 看涨"
    elif impact_level == "Non-Significant":
        return "⚪ 无显著影响"
    elif impact_level == "Bearish":
        return "🔴 看跌"
    elif impact_level == "Extremely Bearish":
        return "🔴🔴 极度看跌"
    else:
        return impact_level

def print_tweet_info(tweet):
    """打印推文信息"""
    # 查找项目信息
    project = Project.get_by_id(tweet.project_id)
    project_name = project.name if project else "未知项目"
    
    # 格式化时间
    created_at = tweet.created_at
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            pass
    
    if isinstance(created_at, datetime):
        created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
    else:
        created_at_str = str(created_at)
    
    # 分析结果
    analysis = tweet.analysis or {}
    impact_level = analysis.get('impact_level', '未分析')
    expected_volatility = analysis.get('expected_volatility', '未知')
    event_type = analysis.get('event_type', '未分类')
    key_factors = analysis.get('key_factors', [])
    historical_reference = analysis.get('historical_reference', '无历史参照')
    
    # 打印信息
    logger.info("=" * 70)
    logger.info(f"推文ID: {tweet.tweet_id}")
    logger.info(f"项目: {project_name} ({tweet.token_symbol})")
    logger.info(f"Twitter账号: @{tweet.twitter_username}")
    logger.info(f"发布时间: {created_at_str}")
    logger.info(f"影响等级: {format_impact_level(impact_level)}")
    logger.info(f"预期波动: {expected_volatility}")
    logger.info(f"事件类型: {event_type}")
    logger.info(f"推文内容:\n{tweet.text}")
    
    if key_factors:
        logger.info("\n关键因素:")
        for i, factor in enumerate(key_factors, 1):
            logger.info(f"{i}. {factor}")
    
    logger.info(f"\n历史参照: {historical_reference}")
    logger.info("-" * 70)

def query_recent_tweets(args):
    """查询最近的推文"""
    try:
        limit = args.limit
        tweets = Tweet.get_recent_tweets(limit=limit)
        
        if not tweets:
            logger.info("没有找到任何推文")
            return True
        
        logger.info(f"最近 {len(tweets)} 条推文:")
        
        for tweet in tweets:
            print_tweet_info(tweet)
        
        return True
    except Exception as e:
        logger.error(f"查询最近推文时出错: {str(e)}")
        return False

def query_project_tweets(args):
    """查询特定项目的推文"""
    try:
        project_id = args.project_id
        limit = args.limit
        
        if not project_id:
            # 查询项目列表
            projects = Project.get_all()
            if not projects:
                logger.info("没有找到任何项目")
                return True
            
            logger.info("请选择一个项目:")
            for i, project in enumerate(projects, 1):
                logger.info(f"{i}. {project.name} ({project.token_symbol})")
            
            choice = input("请输入项目编号: ")
            try:
                index = int(choice) - 1
                if 0 <= index < len(projects):
                    project_id = str(projects[index]._id)
                else:
                    logger.error("无效的项目编号")
                    return False
            except ValueError:
                logger.error("请输入有效的数字")
                return False
        
        # 查找项目信息
        project = Project.get_by_id(project_id)
        if not project:
            logger.error(f"找不到ID为 {project_id} 的项目")
            return False
        
        logger.info(f"查询项目: {project.name} ({project.token_symbol})")
        
        # 查询项目推文
        tweets = Tweet.get_project_tweets(project_id, limit=limit)
        
        if not tweets:
            logger.info("该项目没有任何推文记录")
            return True
        
        logger.info(f"找到 {len(tweets)} 条推文:")
        
        for tweet in tweets:
            print_tweet_info(tweet)
        
        return True
    except Exception as e:
        logger.error(f"查询项目推文时出错: {str(e)}")
        return False

def query_impact_tweets(args):
    """查询特定影响等级的推文"""
    try:
        impact_level = args.impact_level
        limit = args.limit
        
        if not impact_level:
            # 显示可选的影响等级
            impact_levels = [
                "Extremely Bullish",
                "Bullish",
                "Non-Significant",
                "Bearish",
                "Extremely Bearish"
            ]
            
            logger.info("请选择影响等级:")
            for i, level in enumerate(impact_levels, 1):
                logger.info(f"{i}. {format_impact_level(level)}")
            
            choice = input("请输入影响等级编号: ")
            try:
                index = int(choice) - 1
                if 0 <= index < len(impact_levels):
                    impact_level = impact_levels[index]
                else:
                    logger.error("无效的影响等级编号")
                    return False
            except ValueError:
                logger.error("请输入有效的数字")
                return False
        
        # 查询推文
        tweets = Tweet.get_by_impact_level(impact_level, limit=limit)
        
        if not tweets:
            logger.info(f"没有找到影响等级为 {format_impact_level(impact_level)} 的推文")
            return True
        
        logger.info(f"找到 {len(tweets)} 条影响等级为 {format_impact_level(impact_level)} 的推文:")
        
        for tweet in tweets:
            print_tweet_info(tweet)
        
        return True
    except Exception as e:
        logger.error(f"查询影响等级推文时出错: {str(e)}")
        return False

def export_tweets(args):
    """导出推文数据为JSON文件"""
    try:
        output_file = args.output
        project_id = args.project_id
        limit = args.limit
        
        # 查询推文
        if project_id:
            tweets = Tweet.get_project_tweets(project_id, limit=limit)
            file_prefix = f"project_{project_id}"
        else:
            tweets = Tweet.get_recent_tweets(limit=limit)
            file_prefix = "all_tweets"
        
        if not tweets:
            logger.info("没有找到任何推文")
            return True
        
        # 如果没有指定输出文件，则自动生成一个
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{file_prefix}_{timestamp}.json"
        
        # 转换为字典列表
        tweets_data = [tweet.to_dict() for tweet in tweets]
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已将 {len(tweets)} 条推文导出到 {output_file}")
        return True
    except Exception as e:
        logger.error(f"导出推文时出错: {str(e)}")
        return False

def main():
    # 创建主解析器
    parser = argparse.ArgumentParser(description='XMonitor推文查询工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 查询最近推文子命令
    recent_parser = subparsers.add_parser('recent', help='查询最近的推文')
    recent_parser.add_argument('--limit', '-l', type=int, default=10, help='最大返回数量')
    recent_parser.set_defaults(func=query_recent_tweets)
    
    # 查询项目推文子命令
    project_parser = subparsers.add_parser('project', help='查询特定项目的推文')
    project_parser.add_argument('--project-id', '-p', help='项目ID')
    project_parser.add_argument('--limit', '-l', type=int, default=10, help='最大返回数量')
    project_parser.set_defaults(func=query_project_tweets)
    
    # 查询影响等级推文子命令
    impact_parser = subparsers.add_parser('impact', help='查询特定影响等级的推文')
    impact_parser.add_argument('--impact-level', '-i', help='影响等级')
    impact_parser.add_argument('--limit', '-l', type=int, default=10, help='最大返回数量')
    impact_parser.set_defaults(func=query_impact_tweets)
    
    # 导出推文子命令
    export_parser = subparsers.add_parser('export', help='导出推文数据为JSON文件')
    export_parser.add_argument('--output', '-o', help='输出文件名')
    export_parser.add_argument('--project-id', '-p', help='项目ID，如不指定则导出所有推文')
    export_parser.add_argument('--limit', '-l', type=int, default=100, help='最大导出数量')
    export_parser.set_defaults(func=export_tweets)
    
    # 解析命令行参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行相应的功能
    args.func(args)

if __name__ == '__main__':
    main() 