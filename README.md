# 宜家天润超市 运营决策看板

实时连接 SQL Server 数据库，自动获取最新销售数据，以 Web 看板和报表中心两种形式展示连锁超市的核心经营指标。

## 项目结构

```
yjtr_data_analysis/
├── app.py               # 入口：创建 Flask app，注册蓝图，启动服务
├── db.py                # 数据库连接、Redis 缓存、公共工具函数
├── requirements.txt     # Python 依赖
├── .gitignore
│
├── routes/              # 路由蓝图（各模块互相独立）
│   ├── dashboard.py     # 看板首页 API（8 个指标）
│   └── reports.py       # 报表中心 API（T1～T13）
│
├── templates/           # 前端页面（Flask 模板）
│   ├── dashboard.html   # 运营看板
│   └── reports.html     # 报表中心
│
├── sql/                 # SQL 参考脚本
│   ├── basic.sql        # 核心查询逻辑
│   └── basic_backup.sql
│
└── docs/                # 文档与需求资料
    ├── db_tables.md     # 数据库表结构（19 张核心表）
    ├── speed_plan.md    # 性能优化方案
    ├── 报表全量可视化.md
    └── 宜家天润报表需求.xls
```

## 技术架构

| 层级 | 技术 |
|------|------|
| 后端 | Python Flask + pyodbc |
| 缓存 | Redis（降级为内存缓存）5 分钟 TTL |
| 前端 | 原生 HTML/CSS/JS + ECharts 5.5 |
| 数据库 | SQL Server (`enjoy_shq`) |

## 数据流向

```
SQL Server (enjoy_shq)
    │  pyodbc 查询（NOLOCK，避免锁等待）
    ▼
db.py
    │  get_latest_date() → 取销售记录中最新一条的日期，作为看板默认日期
    │  cached_query()    → Redis / 内存 5 分钟缓存
    ▼
routes/dashboard.py   → 8 个看板 API
routes/reports.py     → T1～T13 报表 API
    ▼
前端（ECharts 图表 + 10 分钟自动刷新）
```

## 看板模块（`/`）

| 模块 | API 端点 | 说明 |
|------|----------|------|
| KPI 卡片 | `/api/overview` | 销售额、毛利额、交易笔数、客单价、毛利率，含日环比 |
| 30 天趋势 | `/api/trend` | 近 30 天销售额（柱）+ 毛利额（线）+ 交易笔数（虚线） |
| 门店排名 | `/api/store_rank` | 各分店当日销售额与毛利额横向对比 |
| 品类分布 | `/api/category` | 生鲜/食品/非食品/耗材 四大品类环形图 |
| 时段分析 | `/api/hourly` | 6:00-22:00 每小时销售额与客流分布 |
| 热销 TOP15 | `/api/top_products` | 当日销售额前 15 的商品 |
| 客流日报 | `/api/daily_flow` | 各门店近 7 天客流、客单、销售、毛利 |
| 门店趋势 | `/api/store_trend` | Top10 门店近 7 天销售额折线对比 |

## 报表中心（`/reports`）

| 报表 | API 端点 | 说明 |
|------|----------|------|
| T1 销售客单按时段 | `/api/t1_sale_bytime` | 分时段客流、客单、销售额 |
| T3 品类销售分析 | `/api/t3_category_analysis` | 品类销售、毛利、动销率 |
| T4 销售时段对比 | `/api/t4_sale_compare` | 两个时间段时段对比 |
| T5 畅销缺货 | `/api/t5_stockout` | 库存不足预警 |
| T6 商品销售分析 | `/api/t6_product_sales` | 单品销量、毛利、库存 |
| T7 供应商到货率 | `/api/t7_supplier_delivery` | 订货 vs 到货 |
| T8 负毛利 | `/api/t8_negative_margin` | 负毛利商品明细 |
| T9 高库存低周转 | `/api/t9_high_inventory` | 滞压库存预警 |
| T10 新品报表 | `/api/t10_new_products` | 新品销售追踪 |
| T11.1 供应商动销率 | `/api/t11_supplier_movement` | 供应商品项动销情况 |
| T11.2 品类动销率 | `/api/t11_2_category_movement` | 品类动销分布 |
| T12 品态异常 | `/api/t12_abnormal_status` | 库存状态异常商品 |
| T13 滞销商品 | `/api/t13_slow_moving` | 销量/销额末位商品 |

## 运行方式

### 1. 安装系统依赖（macOS）

需要先安装 Microsoft ODBC Driver 17 for SQL Server：

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql17
```

验证：

```bash
odbcinst -q -d -n "ODBC Driver 17 for SQL Server"
```

### 2. 安装 Python 依赖

```bash
pip3 install -r requirements.txt
```

### 3. 配置数据库连接

编辑 `db.py` 顶部的 `DB_CONFIG`：

```python
DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "你的服务器地址,端口",
    "database": "enjoy_shq",
    "uid": "用户名",
    "pwd": "密码",
}
```

### 4. 启动

```bash
python3 app.py
```

### 5. 访问

| 页面 | 地址 |
|------|------|
| 运营看板 | http://localhost:5001 |
| 报表中心 | http://localhost:5001/reports |

## 配置说明

| 配置项 | 文件 | 默认值 | 说明 |
|--------|------|--------|------|
| `DB_CONFIG` | `db.py` | — | 数据库连接信息 |
| `CACHE_TTL` | `db.py` | `300` | 缓存有效期（秒） |
| `port` | `app.py` | `5001` | Flask 服务端口 |
| `T1_TEST_DATES` | `templates/reports.html` | 固定日期 | 改为 `null` 后自动取当天 |
