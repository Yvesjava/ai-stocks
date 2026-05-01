#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻采集员模块
功能：从多个渠道采集新闻，进行清洗、整理、分类后存储为JSON文件
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
import hashlib
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('news_collector')

class NewsCollector:
    def __init__(self):
        """初始化新闻采集器"""
        self.base_dir = 'data/news'
        self.raw_dir = os.path.join(self.base_dir, 'raw')
        self.processed_dir = os.path.join(self.base_dir, 'processed')
        self.structured_dir = os.path.join(self.base_dir, 'structured')
        
        # 确保目录存在
        for dir_path in [self.raw_dir, self.processed_dir, self.structured_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # 模拟新闻来源
        self.news_sources = [
            {'name': '东方财富网', 'type': '财经媒体'},
            {'name': '同花顺', 'type': '财经媒体'},
            {'name': '雪球', 'type': '财经社区'},
            {'name': '财新网', 'type': '财经媒体'},
            {'name': '第一财经', 'type': '财经媒体'},
            {'name': '新浪财经', 'type': '财经媒体'},
            {'name': '凤凰财经', 'type': '财经媒体'},
            {'name': '沪深交易所', 'type': '官方'}
        ]
        
        # 模拟新闻分类
        self.categories = {
            '公司公告': ['年报', '季报', '重大事项', '股权激励', '分红'],
            '公司财报': ['营收', '利润', '业绩', '财务数据'],
            '行业动态': ['政策', '趋势', '竞争', '技术突破'],
            '宏观政策': ['货币政策', '财政政策', '监管政策'],
            '市场行情': ['大盘', '指数', '成交额', '板块轮动'],
            '概念热点': ['AI', '新能源', '元宇宙', '半导体'],
            '突发事件': ['地震', '疫情', '事故', '危机'],
            '监管动态': ['证监会', '处罚', '通报', '新规'],
            '机构研报': ['买入', '评级', '目标价', '分析'],
            '国际市场': ['美股', '港股', '外汇', '原油']
        }
        
        # 模拟股票池
        self.stocks = [
            {'code': '600519', 'name': 'Guizhou Moutai'},
            {'code': '000858', 'name': 'Wuliangye'},
            {'code': '601318', 'name': 'Ping An'},
            {'code': '600036', 'name': 'China Merchants Bank'},
            {'code': '000333', 'name': 'Midea Group'},
            {'code': '000001', 'name': 'Ping An Bank'},
            {'code': '601888', 'name': 'China Tourism Group Duty Free'},
            {'code': '600276', 'name': 'Hengrui Medicine'},
            {'code': '002594', 'name': 'BYD'},
            {'code': '601012', 'name': 'LONGi Green Energy'}
        ]
        
        # 模拟情感倾向
        self.sentiments = ['positive', 'neutral', 'negative']
        
        # 模拟新闻模板
        self.news_templates = [
            '{company} released Q{quarter} {year} report, revenue {revenue} billion yuan, YoY growth {growth}%',
            '{company} expects {year} Q{quarter} net profit to grow {growth}% YoY, exceeding market expectations',
            '{sector} sector benefits from policy support, {company} and related stocks benefit',
            '{company} reached strategic cooperation with {partner} to jointly develop {project}',
            '{company} plans to {action}, analysts give {rating} rating',
            '{company} launched new {product}, market response {reaction}',
            'Macroeconomic data {data}, {sector} sector affected',
            'Regulatory authorities issued {policy}, {company} and other companies may be affected',
            'International market {event}, A-share {sector} sector fluctuates',
            '{company} encountered {issue}, stock price {trend}'
        ]
    
    def generate_news_id(self, content):
        """生成唯一新闻ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_str = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        return "NEWS_{timestamp}_{hash_str}".format(timestamp=timestamp, hash_str=hash_str)
    
    def generate_mock_news(self, count=10):
        """生成模拟新闻数据"""
        news_list = []
        
        for i in range(count):
            # 随机选择来源
            source = random.choice(self.news_sources)
            
            # 随机选择分类
            category = random.choice(list(self.categories.keys()))
            
            # 随机选择股票
            stock = random.choice(self.stocks)
            
            # 随机生成发布时间（最近7天内）
            publish_time = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # 随机生成新闻内容
            template = random.choice(self.news_templates)
            year = datetime.now().year
            quarter = random.randint(1, 4)
            revenue = round(random.uniform(10, 1000), 2)
            growth = round(random.uniform(-20, 50), 2)
            
            # 填充模板
            news_content = template.format(
                company=stock['name'],
                year=year,
                quarter=quarter,
                revenue=revenue,
                growth=growth,
                sector=random.choice(['Technology', 'Finance', 'Consumer', 'Pharmaceutical', 'New Energy']),
                partner=random.choice(['Tencent', 'Alibaba', 'Huawei', 'BYD', 'CATL']),
                project=random.choice(['New Energy Vehicle', 'AI Chip', 'Cloud Computing', 'Biomedicine']),
                action=random.choice(['repurchase shares', 'increase holdings', 'reduce holdings', 'private placement']),
                rating=random.choice(['Buy', 'Outperform', 'Neutral', 'Underperform', 'Sell']),
                product=random.choice(['Smartphone', 'New Energy Vehicle', 'New Drug', 'Smart Device']),
                reaction=random.choice(['enthusiastic', 'flat', 'questioning']),
                data=random.choice(['better than expected', 'in line with expectations', 'worse than expected']),
                policy=random.choice(['new regulation', 'regulatory requirement', 'favorable policy']),
                event=random.choice(['rising', 'falling', 'fluctuating']),
                issue=random.choice(['performance decline', 'lawsuit', 'violation', 'negative report']),
                trend=random.choice(['falling', 'fluctuating', 'rising'])
            )
            
            # 生成新闻ID
            news_id = self.generate_news_id(news_content)
            
            # 构建新闻数据
            news = {
                "news_id": news_id,
                "title": news_content,
                "original_title": news_content,
                "source": source['name'],
                "source_type": source['type'],
                "source_url": "https://example.com/news/{news_id}".format(news_id=news_id),
                "publish_time": publish_time.isoformat(),
                "collect_time": datetime.now().isoformat(),
                "summary": news_content[:100] + "..." if len(news_content) > 100 else news_content,
                "content": news_content,
                "related_stocks": [{
                    "stock_code": stock['code'],
                    "stock_name": stock['name'],
                    "mention_type": "main target"
                }],
                "category": {
                    "primary": category,
                    "secondary": [random.choice(['Technology', 'Finance', 'Consumer', 'Pharmaceutical', 'New Energy'])],
                    "tags": random.sample(self.categories.get(category, []), min(2, len(self.categories.get(category, []))))
                },
                "sentiment": {
                    "overall": random.choice(self.sentiments),
                    "score": round(random.uniform(-1, 1), 2),
                    "reason": "{category} related news".format(category=category)
                },
                "impact_level": random.choice(['high', 'medium', 'low']),
                "market_reaction_expected": "Expected to impact {stock_name} and related sectors".format(stock_name=stock['name']),
                "metadata": {
                    "word_count": len(news_content),
                    "has_image": random.choice([True, False]),
                    "is_original": True,
                    "is_headline": random.choice([True, False])
                }
            }
            
            news_list.append(news)
        
        return news_list
    
    def save_raw_news(self, news_list):
        """保存原始新闻数据"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        raw_date_dir = os.path.join(self.raw_dir, date_str)
        if not os.path.exists(raw_date_dir):
            os.makedirs(raw_date_dir)
        
        # 按来源分组保存
        source_news = {}
        for news in news_list:
            source = news['source']
            if source not in source_news:
                source_news[source] = []
            source_news[source].append(news)
        
        for source, items in source_news.items():
            # 生成安全的文件名（使用英文替代中文）
            source_eng = {
                '东方财富网': 'EastMoney',
                '同花顺': 'iFinD',
                '雪球': 'XueQiu',
                '财新网': 'Caixin',
                '第一财经': 'FirstFinance',
                '新浪财经': 'SinaFinance',
                '凤凰财经': 'PhoenixFinance',
                '沪深交易所': 'SSE_SZSE'
            }.get(source, source)
            filename = "%s.json" % source_eng.replace(' ', '_')
            filepath = os.path.join(raw_date_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(items, f, indent=2)
            
            logger.info("保存原始新闻到 %s，共 %d 条", filepath, len(items))
    
    def process_news(self, news_list):
        """处理新闻数据"""
        processed_news = []
        
        for news in news_list:
            # 模拟去重（这里简化处理，实际项目中需要更复杂的去重逻辑）
            # 模拟分类（这里使用随机分类，实际项目中需要NLP分类）
            # 模拟情感分析（这里使用随机情感，实际项目中需要情感分析模型）
            
            processed_news.append(news)
        
        return processed_news
    
    def save_processed_news(self, processed_news):
        """保存处理后的新闻数据"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        processed_date_dir = os.path.join(self.processed_dir, date_str)
        if not os.path.exists(processed_date_dir):
            os.makedirs(processed_date_dir)
        
        for news in processed_news:
            filename = "%s.json" % news['news_id']
            filepath = os.path.join(processed_date_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(news, f, indent=2)
            
        logger.info("保存处理后新闻到 %s，共 %d 条", processed_date_dir, len(processed_news))
    
    def save_structured_news(self, processed_news):
        """保存结构化新闻数据供下游Agent使用"""
        structured_file = os.path.join(self.structured_dir, 'news_database.json')
        
        # 读取现有数据
        existing_news = []
        if os.path.exists(structured_file):
            with open(structured_file, 'r') as f:
                try:
                    existing_news = json.load(f)
                except:
                    existing_news = []
        
        # 去重（基于news_id）
        existing_ids = {news['news_id'] for news in existing_news}
        new_news = [news for news in processed_news if news['news_id'] not in existing_ids]
        
        # 合并数据
        all_news = existing_news + new_news
        
        # 按发布时间排序（最新的在前）
        all_news.sort(key=lambda x: x['publish_time'], reverse=True)
        
        # 保存数据
        with open(structured_file, 'w') as f:
            json.dump(all_news, f, indent=2)
        
        logger.info("保存结构化新闻到 %s，新增 %d 条，总计 %d 条", structured_file, len(new_news), len(all_news))
    
    def collect(self, count=10):
        """执行采集流程"""
        logger.info("开始采集新闻，目标数量：%d", count)
        
        # 1. 生成模拟新闻
        news_list = self.generate_mock_news(count)
        logger.info("生成 %d 条模拟新闻", len(news_list))
        
        # 2. 保存原始新闻
        self.save_raw_news(news_list)
        
        # 3. 处理新闻
        processed_news = self.process_news(news_list)
        
        # 4. 保存处理后新闻
        self.save_processed_news(processed_news)
        
        # 5. 保存结构化新闻
        self.save_structured_news(processed_news)
        
        logger.info("新闻采集流程完成")
        return processed_news

def main():
    """主函数"""
    collector = NewsCollector()
    
    # 采集10条新闻
    collected_news = collector.collect(10)
    
    # 打印采集结果
    print("\n采集完成，共收集 %d 条新闻" % len(collected_news))
    print("\n前3条新闻示例：")
    for i, news in enumerate(collected_news[:3]):
        print("\n%d. %s" % (i+1, news['title']))
        print("   来源：%s" % news['source'])
        print("   分类：%s" % news['category']['primary'])
        print("   情感：%s" % news['sentiment']['overall'])
        print("   涉及股票：%s" % [stock['stock_name'] for stock in news['related_stocks']])

if __name__ == '__main__':
    main()
