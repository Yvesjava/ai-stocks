#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告关联性分析模块
功能：分析新闻、分析、报告之间的关联性，追踪数据演变
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/report_correlation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('report_correlation')


class ReportCorrelationAnalyzer:
    """报告关联性分析器"""
    
    def __init__(self):
        self.base_dir = 'data/news'
        self.structured_dir = os.path.join(self.base_dir, 'structured')
        self.analysis_dir = os.path.join(self.base_dir, 'analysis')
        self.reports_dir = os.path.join(self.base_dir, 'reports')
        
    def load_historical_data(self, days: int = 7) -> Dict[str, List]:
        """加载历史数据"""
        historical_data = {
            'news': [],
            'analysis': [],
            'reports': []
        }
        
        # 加载历史新闻数据
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_dir = os.path.join(self.base_dir, 'processed', date)
            if os.path.exists(date_dir):
                for file_name in os.listdir(date_dir):
                    if file_name.startswith('NEWS_') and file_name.endswith('.json'):
                        file_path = os.path.join(date_dir, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                news_data = json.load(f)
                                if isinstance(news_data, list):
                                    historical_data['news'].extend(news_data)
                                else:
                                    historical_data['news'].append(news_data)
                        except Exception as e:
                            logger.error(f"加载新闻数据失败 {file_path}: {e}")
        
        # 加载历史分析数据
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_dir = os.path.join(self.analysis_dir, date)
            analysis_file = os.path.join(date_dir, 'stock_analysis.json')
            if os.path.exists(analysis_file):
                try:
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                        if isinstance(analysis_data, list):
                            historical_data['analysis'].extend(analysis_data)
                        else:
                            historical_data['analysis'].append(analysis_data)
                except Exception as e:
                    logger.error(f"加载分析数据失败 {analysis_file}: {e}")
        
        # 加载历史报告数据
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_dir = os.path.join(self.reports_dir, date)
            if os.path.exists(date_dir):
                for file_name in os.listdir(date_dir):
                    if file_name.startswith('stock_report_') and file_name.endswith('.json'):
                        file_path = os.path.join(date_dir, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                report_data = json.load(f)
                                historical_data['reports'].append(report_data)
                        except Exception as e:
                            logger.error(f"加载报告数据失败 {file_path}: {e}")
        
        return historical_data
    
    def analyze_stock_evolution(self, stock_code: str, days: int = 7) -> Dict:
        """分析股票数据演变"""
        historical_data = self.load_historical_data(days)
        
        evolution = {
            'stock_code': stock_code,
            'time_series': [],
            'news_trend': [],
            'recommendation_trend': [],
            'sentiment_trend': []
        }
        
        # 按日期分析
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # 统计当日新闻
            day_news = [n for n in historical_data['news'] if date in str(n.get('published_at', '')) and stock_code in str(n)]
            
            # 查找当日分析
            day_analysis = None
            for analysis in historical_data['analysis']:
                if isinstance(analysis, dict) and analysis.get('stock_code') == stock_code:
                    if date in analysis.get('analysis_time', ''):
                        day_analysis = analysis
                        break
            
            # 查找当日报告
            day_report = None
            for report in historical_data['reports']:
                if date in report.get('report_date', ''):
                    for stock in report.get('recommended_stocks', []):
                        if stock.get('stock_code') == stock_code:
                            day_report = stock
                            break
                    if day_report:
                        break
            
            # 构建时间序列数据
            time_point = {
                'date': date,
                'news_count': len(day_news),
                'analysis': day_analysis,
                'report': day_report
            }
            
            evolution['time_series'].append(time_point)
            
            # 分析新闻趋势
            if day_news:
                avg_sentiment = sum(n.get('sentiment', {}).get('score', 0) for n in day_news) / len(day_news)
                evolution['news_trend'].append({'date': date, 'count': len(day_news), 'sentiment': avg_sentiment})
                evolution['sentiment_trend'].append({'date': date, 'score': avg_sentiment})
            
            # 分析推荐趋势
            if day_analysis:
                recommendation = day_analysis.get('recommendation', '中性')
                evolution['recommendation_trend'].append({'date': date, 'recommendation': recommendation})
        
        # 按日期排序
        evolution['time_series'].sort(key=lambda x: x['date'])
        evolution['news_trend'].sort(key=lambda x: x['date'])
        evolution['recommendation_trend'].sort(key=lambda x: x['date'])
        evolution['sentiment_trend'].sort(key=lambda x: x['date'])
        
        return evolution
    
    def analyze_news_impact(self, stock_code: str, days: int = 7) -> Dict:
        """分析新闻对推荐的影响"""
        evolution = self.analyze_stock_evolution(stock_code, days)
        
        impact_analysis = {
            'stock_code': stock_code,
            'news_sentiment_correlation': 0,
            'news_count_impact': {},
            'key_events': []
        }
        
        # 分析新闻情绪与推荐的相关性
        sentiment_scores = [item['score'] for item in evolution['sentiment_trend']]
        recommendations = []
        
        # 将推荐评级转换为数值
        recommendation_map = {
            '强烈推荐': 5,
            '推荐': 4,
            '谨慎推荐': 3,
            '中性': 2,
            '不推荐': 1
        }
        
        for item in evolution['recommendation_trend']:
            rec = item['recommendation']
            recommendations.append(recommendation_map.get(rec, 2))
        
        # 简单相关性分析
        if sentiment_scores and recommendations:
            # 计算皮尔逊相关系数
            import statistics
            if len(sentiment_scores) == len(recommendations):
                n = len(sentiment_scores)
                mean_sentiment = statistics.mean(sentiment_scores)
                mean_recommendation = statistics.mean(recommendations)
                
                numerator = sum((s - mean_sentiment) * (r - mean_recommendation) for s, r in zip(sentiment_scores, recommendations))
                denominator = (sum((s - mean_sentiment) ** 2 for s in sentiment_scores) * sum((r - mean_recommendation) ** 2 for r in recommendations)) ** 0.5
                
                if denominator > 0:
                    impact_analysis['news_sentiment_correlation'] = numerator / denominator
        
        # 分析新闻数量的影响
        for time_point in evolution['time_series']:
            news_count = time_point['news_count']
            analysis = time_point['analysis']
            if analysis:
                recommendation = analysis.get('recommendation', '中性')
                if news_count not in impact_analysis['news_count_impact']:
                    impact_analysis['news_count_impact'][news_count] = []
                impact_analysis['news_count_impact'][news_count].append(recommendation)
        
        # 识别关键事件
        for i, time_point in enumerate(evolution['time_series']):
            if time_point['news_count'] > 3:  # 新闻数量异常多
                key_event = {
                    'date': time_point['date'],
                    'event_type': '新闻密集发布',
                    'news_count': time_point['news_count'],
                    'analysis': time_point['analysis']
                }
                impact_analysis['key_events'].append(key_event)
        
        return impact_analysis
    
    def generate_correlation_report(self, stock_code: str, days: int = 7) -> Dict:
        """生成关联性分析报告"""
        evolution = self.analyze_stock_evolution(stock_code, days)
        impact_analysis = self.analyze_news_impact(stock_code, days)
        
        report = {
            'report_date': datetime.now().isoformat(),
            'stock_code': stock_code,
            'analysis_period': f"最近{days}天",
            'evolution_analysis': evolution,
            'impact_analysis': impact_analysis,
            'summary': self._generate_summary(evolution, impact_analysis),
            'insights': self._generate_insights(evolution, impact_analysis)
        }
        
        # 保存报告
        report_dir = os.path.join(self.reports_dir, datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        report_file = os.path.join(report_dir, 'correlation_report_%s.json' % stock_code)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"生成关联性分析报告: {report_file}")
        return report
    
    def _generate_summary(self, evolution: Dict, impact_analysis: Dict) -> str:
        """生成总结"""
        stock_code = evolution['stock_code']
        time_series = evolution['time_series']
        
        summary = f"股票 {stock_code} 关联性分析报告\n"
        summary += f"分析期间: {time_series[0]['date']} 至 {time_series[-1]['date']}\n\n"
        
        # 新闻分析
        total_news = sum(point['news_count'] for point in time_series)
        summary += f"新闻总量: {total_news}条\n"
        
        # 推荐趋势
        recommendations = [item['recommendation'] for item in evolution['recommendation_trend']]
        if recommendations:
            latest_recommendation = recommendations[-1]
            summary += f"最新推荐评级: {latest_recommendation}\n"
        
        # 情绪相关性
        correlation = impact_analysis['news_sentiment_correlation']
        summary += f"新闻情绪与推荐相关性: {correlation:.2f}\n"
        
        return summary
    
    def _generate_insights(self, evolution: Dict, impact_analysis: Dict) -> List[str]:
        """生成洞察"""
        insights = []
        
        # 分析推荐变化
        recommendations = evolution['recommendation_trend']
        if len(recommendations) > 1:
            recent = recommendations[-1]['recommendation']
            previous = recommendations[-2]['recommendation']
            if recent != previous:
                insights.append(f"推荐评级从 '{previous}' 变为 '{recent}'")
        
        # 分析新闻影响
        correlation = impact_analysis['news_sentiment_correlation']
        if abs(correlation) > 0.7:
            if correlation > 0:
                insights.append("新闻情绪与推荐评级呈强正相关")
            else:
                insights.append("新闻情绪与推荐评级呈强负相关")
        
        # 分析关键事件
        if impact_analysis['key_events']:
            event = impact_analysis['key_events'][-1]
            insights.append(f"最近关键事件: {event['event_type']} (日期: {event['date']})")
        
        return insights


def main():
    """测试报告关联性分析"""
    analyzer = ReportCorrelationAnalyzer()
    
    # 测试分析单只股票
    stock_code = "600519"  # 贵州茅台
    report = analyzer.generate_correlation_report(stock_code)
    
    print("报告关联性分析测试")
    print("=" * 60)
    print(report['summary'])
    print("\n洞察:")
    for i, insight in enumerate(report['insights'], 1):
        print(f"{i}. {insight}")
    
    print(f"\n报告已保存到: data/news/reports/{datetime.now().strftime('%Y-%m-%d')}/correlation_report_{stock_code}.json")


if __name__ == '__main__':
    main()
