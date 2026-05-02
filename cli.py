#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Trader System - User Command Line Interface
Functions: Provide command line interface for user interaction with trader system
"""

import os
import sys
import cmd
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/user_interface.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('user_interface')


class StockTraderShell(cmd.Cmd):
    intro = """
============================================================
            Stock Trader System - Command Line Interface
============================================================

Welcome to Stock Trader System!
I am your second-in-command, responsible for scheduling and
managing News Collector, Stock Collector, Stock Analyst,
and Stock Reporter.

Type 'help' or '?' to see available commands.
Type 'start' to begin today's workflow.
Type 'quit' to exit the system.
============================================================
"""

    prompt = '(Stock Trader) '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.trader_manager = None
        self.workflow_engine = None
        self.current_workflow_result = None

    def _init_modules(self):
        if self.trader_manager is None:
            try:
                from trader_manager import TraderManager
                self.trader_manager = TraderManager()
                logger.info("Trader module initialized")
            except Exception as e:
                logger.error("Failed to initialize trader module: %s", e)
                print("Error: Failed to initialize trader module: %s" % e)

        if self.workflow_engine is None:
            try:
                from workflow_integration import WorkFlowEngine
                self.workflow_engine = WorkFlowEngine()
                logger.info("Workflow engine initialized")
            except Exception as e:
                logger.error("Failed to initialize workflow engine: %s", e)
                print("Error: Failed to initialize workflow engine: %s" % e)

    def do_start(self, arg):
        """start - Begin today's complete workflow"""
        print("\n" + "=" * 60)
        print("Starting Today's Workflow")
        print("=" * 60)

        self._init_modules()

        if self.workflow_engine is None:
            print("Error: Workflow engine initialization failed")
            return

        print("\nStage 1: News Collector collecting news...")
        print("-" * 40)

        try:
            import news_collector
            collector = news_collector.NewsCollector()
            news_result = collector.collect(15)
            result_len = len(news_result) if isinstance(news_result, list) else 'N'
            print("OK: News collection completed: %s news collected" % result_len)

            if not isinstance(news_result, list) or len(news_result) == 0:
                print("Warning: News collection result is empty or format error")
        except Exception as e:
            logger.error("News collection failed: %s", e)
            print("FAIL: News collection failed: %s" % e)
            return

        print("\nStage 2: Stock Collector filtering stocks...")
        print("-" * 40)

        try:
            import stock_collector
            stock_collector_instance = stock_collector.StockCollector()
            stock_result = stock_collector_instance.collect()
            stock_count = len(stock_result) if isinstance(stock_result, list) else 0
            print("OK: Stock filtering completed: %d stocks selected" % stock_count)
        except Exception as e:
            logger.error("Stock filtering failed: %s", e)
            print("FAIL: Stock filtering failed: %s" % e)
            return

        print("\nStage 3: Stock Analyst analyzing stocks...")
        print("-" * 40)

        try:
            import stock_analyst
            analyst = stock_analyst.StockAnalyst()
            analysis_result = analyst.analyze()
            analysis_count = len(analysis_result) if isinstance(analysis_result, list) else 0
            print("OK: Stock analysis completed: %d stocks analyzed" % analysis_count)
        except Exception as e:
            logger.error("Stock analysis failed: %s", e)
            print("FAIL: Stock analysis failed: %s" % e)
            return

        print("\nStage 4: Stock Reporter generating report...")
        print("-" * 40)

        try:
            import stock_reporter
            reporter = stock_reporter.StockReporter()
            report_result = reporter.generate_report()
            print("OK: Report generation completed")
            self.current_workflow_result = report_result
        except Exception as e:
            logger.error("Report generation failed: %s", e)
            print("FAIL: Report generation failed: %s" % e)
            return

        print("\n" + "=" * 60)
        print("Today's Workflow Completed!")
        print("=" * 60)

        print("\nType 'report' to view today's investment report")
        print("Type 'status' to view work status")

    def do_status(self, arg):
        """status - View current work status and employee performance"""
        self._init_modules()

        if self.trader_manager is None:
            print("Error: Trader module initialization failed")
            return

        status = self.trader_manager.get_workflow_status()

        print("\n" + "=" * 60)
        print("Stock Trader System - Work Status")
        print("=" * 60)
        print("Query time: %s" % status['timestamp'])
        print()

        print("[Employee Status]")
        for role, emp_status in status['employees'].items():
            working = "Working" if emp_status['is_working_time'] else "Off Duty"
            print("  %s: %s, Current Score: %.1f" % (emp_status['name'], working, emp_status['current_score']))

        print()
        print("[Task Statistics]")
        print("  Pending tasks: %d" % len(status['pending_tasks']))
        print("  In-progress tasks: %d" % len(status['in_progress_tasks']))
        print("  Completed tasks: %d" % len(status['completed_tasks']))

        if status['pending_tasks']:
            print()
            print("[Pending Tasks]")
            for task in status['pending_tasks']:
                print("  - %s (%s)" % (task['task_name'], task['role']))

        if status['in_progress_tasks']:
            print()
            print("[In-Progress Tasks]")
            for task in status['in_progress_tasks']:
                print("  - %s (%s)" % (task['task_name'], task['role']))

    def do_report(self, arg):
        """report - View today's investment recommendation report"""
        self._init_modules()

        if self.current_workflow_result is None:
            print("Please run 'start' command first to generate today's report")
            return

        print("\n" + "=" * 60)
        print("          Today's Stock Investment Report")
        print("=" * 60)
        print("Generated at: %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print()

        if isinstance(self.current_workflow_result, dict):
            if 'market_overview' in self.current_workflow_result:
                print("[Market Overview]")
                print(self.current_workflow_result.get('market_overview', 'N/A'))
                print()

            if 'stock_analysis' in self.current_workflow_result:
                print("[Stock Analysis]")
                analysis = self.current_workflow_result['stock_analysis']
                if isinstance(analysis, list):
                    for i, stock in enumerate(analysis[:5], 1):
                        print("%d. %s (%s)" % (i, stock.get('stock_name', 'N/A'), stock.get('stock_code', 'N/A')))
                        print("     Recommendation: %s" % stock.get('recommendation', 'N/A'))
                        print("     Risk: %s" % stock.get('risk_level', 'N/A'))
                        print()
                else:
                    print(analysis)

            if 'recommended_stocks' in self.current_workflow_result:
                print("[Recommended Stocks]")
                stocks = self.current_workflow_result['recommended_stocks']
                if isinstance(stocks, list):
                    for i, stock in enumerate(stocks[:5], 1):
                        print("%d. %s (%s)" % (i, stock.get('stock_name', 'N/A'), stock.get('stock_code', 'N/A')))
                        if 'recommendation' in stock:
                            print("     Rating: %s" % stock['recommendation'])
                        if 'target_price' in stock:
                            print("     Target Price: %s" % stock['target_price'])
                        if 'reason' in stock:
                            print("     Reason: %s" % stock['reason'])
                        print()
        else:
            print(self.current_workflow_result)

    def do_news(self, arg):
        """news [count] - View latest news, default 10 items"""
        self._init_modules()

        try:
            import news_collector
            collector = news_collector.NewsCollector()
            limit = int(arg) if arg else 10

            news_data = collector.collect(limit)
            data_len = len(news_data) if isinstance(news_data, list) else 0

            print("\n" + "=" * 60)
            print("          Latest Financial News (%d items)" % data_len)
            print("=" * 60)

            if isinstance(news_data, list):
                for i, news in enumerate(news_data[:limit], 1):
                    print("\n%d. %s" % (i, news.get('title', 'N/A')))
                    print("   Source: %s" % news.get('source', 'N/A'))
                    print("   Time: %s" % news.get('publish_time', 'N/A'))
                    print("   Category: %s" % news.get('category', 'N/A'))
            else:
                print("News data format error")

        except Exception as e:
            logger.error("Failed to get news: %s", e)
            print("Error: Failed to get news - %s" % e)

    def do_stocks(self, arg):
        """stocks - View current filtered stock list"""
        self._init_modules()

        stock_list_file = 'data/news/structured/stock_list.json'

        if not os.path.exists(stock_list_file):
            print("Please run 'start' command first to collect stock data")
            return

        try:
            with open(stock_list_file, 'r', encoding='utf-8') as f:
                stocks = json.load(f)

            print("\n" + "=" * 60)
            print("          Filtered Stock List (%d stocks)" % len(stocks))
            print("=" * 60)

            for i, stock in enumerate(stocks[:10], 1):
                print("\n%d. %s (%s)" % (i, stock.get('stock_name', 'N/A'), stock.get('stock_code', 'N/A')))
                print("   Priority Score: %s" % stock.get('priority_score', 'N/A'))
                print("   Mention Count: %s" % stock.get('mention_count', 'N/A'))
                if 'latest_news_time' in stock:
                    print("   Latest News Time: %s" % stock['latest_news_time'])

        except Exception as e:
            logger.error("Failed to read stock list: %s", e)
            print("Error: Failed to read stock list - %s" % e)

    def do_analysis(self, arg):
        """analysis - View stock analysis results"""
        self._init_modules()

        analysis_file = 'data/news/structured/stock_analysis.json'

        if not os.path.exists(analysis_file):
            print("Please run 'start' command first to run analysis")
            return

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analyses = json.load(f)

            data_len = len(analyses) if isinstance(analyses, list) else 0
            print("\n" + "=" * 60)
            print("          Stock Analysis Results (%d stocks)" % data_len)
            print("=" * 60)

            if isinstance(analyses, list):
                for i, analysis in enumerate(analyses[:5], 1):
                    print("\n%d. %s (%s)" % (i, analysis.get('stock_name', 'N/A'), analysis.get('stock_code', 'N/A')))
                    print("   Recommendation: %s" % analysis.get('recommendation', 'N/A'))
                    print("   Risk Level: %s" % analysis.get('risk_level', 'N/A'))
                    if 'target_price' in analysis:
                        print("   Target Price: %s" % analysis['target_price'])

        except Exception as e:
            logger.error("Failed to read analysis results: %s", e)
            print("Error: Failed to read analysis results - %s" % e)

    def do_performance(self, arg):
        """performance - View employee performance scores"""
        self._init_modules()

        if self.trader_manager is None:
            print("Error: Trader module initialization failed")
            return

        print("\n" + "=" * 60)
        print("          Employee Performance Scores")
        print("=" * 60)

        for role, employee in self.trader_manager.employees.items():
            avg_score = employee.get_average_score()
            rating = "Excellent" if avg_score >= 90 else "Good" if avg_score >= 80 else "Qualified" if avg_score >= 70 else "Unqualified"

            print("\n%s (%s)" % (employee.name, employee.role))
            print("  Work Hours: %d:00 - %d:00" % (employee.work_start_hour, employee.work_end_hour))
            print("  Current Score: %.1f (%s)" % (avg_score, rating))
            print("  Score Count: %d" % len(employee.daily_scores))

    def do_daily_report(self, arg):
        """daily_report - Generate and display daily work report"""
        self._init_modules()

        if self.trader_manager is None:
            print("Error: Trader module initialization failed")
            return

        print("\nGenerating daily work report...")
        report = self.trader_manager.generate_daily_report()

        user_report = self.trader_manager.report_to_user()
        print(user_report)

        report_file = "data/news/reports/daily_report_%s.txt" % datetime.now().strftime('%Y%m%d_%H%M%S')
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(user_report)
            print("\nReport saved to: %s" % report_file)
        except Exception as e:
            logger.error("Failed to save report: %s", e)

    def do_emergency(self, arg):
        """emergency <task description> - Issue emergency task"""
        if not arg:
            print("Please provide emergency task description")
            return

        self._init_modules()

        if self.trader_manager is None:
            print("Error: Trader module initialization failed")
            return

        task_id = self.trader_manager.dispatch_emergency_task(
            task_name="Emergency Task",
            role="news_collector",
            description=arg,
            priority="high"
        )

        print("\nOK: Emergency task issued: %s" % task_id)
        print("  Task Description: %s" % arg)
        print("  Related personnel will handle it immediately")

    def do_help(self, arg):
        """help - Show help information"""
        commands = {
            'start': 'start - Start today complete workflow',
            'status': 'status - View current work status and employee performance',
            'report': 'report - View today investment recommendation report',
            'news': 'news [count] - View latest news, default 10 items',
            'stocks': 'stocks - View current filtered stock list',
            'analysis': 'analysis - View stock analysis results',
            'performance': 'performance - View employee performance scores',
            'daily_report': 'daily_report - Generate and display daily work report',
            'emergency': 'emergency <desc> - Issue emergency task',
            'quit': 'quit - Exit the system'
        }

        print("\n" + "=" * 60)
        print("          Stock Trader System - Available Commands")
        print("=" * 60)

        for cmd_key, desc in commands.items():
            print("\n  %s" % desc)

        print("\n" + "=" * 60)

    def do_quit(self, arg):
        """quit - Exit the system"""
        print("\nThank you for using Stock Trader System, goodbye!")
        return True

    def do_exit(self, arg):
        """exit - Exit the system"""
        return self.do_quit(arg)

    def do_EOF(self, arg):
        """Exit the system"""
        print()
        return self.do_quit(arg)


def main():
    print("Starting Stock Trader System...")

    if sys.version_info[0] < 3:
        print("Error: Python 3.x is recommended")
        print("Continuing anyway...")

    shell = StockTraderShell()

    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        print("Executing command: %s" % command)
        shell.onecmd(command)
    else:
        shell.cmdloop()


if __name__ == '__main__':
    main()