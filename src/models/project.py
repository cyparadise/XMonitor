#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime
from bson import ObjectId
import pymongo
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# MongoDB连接
try:
    mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
    db = mongo_client[os.getenv('MONGO_DB_NAME', 'xmonitor')]
    projects_collection = db.projects
    logger.debug("项目模型已连接到MongoDB")
except Exception as e:
    logger.error(f"项目模型MongoDB连接失败: {str(e)}")
    db = None
    projects_collection = None

class Project:
    """项目模型类，用于管理加密货币项目"""
    
    def __init__(self, name, token_symbol, twitter_username, description="", active=True, _id=None):
        """
        初始化项目
        
        参数:
            name (str): 项目名称
            token_symbol (str): 代币符号，如BTC、ETH等
            twitter_username (str): Twitter用户名，不包含@
            description (str): 项目描述
            active (bool): 是否激活监控
            _id (ObjectId, optional): MongoDB的ObjectId
        """
        self.name = name
        self.token_symbol = token_symbol
        self.twitter_username = twitter_username
        self.description = description
        self.active = active
        self._id = _id
        self.created_at = datetime.utcnow()
        
    def save(self):
        """保存项目到数据库"""
        if not projects_collection:
            logger.error("无法保存项目：MongoDB连接未初始化")
            return None
            
        project_data = {
            "name": self.name,
            "token_symbol": self.token_symbol,
            "twitter_username": self.twitter_username,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at,
        }
        
        if self._id:  # 更新现有项目
            projects_collection.update_one(
                {"_id": self._id},
                {"$set": project_data}
            )
            logger.info(f"已更新项目: {self.name}")
            return self._id
        else:  # 创建新项目
            result = projects_collection.insert_one(project_data)
            self._id = result.inserted_id
            logger.info(f"已创建新项目: {self.name}")
            return self._id
    
    def to_dict(self):
        """将项目转换为字典"""
        return {
            "_id": str(self._id) if self._id else None,
            "name": self.name,
            "token_symbol": self.token_symbol,
            "twitter_username": self.twitter_username,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at)
        }
    
    @classmethod
    def get_by_id(cls, project_id):
        """根据ID获取项目"""
        if not projects_collection:
            logger.error("无法获取项目：MongoDB连接未初始化")
            return None
            
        project_data = projects_collection.find_one({"_id": ObjectId(project_id)})
        if not project_data:
            return None
            
        return cls(
            name=project_data["name"],
            token_symbol=project_data["token_symbol"],
            twitter_username=project_data["twitter_username"],
            description=project_data.get("description", ""),
            active=project_data.get("active", True),
            _id=project_data["_id"]
        )
    
    @classmethod
    def get_by_twitter_username(cls, twitter_username):
        """根据Twitter用户名获取项目"""
        if not projects_collection:
            logger.error("无法获取项目：MongoDB连接未初始化")
            return None
            
        project_data = projects_collection.find_one({"twitter_username": twitter_username})
        if not project_data:
            return None
            
        return cls(
            name=project_data["name"],
            token_symbol=project_data["token_symbol"],
            twitter_username=project_data["twitter_username"],
            description=project_data.get("description", ""),
            active=project_data.get("active", True),
            _id=project_data["_id"]
        )
    
    @classmethod
    def get_all(cls, active_only=False):
        """获取所有项目"""
        if not projects_collection:
            logger.error("无法获取项目：MongoDB连接未初始化")
            return []
            
        query = {"active": True} if active_only else {}
        projects_data = projects_collection.find(query)
        
        projects = []
        for project_data in projects_data:
            project = cls(
                name=project_data["name"],
                token_symbol=project_data["token_symbol"],
                twitter_username=project_data["twitter_username"],
                description=project_data.get("description", ""),
                active=project_data.get("active", True),
                _id=project_data["_id"]
            )
            projects.append(project)
            
        return projects
    
    @classmethod
    def delete(cls, project_id):
        """删除项目"""
        if not projects_collection:
            logger.error("无法删除项目：MongoDB连接未初始化")
            return False
            
        result = projects_collection.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0 