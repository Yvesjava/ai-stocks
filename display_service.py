#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
展示服务模块
功能：支持多端展示，包括数据大屏、移动端等
"""

import os
import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/display_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('display_service')


class DisplayService:
    """展示服务"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.server = None
        self.data_manager = None
        self._load_data_manager()
    
    def _load_data_manager(self):
        """加载数据管理器"""
        try:
            from data_manager import DataManager
            self.data_manager = DataManager()
        except Exception as e:
            logger.error(f"加载数据管理器失败: {e}")
            self.data_manager = None
    
    def start_server(self):
        """启动展示服务器"""
        class DisplayHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.display_service = self
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                if self.path == '/':
                    self.send_html_response('index.html')
                elif self.path == '/api/report':
                    self.send_report_data()
                elif self.path == '/api/stocks':
                    self.send_stocks_data()
                elif self.path == '/api/statistics':
                    self.send_statistics_data()
                elif self.path == '/data大屏':
                    self.send_html_response('dashboard.html')
                elif self.path == '/移动端':
                    self.send_html_response('mobile.html')
                else:
                    self.send_error(404, 'Not Found')
            
            def send_html_response(self, filename):
                """发送HTML响应"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_content = self.get_html_content(filename)
                self.wfile.write(html_content.encode('utf-8'))
            
            def send_report_data(self):
                """发送报告数据"""
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                if hasattr(self, 'display_service') and self.display_service.data_manager:
                    report_data = self.display_service.data_manager.load_stock_report()
                else:
                    report_data = {}
                
                self.wfile.write(json.dumps(report_data, ensure_ascii=False).encode('utf-8'))
            
            def send_stocks_data(self):
                """发送股票数据"""
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                if hasattr(self, 'display_service') and self.display_service.data_manager:
                    analysis_data = self.display_service.data_manager.load_stock_analysis()
                else:
                    analysis_data = []
                
                self.wfile.write(json.dumps(analysis_data, ensure_ascii=False).encode('utf-8'))
            
            def send_statistics_data(self):
                """发送统计数据"""
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                if hasattr(self, 'display_service') and self.display_service.data_manager:
                    stats = self.display_service.data_manager.get_data_statistics()
                else:
                    stats = {}
                
                self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            
            def get_html_content(self, filename):
                """获取HTML内容"""
                if filename == 'index.html':
                    return self.get_index_html()
                elif filename == 'dashboard.html':
                    return self.get_dashboard_html()
                elif filename == 'mobile.html':
                    return self.get_mobile_html()
                return '<h1>404 Not Found</h1>'
            
            def get_index_html(self):
                """获取首页HTML"""
                return '''
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>股票报告展示系统</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 20px;
                            background-color: #f0f2f5;
                        }
                        .container {
                            max-width: 1200px;
                            margin: 0 auto;
                            background-color: white;
                            padding: 30px;
                            border-radius: 8px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }
                        h1 {
                            color: #333;
                            text-align: center;
                        }
                        .nav {
                            display: flex;
                            justify-content: center;
                            margin: 30px 0;
                        }
                        .nav a {
                            margin: 0 20px;
                            padding: 10px 20px;
                            background-color: #1890ff;
                            color: white;
                            text-decoration: none;
                            border-radius: 4px;
                        }
                        .nav a:hover {
                            background-color: #40a9ff;
                        }
                        .info {
                            text-align: center;
                            margin-top: 50px;
                            color: #666;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>股票报告展示系统</h1>
                        <div class="nav">
                            <a href="/data大屏">数据大屏</a>
                            <a href="/移动端">移动端</a>
                            <a href="/api/report" target="_blank">API - 报告数据</a>
                            <a href="/api/stocks" target="_blank">API - 股票数据</a>
                        </div>
                        <div class="info">
                            <p>系统已启动，可通过上方链接访问不同展示页面</p>
                            <p>当前时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            
            def get_dashboard_html(self):
                """获取数据大屏HTML"""
                return '''
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>股票报告数据大屏</title>
                    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                    <style>
                        body {
                            margin: 0;
                            padding: 0;
                            background-color: #001529;
                            color: white;
                            font-family: Arial, sans-serif;
                        }
                        .container {
                            padding: 20px;
                        }
                        .header {
                            text-align: center;
                            margin-bottom: 30px;
                        }
                        .dashboard {
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            grid-template-rows: repeat(2, 1fr);
                            gap: 20px;
                            height: 80vh;
                        }
                        .chart {
                            background-color: rgba(255,255,255,0.1);
                            border-radius: 8px;
                            padding: 20px;
                        }
                        .chart h3 {
                            margin-top: 0;
                            color: #1890ff;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>股票报告数据大屏</h1>
                            <p id="update-time">更新时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
                        </div>
                        <div class="dashboard">
                            <div class="chart">
                                <h3>推荐股票分布</h3>
                                <div id="stock-distribution" style="width: 100%; height: 300px;"></div>
                            </div>
                            <div class="chart">
                                <h3>推荐评级分布</h3>
                                <div id="recommendation-distribution" style="width: 100%; height: 300px;"></div>
                            </div>
                            <div class="chart">
                                <h3>股票优先级分布</h3>
                                <div id="priority-distribution" style="width: 100%; height: 300px;"></div>
                            </div>
                            <div class="chart">
                                <h3>风险等级分布</h3>
                                <div id="risk-distribution" style="width: 100%; height: 300px;"></div>
                            </div>
                        </div>
                    </div>
                    <script>
                        // 初始化图表
                        const stockChart = echarts.init(document.getElementById('stock-distribution'));
                        const recommendationChart = echarts.init(document.getElementById('recommendation-distribution'));
                        const priorityChart = echarts.init(document.getElementById('priority-distribution'));
                        const riskChart = echarts.init(document.getElementById('risk-distribution'));
                        
                        // 加载数据
                        fetch('/api/stocks')
                            .then(response => response.json())
                            .then(data => {
                                // 处理数据
                                const stockNames = data.map(item => item.stock_name);
                                const priorityScores = data.map(item => item.priority_score || 0);
                                const recommendations = data.map(item => item.recommendation);
                                const riskLevels = data.map(item => item.risk_level);
                                
                                // 统计推荐评级
                                const recommendationCount = {};
                                recommendations.forEach(rec => {
                                    recommendationCount[rec] = (recommendationCount[rec] || 0) + 1;
                                });
                                
                                // 统计风险等级
                                const riskCount = {};
                                riskLevels.forEach(risk => {
                                    riskCount[risk] = (riskCount[risk] || 0) + 1;
                                });
                                
                                // 股票分布图表
                                stockChart.setOption({
                                    title: {
                                        text: '推荐股票',
                                        left: 'center',
                                        textStyle: { color: '#fff' }
                                    },
                                    tooltip: {
                                        trigger: 'axis',
                                        axisPointer: {
                                            type: 'shadow'
                                        }
                                    },
                                    xAxis: {
                                        type: 'category',
                                        data: stockNames,
                                        axisLabel: {
                                            color: '#fff',
                                            rotate: 45
                                        }
                                    },
                                    yAxis: {
                                        type: 'value',
                                        axisLabel: {
                                            color: '#fff'
                                        }
                                    },
                                    series: [{
                                        data: priorityScores,
                                        type: 'bar',
                                        itemStyle: {
                                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                                { offset: 0, color: '#83bff6' },
                                                { offset: 0.5, color: '#188df0' },
                                                { offset: 1, color: '#188df0' }
                                            ])
                                        }
                                    }]
                                });
                                
                                // 推荐评级分布图表
                                recommendationChart.setOption({
                                    title: {
                                        text: '推荐评级分布',
                                        left: 'center',
                                        textStyle: { color: '#fff' }
                                    },
                                    tooltip: {
                                        trigger: 'item'
                                    },
                                    series: [{
                                        type: 'pie',
                                        radius: '60%',
                                        data: Object.entries(recommendationCount).map(([name, value]) => ({ name, value })),
                                        emphasis: {
                                            itemStyle: {
                                                shadowBlur: 10,
                                                shadowOffsetX: 0,
                                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                                            }
                                        }
                                    }]
                                });
                                
                                // 风险等级分布图表
                                riskChart.setOption({
                                    title: {
                                        text: '风险等级分布',
                                        left: 'center',
                                        textStyle: { color: '#fff' }
                                    },
                                    tooltip: {
                                        trigger: 'item'
                                    },
                                    series: [{
                                        type: 'pie',
                                        radius: '60%',
                                        data: Object.entries(riskCount).map(([name, value]) => ({ name, value })),
                                        emphasis: {
                                            itemStyle: {
                                                shadowBlur: 10,
                                                shadowOffsetX: 0,
                                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                                            }
                                        }
                                    }]
                                });
                            });
                        
                        // 响应式处理
                        window.addEventListener('resize', function() {
                            stockChart.resize();
                            recommendationChart.resize();
                            priorityChart.resize();
                            riskChart.resize();
                        });
                    </script>
                </body>
                </html>
                '''
            
            def get_mobile_html(self):
                """获取移动端HTML"""
                return '''
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                    <title>股票报告 - 移动端</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f5f5f5;
                        }
                        .header {
                            background-color: #1890ff;
                            color: white;
                            padding: 15px;
                            text-align: center;
                            position: sticky;
                            top: 0;
                            z-index: 100;
                        }
                        .header h1 {
                            margin: 0;
                            font-size: 18px;
                        }
                        .content {
                            padding: 15px;
                        }
                        .stock-card {
                            background-color: white;
                            border-radius: 8px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }
                        .stock-card h3 {
                            margin-top: 0;
                            color: #333;
                            font-size: 16px;
                        }
                        .stock-info {
                            display: flex;
                            justify-content: space-between;
                            margin: 10px 0;
                            font-size: 14px;
                        }
                        .stock-info .label {
                            color: #666;
                        }
                        .stock-info .value {
                            font-weight: bold;
                        }
                        .recommendation {
                            padding: 5px 10px;
                            border-radius: 12px;
                            font-size: 12px;
                            display: inline-block;
                            margin-top: 10px;
                        }
                        .strong-buy {
                            background-color: #52c41a;
                            color: white;
                        }
                        .buy {
                            background-color: #1890ff;
                            color: white;
                        }
                        .hold {
                            background-color: #faad14;
                            color: white;
                        }
                        .neutral {
                            background-color: #722ed1;
                            color: white;
                        }
                        .sell {
                            background-color: #f5222d;
                            color: white;
                        }
                        .summary {
                            background-color: white;
                            border-radius: 8px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }
                        .summary h2 {
                            font-size: 16px;
                            color: #333;
                            margin-top: 0;
                        }
                        .summary p {
                            font-size: 14px;
                            line-height: 1.5;
                            color: #666;
                        }
                        .loading {
                            text-align: center;
                            padding: 20px;
                            color: #666;
                        }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>股票推荐报告</h1>
                    </div>
                    <div class="content">
                        <div id="loading" class="loading">加载中...</div>
                        <div id="summary" class="summary" style="display: none;"></div>
                        <div id="stocks" style="display: none;"></div>
                    </div>
                    <script>
                        // 加载报告数据
                        fetch('/api/report')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('loading').style.display = 'none';
                                
                                // 显示总结
                                const summaryDiv = document.getElementById('summary');
                                summaryDiv.style.display = 'block';
                                summaryDiv.innerHTML = `
                                    <h2>市场简评</h2>
                                    <p>${data.summary || '暂无数据'}</p>
                                    <div style="margin-top: 10px; font-size: 12px; color: #999;">
                                        生成时间: ${data.report_date || '未知'}
                                    </div>
                                `;
                                
                                // 显示股票列表
                                const stocksDiv = document.getElementById('stocks');
                                stocksDiv.style.display = 'block';
                                
                                if (data.recommended_stocks && data.recommended_stocks.length > 0) {
                                    data.recommended_stocks.forEach(stock => {
                                        const stockCard = document.createElement('div');
                                        stockCard.className = 'stock-card';
                                        
                                        // 根据推荐评级设置样式
                                        let recommendationClass = 'neutral';
                                        if (stock.recommendation === 'Strong Buy' || stock.recommendation === '强烈推荐') {
                                            recommendationClass = 'strong-buy';
                                        } else if (stock.recommendation === 'Buy' || stock.recommendation === '推荐') {
                                            recommendationClass = 'buy';
                                        } else if (stock.recommendation === 'Hold' || stock.recommendation === '谨慎推荐') {
                                            recommendationClass = 'hold';
                                        } else if (stock.recommendation === 'Sell' || stock.recommendation === '不推荐') {
                                            recommendationClass = 'sell';
                                        }
                                        
                                        stockCard.innerHTML = `
                                            <h3>${stock.stock_name} (${stock.stock_code})</h3>
                                            <div class="stock-info">
                                                <span class="label">推荐评级:</span>
                                                <span class="value">${stock.recommendation}</span>
                                            </div>
                                            <div class="stock-info">
                                                <span class="label">目标价:</span>
                                                <span class="value">${stock.target_price}元</span>
                                            </div>
                                            <div class="stock-info">
                                                <span class="label">风险等级:</span>
                                                <span class="value">${stock.risk_level}</span>
                                            </div>
                                            <div class="stock-info">
                                                <span class="label">优先级:</span>
                                                <span class="value">${stock.priority_score}</span>
                                            </div>
                                            <div class="stock-info">
                                                <span class="label">核心逻辑:</span>
                                            </div>
                                            <p style="font-size: 14px; color: #666; margin-top: 5px;">${stock.brief || '暂无'}</p>
                                            <div class="recommendation ${recommendationClass}">
                                                ${stock.recommendation}
                                            </div>
                                        `;
                                        
                                        stocksDiv.appendChild(stockCard);
                                    });
                                } else {
                                    stocksDiv.innerHTML = '<div class="stock-card"><p style="text-align: center; color: #999;">暂无推荐股票</p></div>';
                                }
                            })
                            .catch(error => {
                                console.error('加载数据失败:', error);
                                document.getElementById('loading').innerHTML = '加载失败，请刷新重试';
                            });
                    </script>
                </body>
                </html>
                '''
        
        # 创建服务器
        self.server = HTTPServer(('', self.port), DisplayHandler)
        logger.info(f"展示服务已启动，访问地址: http://localhost:{self.port}")
        
        # 启动服务器线程
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        return self.server
    
    def stop_server(self):
        """停止展示服务器"""
        if self.server:
            self.server.shutdown()
            logger.info("展示服务已停止")


def main():
    """测试展示服务"""
    display_service = DisplayService()
    display_service.start_server()
    
    print(f"展示服务已启动，访问地址: http://localhost:8000")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 保持运行
        while True:
            pass
    except KeyboardInterrupt:
        display_service.stop_server()
        print("服务已停止")


if __name__ == '__main__':
    main()
