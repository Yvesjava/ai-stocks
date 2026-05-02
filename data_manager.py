#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
功能：管理从新闻到分析到报告的完整数据链路
"""

import os
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/data_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('data_manager')


class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.base_dir = 'data/news'
        self.raw_dir = os.path.join(self.base_dir, 'raw')
        self.processed_dir = os.path.join(self.base_dir, 'processed')
        self.structured_dir = os.path.join(self.base_dir, 'structured')
        self.reports_dir = os.path.join(self.base_dir, 'reports')
        self.analysis_dir = os.path.join(self.base_dir, 'analysis')
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.raw_dir,
            self.processed_dir,
            self.structured_dir,
            self.reports_dir,
            self.analysis_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
            # 按日期创建子目录
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_dir = os.path.join(directory, date_str)
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
    
    def get_date_directory(self, data_type, date=None):
        """获取指定类型和日期的目录"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        dir_map = {
            'raw': self.raw_dir,
            'processed': self.processed_dir,
            'structured': self.structured_dir,
            'reports': self.reports_dir,
            'analysis': self.analysis_dir
        }
        
        base_dir = dir_map.get(data_type, self.base_dir)
        return os.path.join(base_dir, date)
    
    def save_news_data(self, news_data, source, date=None):
        """保存新闻数据"""
        date_dir = self.get_date_directory('raw', date)
        file_path = os.path.join(date_dir, '%s.json' % source)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, indent=2, ensure_ascii=False)
            logger.info("保存新闻数据到 %s", file_path)
            return file_path
        except Exception as e:
            logger.error("保存新闻数据失败: %s", e)
            return None
    
    def save_processed_news(self, processed_news, date=None):
        """保存处理后的新闻数据"""
        date_dir = self.get_date_directory('processed', date)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = os.path.join(date_dir, 'NEWS_%s_%s.json' % (timestamp, os.urandom(4).encode('hex')))
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(processed_news, f, indent=2, ensure_ascii=False)
            logger.info("保存处理后的新闻数据到 %s", file_path)
            return file_path
        except Exception as e:
            logger.error("保存处理后的新闻数据失败: %s", e)
            return None
    
    def save_stock_analysis(self, analysis_data, date=None):
        """保存股票分析数据"""
        date_dir = self.get_date_directory('analysis', date)
        file_path = os.path.join(date_dir, 'stock_analysis.json')
        
        try:
            # 保存按日期的分析数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            # 同时更新全局分析文件
            global_file = os.path.join(self.structured_dir, 'stock_analysis.json')
            with open(global_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            logger.info("保存股票分析数据到 %s 和 %s", file_path, global_file)
            return file_path
        except Exception as e:
            logger.error("保存股票分析数据失败: %s", e)
            return None
    
    def save_stock_report(self, report_data, date=None):
        """保存股票报告数据"""
        date_dir = self.get_date_directory('reports', date)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = os.path.join(date_dir, 'stock_report_%s.json' % timestamp)
        
        try:
            # 保存报告数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            # 同时更新最新报告文件
            latest_file = os.path.join(self.structured_dir, 'stock_report.json')
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info("保存股票报告数据到 %s 和 %s", file_path, latest_file)
            return file_path
        except Exception as e:
            logger.error("保存股票报告数据失败: %s", e)
            return None
    
    def load_news_data(self, source, date=None):
        """加载新闻数据"""
        date_dir = self.get_date_directory('raw', date)
        file_path = os.path.join(date_dir, '%s.json' % source)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("加载新闻数据从 %s", file_path)
            return data
        except Exception as e:
            logger.error("加载新闻数据失败: %s", e)
            return []
    
    def load_processed_news(self, date=None):
        """加载处理后的新闻数据"""
        date_dir = self.get_date_directory('processed', date)
        processed_news = []
        
        try:
            for file_name in os.listdir(date_dir):
                if file_name.startswith('NEWS_') and file_name.endswith('.json'):
                    file_path = os.path.join(date_dir, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        news = json.load(f)
                        if isinstance(news, list):
                            processed_news.extend(news)
                        else:
                            processed_news.append(news)
            return processed_news
        except Exception as e:
            logger.error("加载处理后的新闻数据失败: %s", e)
            return []
    
    def load_stock_analysis(self, date=None):
        """加载股票分析数据"""
        if date:
            date_dir = self.get_date_directory('analysis', date)
            file_path = os.path.join(date_dir, 'stock_analysis.json')
        else:
            file_path = os.path.join(self.structured_dir, 'stock_analysis.json')
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error("加载股票分析数据失败: %s", e)
            return []
    
    def load_stock_report(self, date=None):
        """加载股票报告数据"""
        if date:
            date_dir = self.get_date_directory('reports', date)
            # 找到最新的报告文件
            files = [f for f in os.listdir(date_dir) if f.startswith('stock_report_') and f.endswith('.json')]
            if files:
                files.sort(reverse=True)
                file_path = os.path.join(date_dir, files[0])
            else:
                return {}
        else:
            # 默认加载最新的报告
            file_path = os.path.join(self.structured_dir, 'stock_report.json')
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error("加载股票报告数据失败: %s", e)
            return {}
    
    def get_data_chain(self, stock_code, date=None):
        """获取股票的完整数据链路"""
        data_chain = {
            'stock_code': stock_code,
            'news': [],
            'analysis': {},
            'report': {}
        }
        
        # 加载相关新闻
        processed_news = self.load_processed_news(date)
        data_chain['news'] = [news for news in processed_news if stock_code in str(news)]
        
        # 加载分析数据
        analysis_data = self.load_stock_analysis(date)
        for analysis in analysis_data:
            if analysis.get('stock_code') == stock_code:
                data_chain['analysis'] = analysis
                break
        
        # 加载报告数据
        report_data = self.load_stock_report(date)
        if report_data:
            for stock in report_data.get('recommended_stocks', []):
                if stock.get('stock_code') == stock_code:
                    data_chain['report'] = stock
                    break
        
        return data_chain
    
    def get_data_statistics(self, date=None):
        """获取数据统计信息"""
        stats = {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'news_count': 0,
            'stock_analysis_count': 0,
            'recommended_stocks_count': 0
        }
        
        # 统计新闻数量
        processed_news = self.load_processed_news(date)
        stats['news_count'] = len(processed_news)
        
        # 统计分析股票数量
        analysis_data = self.load_stock_analysis(date)
        stats['stock_analysis_count'] = len(analysis_data)
        
        # 统计推荐股票数量
        report_data = self.load_stock_report(date)
        stats['recommended_stocks_count'] = len(report_data.get('recommended_stocks', []))
        
        return stats


def main():
    """测试数据管理器"""
    data_manager = DataManager()
    
    print("测试数据管理器...")
    
    # 测试获取目录
    date = datetime.now().strftime('%Y-%m-%d')
    print("今日日期: %s" % date)
    print("原始新闻目录: %s" % data_manager.get_date_directory('raw'))
    print("处理后新闻目录: %s" % data_manager.get_date_directory('processed'))
    print("分析数据目录: %s" % data_manager.get_date_directory('analysis'))
    print("报告目录: %s" % data_manager.get_date_directory('reports'))
    
    # 测试数据统计
    stats = data_manager.get_data_statistics()
    print("\n数据统计:")
    for key, value in stats.items():
        print("%s: %s" % (key, value))
    
    # 测试数据链路
    sample_stock = "600519"
    data_chain = data_manager.get_data_chain(sample_stock)
    print("\n股票 %s 的数据链路:" % sample_stock)
    print("相关新闻数量: %d" % len(data_chain['news']))
    print("是否有分析数据: %s" % ('是' if data_chain['analysis'] else '否'))
    print("是否在推荐报告中: %s" % ('是' if data_chain['report'] else '否'))


if __name__ == '__main__':
    main()
