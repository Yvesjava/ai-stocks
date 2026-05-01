#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知服务模块
功能：通过多种IM渠道发送股票报告通知
支持：QQ、微信、企业微信等
"""

import os
import logging
from datetime import datetime
import abc

# 兼容 Python 2.7
if hasattr(abc, 'ABC'):
    ABC = abc.ABC
else:
    class ABC(object):
        __metaclass__ = abc.ABCMeta

abstractmethod = abc.abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/notification_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('notification_service')


class NotificationChannel(ABC):
    """通知渠道抽象基类"""
    
    @abstractmethod
    def send(self, message, report_data=None):
        """发送通知"""
        pass
    
    @abstractmethod
    def format_message(self, report_data):
        """格式化消息"""
        pass


class WeChatNotification(NotificationChannel):
    """微信通知"""
    
    def __init__(self, app_id=None, app_secret=None, template_id=None):
        self.app_id = app_id or os.environ.get('WECHAT_APP_ID', '')
        self.app_secret = app_secret or os.environ.get('WECHAT_APP_SECRET', '')
        self.template_id = template_id or os.environ.get('WECHAT_TEMPLATE_ID', '')
        self.access_token = None
    
    def send(self, message, report_data=None):
        try:
            if report_data:
                message = self.format_message(report_data)
            
            # 实际发送逻辑（这里使用模拟）
            logger.info("[微信] 发送通知: %s...", message[:50])
            return True
        except Exception as e:
            logger.error("[微信] 发送失败: %s", e)
            return False
    
    def format_message(self, report_data):
        date_str = report_data.get('report_date', datetime.now().isoformat())
        total_stocks = report_data.get('total_stocks', 0)
        
        message = "【股票推荐报告】\n"
        message += "生成时间: %s\n" % date_str
        message += "推荐股票: %d只\n\n" % total_stocks
        
        if report_data.get('recommended_stocks'):
            message += "推荐股票列表:\n"
            for i, stock in enumerate(report_data['recommended_stocks'][:3], 1):
                message += "%d. %s (%s)\n" % (i, stock['stock_name'], stock['stock_code'])
                message += "   推荐评级: %s\n" % stock['recommendation']
                message += "   目标价: %s元\n" % stock['target_price']
        
        message += "\n详情请查看完整报告"
        return message


class QQNotification(NotificationChannel):
    """QQ通知"""
    
    def __init__(self, qq_bot_key=None):
        self.qq_bot_key = qq_bot_key or os.environ.get('QQ_BOT_KEY', '')
    
    def send(self, message, report_data=None):
        try:
            if report_data:
                message = self.format_message(report_data)
            
            # 实际发送逻辑（这里使用模拟）
            logger.info("[QQ] 发送通知: %s...", message[:50])
            return True
        except Exception as e:
            logger.error("[QQ] 发送失败: %s", e)
            return False
    
    def format_message(self, report_data):
        return self._format_generic_message(report_data)


class WeComNotification(NotificationChannel):
    """企业微信通知"""
    
    def __init__(self, corp_id=None, corp_secret=None, agent_id=None):
        self.corp_id = corp_id or os.environ.get('WECOM_CORP_ID', '')
        self.corp_secret = corp_secret or os.environ.get('WECOM_CORP_SECRET', '')
        self.agent_id = agent_id or os.environ.get('WECOM_AGENT_ID', '')
        self.access_token = None
    
    def send(self, message, report_data=None):
        try:
            if report_data:
                message = self.format_message(report_data)
            
            # 实际发送逻辑（这里使用模拟）
            logger.info("[企业微信] 发送通知: %s...", message[:50])
            return True
        except Exception as e:
            logger.error("[企业微信] 发送失败: %s", e)
            return False
    
    def format_message(self, report_data):
        return self._format_generic_message(report_data)
    
    def _format_generic_message(self, report_data):
        date_str = report_data.get('report_date', datetime.now().isoformat())
        total_stocks = report_data.get('total_stocks', 0)
        
        message = "股票推荐报告\n"
        message += "==================\n"
        message += "📅 生成时间: %s\n" % date_str
        message += "📊 推荐股票: %d只\n" % total_stocks
        
        if report_data.get('recommended_stocks'):
            message += "\n🔥 推荐股票：\n"
            for i, stock in enumerate(report_data['recommended_stocks'][:3], 1):
                message += "%d. %s (%s)\n" % (i, stock['stock_name'], stock['stock_code'])
                message += "   ⭐ 评级: %s\n" % stock['recommendation']
                message += "   💰 目标价: %s元\n" % stock['target_price']
        
        message += "\n📈 详情请查看完整报告"
        return message


class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.channels = {
            'wechat': WeChatNotification(),
            'qq': QQNotification(),
            'wecom': WeComNotification()
        }
        
    def send_notification(self, report_data, channels=None):
        """发送通知到指定渠道"""
        if not channels:
            channels = list(self.channels.keys())
        
        results = {}
        for channel in channels:
            if channel in self.channels:
                success = self.channels[channel].send("", report_data)
                results[channel] = success
                logger.info("通知发送结果 - %s: %s", channel, '成功' if success else '失败')
            else:
                logger.warning("未知的通知渠道: %s", channel)
                results[channel] = False
        
        return results
    
    def test_connection(self, channel):
        """测试通知渠道连接"""
        if channel in self.channels:
            try:
                test_message = "测试消息：股票报告通知服务正常"
                return self.channels[channel].send(test_message)
            except Exception as e:
                logger.error("测试 %s 连接失败: %s", channel, e)
                return False
        return False
    
    def get_supported_channels(self):
        """获取支持的通知渠道"""
        return list(self.channels.keys())


def main():
    """测试通知服务"""
    notification_service = NotificationService()
    
    # 测试数据
    test_report = {
        "report_date": datetime.now().isoformat(),
        "total_stocks": 5,
        "recommended_stocks": [
            {
                "stock_code": "600519",
                "stock_name": "贵州茅台",
                "recommendation": "强烈推荐",
                "target_price": 1800.0
            },
            {
                "stock_code": "000858",
                "stock_name": "五粮液",
                "recommendation": "推荐",
                "target_price": 160.0
            }
        ]
    }
    
    print("测试通知服务...")
    print("支持的渠道: %s" % notification_service.get_supported_channels())
    
    # 测试所有渠道
    results = notification_service.send_notification(test_report)
    print("\n通知发送结果:")
    for channel, success in results.items():
        print("%s: %s" % (channel, '成功' if success else '失败'))


if __name__ == '__main__':
    main()
