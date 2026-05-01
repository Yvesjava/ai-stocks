#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run the stock trader workflow"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_integration import WorkFlowEngine
from datetime import datetime

if __name__ == '__main__':
    print('=' * 60)
    print('Stock Trader Management System - Workflow Execution')
    print('=' * 60)

    engine = WorkFlowEngine()

    print('\nStart time: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('\nStarting workflow...\n')

    result = engine.run_full_workflow(stop_on_error=False)

    print('\n' + '=' * 60)
    if result:
        print('Workflow completed successfully')
    else:
        print('Workflow completed with errors')
    print('=' * 60)

    summary = engine.get_workflow_summary()
    print('\nWorkflow Summary:')
    print('  Workflow ID: %s' % summary['workflow_id'])
    print('  Started at: %s' % summary['started_at'])
    print('  Completed at: %s' % summary['completed_at'])
    print('  Total duration: %.2f seconds' % (summary['total_duration'] or 0))

    print('\nStage Results:')
    for stage_name, stage_info in summary['stages'].items():
        status = stage_info.get('status', 'unknown')
        duration = stage_info.get('duration', 0)
        error = stage_info.get('error')
        print('  %s: %s (%.2fs)' % (stage_name, status, duration or 0))
        if error:
            print('    Error: %s' % error)

    engine.save_workflow_result()
    print('\nEnd time: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))