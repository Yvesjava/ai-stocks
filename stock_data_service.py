import requests
import json
from datetime import datetime

class StockDataService:
    def __init__(self):
        self.base_url = "http://192.168.10.10"
        self.token = None
        self.session = requests.Session()

    def login(self, username="admin", password="admin123"):
        try:
            resp = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    self.token = data["data"]["access_token"]
                    return True, "Login successful"
            return False, f"Login failed: {resp.text}"
        except Exception as e:
            return False, f"Login error: {str(e)}"

    def _get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get_realtime_quote(self, stock_code):
        if not self.token:
            success, msg = self.login()
            if not success:
                return None, msg

        try:
            resp = self.session.post(
                f"{self.base_url}/api/stocks/realtime",
                json={"stock_code": stock_code},
                headers=self._get_headers(),
                timeout=30
            )

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            elif resp.status_code == 404:
                return None, "API endpoint not found - TradingAgents-CN backend is proprietary"
            else:
                return None, f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"

    def analyze_stock(self, stock_code, stock_name=""):
        if not self.token:
            success, msg = self.login()
            if not success:
                return None, msg

        try:
            resp = self.session.post(
                f"{self.base_url}/api/analyze/stock",
                json={"stock_code": stock_code, "stock_name": stock_name},
                headers=self._get_headers(),
                timeout=120
            )

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data["data"], "Success"
                return None, data.get("message", "Unknown error")
            elif resp.status_code == 404:
                return None, "Analysis API not found - TradingAgents-CN backend is proprietary"
            else:
                return None, f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            return None, f"Request error: {str(e)}"


def get_stock_realtime_price(stock_code):
    service = StockDataService()

    result, msg = service.get_realtime_quote(stock_code)
    if result:
        return {
            "success": True,
            "stock_code": stock_code,
            "current_price": result.get("current_price") or result.get("price"),
            "change": result.get("change"),
            "change_percent": result.get("change_percent"),
            "high": result.get("high"),
            "low": result.get("low"),
            "open": result.get("open"),
            "previous_close": result.get("previous_close"),
            "volume": result.get("volume"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        return {
            "success": False,
            "stock_code": stock_code,
            "error": msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":
    print("Testing Stock Data Service...")
    print("-" * 50)

    stocks = {
        "002594": "比亚迪",
        "000858": "五粮液",
        "600519": "贵州茅台"
    }

    for code, name in stocks.items():
        result = get_stock_realtime_price(code)
        print(f"\n{name} ({code}):")
        if result["success"]:
            print(f"  当前价: {result['current_price']}")
            print(f"  涨跌: {result['change']} ({result['change_percent']}%)")
        else:
            print(f"  错误: {result['error']}")
