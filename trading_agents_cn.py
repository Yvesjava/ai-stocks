import requests
import json
from datetime import datetime

class TradingAgentsCN:
    def __init__(self, base_url="http://192.168.10.10", username="admin", password="admin123"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.token_expires_at = None
        self.session = requests.Session()

    def _generate_request_id(self):
        """生成请求ID"""
        timestamp = int(datetime.now().timestamp() * 1000)
        import random
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"req_{timestamp}_{random_str}"

    def login(self):
        """登录并获取token"""
        url = f"{self.base_url}/api/auth/login"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'pragma': 'no-cache',
            'x-request-id': self._generate_request_id()
        }
        body = '{"username":"admin","password":"admin123"}'

        try:
            response = self.session.post(url, headers=headers, data=body, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data["data"]["access_token"]
                    expires_in = data["data"]["expires_in"]
                    self.token_expires_at = datetime.now().timestamp() + expires_in
                    return True, "Login successful"
                return False, data.get("message", "Login failed")
            return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Login error: {str(e)}"

    def _get_headers(self):
        """获取请求头"""
        if self.token and datetime.now().timestamp() < self.token_expires_at:
            return {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'zh-CN',
                'authorization': f'Bearer {self.token}',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'x-request-id': self._generate_request_id()
            }
        success, msg = self.login()
        if success:
            return self._get_headers()
        return {}

    def get_favorites(self):
        """获取自选股"""
        url = f"{self.base_url}/api/favorites/"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        try:
            response = self.session.get(url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def add_to_favorites(self, stock_code, stock_name, market="A股", tags=None, notes=""):
        """添加股票到自选股"""
        url = f"{self.base_url}/api/favorites/"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        if tags is None:
            tags = []

        body = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "market": market,
            "tags": tags,
            "notes": notes
        }

        try:
            response = self.session.post(url, headers=headers, json=body, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def get_stock_data(self, stock_code):
        """获取单个股票数据"""
        favorites, msg = self.get_favorites()
        if not favorites:
            return None, msg

        for stock in favorites:
            if stock["stock_code"] == stock_code:
                return stock, "Success"
        return None, f"Stock {stock_code} not found in favorites"

    def sync_stock_data(self, stock_code, sync_realtime=True, sync_historical=True, sync_financial=True, data_source="akshare", days=365):
        """同步股票数据"""
        url = f"{self.base_url}/api/stock-sync/single"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        body = {
            "symbol": stock_code,
            "sync_realtime": sync_realtime,
            "sync_historical": sync_historical,
            "sync_financial": sync_financial,
            "data_source": data_source,
            "days": days
        }

        try:
            response = self.session.post(url, headers=headers, json=body, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def analyze_stock(self, stock_code, market_type="A股", analysis_date=None, research_depth="全面",
                     selected_analysts=["market", "fundamentals", "news"],
                     include_sentiment=True, include_risk=True, language="zh-CN",
                     quick_analysis_model="qwen-flash", deep_analysis_model="qwen-plus"):
        """分析股票"""
        url = f"{self.base_url}/api/analysis/single"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        if not analysis_date:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        body = {
            "symbol": stock_code,
            "stock_code": stock_code,
            "parameters": {
                "market_type": market_type,
                "analysis_date": analysis_date,
                "research_depth": research_depth,
                "selected_analysts": selected_analysts,
                "include_sentiment": include_sentiment,
                "include_risk": include_risk,
                "language": language,
                "quick_analysis_model": quick_analysis_model,
                "deep_analysis_model": deep_analysis_model
            }
        }

        try:
            response = self.session.post(url, headers=headers, json=body, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def get_task_status(self, task_id):
        """获取任务状态"""
        url = f"{self.base_url}/api/analysis/tasks/{task_id}/status"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        try:
            response = self.session.get(url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def get_report_detail(self, report_id):
        """获取报告详情"""
        url = f"{self.base_url}/api/reports/{report_id}/detail"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        try:
            response = self.session.get(url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def get_basic_stock_info(self, stock_code):
        """获取股票基本信息"""
        url = f"{self.base_url}/api/stock-data/basic-info/{stock_code}"
        headers = self._get_headers()

        if not headers.get('authorization'):
            return None, "No valid token"

        try:
            response = self.session.get(url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            return None, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def wait_for_completion(self, task_id, timeout=3600, interval=5):
        """等待任务完成"""
        start_time = datetime.now().timestamp()
        while datetime.now().timestamp() - start_time < timeout:
            task_status, msg = self.get_task_status(task_id)
            if task_status:
                status = task_status.get('status')
                progress = task_status.get('progress', 0)
                message = task_status.get('message', '')
                print(f"进度: {progress}% - {message}")

                if status == 'completed':
                    print("分析完成！")
                    return task_status, "Success"
                elif status == 'failed':
                    error_msg = task_status.get('error_message', 'Unknown error')
                    print(f"分析失败: {error_msg}")
                    return None, error_msg
            import time
            time.sleep(interval)
        return None, "Timeout waiting for task completion"

    def refresh_favorites(self):
        """刷新自选股数据"""
        return self.get_favorites()


def main():
    """测试 TradingAgentsCN 工具"""
    print("Testing TradingAgents-CN...")
    print("=" * 60)

    client = TradingAgentsCN()

    success, msg = client.login()
    print(f"Login: {success} - {msg}")

    if success:
        print("\n1. Getting favorites:")
        favorites, msg = client.get_favorites()
        if favorites:
            print(f"   Favorites ({len(favorites)} stocks):")
            for stock in favorites:
                print(f"   - {stock['stock_name']} ({stock['stock_code']}): {stock['current_price']}")
        else:
            print(f"   Failed to get favorites: {msg}")

        print("\n2. Adding stock to favorites:")
        result, msg = client.add_to_favorites("002594", "比亚迪", "A股")
        if result:
            print(f"   Success: Added {result.get('stock_code')}")
        else:
            print(f"   Failed: {msg}")

        print("\n3. Getting updated favorites:")
        favorites, msg = client.get_favorites()
        if favorites:
            print(f"   Favorites ({len(favorites)} stocks):")
            for stock in favorites:
                print(f"   - {stock['stock_name']} ({stock['stock_code']}): {stock['current_price']}")
        else:
            print(f"   Failed to get favorites: {msg}")

        print("\n4. Getting BYD basic info:")
        basic_info, msg = client.get_basic_stock_info("002594")
        if basic_info:
            print(f"   Symbol: {basic_info.get('symbol')}")
            print(f"   Name: {basic_info.get('name')}")
            print(f"   Market: {basic_info.get('market')}")
            print(f"   Exchange: {basic_info.get('sse')}")
        else:
            print(f"   Failed: {msg}")


if __name__ == "__main__":
    main()
