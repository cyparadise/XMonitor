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
    tweets_collection = db.tweets
    logger.debug("推文模型已连接到MongoDB")
except Exception as e:
    logger.error(f"推文模型MongoDB连接失败: {str(e)}")
    db = None
    tweets_collection = None

class Tweet:
    """推文模型类，用于管理Twitter推文和分析结果"""
    
    def __init__(self, tweet_id, project_id, twitter_username, text, token_symbol=None, 
                 analysis=None, created_at=None, _id=None):
        """
        初始化推文
        
        参数:
            tweet_id (str): Twitter推文ID
            project_id (str): 关联的项目ID
            twitter_username (str): 发推文的Twitter用户名
            text (str): 推文内容
            token_symbol (str, optional): 代币符号
            analysis (dict, optional): 分析结果
            created_at (datetime, optional): 创建时间
            _id (ObjectId, optional): MongoDB的ObjectId
        """
        self.tweet_id = tweet_id
        self.project_id = project_id
        self.twitter_username = twitter_username
        self.text = text
        self.token_symbol = token_symbol
        self.analysis = analysis or {}
        self.created_at = created_at or datetime.utcnow()
        self._id = _id
        
    def save(self):
        """保存推文到数据库"""
        if not tweets_collection:
            logger.error("无法保存推文：MongoDB连接未初始化")
            return None
            
        tweet_data = {
            "tweet_id": self.tweet_id,
            "project_id": self.project_id,
            "twitter_username": self.twitter_username,
            "text": self.text,
            "token_symbol": self.token_symbol,
            "analysis": self.analysis,
            "created_at": self.created_at,
        }
        
        if self._id:  # 更新现有推文
            tweets_collection.update_one(
                {"_id": self._id},
                {"$set": tweet_data}
            )
            logger.info(f"已更新推文, ID: {self.tweet_id}")
            return self._id
        else:  # 创建新推文
            result = tweets_collection.insert_one(tweet_data)
            self._id = result.inserted_id
            logger.info(f"已保存新推文, ID: {self.tweet_id}")
            return self._id
    
    def to_dict(self):
        """将推文转换为字典"""
        return {
            "_id": str(self._id) if self._id else None,
            "tweet_id": self.tweet_id,
            "project_id": self.project_id,
            "twitter_username": self.twitter_username,
            "text": self.text,
            "token_symbol": self.token_symbol,
            "analysis": self.analysis,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at)
        }
    
    @classmethod
    def get_by_id(cls, tweet_id):
        """根据ID获取推文"""
        if not tweets_collection:
            logger.error("无法获取推文：MongoDB连接未初始化")
            return None
            
        tweet_data = tweets_collection.find_one({"_id": ObjectId(tweet_id)})
        if not tweet_data:
            return None
            
        return cls(
            tweet_id=tweet_data["tweet_id"],
            project_id=tweet_data["project_id"],
            twitter_username=tweet_data["twitter_username"],
            text=tweet_data["text"],
            token_symbol=tweet_data.get("token_symbol"),
            analysis=tweet_data.get("analysis", {}),
            created_at=tweet_data["created_at"],
            _id=tweet_data["_id"]
        )
    
    @classmethod
    def get_by_twitter_id(cls, twitter_id):
        """根据Twitter ID获取推文"""
        if not tweets_collection:
            logger.error("无法获取推文：MongoDB连接未初始化")
            return None
            
        tweet_data = tweets_collection.find_one({"tweet_id": twitter_id})
        if not tweet_data:
            return None
            
        return cls(
            tweet_id=tweet_data["tweet_id"],
            project_id=tweet_data["project_id"],
            twitter_username=tweet_data["twitter_username"],
            text=tweet_data["text"],
            token_symbol=tweet_data.get("token_symbol"),
            analysis=tweet_data.get("analysis", {}),
            created_at=tweet_data["created_at"],
            _id=tweet_data["_id"]
        )
    
    @classmethod
    def get_project_tweets(cls, project_id, limit=100):
        """获取项目的所有推文"""
        if not tweets_collection:
            logger.error("无法获取推文：MongoDB连接未初始化")
            return []
            
        tweets_data = tweets_collection.find({"project_id": project_id}).sort("created_at", -1).limit(limit)
        
        tweets = []
        for tweet_data in tweets_data:
            tweet = cls(
                tweet_id=tweet_data["tweet_id"],
                project_id=tweet_data["project_id"],
                twitter_username=tweet_data["twitter_username"],
                text=tweet_data["text"],
                token_symbol=tweet_data.get("token_symbol"),
                analysis=tweet_data.get("analysis", {}),
                created_at=tweet_data["created_at"],
                _id=tweet_data["_id"]
            )
            tweets.append(tweet)
            
        return tweets
    
    @classmethod
    def get_recent_tweets(cls, limit=100):
        """获取最近的推文"""
        if not tweets_collection:
            logger.error("无法获取推文：MongoDB连接未初始化")
            return []
            
        tweets_data = tweets_collection.find().sort("created_at", -1).limit(limit)
        
        tweets = []
        for tweet_data in tweets_data:
            tweet = cls(
                tweet_id=tweet_data["tweet_id"],
                project_id=tweet_data["project_id"],
                twitter_username=tweet_data["twitter_username"],
                text=tweet_data["text"],
                token_symbol=tweet_data.get("token_symbol"),
                analysis=tweet_data.get("analysis", {}),
                created_at=tweet_data["created_at"],
                _id=tweet_data["_id"]
            )
            tweets.append(tweet)
            
        return tweets
    
    @classmethod
    def get_by_impact_level(cls, impact_level, limit=100):
        """根据影响等级获取推文"""
        if not tweets_collection:
            logger.error("无法获取推文：MongoDB连接未初始化")
            return []
            
        tweets_data = tweets_collection.find({"analysis.impact_level": impact_level}).sort("created_at", -1).limit(limit)
        
        tweets = []
        for tweet_data in tweets_data:
            tweet = cls(
                tweet_id=tweet_data["tweet_id"],
                project_id=tweet_data["project_id"],
                twitter_username=tweet_data["twitter_username"],
                text=tweet_data["text"],
                token_symbol=tweet_data.get("token_symbol"),
                analysis=tweet_data.get("analysis", {}),
                created_at=tweet_data["created_at"],
                _id=tweet_data["_id"]
            )
            tweets.append(tweet)
            
        return tweets 