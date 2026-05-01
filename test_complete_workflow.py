import time
from trading_agents_cn import TradingAgentsCN

def test_complete_workflow():
    """测试完整工作流"""
    print("Testing complete workflow...")
    print("=" * 60)

    # 初始化客户端
    client = TradingAgentsCN()

    # 1. 登录
    print("1. Logging in...")
    success, msg = client.login()
    print(f"Login: {success} - {msg}")

    if success:
        # 2. 同步比亚迪数据
        byd_code = "002594"
        print(f"\n2. Syncing BYD ({byd_code}) data...")
        sync_result, msg = client.sync_stock_data(byd_code)
        if sync_result:
            print(f"Overall success: {sync_result.get('overall_success')}")
            print(f"Historical sync: {sync_result.get('historical_sync', {}).get('success')}")
            print(f"Financial sync: {sync_result.get('financial_sync', {}).get('success')}")
        else:
            print(f"Failed to sync stock data: {msg}")

        # 3. 分析比亚迪
        print(f"\n3. Analyzing BYD ({byd_code})...")
        analysis_result, msg = client.analyze_stock(byd_code)
        if analysis_result:
            task_id = analysis_result.get('task_id')
            print(f"Task ID: {task_id}")
            print(f"Status: {analysis_result.get('status')}")
            
            # 4. 等待分析完成
            print("\n4. Waiting for analysis completion...")
            completed_task, msg = client.wait_for_completion(task_id, timeout=600)
            if completed_task:
                # 5. 获取报告
                # 注意：这里需要从任务结果中获取报告ID，暂时使用测试ID
                # 实际使用时需要从completed_task中提取报告ID
                test_report_id = "69afc9b3125d37569a44c4a2"
                print(f"\n5. Getting report detail...")
                report, msg = client.get_report_detail(test_report_id)
                if report:
                    print(f"Report ID: {report.get('id')}")
                    print(f"Stock: {report.get('stock_name')} ({report.get('stock_symbol')})")
                    print(f"Analysis date: {report.get('analysis_date')}")
                    print(f"Status: {report.get('status')}")
                    print(f"Recommendation: {report.get('recommendation')}")
                    print(f"Confidence: {report.get('confidence_score')}")
                    print(f"Risk level: {report.get('risk_level')}")
                    
                    # 打印摘要
                    summary = report.get('summary', '')
                    if summary:
                        print(f"\nSummary: {summary[:200]}...")
                else:
                    print(f"Failed to get report: {msg}")
            else:
                print(f"Analysis failed: {msg}")
        else:
            print(f"Failed to start analysis: {msg}")


if __name__ == "__main__":
    test_complete_workflow()
