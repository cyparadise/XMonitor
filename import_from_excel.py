#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模型
from src.models.project import Project

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """从Excel文件导入项目数据的主函数"""
    excel_path = os.getenv('PROJECTS_EXCEL_PATH', 'data/projects.xlsx')
    
    logger.info(f"开始从Excel文件导入项目: {excel_path}")
    
    try:
        # 导入项目
        imported_ids = Project.import_from_excel(excel_path)
        
        if imported_ids:
            logger.info(f"成功导入 {len(imported_ids)} 个项目")
        else:
            logger.warning("没有成功导入任何项目，请检查Excel文件")
            
    except Exception as e:
        logger.error(f"导入过程中发生错误: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 导入完成！\n")
    else:
        print("\n❌ 导入失败，请检查错误信息。\n") 