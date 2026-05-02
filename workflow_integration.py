#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Trader Workflow Integration System
Functions: Coordinate News Collector, Stock Collector, Stock Analyst, and Stock Reporter workflow
Implement: Task assignment, execution, verification, and scoring
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/workflow_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('workflow_integration')


class WorkFlowEngine(object):
    def __init__(self):
        logger.info("Initializing Workflow Engine")

        self.modules = {
            'news_collector': {
                'class_name': 'NewsCollector',
                'module_name': 'news_collector',
                'input': None,
                'output': 'data/news/structured/news_database.json',
                'method': 'collect'
            },
            'stock_collector': {
                'class_name': 'StockCollector',
                'module_name': 'stock_collector',
                'input': 'data/news/structured/news_database.json',
                'output': 'data/news/structured/stock_list.json',
                'method': 'collect'
            },
            'stock_analyst': {
                'class_name': 'StockAnalyst',
                'module_name': 'stock_analyst',
                'input': 'data/news/structured/stock_list.json',
                'output': 'data/news/structured/stock_analysis.json',
                'method': 'analyze'
            },
            'stock_reporter': {
                'class_name': 'StockReporter',
                'module_name': 'stock_reporter',
                'input': 'data/news/structured/stock_analysis.json',
                'output': 'data/news/reports/stock_report.json',
                'method': 'generate_report'
            }
        }

        self.workflow_status = {
            'workflow_id': None,
            'started_at': None,
            'completed_at': None,
            'stages': {},
            'current_stage': None,
            'issues': [],
            'final_result': None
        }

    def generate_workflow_id(self):
        return "WF_%s" % datetime.now().strftime('%Y%m%d_%H%M%S')

    def check_input_available(self, module_name):
        module_info = self.modules[module_name]
        input_file = module_info['input']

        if input_file is None:
            return True

        if not os.path.exists(input_file):
            logger.warning("Input file does not exist: %s", input_file)
            return False

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return len(data) > 0
        except Exception as e:
            logger.error("Failed to read input file: %s", e)
            return False

    def load_output_data(self, module_name):
        module_info = self.modules[module_name]
        output_file = module_info['output']

        if not os.path.exists(output_file):
            logger.warning("Output file does not exist: %s", output_file)
            return None

        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data_len = len(data) if isinstance(data, list) else 'dict'
            logger.info("Loaded %s output data: %s", module_name, data_len)
            return data
        except Exception as e:
            logger.error("Failed to read output file: %s", e)
            return None

    def execute_module(self, module_name):
        logger.info("Executing module: %s", module_name)

        module_info = self.modules[module_name]
        start_time = datetime.now()

        try:
            if module_name == 'news_collector':
                import news_collector
                collector = news_collector.NewsCollector()
                result = collector.collect(15)

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

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.workflow_status['stages'][module_name] = {
                'status': 'completed',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'result': result
            }

            logger.info("Module %s executed successfully, duration: %.2fs", module_name, duration)
            return True

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            self.workflow_status['stages'][module_name] = {
                'status': 'failed',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'error': str(e)
            }

            logger.error("Module %s execution failed: %s", module_name, e)
            return False

    def verify_stage_output(self, module_name):
        logger.info("Verifying stage output: %s", module_name)

        output_data = self.load_output_data(module_name)

        if output_data is None:
            return False, "Output file is empty or does not exist"

        if isinstance(output_data, list) and len(output_data) == 0:
            return False, "Output data is empty"

        verification_rules = {
            'news_collector': {
                'min_items': 15,
                'required_fields': ['title', 'source', 'publish_time', 'category']
            },
            'stock_collector': {
                'min_items': 5,
                'required_fields': ['stock_code', 'stock_name', 'priority_score']
            },
            'stock_analyst': {
                'min_items': 3,
                'required_fields': ['stock_code', 'recommendation', 'risk_level']
            },
            'stock_reporter': {
                'required_sections': ['market_overview', 'stock_analysis', 'recommendations']
            }
        }

        rules = verification_rules.get(module_name, {})

        if 'min_items' in rules:
            if isinstance(output_data, list) and len(output_data) < rules['min_items']:
                return False, "Insufficient data: need at least %d, got %d" % (rules['min_items'], len(output_data))

        if 'required_fields' in rules:
            required_fields = rules['required_fields']
            if isinstance(output_data, list):
                for idx, item in enumerate(output_data):
                    missing_fields = [f for f in required_fields if f not in item]
                    if missing_fields:
                        return False, "Item %d missing fields: %s" % (idx + 1, missing_fields)

        if 'required_sections' in rules:
            if isinstance(output_data, dict):
                missing_sections = [s for s in rules['required_sections'] if s not in output_data]
                if missing_sections:
                    return False, "Report missing sections: %s" % missing_sections

        return True, "Verification passed"

    def run_full_workflow(self, stop_on_error=True):
        logger.info("Starting full workflow execution")

        self.workflow_status['workflow_id'] = self.generate_workflow_id()
        self.workflow_status['started_at'] = datetime.now().isoformat()
        self.workflow_status['current_stage'] = 'news_collector'

        execution_order = ['news_collector', 'stock_collector', 'stock_analyst', 'stock_reporter']

        for module_name in execution_order:
            logger.info("=== Starting stage: %s ===", module_name)

            if not self.check_input_available(module_name):
                logger.error("Input data not available, skipping %s", module_name)
                if stop_on_error:
                    return False
                continue

            success = self.execute_module(module_name)

            if not success and stop_on_error:
                logger.error("Module execution failed, terminating workflow")
                return False

            passed, message = self.verify_stage_output(module_name)

            if not passed:
                logger.error("Output verification failed: %s", message)
                if stop_on_error:
                    return False

            time.sleep(0.5)

        self.workflow_status['completed_at'] = datetime.now().isoformat()
        self.workflow_status['final_result'] = 'success'

        logger.info("Full workflow execution completed")
        return True

    def get_workflow_summary(self):
        summary = {
            'workflow_id': self.workflow_status['workflow_id'],
            'started_at': self.workflow_status['started_at'],
            'completed_at': self.workflow_status['completed_at'],
            'total_duration': None,
            'stages': {},
            'issues': self.workflow_status.get('issues', []),
            'final_result': self.workflow_status.get('final_result')
        }

        if summary['started_at'] and summary['completed_at']:
            start = datetime.fromisoformat(summary['started_at'])
            end = datetime.fromisoformat(summary['completed_at'])
            summary['total_duration'] = (end - start).total_seconds()

        for stage_name, stage_info in self.workflow_status.get('stages', {}).items():
            summary['stages'][stage_name] = {
                'status': stage_info.get('status'),
                'duration': stage_info.get('duration_seconds'),
                'error': stage_info.get('error')
            }

        return summary

    def save_workflow_result(self):
        result_file = "data/news/reports/workflow_result_%s.json" % datetime.now().strftime('%Y%m%d_%H%M%S')

        dir_path = os.path.dirname(result_file)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_status, f, ensure_ascii=False, indent=2)
            logger.info("Workflow result saved: %s", result_file)
            return result_file
        except Exception as e:
            logger.error("Failed to save workflow result: %s", e)
            return None

    def load_latest_results(self):
        reports_dir = 'data/news/reports'
        if not os.path.exists(reports_dir):
            return None

        try:
            files = [f for f in os.listdir(reports_dir) if f.endswith('.json') and f.startswith('stock_')]
            if not files:
                return None

            latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(reports_dir, f)))
            file_path = os.path.join(reports_dir, latest_file)

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error("Failed to load latest results: %s", e)
            return None


def main():
    logger.info("Starting Workflow Engine")

    engine = WorkFlowEngine()

    logger.info("Starting full workflow execution...")
    success = engine.run_full_workflow()

    if success:
        logger.info("Workflow completed successfully")

        summary = engine.get_workflow_summary()
        logger.info("Workflow summary: %s", summary)

        engine.save_workflow_result()

        logger.info("Loading latest results...")
        results = engine.load_latest_results()
        if results:
            logger.info("Results loaded successfully")
    else:
        logger.error("Workflow execution failed")


if __name__ == '__main__':
    main()