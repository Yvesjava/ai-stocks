#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI股票分析系统主脚本
功能：协调四个核心模块的运行，形成完整的工作流程
"""

import os
import sys
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('stock_analysis_system')

class StockAnalysisSystem:
    def __init__(self):
        """初始化股票分析系统"""
        self.modules = {
            'news_collector': 'news_collector.py',
            'stock_collector': 'stock_collector.py',
            'stock_analyst': 'stock_analyst.py',
            'stock_reporter': 'stock_reporter.py'
        }
        
        # 检查模块是否存在
        for name, file in self.modules.items():
            if not os.path.exists(file):
                logger.error("Module file does not exist: %s", file)
                sys.exit(1)
        
        logger.info("Stock analysis system initialized")
    
    def run_module(self, module_name):
        """运行指定模块"""
        logger.info("Start running %s module", module_name)
        
        try:
            # 动态导入模块
            if module_name == 'news_collector':
                import news_collector
                collector = news_collector.NewsCollector()
                result = collector.collect(15)  # 采集15条新闻
            elif module_name == 'stock_collector':
                import stock_collector
                collector = stock_collector.StockCollector()
                result = collector.collect()
            elif module_name == 'stock_analyst':
                import stock_analyst
                analyst = stock_analyst.StockAnalyst()
                result = analyst.analyze()
            elif module_name == 'stock_reporter':
                import stock_reporter
                reporter = stock_reporter.StockReporter()
                result = reporter.generate_report()
            else:
                logger.error("Unknown module: %s", module_name)
                return False
            
            logger.info("%s module completed", module_name)
            return True
        except Exception as e:
            logger.error("Failed to run %s module: %s", module_name, e)
            return False
    
    def run_full_process(self):
        """运行完整流程"""
        logger.info("Start running full analysis process")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 1. 运行新闻采集员
        if not self.run_module('news_collector'):
            logger.error("News collection failed, process terminated")
            return False
        
        # 短暂延迟，确保文件写入完成
        time.sleep(1)
        
        # 2. 运行股票收集员
        if not self.run_module('stock_collector'):
            logger.error("Stock collection failed, process terminated")
            return False
        
        # 短暂延迟
        time.sleep(1)
        
        # 3. 运行股票分析员
        if not self.run_module('stock_analyst'):
            logger.error("Stock analysis failed, process terminated")
            return False
        
        # 短暂延迟
        time.sleep(1)
        
        # 4. 运行股票报告员
        if not self.run_module('stock_reporter'):
            logger.error("Report generation failed, process terminated")
            return False
        
        # 计算运行时间
        end_time = datetime.now()
        run_time = (end_time - start_time).total_seconds()
        
        logger.info("Full analysis process completed in %.2f seconds", run_time)
        return True
    
    def run_scheduled(self, interval=3600):
        """定时运行流程"""
        logger.info("Start scheduled mode, interval %d seconds", interval)
        
        try:
            while True:
                logger.info("===== Start new round of analysis =====")
                self.run_full_process()
                logger.info("===== Analysis completed, waiting %d seconds =====", interval)
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Scheduled run manually terminated")
            return

def main():
    """主函数"""
    system = StockAnalysisSystem()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == 'scheduled':
            # 定时运行模式
            interval = 3600  # 默认1小时
            if len(sys.argv) > 2:
                try:
                    interval = int(sys.argv[2])
                except:
                    pass
            system.run_scheduled(interval)
        else:
            # 运行指定模块
            module_name = sys.argv[1]
            if module_name in system.modules:
                system.run_module(module_name)
            else:
                print("未知模块：%s" % module_name)
                print("可用模块：%s" % list(system.modules.keys()))
    else:
        # 默认运行完整流程
        system.run_full_process()

if __name__ == '__main__':
    main()
