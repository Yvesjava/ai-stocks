#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
股票收集员模块
功能：分析新闻采集器提供的结构化数据，提取相关股票并进行初步筛选
"""

import os
import json
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/stock_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('stock_collector')

class StockCollector:
    def __init__(self):
        """初始化股票收集器"""
        self.news_structured_file = 'data/news/structured/news_database.json'
        self.stock_list_file = 'data/news/structured/stock_list.json'
        
        # 确保目录存在
        dir_path = os.path.dirname(self.stock_list_file)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # 行业板块映射（简化版）
        self.industry_mapping = {
            'Liquor': ['600519', '000858'],
            'Banking': ['601318', '600036', '000001'],
            'Home Appliances': ['000333'],
            'Pharmaceutical': ['600276'],
            'New Energy': ['002594', '601012'],
            'Duty Free': ['601888']
        }
        
        # 初筛规则
        self.screening_rules = {
            'min_mention_count': 1,  # 最低提及次数
            'max_time_gap': 7,  # 最大时间间隔（天）
            'positive_sentiment_threshold': -1.0,  # 积极情感阈值
            'impact_levels': ['high', 'medium', 'low']  # 关注的影响级别
        }
    
    def load_news_data(self):
        """加载新闻数据"""
        if not os.path.exists(self.news_structured_file):
            logger.warning("News data file does not exist: %s", self.news_structured_file)
            return []
        
        try:
            with open(self.news_structured_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            logger.info("Loaded %d news items", len(news_data))
            return news_data
        except Exception as e:
            logger.error("Failed to load news data: %s", e)
            return []
    
    def extract_stocks_from_news(self, news_data):
        """从新闻中提取股票"""
        stock_mentions = {}
        
        for news in news_data:
            # 检查新闻时间
            try:
                # 尝试解析ISO格式的时间字符串
                publish_time = datetime.strptime(news['publish_time'], '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                try:
                    # 尝试解析不含微秒的ISO格式
                    publish_time = datetime.strptime(news['publish_time'], '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    # 如果解析失败，跳过这条新闻
                    continue
            time_gap = (datetime.now() - publish_time).days
            
            # 过滤时间太久的新闻
            if time_gap > self.screening_rules['max_time_gap']:
                continue
            
            # 提取相关股票
            for stock in news.get('related_stocks', []):
                stock_code = stock['stock_code']
                stock_name = stock['stock_name']
                
                if stock_code not in stock_mentions:
                    stock_mentions[stock_code] = {
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'mentions': 0,
                        'news_ids': [],
                        'sentiment_score': 0,
                        'impact_levels': set(),
                        'latest_news_time': news['publish_time'],
                        'reasons': []
                    }
                
                # 统计提及次数
                stock_mentions[stock_code]['mentions'] += 1
                stock_mentions[stock_code]['news_ids'].append(news['news_id'])
                
                # 累计情感分数
                sentiment_score = news['sentiment'].get('score', 0)
                stock_mentions[stock_code]['sentiment_score'] += sentiment_score
                
                # 记录影响级别
                impact_level = news.get('impact_level', 'low')
                stock_mentions[stock_code]['impact_levels'].add(impact_level)
                
                # 记录最新新闻时间
                if news['publish_time'] > stock_mentions[stock_code]['latest_news_time']:
                    stock_mentions[stock_code]['latest_news_time'] = news['publish_time']
                
                # 提取推荐理由
                try:
                    category = str(news['category']['primary'])
                    summary = str(news['summary'][:50])
                    reason = f"{category}: {summary}"
                    stock_mentions[stock_code]['reasons'].append(reason)
                except Exception:
                    stock_mentions[stock_code]['reasons'].append(
                        f"News mention: {str(news['summary'][:50])}"
                    )
        
        return stock_mentions
    
    def screen_stocks(self, stock_mentions):
        """筛选股票"""
        screened_stocks = []
        
        for stock_code, stock_info in stock_mentions.items():
            # 应用筛选规则
            if stock_info['mentions'] < self.screening_rules['min_mention_count']:
                continue
            
            # 计算平均情感分数
            avg_sentiment = stock_info['sentiment_score'] / stock_info['mentions']
            if avg_sentiment < self.screening_rules['positive_sentiment_threshold']:
                continue
            
            # 检查影响级别
            impact_intersection = set(stock_info['impact_levels']) & set(self.screening_rules['impact_levels'])
            if not impact_intersection:
                continue
            
            # 计算优先级分数
            priority_score = self.calculate_priority_score(stock_info, avg_sentiment)
            
            # 构建筛选结果
            stock_result = {
                "stock_code": stock_code,
                "stock_name": stock_info['stock_name'],
                "source_news": stock_info['news_ids'],
                "selection_reasons": stock_info['reasons'][:3],  # 只保留前3个理由
                "priority_score": priority_score,
                "mention_count": stock_info['mentions'],
                "average_sentiment": round(avg_sentiment, 2),
                "impact_levels": list(stock_info['impact_levels']),
                "latest_news_time": stock_info['latest_news_time'],
                "timestamp": datetime.now().isoformat()
            }
            
            screened_stocks.append(stock_result)
        
        # 按优先级分数排序
        screened_stocks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return screened_stocks
    
    def calculate_priority_score(self, stock_info, avg_sentiment):
        """计算优先级分数"""
        # 基础分数
        base_score = 50
        
        # 提及次数加分（最多30分）
        mention_score = min(stock_info['mentions'] * 5, 30)
        
        # 情感分数（最多15分）
        sentiment_score = max(0, min(avg_sentiment * 15, 15))
        
        # 影响级别加分
        impact_score = 0
        if 'high' in stock_info['impact_levels']:
            impact_score += 10
        if 'medium' in stock_info['impact_levels']:
            impact_score += 5
        
        # 时间因素（越新越高分，最多10分）
        try:
            # 尝试解析ISO格式的时间字符串
            latest_time = datetime.strptime(stock_info['latest_news_time'], '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            try:
                # 尝试解析不含微秒的ISO格式
                latest_time = datetime.strptime(stock_info['latest_news_time'], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                # 如果解析失败，使用当前时间（最低分）
                latest_time = datetime.now() - timedelta(days=7)
        time_gap = (datetime.now() - latest_time).total_seconds() / 3600
        time_score = max(0, 10 - time_gap / 2.4)  # 24小时内满分10分
        
        total_score = base_score + mention_score + sentiment_score + impact_score + time_score
        return round(total_score, 2)
    
    def save_stock_list(self, screened_stocks):
        """保存筛选后的股票列表"""
        # 读取现有数据
        existing_stocks = []
        if os.path.exists(self.stock_list_file):
            with open(self.stock_list_file, 'r', encoding='utf-8') as f:
                try:
                    existing_stocks = json.load(f)
                except:
                    existing_stocks = []
        
        # 去重（基于stock_code）
        existing_codes = {stock['stock_code'] for stock in existing_stocks}
        new_stocks = [stock for stock in screened_stocks if stock['stock_code'] not in existing_codes]
        
        # 合并数据
        all_stocks = existing_stocks + new_stocks
        
        # 按优先级排序
        all_stocks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # 保存数据
        with open(self.stock_list_file, 'w', encoding='utf-8') as f:
            json.dump(all_stocks, f, indent=2)
        
        logger.info("Saved stock list to %s, added %d stocks, total %d stocks", self.stock_list_file, len(new_stocks), len(all_stocks))
        return all_stocks
    
    def collect(self):
        """执行股票收集流程"""
        logger.info("Start collecting stocks")
        
        # 1. 加载新闻数据
        news_data = self.load_news_data()
        if not news_data:
            logger.warning("No news data available for analysis")
            return []
        
        # 2. 从新闻中提取股票
        stock_mentions = self.extract_stocks_from_news(news_data)
        logger.info("Extracted %d stocks from news", len(stock_mentions))
        
        # 3. 筛选股票
        screened_stocks = self.screen_stocks(stock_mentions)
        logger.info("Screened to %d stocks", len(screened_stocks))
        
        # 4. 保存股票列表
        all_stocks = self.save_stock_list(screened_stocks)
        
        logger.info("Stock collection process completed")
        return all_stocks

def main():
    """主函数"""
    collector = StockCollector()
    
    # 执行股票收集
    collected_stocks = collector.collect()
    
    # 打印收集结果
    print("\nCollection completed, screened %d stocks" % len(collected_stocks))
    print("\nTop 5 stocks:")
    for i, stock in enumerate(collected_stocks[:5]):
        print("\n%d. %s (%s)" % (i+1, stock['stock_name'], stock['stock_code']))
        print("   Priority score: %s" % stock['priority_score'])
        print("   Mention count: %s" % stock['mention_count'])
        print("   Average sentiment: %s" % stock['average_sentiment'])
        print("   Impact levels: %s" % ', '.join(stock['impact_levels']))
        print("   Latest news time: %s" % stock['latest_news_time'])
        print("   Selection reasons:")
        for j, reason in enumerate(stock['selection_reasons']):
            print("     %d. %s" % (j+1, reason))

if __name__ == '__main__':
    main()
