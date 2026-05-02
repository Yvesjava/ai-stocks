#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Trader Manager System
Functions: Schedule and manage News Collector, Stock Collector, Stock Analyst, Stock Reporter
Including: Task assignment, progress monitoring, work verification, performance scoring, and feedback
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/trader_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('trader_manager')


class WorkStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Employee(object):
    def __init__(self, name, role, work_start_hour, work_end_hour):
        self.name = name
        self.role = role
        self.work_start_hour = work_start_hour
        self.work_end_hour = work_end_hour
        self.daily_scores = []
        self.task_history = []

    def is_working_time(self):
        now = datetime.now()
        current_hour = now.hour
        return self.work_start_hour <= current_hour <= self.work_end_hour

    def add_score(self, score):
        self.daily_scores.append({
            'timestamp': datetime.now().isoformat(),
            'score': score
        })

    def get_average_score(self):
        if not self.daily_scores:
            return 0
        return sum(s['score'] for s in self.daily_scores) / len(self.daily_scores)


class Task(object):
    def __init__(self, task_id, task_name, role, description, deadline, quality_requirements):
        self.task_id = task_id
        self.task_name = task_name
        self.role = role
        self.description = description
        self.deadline = deadline
        self.quality_requirements = quality_requirements
        self.status = WorkStatus.PENDING
        self.result = None
        self.issues = []
        self.score = None
        self.start_time = None
        self.end_time = None

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'role': self.role,
            'description': self.description,
            'deadline': self.deadline,
            'quality_requirements': self.quality_requirements,
            'status': self.status.value,
            'result': self.result,
            'issues': self.issues,
            'score': self.score,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class VerificationResult(object):
    def __init__(self, passed, score, comments, issues):
        self.passed = passed
        self.score = score
        self.comments = comments
        self.issues = issues


class TraderManager(object):
    def __init__(self):
        logger.info("Initializing Stock Trader Manager System")

        self.employees = {
            'news_collector': Employee('News Collector', 'News Collector', 8, 16),
            'stock_collector': Employee('Stock Collector', 'Stock Collector', 9, 15),
            'stock_analyst': Employee('Stock Analyst', 'Stock Analyst', 9, 17),
            'stock_reporter': Employee('Stock Reporter', 'Stock Reporter', 15, 20)
        }

        self.tasks = {}
        self.task_counter = 0
        self.daily_report = None
        self.verification_standards = self._init_verification_standards()

        self.scoring_weights = {
            'news_collector': {'completeness': 0.30, 'accuracy': 0.25, 'timeliness': 0.25, 'classification': 0.20},
            'stock_collector': {'completeness': 0.30, 'accuracy': 0.30, 'timeliness': 0.25, 'format': 0.15},
            'stock_analyst': {'depth': 0.35, 'logic': 0.25, 'recommendation': 0.25, 'speed': 0.15},
            'stock_reporter': {'completeness': 0.25, 'accuracy': 0.25, 'depth': 0.30, 'format': 0.20}
        }

    def _init_verification_standards(self):
        return {
            'news_collector': {
                'min_news_count': 15,
                'required_categories': ['Company News', 'Industry News', 'Market News'],
                'max_age_hours': 24,
                'required_sources': 3
            },
            'stock_collector': {
                'min_stock_count': 5,
                'required_fields': ['stock_code', 'stock_name', 'priority_score'],
                'max_age_hours': 24
            },
            'stock_analyst': {
                'min_analysis_count': 3,
                'required_fields': ['recommendation', 'risk_level', 'target_price'],
                'analysis_dimensions': ['technical', 'fundamental', 'news']
            },
            'stock_reporter': {
                'required_sections': ['market_overview', 'stock_analysis', 'recommendations'],
                'min_recommended_stocks': 3,
                'max_report_age_hours': 24
            }
        }

    def create_task(self, task_name, role, description, deadline, quality_requirements):
        self.task_counter += 1
        task_id = "TASK_%s_%04d" % (datetime.now().strftime('%Y%m%d'), self.task_counter)
        task = Task(task_id, task_name, role, description, deadline, quality_requirements)
        self.tasks[task_id] = task
        logger.info("Created task: %s - %s (Role: %s)", task_id, task_name, role)
        return task_id

    def assign_task(self, task_id, employee_role):
        if task_id not in self.tasks:
            logger.error("Task does not exist: %s", task_id)
            return False

        task = self.tasks[task_id]
        task.status = WorkStatus.IN_PROGRESS
        task.start_time = datetime.now()

        logger.info("Assigned task %s to %s", task_id, employee_role)
        return True

    def receive_report(self, task_id, result, issues=None):
        if task_id not in self.tasks:
            logger.error("Task does not exist: %s", task_id)
            return False

        task = self.tasks[task_id]
        task.status = WorkStatus.COMPLETED
        task.end_time = datetime.now()
        task.result = result
        task.issues = issues or []

        logger.info("Received work report for task %s", task_id)
        return True

    def verify_work(self, role, work_output):
        logger.info("Starting verification for %s", role)

        if role not in self.verification_standards:
            logger.error("Unknown role: %s", role)
            return VerificationResult(False, 0, "Unknown role", ["Role does not exist"])

        standards = self.verification_standards[role]
        issues = []
        score_details = {}

        if role == 'news_collector':
            score_details = self._verify_news_collector(work_output, standards, issues)
        elif role == 'stock_collector':
            score_details = self._verify_stock_collector(work_output, standards, issues)
        elif role == 'stock_analyst':
            score_details = self._verify_stock_analyst(work_output, standards, issues)
        elif role == 'stock_reporter':
            score_details = self._verify_stock_reporter(work_output, standards, issues)

        total_score = sum(score_details.values())
        passed = len(issues) == 0 and total_score >= 70

        verification = VerificationResult(passed, total_score, "Verification passed" if passed else "Verification failed", issues)

        logger.info("%s verification result: %s, Score: %d", role, "Passed" if passed else "Failed", total_score)
        return verification

    def _verify_news_collector(self, work_output, standards, issues):
        score = {'collection_count': 0, 'completeness': 0, 'accuracy': 0, 'timeliness': 0, 'classification': 0}

        if not isinstance(work_output, list):
            issues.append("Output format error: should be list")
            return score

        news_count = len(work_output)

        if news_count >= standards['min_news_count']:
            score['collection_count'] = 20
        elif news_count >= standards['min_news_count'] * 0.8:
            score['collection_count'] = 15
        elif news_count >= standards['min_news_count'] * 0.5:
            score['collection_count'] = 10
        else:
            issues.append("Insufficient news count: need at least %d, got %d" % (standards['min_news_count'], news_count))

        if news_count >= standards['min_news_count']:
            score['completeness'] = 25

        categories = set()
        sources = set()
        for news in work_output:
            if 'category' in news:
                categories.add(news['category'])
            if 'source' in news:
                sources.add(news['source'])

        if len(categories) < len(standards['required_categories']):
            issues.append("Incomplete classification: missing %s" % (set(standards['required_categories']) - categories))
        else:
            score['classification'] = 15

        if len(sources) < standards['required_sources']:
            issues.append("Insufficient sources: need at least %d, got %d" % (standards['required_sources'], len(sources)))
        else:
            score['accuracy'] = 20

        has_recent = False
        for news in work_output:
            if 'publish_time' in news:
                try:
                    pub_time = datetime.fromisoformat(news['publish_time'])
                    if (datetime.now() - pub_time).total_seconds() < standards['max_age_hours'] * 3600:
                        has_recent = True
                        break
                except:
                    pass

        if has_recent:
            score['timeliness'] = 20
        else:
            issues.append("News timeliness insufficient: no latest news within 24 hours")

        return score

    def _verify_stock_collector(self, work_output, standards, issues):
        score = {'completeness': 0, 'accuracy': 0, 'timeliness': 0, 'format': 0}

        if not isinstance(work_output, list):
            issues.append("Output format error: should be list")
            return score

        stock_count = len(work_output)
        if stock_count < standards['min_stock_count']:
            issues.append("Insufficient stock count: need at least %d, got %d" % (standards['min_stock_count'], stock_count))
        else:
            score['completeness'] = 30

        valid_stocks = 0
        for stock in work_output:
            if all(field in stock for field in standards['required_fields']):
                valid_stocks += 1

        accuracy_ratio = valid_stocks / max(stock_count, 1)
        score['accuracy'] = 30 * accuracy_ratio

        if stock_count > 0 and accuracy_ratio < 1.0:
            issues.append("Some stock data fields incomplete")

        has_recent = False
        for stock in work_output:
            if 'timestamp' in stock:
                try:
                    ts = datetime.fromisoformat(stock['timestamp'])
                    if (datetime.now() - ts).total_seconds() < standards['max_age_hours'] * 3600:
                        has_recent = True
                        break
                except:
                    pass

        if has_recent:
            score['timeliness'] = 25
        else:
            issues.append("Data timeliness insufficient: no update within 24 hours")

        if stock_count > 0:
            score['format'] = 15

        return score

    def _verify_stock_analyst(self, work_output, standards, issues):
        score = {'depth': 0, 'logic': 0, 'recommendation': 0, 'speed': 0}

        if not isinstance(work_output, list):
            issues.append("Output format error: should be list")
            return score

        analysis_count = len(work_output)
        if analysis_count < standards['min_analysis_count']:
            issues.append("Insufficient analysis count: need at least %d, got %d" % (standards['min_analysis_count'], analysis_count))
        else:
            score['depth'] = 35

        valid_analyses = 0
        for analysis in work_output:
            if all(field in analysis for field in standards['required_fields']):
                valid_analyses += 1

        logic_ratio = valid_analyses / max(analysis_count, 1)
        score['logic'] = 25 * logic_ratio

        if logic_ratio < 1.0:
            issues.append("Some analysis missing required fields")

        score['recommendation'] = 25
        score['speed'] = 15

        return score

    def _verify_stock_reporter(self, work_output, standards, issues):
        score = {'completeness': 0, 'accuracy': 0, 'depth': 0, 'format': 0}

        if not isinstance(work_output, dict):
            issues.append("Output format error: should be dict")
            return score

        sections = work_output.get('sections', [])
        missing_sections = [s for s in standards['required_sections'] if s not in sections]

        if missing_sections:
            issues.append("Report missing required sections: %s" % missing_sections)
        else:
            score['completeness'] = 25

        recommended_stocks = work_output.get('recommended_stocks', [])
        if len(recommended_stocks) < standards['min_recommended_stocks']:
            issues.append("Insufficient recommended stocks: need at least %d, got %d" % (standards['min_recommended_stocks'], len(recommended_stocks)))
        else:
            score['accuracy'] = 25

        if len(recommended_stocks) >= standards['min_recommended_stocks']:
            score['depth'] = 30

        score['format'] = 20

        return score

    def score_employee(self, role, verification_result):
        if role not in self.employees:
            logger.error("Unknown employee role: %s", role)
            return 0

        employee = self.employees[role]
        score = verification_result.score
        employee.add_score(score)

        logger.info("%s current score: %d, historical average: %.2f", employee.name, score, employee.get_average_score())
        return score

    def generate_daily_report(self):
        logger.info("Generating daily work report")

        report_time = datetime.now()
        report = {
            'report_id': "REPORT_%s" % report_time.strftime('%Y%m%d'),
            'generated_at': report_time.isoformat(),
            'market_date': report_time.strftime('%Y-%m-%d'),
            'task_summary': {},
            'employee_performance': {},
            'issues_and_feedback': [],
            'recommendations': []
        }

        for task_id, task in self.tasks.items():
            if task.status == WorkStatus.COMPLETED or task.status == WorkStatus.VERIFIED:
                report['task_summary'][task_id] = {
                    'task_name': task.task_name,
                    'role': task.role,
                    'status': task.status.value,
                    'score': task.score,
                    'issues': task.issues
                }

        for role, employee in self.employees.items():
            report['employee_performance'][role] = {
                'name': employee.name,
                'role': employee.role,
                'today_average_score': employee.get_average_score(),
                'task_count': len([t for t in self.tasks.values() if t.role == role])
            }

        self.daily_report = report
        logger.info("Daily report generated: %s", report['report_id'])
        return report

    def report_to_user(self):
        if not self.daily_report:
            self.generate_daily_report()

        report = self.daily_report

        user_report = """
%s
Stock Trader Daily Work Report
Generated at: %s
Market Date: %s
%s

1. Today's Task Completion
""" % ("=" * 60, report['generated_at'], report['market_date'], "=" * 60)

        for task_id, task_info in report['task_summary'].items():
            status_icon = "OK" if task_info['status'] == 'verified' else "CIRCLE"
            user_report += "  %s %s - %s - Score: %s\n" % (status_icon, task_info['task_name'], task_info['role'], task_info['score'])
            if task_info['issues']:
                for issue in task_info['issues']:
                    user_report += "      Issue: %s\n" % issue

        user_report += "\n2. Employee Performance\n"
        for role, perf in report['employee_performance'].items():
            score = perf['today_average_score']
            rating = "Excellent" if score >= 90 else "Good" if score >= 80 else "Qualified" if score >= 70 else "Unqualified"
            user_report += "  %s: Average Score %.1f (%s)\n" % (perf['name'], score, rating)

        if report['issues_and_feedback']:
            user_report += "\n3. Issues and Feedback\n"
            for issue in report['issues_and_feedback']:
                user_report += "  - %s\n" % issue

        if report['recommendations']:
            user_report += "\n4. Recommendations\n"
            for rec in report['recommendations']:
                user_report += "  - %s\n" % rec

        user_report += "\n%s" % "=" * 60
        user_report += "\nNote: For detailed data, see data/news/logs/trader_manager.log"

        return user_report

    def dispatch_emergency_task(self, task_name, role, description, priority="high"):
        logger.warning("Emergency task dispatched: %s (Priority: %s)", task_name, priority)
        quality_requirements = ["Emergency task", "Priority handling", "Timely feedback"]
        task_id = self.create_task(task_name, role, description, datetime.now(), quality_requirements)
        return task_id

    def get_workflow_status(self):
        status = {
            'timestamp': datetime.now().isoformat(),
            'employees': {},
            'pending_tasks': [],
            'in_progress_tasks': [],
            'completed_tasks': []
        }

        for role, employee in self.employees.items():
            status['employees'][role] = {
                'name': employee.name,
                'is_working_time': employee.is_working_time(),
                'current_score': employee.get_average_score()
            }

        for task_id, task in self.tasks.items():
            task_info = {'task_id': task_id, 'task_name': task.task_name, 'role': task.role}
            if task.status == WorkStatus.PENDING:
                status['pending_tasks'].append(task_info)
            elif task.status == WorkStatus.IN_PROGRESS:
                status['in_progress_tasks'].append(task_info)
            elif task.status in [WorkStatus.COMPLETED, WorkStatus.VERIFIED]:
                status['completed_tasks'].append(task_info)

        return status

    def save_workflow_status(self):
        status_file = 'data/news/logs/workflow_status.json'
        status = self.get_workflow_status()

        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
            logger.info("Workflow status saved: %s", status_file)
            return True
        except Exception as e:
            logger.error("Failed to save workflow status: %s", e)
            return False

    def load_workflow_status(self):
        status_file = 'data/news/logs/workflow_status.json'

        if not os.path.exists(status_file):
            logger.warning("Workflow status file does not exist: %s", status_file)
            return None

        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            logger.info("Workflow status loaded")
            return status
        except Exception as e:
            logger.error("Failed to load workflow status: %s", e)
            return None


def main():
    logger.info("Starting Stock Trader Manager System")

    manager = TraderManager()

    logger.info("Creating daily tasks...")
    manager.create_task(
        "Daily News Collection",
        "news_collector",
        "Collect today's stock-related news including company announcements, industry dynamics, market news",
        datetime.now(),
        ["Cover major financial media", "At least 15 news items", "Clear classification"]
    )

    manager.create_task(
        "Daily Stock Data Collection",
        "stock_collector",
        "Extract related stocks from news data, filter and score",
        datetime.now(),
        ["At least 5 stocks", "Complete data fields", "Timely update"]
    )

    manager.create_task(
        "Daily Stock Analysis",
        "stock_analyst",
        "Analyze filtered stocks from technical, fundamental, and news perspectives",
        datetime.now(),
        ["At least 3 stocks analyzed", "Include recommendation rating", "Clear risk level"]
    )

    manager.create_task(
        "Daily Investment Report Generation",
        "stock_reporter",
        "Generate final investment recommendation report",
        datetime.now(),
        ["Include market overview", "At least 3 recommended stocks", "Standard report format"]
    )

    logger.info("Initialization complete, waiting for task assignment...")

    status = manager.get_workflow_status()
    logger.info("Current status: Pending %d, In Progress %d, Completed %d",
                len(status['pending_tasks']), len(status['in_progress_tasks']), len(status['completed_tasks']))


if __name__ == '__main__':
    main()