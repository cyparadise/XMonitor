#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

def add_project(args):
    """添加新项目"""
    try:
        project = Project(
            name=args.name,
            token_symbol=args.token_symbol,
            twitter_username=args.twitter_username,
            description=args.description
        )
        project_id = project.save()
        
        if project_id:
            logger.info(f"已成功添加项目: {args.name}")
            logger.info(f"项目ID: {project_id}")
            logger.info(f"代币符号: {args.token_symbol}")
            logger.info(f"Twitter用户名: {args.twitter_username}")
            return True
        else:
            logger.error("添加项目失败")
            return False
    except Exception as e:
        logger.error(f"添加项目时出错: {str(e)}")
        return False

def list_projects(args):
    """列出所有项目"""
    try:
        projects = Project.get_all(active_only=args.active_only)
        
        if not projects:
            logger.info("没有找到任何项目")
            return True
        
        logger.info("项目列表:")
        logger.info("=" * 50)
        
        for i, project in enumerate(projects, 1):
            logger.info(f"{i}. 名称: {project.name}")
            logger.info(f"   ID: {project._id}")
            logger.info(f"   代币符号: {project.token_symbol}")
            logger.info(f"   Twitter用户名: {project.twitter_username}")
            logger.info(f"   描述: {project.description}")
            logger.info(f"   状态: {'激活' if project.active else '禁用'}")
            logger.info("-" * 50)
        
        return True
    except Exception as e:
        logger.error(f"列出项目时出错: {str(e)}")
        return False

def update_project(args):
    """更新项目信息"""
    try:
        project = Project.get_by_id(args.id)
        
        if not project:
            logger.error(f"找不到ID为 {args.id} 的项目")
            return False
        
        # 更新项目信息
        if args.name:
            project.name = args.name
        if args.token_symbol:
            project.token_symbol = args.token_symbol
        if args.twitter_username:
            project.twitter_username = args.twitter_username
        if args.description:
            project.description = args.description
        if args.active is not None:
            project.active = args.active
        
        project_id = project.save()
        
        if project_id:
            logger.info(f"已成功更新项目: {project.name}")
            return True
        else:
            logger.error("更新项目失败")
            return False
    except Exception as e:
        logger.error(f"更新项目时出错: {str(e)}")
        return False

def delete_project(args):
    """删除项目"""
    try:
        if not args.force:
            # 二次确认
            confirm = input(f"确定要删除ID为 {args.id} 的项目吗？此操作不可恢复。(y/n): ")
            if confirm.lower() != 'y':
                logger.info("已取消删除操作")
                return True
        
        result = Project.delete(args.id)
        
        if result:
            logger.info(f"已成功删除项目，ID: {args.id}")
            return True
        else:
            logger.error(f"删除项目失败，可能找不到ID为 {args.id} 的项目")
            return False
    except Exception as e:
        logger.error(f"删除项目时出错: {str(e)}")
        return False

def main():
    # 创建主解析器
    parser = argparse.ArgumentParser(description='XMonitor项目管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加项目子命令
    add_parser = subparsers.add_parser('add', help='添加新项目')
    add_parser.add_argument('--name', '-n', required=True, help='项目名称')
    add_parser.add_argument('--token-symbol', '-t', required=True, help='代币符号')
    add_parser.add_argument('--twitter-username', '-u', required=True, help='Twitter用户名，不包含@')
    add_parser.add_argument('--description', '-d', default='', help='项目描述')
    add_parser.set_defaults(func=add_project)
    
    # 列出项目子命令
    list_parser = subparsers.add_parser('list', help='列出所有项目')
    list_parser.add_argument('--active-only', '-a', action='store_true', help='只显示激活的项目')
    list_parser.set_defaults(func=list_projects)
    
    # 更新项目子命令
    update_parser = subparsers.add_parser('update', help='更新项目信息')
    update_parser.add_argument('--id', '-i', required=True, help='项目ID')
    update_parser.add_argument('--name', '-n', help='项目名称')
    update_parser.add_argument('--token-symbol', '-t', help='代币符号')
    update_parser.add_argument('--twitter-username', '-u', help='Twitter用户名，不包含@')
    update_parser.add_argument('--description', '-d', help='项目描述')
    update_parser.add_argument('--active', '-a', type=bool, help='是否激活')
    update_parser.set_defaults(func=update_project)
    
    # 删除项目子命令
    delete_parser = subparsers.add_parser('delete', help='删除项目')
    delete_parser.add_argument('--id', '-i', required=True, help='项目ID')
    delete_parser.add_argument('--force', '-f', action='store_true', help='强制删除，不进行确认')
    delete_parser.set_defaults(func=delete_project)
    
    # 解析命令行参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行相应的功能
    args.func(args)

if __name__ == '__main__':
    main() 