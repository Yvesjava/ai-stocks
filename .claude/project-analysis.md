# AI-Stocks 项目分析文档 (2026-05-03)

## 一、项目概况

多Agent协同的智能股票分析系统，模拟新闻采集→股票筛选→深度分析→报告生成的四阶段流水线。纯Python实现，无Web框架，JSON文件存储。

---

## 二、完整文件清单

### 核心业务模块 (4个Agent)

| 文件 | 行数 | Shebang | 外部依赖 | 核心类 | 入口方法 | 说明 |
|------|------|---------|---------|--------|---------|------|
| `news_collector.py` | 327 | python3 | random, hashlib | `NewsCollector` | `collect(count=10)` | 生成模拟新闻，输出 `news_database.json` |
| `stock_collector.py` | 294 | python2 | 无 | `StockCollector` | `collect()` | 从新闻提取股票，输出 `stock_list.json` |
| `stock_analyst.py` | 314 | python2 | random | `StockAnalyst` | `analyze()` | **全模拟数据**分析，输出 `stock_analysis.json` |
| `stock_reporter.py` | 400 | python3 | `notification_service`, `data_manager` | `StockReporter` | `generate_report()` | 三层筛选+报告生成，输出报告JSON/MD |

### 基础设施模块

| 文件 | 行数 | 核心类 | 说明 |
|------|------|--------|------|
| `data_manager.py` | 306 | `DataManager` | JSON文件CRUD，完整数据链路查询 |
| `notification_service.py` | 234 | `NotificationService`, `WeChatNotification`, `QQNotification`, `WeComNotification` | 多渠道IM通知（均为模拟） |
| `display_service.py` | 628 | `DisplayService` | HTTP服务器(port 8000)，内嵌HTML+ECharts |
| `trader_manager.py` | 574 | `TraderManager`, `Employee`, `Task`, `VerificationResult` | 任务管理+绩效评分系统 |
| `report_correlation.py` | 328 | `ReportCorrelationAnalyzer` | 历史数据关联性分析+皮尔逊相关系数 |

### 外部API客户端

| 文件 | 行数 | 目标服务 | 说明 |
|------|------|---------|------|
| `trading_agents_cn.py` | 326 | `http://192.168.10.10` | TradingAgents-CN完整API客户端(7个端点) |
| `stock_data_service.py` | 130 | `http://192.168.10.10` | 简化版行情API客户端 |

### 编排入口

| 文件 | 行数 | 说明 |
|------|------|------|
| `main.py` | 161 | 原始编排器，支持单模块/完整流程/定时模式 |
| `workflow_integration.py` | 350 | `WorkFlowEngine` - 带验证和错误容忍的编排器 |
| `cli.py` | 447 | 交互式CLI (`python cli.py`)，基于`cmd.Cmd` |
| `run_workflow.py` | 49 | 一键运行脚本 |
| `stock_workflow.py` | 239 | TradingAgents-CN八步完整工作流 |

### 测试文件

| 文件 | 说明 |
|------|------|
| `test_complete_workflow.py` | TradingAgents-CN完整流程集成测试 |
| `test_login.py` | 简单登录测试 |

### 文档

| 文件 | 说明 |
|------|------|
| `目标文档.md` | 项目架构+Agent职责+数据格式规范 |
| `score_record.md` | 评分记录(当前40/100) |
| `docs/新闻采集员工作规范.md` | 新闻采集员SOP |
| `docs/股票分析员工作规范.md` | 股票分析员SOP |
| `docs/股票报告员工作规范.md` | 股票报告员SOP |

---

## 三、数据流与文件契约

```
news_collector.collect(15)
  → data/news/raw/{date}/{Source}.json         (按来源分文件)
  → data/news/processed/{date}/NEWS_{ts}.json  (逐条存储)
  → data/news/structured/news_database.json    (聚合，去重，下游输入)

stock_collector.collect()
  输入: news_database.json
  → data/news/structured/stock_list.json       (按priority_score降序)

stock_analyst.analyze()
  输入: stock_list.json
  → data/news/structured/stock_analysis.json   (去重合并，按priority_score降序)

stock_reporter.generate_report()
  输入: stock_analysis.json
  → data/news/structured/stock_report.json     (最新覆盖)
  → data/news/reports/{date}/stock_report_{ts}.json
  → data/news/reports/{date}/stock_report.md
```

关键发现：
- `stock_list.json` 和 `stock_analysis.json` 都是**累积而非覆盖**，按stock_code去重
- `stock_report.json` 是**覆盖写**，始终只有最新一份
- 每个Agent的`main()`都可独立运行测试

---

## 四、API端点汇总

### display_service.py (port 8000)
| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页导航 |
| `/api/report` | GET | JSON格式最新报告 |
| `/api/stocks` | GET | JSON格式股票分析 |
| `/api/statistics` | GET | JSON格式数据统计 |
| `/data大屏` | GET | ECharts数据大屏 |
| `/移动端` | GET | 移动端卡片视图 |

### trading_agents_cn.py (向 `http://192.168.10.10`)
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | JWT登录 |
| GET | `/api/favorites/` | 获取自选股 |
| POST | `/api/favorites/` | 添加自选股 |
| GET | `/api/stock-data/basic-info/{code}` | 股票基本信息 |
| POST | `/api/stock-sync/single` | 同步股票数据 |
| POST | `/api/analysis/single` | 创建分析任务(异步) |
| GET | `/api/analysis/tasks/{id}/status` | 轮询任务状态 |
| GET | `/api/reports/{id}/detail` | 获取分析报告 |

---

## 五、关键问题与改进方向

### 严重问题

1. **stock_analyst.py 全模拟数据** — 核心分析环节使用 `random.choice()` 生成技术指标、推荐评级、目标价格。`score_record.md` 记录因股价数据严重失实已被扣分至40/100。

2. **TradingAgents-CN后端不可达** — 目标服务 `http://192.168.10.10` 为内网专有部署，代码注释明确标注API返回404。实际上所有外部数据获取均不可用。

3. **news_collector.py 全模拟新闻** — `generate_mock_news()` 使用10个英文模板随机拼接生成假新闻，无任何真实数据源接入。

4. **notification_service.py 全模拟发送** — 三个渠道(微信/QQ/企业微信)的 `send()` 方法只写日志，不做实际HTTP调用。

### 代码质量问题

5. **混合Python 2/3** — `news_collector.py` 和 `stock_reporter.py` 是 python3，`stock_collector.py` 和 `stock_analyst.py` 是 python2(#!)且使用了 `unicode` 类型(仅Python2存在)。cross-python兼容性差。
6. **无 requirements.txt** — 唯一外部依赖是 `requests`，但没有依赖声明文件。
7. **硬编码** — API地址(`192.168.10.10`)、登录凭据(`admin/admin123`)、股价(`stock_current_price_map`)均硬编码在源码中。
8. **日志路径硬编码** — 每个模块的日志输出路径均为 `data/news/logs/`，相对路径依赖于CWD。
9. **英文化不一致** — Agent输出以英文为主(English templates)，但 `stock_reporter.py` 的筛选逻辑同时处理中英文推荐评级。

### 架构问题

10. **两份编排器并存** — `main.py` (class `StockAnalysisSystem`) 和 `workflow_integration.py` (class `WorkFlowEngine`) 功能高度重复，后者多了输入验证。
11. **两份API客户端并存** — `stock_data_service.py` 和 `trading_agents_cn.py` 都封装了同一后端的登录和行情接口，但API路径、参数格式不同 (`/api/stocks/realtime` vs `/api/stock-data/...`)。
12. **stock_collector.py 第131行有Python2 `unicode` 调用** — 在Python3中会直接报 `NameError`。

---

## 六、运行方式速查

```bash
# 单次完整流程
python main.py                          # 四阶段顺序执行
python run_workflow.py                  # 使用WorkFlowEngine(带验证)
python main.py scheduled 1800           # 每30分钟循环

# 单模块运行
python main.py news_collector           # 仅采集新闻
python main.py stock_collector          # 仅筛选股票
python main.py stock_analyst            # 仅分析股票
python main.py stock_reporter           # 仅生成报告

# 交互式CLI
python cli.py                           # 进入shell，输入start/status/report等

# Web展示
python display_service.py               # 启动http://localhost:8000

# 外部API测试
python trading_agents_cn.py             # 测试TradingAgents-CN连接
python test_complete_workflow.py        # 完整集成测试
```

---

## 七、环境变量

`notification_service.py` 需要(但实际不影响运行，因为发送是模拟的)：

| 变量 | 用途 |
|------|------|
| `WECHAT_APP_ID` | 微信公众号AppID |
| `WECHAT_APP_SECRET` | 微信公众号AppSecret |
| `WECHAT_TEMPLATE_ID` | 微信模板消息ID |
| `QQ_BOT_KEY` | QQ机器人密钥 |
| `WECOM_CORP_ID` | 企业微信CorpID |
| `WECOM_CORP_SECRET` | 企业微信CorpSecret |
| `WECOM_AGENT_ID` | 企业微信AgentID |

---

## 八、模块依赖图

```python
# 内部依赖关系
stock_reporter.py → notification_service.py, data_manager.py
data_manager.py → (无内部依赖，纯JSON操作)
notification_service.py → (无内部依赖)
display_service.py → data_manager.py
trader_manager.py → (无内部依赖)
workflow_integration.py → (动态import四个Agent)
cli.py → trader_manager.py, workflow_integration.py, 动态import四个Agent
stock_workflow.py → trading_agents_cn.py
test_complete_workflow.py → trading_agents_cn.py

# 外部依赖
trading_agents_cn.py → requests
stock_data_service.py → requests
notification_service.py → abc (标准库)
display_service.py → http.server, threading (标准库)
```

---

## 九、数据文件当前状态

```
data/news/structured/news_database.json   — 存在 (模拟新闻)
data/news/structured/stock_list.json      — 存在 (筛选后的股票列表)
data/news/structured/stock_analysis.json  — 存在 (模拟分析结果)
data/news/structured/stock_report.json    — 存在 (最新报告)
data/news/raw/2026-04-25/                 — 历史原始新闻
data/news/processed/2026-04-25/           — 历史处理后新闻
data/news/reports/                        — 历史报告
data/news/logs/                           — 各模块日志
```

---

## 十、CodeBuddy Teams 子系统

`.codebuddy/teams/byd-catl-analysis/` 包含一个独立的比亚迪vs宁德时代分析团队：

- `config.json` — 定义team-lead + 4个analyst(新闻/情绪/市场/基本面)
- `inboxes/` — 各agent的JSON格式分析报告inbox
- 与Python主系统独立运行，通过CodeBuddy IDE plugin驱动

---

## 十一、建议的后续开发优先级

1. **接入真实行情数据源**(如AkShare/Tushare)替换模拟数据
2. **接入真实新闻源**替换 `generate_mock_news()`
3. **统一Python版本**到Python 3，修复 `unicode` 调用等兼容问题
4. **清理重复代码**：合并两个编排器和两个API客户端
5. **创建 requirements.txt**
6. **配置外置化**：将API地址、凭据移入.env/config文件
7. **打通 notification_service** 的真实发送逻辑
