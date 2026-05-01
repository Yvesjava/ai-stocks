from trading_agents_cn import TradingAgentsCN
from datetime import datetime
import time

class StockTradingWorkflow:
    """股票交易工作流"""
    def __init__(self, base_url="http://192.168.10.10", username="admin", password="admin123"):
        self.client = TradingAgentsCN(base_url, username, password)
        self.logs = []

    def _log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.logs.append(log_message)
        print(log_message)

    def login(self):
        """1. 登录认证"""
        self._log("开始登录认证...")
        success, msg = self.client.login()
        if success:
            self._log(f"登录成功: {msg}")
            return True, ""
        else:
            self._log(f"登录失败: {msg}")
            return False, msg

    def check_stock_exists(self, stock_code):
        """2. 检查股票是否存在"""
        self._log(f"检查股票 {stock_code} 是否存在...")
        basic_info, msg = self.client.get_basic_stock_info(stock_code)
        if basic_info:
            stock_name = basic_info.get('name', 'Unknown')
            self._log(f"股票存在: {stock_name} ({stock_code})")
            return True, stock_name
        else:
            self._log(f"股票不存在: {msg}")
            return False, msg

    def get_favorites(self):
        """3. 获取自选股"""
        self._log("获取自选股列表...")
        favorites, msg = self.client.get_favorites()
        if favorites:
            self._log(f"自选股数量: {len(favorites)}")
            for stock in favorites:
                self._log(f"  - {stock['stock_name']} ({stock['stock_code']}): {stock['current_price']}")
            return favorites
        else:
            self._log(f"获取自选股失败: {msg}")
            return []

    def add_to_favorites(self, stock_code, stock_name, market="A股"):
        """4. 添加自选股"""
        self._log(f"添加 {stock_name} ({stock_code}) 到自选股...")
        result, msg = self.client.add_to_favorites(stock_code, stock_name, market)
        if result:
            self._log(f"添加成功: {stock_code}")
            return True
        else:
            if "已在自选股中" in msg:
                self._log(f"股票已在自选股中: {msg}")
                return True
            else:
                self._log(f"添加失败: {msg}")
                return False

    def sync_stock_data(self, stock_code):
        """5. 同步股票数据"""
        self._log(f"同步 {stock_code} 数据...")
        sync_result, msg = self.client.sync_stock_data(stock_code)
        if sync_result:
            self._log(f"历史数据同步: {sync_result.get('historical_sync', {}).get('success')}")
            self._log(f"财务数据同步: {sync_result.get('financial_sync', {}).get('success')}")
            return True
        else:
            self._log(f"同步失败: {msg}")
            return False

    def analyze_stock(self, stock_code, research_depth="全面"):
        """6. 分析股票"""
        self._log(f"分析 {stock_code}...")
        analysis_result, msg = self.client.analyze_stock(stock_code, research_depth=research_depth)
        if analysis_result:
            task_id = analysis_result.get('task_id')
            self._log(f"分析任务创建成功: {task_id}")
            return task_id
        else:
            self._log(f"分析任务创建失败: {msg}")
            return None

    def wait_for_analysis_completion(self, task_id, timeout=1800):
        """7. 等待分析完成"""
        self._log(f"等待分析任务完成: {task_id}")
        task_status, msg = self.client.wait_for_completion(task_id, timeout=timeout)
        if task_status:
            self._log("分析任务完成")
            return True
        else:
            self._log(f"分析任务失败: {msg}")
            return False

    def get_report(self, report_id):
        """8. 获取报告"""
        self._log(f"获取报告: {report_id}")
        report, msg = self.client.get_report_detail(report_id)
        if report:
            self._log(f"报告获取成功: {report.get('stock_name')} ({report.get('stock_symbol')})")
            self._log(f"推荐: {report.get('recommendation')}")
            return report
        else:
            self._log(f"报告获取失败: {msg}")
            return None

    def run_full_workflow(self, stock_code, stock_name=None, research_depth="全面"):
        """运行完整工作流"""
        self._log("开始完整工作流")
        self._log("=" * 60)

        # 1. 登录
        login_success, msg = self.login()
        if not login_success:
            return False, f"登录失败: {msg}"

        # 2. 检查股票是否存在
        stock_exists, stock_name = self.check_stock_exists(stock_code)
        if not stock_exists:
            return False, f"股票不存在: {stock_name}"

        # 3. 获取自选股
        favorites = self.get_favorites()

        # 4. 检查是否在自选股中，不在则添加
        in_favorites = any(stock['stock_code'] == stock_code for stock in favorites)
        if not in_favorites:
            add_success = self.add_to_favorites(stock_code, stock_name)
            if not add_success:
                return False, "添加自选股失败"

        # 5. 同步股票数据
        sync_success = self.sync_stock_data(stock_code)
        if not sync_success:
            self._log("同步数据失败，但继续分析")

        # 6. 分析股票
        task_id = self.analyze_stock(stock_code, research_depth)
        if not task_id:
            return False, "分析任务创建失败"

        # 7. 等待分析完成
        completion_success = self.wait_for_analysis_completion(task_id)
        if not completion_success:
            return False, "分析任务失败"

        # 8. 获取报告（注意：需要从任务结果中提取报告ID）
        # 这里需要根据实际情况调整，暂时返回任务ID
        self._log("工作流完成")
        self._log("=" * 60)
        return True, task_id

    def get_stock_collector_workflow(self, stock_code):
        """股票收集员工作流"""
        self._log("开始股票收集员工作流")
        self._log("=" * 60)

        # 1. 登录
        login_success, msg = self.login()
        if not login_success:
            return False, f"登录失败: {msg}"

        # 2. 检查股票是否存在
        stock_exists, stock_name = self.check_stock_exists(stock_code)
        if not stock_exists:
            self._log("股票不存在，股票收集员需要受到惩罚")
            return False, "股票不存在，股票收集员错误"

        self._log("股票收集员工作流完成")
        self._log("=" * 60)
        return True, stock_name


class StockCollectorAgent:
    """股票收集员Agent"""
    def __init__(self, workflow):
        self.workflow = workflow
        self.score = 100
        self.penalties = []

    def check_stock(self, stock_code):
        """检查股票"""
        success, msg = self.workflow.get_stock_collector_workflow(stock_code)
        if not success:
            # 股票不存在，惩罚股票收集员
            self.score -= 20
            penalty = f"股票 {stock_code} 不存在，扣20分"
            self.penalties.append(penalty)
            self.workflow._log(penalty)
            self.workflow._log(f"当前分数: {self.score}")
        else:
            self.workflow._log(f"股票 {stock_code} 存在，检查通过")
        return success, msg

    def get_score(self):
        """获取分数"""
        return self.score

    def get_penalties(self):
        """获取惩罚记录"""
        return self.penalties


def main():
    """测试工作流"""
    workflow = StockTradingWorkflow()
    collector = StockCollectorAgent(workflow)

    # 测试股票收集员工作流
    print("=== 测试股票收集员工作流 ===")
    # 测试存在的股票
    success, msg = collector.check_stock("002594")
    print(f"比亚迪检查结果: {success} - {msg}")
    
    # 测试不存在的股票
    success, msg = collector.check_stock("999999")
    print(f"不存在股票检查结果: {success} - {msg}")
    
    print(f"股票收集员分数: {collector.get_score()}")
    print(f"惩罚记录: {collector.get_penalties()}")

    # 测试完整工作流
    print("\n=== 测试完整工作流 ===")
    success, result = workflow.run_full_workflow("002594")
    print(f"完整工作流结果: {success} - {result}")


if __name__ == "__main__":
    main()
