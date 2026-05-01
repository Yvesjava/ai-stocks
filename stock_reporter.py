#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票报告员模块
功能：对分析后的股票进行最终筛选，生成推荐简报和摘要，并通过多渠道通知
"""

import os
import json
import logging
from datetime import datetime
from notification_service import NotificationService
from data_manager import DataManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/stock_reporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('stock_reporter')

class StockReporter:
    def __init__(self):
        """初始化股票报告员"""
        # 初始化数据管理器和通知服务
        self.data_manager = DataManager()
        self.notification_service = NotificationService()
        
        # 最终筛选规则
        self.final_screening_rules = {
            'min_recommendation': 'Hold',  # 最低推荐评级
            'max_risk_level': 'Medium',  # 最高风险等级
            'min_priority_score': 50,  # 最低优先级分数
            'max_stocks': 10  # 最多推荐股票数量
        }
        
        # 推荐评级映射（用于比较）
        self.recommendation_map = {
            'Strong Buy': 5,
            'Buy': 4,
            'Hold': 3,
            'Neutral': 2,
            'Sell': 1
        }
        
        # 风险等级映射（用于比较）
        self.risk_level_map = {
            'Low': 1,
            'Medium': 2,
            'High': 3
        }
        
        # 中文映射
        self.chinese_recommendation_map = {
            '强烈推荐': 'Strong Buy',
            '推荐': 'Buy',
            '谨慎推荐': 'Hold',
            '中性': 'Neutral',
            '不推荐': 'Sell'
        }
        
        self.chinese_risk_map = {
            '低': 'Low',
            '中': 'Medium',
            '高': 'High'
        }

        self.stock_name_cn_map = {
            'LONGi Green Energy': '隆基绿能',
            'BYD': '比亚迪',
            'Midea Group': '美的集团',
            'Wuliangye': '五粮液',
            'China Merchants Bank': '招商银行',
            'Hengrui Medicine': '恒瑞医药',
            'Ping An': '中国平安',
            'Guizhou Moutai': '贵州茅台',
            'Ping An Bank': '平安银行',
            'China Tourism Group Duty Free': '中国中免'
        }

        self.stock_current_price_map = {
            '601012': 25.50,
            '002594': 350.20,
            '000333': 580.30,
            '000858': 380.10,
            '600036': 520.80,
            '600276': 45.60,
            '601318': 48.50,
            '600519': 1680.30,
            '000001': 12.80,
            '601888': 75.90
        }
    
    def load_analysis_results(self):
        """加载分析结果"""
        try:
            analysis_results = self.data_manager.load_stock_analysis()
            logger.info("加载 %d 条分析结果", len(analysis_results))
            return analysis_results
        except Exception as e:
            logger.error("加载分析结果失败：%s", e)
            return []
    
    def final_screening(self, analysis_results):
        """最终筛选股票"""
        logger.info("开始最终筛选，共 %d 只股票", len(analysis_results))
        
        filtered_stocks = []
        for stock in analysis_results:
            # 检查推荐评级（处理中文）
            recommendation = stock.get('recommendation', 'Neutral')
            if recommendation in self.chinese_recommendation_map:
                recommendation = self.chinese_recommendation_map[recommendation]
            if self.recommendation_map.get(recommendation, 0) < self.recommendation_map.get(self.final_screening_rules['min_recommendation'], 3):
                continue
            
            # 检查风险等级（处理中文）
            risk_level = stock.get('risk_level', 'Medium')
            if risk_level in self.chinese_risk_map:
                risk_level = self.chinese_risk_map[risk_level]
            if self.risk_level_map.get(risk_level, 2) > self.risk_level_map.get(self.final_screening_rules['max_risk_level'], 2):
                continue
            
            # 检查优先级分数
            priority_score = stock.get('priority_score', 0)
            if priority_score < self.final_screening_rules['min_priority_score']:
                continue
            
            filtered_stocks.append(stock)
        
        # 按优先级分数排序
        filtered_stocks.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # 限制推荐数量
        filtered_stocks = filtered_stocks[:self.final_screening_rules['max_stocks']]
        
        logger.info("筛选完成，共 %d 只推荐股票", len(filtered_stocks))
        return filtered_stocks
    
    def generate_stock_brief(self, stock):
        """生成股票简报"""
        brief = {
            "stock_code": stock['stock_code'],
            "stock_name": stock['stock_name'],
            "recommendation": stock['recommendation'],
            "risk_level": stock['risk_level'],
            "target_price": stock.get('target_price', 0),
            "priority_score": stock.get('priority_score', 0),
            "analysis_time": stock.get('analysis_time', datetime.now().isoformat()),
            "key_highlights": [],
            "brief": "",
            "risk_warning": "",
            "action_suggestion": ""
        }
        
        # 从分析报告中提取信息
        analysis_report = stock.get('analysis_report', {})
        
        # 核心逻辑
        brief['brief'] = analysis_report.get('comprehensive_opinion', '暂无综合观点')
        
        # 技术面关键点
        technical_analysis = analysis_report.get('technical_analysis', '')
        if '金叉' in technical_analysis or '多头' in technical_analysis:
            brief['key_highlights'].append("技术面呈现金叉或多头排列")
        if '突破' in technical_analysis:
            brief['key_highlights'].append("技术面突破形态")
        
        # 基本面关键点
        fundamental_analysis = analysis_report.get('fundamental_analysis', '')
        if '增长' in fundamental_analysis:
            brief['key_highlights'].append("业绩增长预期")
        if '改善' in fundamental_analysis:
            brief['key_highlights'].append("基本面持续改善")
        
        # 消息面关键点
        news_analysis = analysis_report.get('news_analysis', '')
        if '积极' in news_analysis or '正面' in news_analysis:
            brief['key_highlights'].append("消息面积极")
        
        # 风险提示
        reasoning = stock.get('reasoning', '')
        if '风险' in reasoning:
            brief['risk_warning'] = reasoning
        
        # 操作建议
        brief['action_suggestion'] = self.generate_action_suggestion(stock['recommendation'])
        
        return brief
    
    def generate_action_suggestion(self, recommendation):
        """生成操作建议"""
        if recommendation in ['Strong Buy', '强烈推荐']:
            return '积极买入，可逢低加仓'
        elif recommendation in ['Buy', '推荐']:
            return '适度买入，持有待涨'
        elif recommendation in ['Hold', '谨慎推荐']:
            return '以观察为主，适时布局'
        elif recommendation in ['Neutral', '中性']:
            return '保持观察，等待机会'
        else:
            return '建议规避'
    
    def generate_summary(self, filtered_stocks):
        """生成摘要"""
        if not filtered_stocks:
            return "暂无符合条件的推荐股票"
        
        date_str = datetime.now().strftime('%Y年%m月%d日')
        summary = "# [强亿] 股票推荐报告\n\n"
        summary += "> **生成时间**：%s\n" % date_str
        summary += "> **推荐股票数量**：%d只\n\n" % len(filtered_stocks)
        
        summary += "## [统计] 市场概览\n"
        summary += "### 市场简评\n"
        summary += "市场整体呈现震荡走势，板块轮动加速。\n"
        summary += "推荐股票主要集中在业绩增长明确、技术形态良好的个股。\n"
        summary += "投资者可关注基本面改善且消息面积极的优质标的。\n\n"
        
        # 统计推荐情况
        recommendation_counts = {}
        for stock in filtered_stocks:
            rec = stock['recommendation']
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        summary += "### 推荐统计\n"
        summary += "| 推荐评级 | 股票数量 |\n"
        summary += "|---------|---------|\n"
        for rec, count in recommendation_counts.items():
            summary += "| %s | %d只 |\n" % (rec, count)
        summary += "\n"
        
        summary += "## [推荐] 推荐股票\n"
        for i, stock in enumerate(filtered_stocks, 1):
            brief = self.generate_stock_brief(stock)
            
            # 根据推荐评级添加标记
            if brief['recommendation'] in ['Strong Buy', '强烈推荐']:
                emoji = "[强]"
            elif brief['recommendation'] in ['Buy', '推荐']:
                emoji = "[荐]"
            elif brief['recommendation'] in ['Hold', '谨慎推荐']:
                emoji = "[慎]"
            elif brief['recommendation'] in ['Neutral', '中性']:
                emoji = "[中]"
            else:
                emoji = "[不]"
            
            stock_code = brief['stock_code']
            stock_name_cn = self.stock_name_cn_map.get(brief['stock_name'], brief['stock_name'])
            current_price = self.stock_current_price_map.get(stock_code, 0)

            summary += "### %s %d. %s (%s)\n" % (emoji, i, stock_name_cn, stock_code)
            summary += "**推荐评级**：%s\n" % brief['recommendation']
            summary += "**现价/目标价**：%s / %s元\n" % (current_price, brief['target_price'])
            summary += "**风险等级**：%s\n" % brief['risk_level']
            summary += "**优先级分数**：%s\n\n" % brief['priority_score']
            
            summary += "**核心逻辑**：%s\n\n" % brief['brief']
            
            if brief['key_highlights']:
                summary += "**关键要点**：\n"
                for highlight in brief['key_highlights']:
                    summary += "- [+] %s\n" % highlight
                summary += "\n"
            
            if brief['risk_warning']:
                summary += "**风险提示**：%s\n\n" % brief['risk_warning']
            
            summary += "**操作建议**：%s\n\n" % brief['action_suggestion']
            summary += "---\n\n"
        
        summary += "## [建议] 投资建议\n"
        summary += "### 整体策略\n"
        summary += "1. **分散投资**：建议将资金分散到不同行业和风险等级的股票中\n"
        summary += "2. **关注时机**：根据市场情况选择合适的入场时机\n"
        summary += "3. **设置止损**：为每只股票设置合理的止损位\n"
        summary += "4. **定期复盘**：每周回顾投资组合表现，及时调整策略\n\n"
        
        summary += "## [声明] 免责声明\n"
        summary += "本报告仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。\n"
        summary += "报告中的信息均来源于公开渠道，我们对其准确性和完整性不做任何保证。\n"
        summary += "投资者应根据自身情况做出投资决策，并承担相应风险。\n"
        
        return summary
    
    def save_report(self, report_data, summary):
        """保存报告"""
        # 使用数据管理器保存报告
        file_path = self.data_manager.save_stock_report(report_data)
        
        # 生成Markdown报告
        md_report_file = os.path.join(os.path.dirname(file_path), 'stock_report.md')
        
        with open(md_report_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info("保存报告到 %s 和 %s", file_path, md_report_file)
        return file_path
    
    def send_notification(self, report_data):
        """发送报告通知"""
        logger.info("开始发送报告通知")
        
        # 发送通知到所有支持的渠道
        results = self.notification_service.send_notification(report_data)
        
        # 记录通知结果
        for channel, success in results.items():
            logger.info("通知发送结果 - %s: %s", channel, '成功' if success else '失败')
        
        return results
    
    def generate_report(self):
        """生成最终报告"""
        logger.info("开始生成股票推荐报告")
        
        # 1. 加载分析结果
        analysis_results = self.load_analysis_results()
        if not analysis_results:
            logger.warning("没有分析结果可供生成报告")
            return None
        
        # 2. 最终筛选
        filtered_stocks = self.final_screening(analysis_results)
        if not filtered_stocks:
            logger.warning("没有股票通过最终筛选")
            return None
        
        # 3. 生成股票简报
        stock_briefs = []
        for stock in filtered_stocks:
            try:
                brief = self.generate_stock_brief(stock)
                stock_briefs.append(brief)
            except Exception as e:
                logger.error("生成股票简报失败：%s", e)
                continue
        
        # 4. 生成摘要
        try:
            summary = self.generate_summary(filtered_stocks)
        except Exception as e:
            logger.error("生成摘要失败：%s", e)
            summary = "生成摘要时出错"
        
        # 5. 构建报告数据
        report_data = {
            "report_date": datetime.now().isoformat(),
            "total_analyzed": len(analysis_results),
            "total_stocks": len(filtered_stocks),
            "recommended_stocks": stock_briefs,
            "summary": summary,
            "generated_by": "Stock Reporter Agent"
        }
        
        # 6. 保存报告
        try:
            self.save_report(report_data, summary)
        except Exception as e:
            logger.error("保存报告失败：%s", e)
            return None
        
        # 7. 发送通知
        try:
            self.send_notification(report_data)
        except Exception as e:
            logger.error("发送通知失败：%s", e)
        
        logger.info("股票报告生成完成")
        return report_data

def main():
    """主函数"""
    reporter = StockReporter()
    
    # 生成报告
    report_data = reporter.generate_report()
    
    # 打印报告摘要
    if report_data:
        print("\n股票报告摘要：")
        print("- 报告时间：%s" % report_data['report_date'])
        print("- 分析股票数：%d" % report_data['total_analyzed'])
        print("- 推荐股票数：%d" % report_data['total_stocks'])
        print("\n推荐股票：")
        for i, stock in enumerate(report_data['recommended_stocks']):
            print("%d. %s (%s) - %s" % (i+1, stock['stock_name'], stock['stock_code'], stock['recommendation']))
        print("\n完整报告已保存到：")
        print("- data/news/reports/ 目录")
    else:
        print("未生成报告")

if __name__ == '__main__':
    main()
