#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻采集员模块
功能：从财联社、东方财富等真实渠道采集新闻，清洗整理后存储为JSON文件
"""

import os
import json
import re
import logging
from datetime import datetime, timedelta
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/news/logs/collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('news_collector')


class NewsCollector:
    def __init__(self):
        self.base_dir = 'data/news'
        self.raw_dir = os.path.join(self.base_dir, 'raw')
        self.processed_dir = os.path.join(self.base_dir, 'processed')
        self.structured_dir = os.path.join(self.base_dir, 'structured')

        for dir_path in [self.raw_dir, self.processed_dir, self.structured_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        self.stocks = {
            '600519': ('贵州茅台', ['茅台', '贵州茅台', '飞天茅台']),
            '000858': ('五粮液', ['五粮液']),
            '601318': ('中国平安', ['中国平安', '平安']),
            '600036': ('招商银行', ['招商银行', '招行']),
            '000333': ('美的集团', ['美的集团', '美的']),
            '000001': ('平安银行', ['平安银行']),
            '601888': ('中国中免', ['中国中免', '中免']),
            '600276': ('恒瑞医药', ['恒瑞医药', '恒瑞']),
            '002594': ('比亚迪', ['比亚迪', 'BYD']),
            '601012': ('隆基绿能', ['隆基绿能', '隆基']),
            '300750': ('宁德时代', ['宁德时代', '宁德', 'CATL']),
            '601857': ('中国石油', ['中国石油', '中石油']),
            '600028': ('中国石化', ['中国石化', '中石化']),
            '601398': ('工商银行', ['工商银行', '工行']),
            '601288': ('农业银行', ['农业银行', '农行']),
            '601939': ('建设银行', ['建设银行', '建行']),
            '601988': ('中国银行', ['中国银行', '中行']),
            '000651': ('格力电器', ['格力电器', '格力']),
            '002415': ('海康威视', ['海康威视', '海康']),
            '000725': ('京东方A', ['京东方', '京东方A']),
            '300059': ('东方财富', ['东方财富', '东财']),
            '603259': ('药明康德', ['药明康德', '药明']),
            '600900': ('长江电力', ['长江电力']),
            '601899': ('紫金矿业', ['紫金矿业', '紫金']),
            '600809': ('山西汾酒', ['山西汾酒', '汾酒']),
            '002475': ('立讯精密', ['立讯精密', '立讯']),
            '688981': ('中芯国际', ['中芯国际', '中芯']),
            '000002': ('万科A', ['万科', '万科A']),
            '600030': ('中信证券', ['中信证券', '中信']),
            '300124': ('汇川技术', ['汇川技术', '汇川']),
            '002714': ('牧原股份', ['牧原股份', '牧原']),
            '000568': ('泸州老窖', ['泸州老窖', '老窖']),
            '601166': ('兴业银行', ['兴业银行', '兴业']),
            '600887': ('伊利股份', ['伊利股份', '伊利']),
            '002230': ('科大讯飞', ['科大讯飞', '科大讯飞', '讯飞']),
            '601888': ('中国中免', ['中国中免', '中免']),
            '600048': ('保利发展', ['保利发展', '保利']),
            '002594': ('比亚迪', ['比亚迪', 'BYD']),
            '002241': ('歌尔股份', ['歌尔股份', '歌尔']),
            '600585': ('海螺水泥', ['海螺水泥', '海螺']),
            '600690': ('海尔智家', ['海尔智家', '海尔']),
            '688111': ('金山办公', ['金山办公', '金山']),
            '002027': ('分众传媒', ['分众传媒', '分众']),
            '601728': ('中国电信', ['中国电信', '电信']),
        }

        self.category_keywords = {
            '公司公告': ['公告', '披露', '董事会', '股东大会', '重组', '停牌', '复牌'],
            '公司财报': ['营收', '利润', '业绩', '财报', '年报', '季报', '净利润', '同比增长'],
            '行业动态': ['行业', '产业', '政策', '赛道', '板块'],
            '宏观政策': ['央行', '利率', '货币', '财政', '证监会'],
            '市场行情': ['大盘', '指数', '成交额', '涨停', '跌停', 'A股', '沪指', '深指'],
            '概念热点': ['AI', '人工智能', '新能源', '芯片', '半导体', '机器人'],
            '突发事件': ['突发', '紧急', '预警', '危机'],
            '监管动态': ['监管', '处罚', '违规', '问询', '调查'],
            '机构研报': ['研报', '评级', '目标价', '推荐', '买入'],
            '国际市场': ['美股', '港股', '美联储', '原油', '黄金', '外汇'],
        }

        self.positive_words = ['增长', '上涨', '利好', '突破', '创新高', '盈利', '改善', '提升',
                               '加速', '扩张', '中标', '签约', '分红', '回购', '增持', '大涨']
        self.negative_words = ['下跌', '亏损', '下滑', '风险', '处罚', '违规', '暴跌', '衰退',
                               '萎缩', '危机', '诉讼', '警告', '减持', '跌停', '退市', '爆雷']

    # ============================================================
    # 真实数据源
    # ============================================================

    def _fetch_cls_news(self):
        """从财联社电报获取新闻"""
        import akshare as ak
        df = ak.stock_info_global_cls()
        items = []
        for _, row in df.iterrows():
            title = str(row.iloc[0]).strip() if row.iloc[0] else ''
            content = str(row.iloc[1]).strip() if row.iloc[1] else ''
            pub_date = str(row.iloc[2]).strip() if row.iloc[2] else ''
            pub_time = str(row.iloc[3]).strip() if row.iloc[3] else ''
            if not title and not content:
                continue
            text = content if content else title
            publish_time = f"{pub_date} {pub_time}" if pub_date else datetime.now().isoformat()
            items.append({
                'title': title if title else text[:40],
                'content': text,
                'publish_time': publish_time,
                'url': '',
            })
        logger.info("财联社: 获取 %d 条电报", len(items))
        return items

    def _fetch_eastmoney_news(self):
        """从东方财富获取新闻"""
        import akshare as ak
        df = ak.stock_info_global_em()
        items = []
        for _, row in df.iterrows():
            title = str(row.iloc[0]).strip() if row.iloc[0] else ''
            summary = str(row.iloc[1]).strip() if row.iloc[1] else ''
            pub_time = str(row.iloc[2]).strip() if row.iloc[2] else ''
            url = str(row.iloc[3]).strip() if row.iloc[3] else ''
            if not title:
                continue
            content = summary if summary else title
            items.append({
                'title': title,
                'content': content,
                'publish_time': pub_time,
                'url': url,
            })
        logger.info("东方财富: 获取 %d 条新闻", len(items))
        return items

    def _fetch_sina_news(self):
        """从新浪财经获取新闻（2列：时间、内容，无独立标题列）"""
        import akshare as ak
        try:
            df = ak.stock_info_global_sina()
            items = []
            for _, row in df.iterrows():
                pub_time = str(row.iloc[0]).strip() if row.iloc[0] else ''
                content = str(row.iloc[1]).strip() if row.iloc[1] else ''
                if not content:
                    continue
                # 用内容前30字作为标题
                title = content[:30]
                items.append({
                    'title': title,
                    'content': content,
                    'publish_time': pub_time,
                    'url': '',
                })
            logger.info("新浪财经: 获取 %d 条新闻", len(items))
            return items
        except Exception as e:
            logger.warning("新浪财经获取失败: %s", e)
            return []

    # ============================================================
    # 采集主流程
    # ============================================================

    def fetch_all_news(self):
        """从所有真实数据源采集新闻"""
        sources = [
            ('财联社', self._fetch_cls_news),
            ('东方财富', self._fetch_eastmoney_news),
            ('新浪财经', self._fetch_sina_news),
        ]
        all_news = []
        for name, fetcher in sources:
            try:
                items = fetcher()
                for item in items:
                    item['source'] = name
                all_news.extend(items)
            except Exception as e:
                logger.warning("数据源 %s 获取失败: %s", name, e)
        return all_news

    # ============================================================
    # 新闻处理
    # ============================================================

    def detect_stocks(self, text):
        """从新闻文字中识别涉及的股票"""
        matched = []
        for code, (name, aliases) in self.stocks.items():
            for alias in aliases:
                if alias in text:
                    matched.append({
                        'stock_code': code,
                        'stock_name': name,
                        'mention_type': '直接提及'
                    })
                    break
        return matched

    def classify_news(self, text):
        """对新闻进行自动分类"""
        primary = '市场行情'
        max_hits = 0
        secondary = []
        for category, keywords in self.category_keywords.items():
            hits = sum(1 for kw in keywords if kw in text)
            if hits > max_hits:
                max_hits = hits
                primary = category
            if hits > 0 and category != primary:
                secondary.append(category)
        if not secondary:
            secondary = ['市场行情']
        tags = [kw for kw, v in self.category_keywords.items() for word in self.category_keywords[kw]
                if word in text][:3]
        return primary, secondary[:2], tags

    def analyze_sentiment(self, text):
        """基于关键词的情感分析"""
        pos = sum(1 for w in self.positive_words if w in text)
        neg = sum(1 for w in self.negative_words if w in text)
        if pos > neg:
            score = min(0.3 + pos * 0.15, 1.0)
            return 'positive', round(score, 2), '正面关键词占比高'
        elif neg > pos:
            score = max(-0.3 - neg * 0.15, -1.0)
            return 'negative', round(score, 2), '负面关键词占比高'
        else:
            return 'neutral', 0.0, '无明显情感倾向'

    def determine_impact(self, text, stocks_count):
        """判断新闻影响级别"""
        high_signals = ['突发', '紧急', '重大', '重组', '停牌', '处罚', '退市', '涨停', '跌停']
        medium_signals = ['增长', '下滑', '政策', '监管', '收购', '增持', '减持']
        if any(kw in text for kw in high_signals) or stocks_count >= 3:
            return 'high'
        elif any(kw in text for kw in medium_signals) or stocks_count >= 1:
            return 'medium'
        return 'low'

    def parse_publish_time(self, time_str):
        """解析各种格式的发布时间，返回ISO格式"""
        if not time_str:
            return datetime.now().isoformat()
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%d',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        # 尝试提取日期+时间
        match = re.search(r'(\d{4}-\d{2}-\d{2}).*?(\d{2}:\d{2}(:\d{2})?)', time_str)
        if match:
            t = f"{match.group(1)} {match.group(2)}"
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
                try:
                    return datetime.strptime(t, fmt).isoformat()
                except ValueError:
                    continue
        return datetime.now().isoformat()

    def build_news_item(self, raw, source_name):
        """将原始新闻转换为标准格式"""
        text = raw.get('content', '') or raw.get('title', '')
        title = raw.get('title', text[:40])

        # 识别股票
        related_stocks = self.detect_stocks(text)

        # 分类
        primary, secondary, tags = self.classify_news(text)

        # 情感分析
        sentiment_label, sentiment_score, sentiment_reason = self.analyze_sentiment(text)

        # 影响级别
        impact = self.determine_impact(text, len(related_stocks))

        # 发布时间
        publish_time = self.parse_publish_time(raw.get('publish_time', ''))

        news_id = self.generate_news_id(title + text[:50])

        return {
            'news_id': news_id,
            'title': title,
            'original_title': title,
            'source': source_name,
            'source_type': '财经媒体',
            'source_url': raw.get('url', ''),
            'publish_time': publish_time,
            'collect_time': datetime.now().isoformat(),
            'summary': text[:100] + ('...' if len(text) > 100 else ''),
            'content': text,
            'related_stocks': related_stocks,
            'category': {
                'primary': primary,
                'secondary': secondary,
                'tags': tags if tags else [primary],
            },
            'sentiment': {
                'overall': sentiment_label,
                'score': sentiment_score,
                'reason': sentiment_reason,
            },
            'impact_level': impact,
            'market_reaction_expected': '预计影响相关个股' if related_stocks else '暂无明显个股指向',
            'metadata': {
                'word_count': len(text),
                'has_image': False,
                'is_original': True,
                'is_headline': False,
            }
        }

    def generate_news_id(self, content):
        """生成唯一新闻ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_str = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        return f"NEWS_{timestamp}_{hash_str}"

    # ============================================================
    # 数据持久化
    # ============================================================

    def save_raw_news(self, news_list):
        """保存原始新闻数据（按来源分组）"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        raw_date_dir = os.path.join(self.raw_dir, date_str)
        if not os.path.exists(raw_date_dir):
            os.makedirs(raw_date_dir)
        source_news = {}
        for news in news_list:
            source = news['source']
            if source not in source_news:
                source_news[source] = []
            source_news[source].append(news)
        for source, items in source_news.items():
            safe_name = source.replace(' ', '_')
            filepath = os.path.join(raw_date_dir, f"{safe_name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            logger.info("保存原始新闻到 %s，共 %d 条", filepath, len(items))

    def save_processed_news(self, processed_news):
        """保存处理后的新闻数据（逐条存储）"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        processed_date_dir = os.path.join(self.processed_dir, date_str)
        if not os.path.exists(processed_date_dir):
            os.makedirs(processed_date_dir)
        for news in processed_news:
            filepath = os.path.join(processed_date_dir, f"{news['news_id']}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news, f, indent=2, ensure_ascii=False)
        logger.info("保存处理后新闻到 %s，共 %d 条", processed_date_dir, len(processed_news))

    def save_structured_news(self, processed_news):
        """保存结构化新闻数据供下游Agent使用"""
        structured_file = os.path.join(self.structured_dir, 'news_database.json')
        existing_news = []
        if os.path.exists(structured_file):
            with open(structured_file, 'r', encoding='utf-8') as f:
                try:
                    existing_news = json.load(f)
                except Exception:
                    existing_news = []
        existing_ids = {news['news_id'] for news in existing_news}
        new_news = [news for news in processed_news if news['news_id'] not in existing_ids]
        all_news = existing_news + new_news
        all_news.sort(key=lambda x: x['publish_time'], reverse=True)
        with open(structured_file, 'w', encoding='utf-8') as f:
            json.dump(all_news, f, indent=2, ensure_ascii=False)
        logger.info("保存结构化新闻到 %s，新增 %d 条，总计 %d 条",
                     structured_file, len(new_news), len(all_news))

    # ============================================================
    # 主入口
    # ============================================================

    def collect(self, count=15):
        """执行采集流程"""
        logger.info("开始从真实数据源采集新闻，目标数量：%d", count)

        raw_items = self.fetch_all_news()
        if not raw_items:
            logger.warning("所有数据源均未返回结果，本次采集为空")
            return []

        logger.info("共获取 %d 条原始新闻，正在处理...", len(raw_items))

        # 转换为标准格式并去重
        processed = []
        seen_titles = set()
        for raw in raw_items:
            item = self.build_news_item(raw, raw['source'])
            title_key = item['title'][:30]
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            processed.append(item)

        # 优先选取有股票关联的新闻，再补充其他新闻
        with_stocks = [n for n in processed if n['related_stocks']]
        without_stocks = [n for n in processed if not n['related_stocks']]
        logger.info("含股票关联: %d 条, 其他: %d 条", len(with_stocks), len(without_stocks))

        # 按发布时间降序排列
        with_stocks.sort(key=lambda x: x['publish_time'], reverse=True)
        without_stocks.sort(key=lambda x: x['publish_time'], reverse=True)

        # 优先取含股票关联的新闻，不足时用其他新闻补充
        selected = with_stocks[:count]
        if len(selected) < count:
            selected += without_stocks[:(count - len(selected))]

        processed = selected

        # 持久化
        self.save_raw_news(processed)
        self.save_processed_news(processed)
        self.save_structured_news(processed)

        logger.info("新闻采集流程完成，有效新闻 %d 条", len(processed))
        return processed


def main():
    collector = NewsCollector()

    print("=" * 60)
    print("  股票分析系统 - 新闻采集员")
    print("  数据源: 财联社, 东方财富, 新浪财经")
    print("=" * 60)

    collected = collector.collect(15)

    if not collected:
        print("\n[警告] 未能获取到新闻，请检查网络连接")
        return

    print(f"\n采集完成，共收集 {len(collected)} 条新闻\n")

    for i, news in enumerate(collected[:5]):
        print(f"{i+1}. {news['title']}")
        print(f"   来源: {news['source']}")
        print(f"   分类: {news['category']['primary']}")
        print(f"   情感: {news['sentiment']['overall']} ({news['sentiment']['score']})")
        stocks = [s['stock_name'] for s in news['related_stocks']]
        if stocks:
            print(f"   涉及股票: {', '.join(stocks)}")
        else:
            print("   涉及股票: 无")
        print()


if __name__ == '__main__':
    main()
