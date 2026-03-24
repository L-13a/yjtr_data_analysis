# 宜家天润超市 运营决策看板

实时连接 SQL Server 数据库，自动获取最新销售数据，以 Web 看板形式展示连锁超市的核心经营指标。

## 项目结构

```
yjtr_data_analysis/
├── app.py                  # Flask 后端（数据库连接 + 8 个 REST API）
├── templates/
│   └── dashboard.html      # 前端看板（ECharts 图表 + 自动刷新）
├── db_tables.md            # 数据库表结构文档（19 张核心表）
└── README.md               # 项目说明
```

## 技术架构

| 层级 | 技术 |
|------|------|
| 后端 | Python Flask + pyodbc |
| 前端 | 原生 HTML/CSS/JS + ECharts 5.5 |
| 数据库 | SQL Server (`enjoy_shq_test`) |
| 缓存策略 | 后端 5 分钟内存缓存 + 前端 10 分钟轮询刷新 |

## 数据流向

```
SQL Server (enjoy_shq_test)
    │
    │  pyodbc 查询
    ▼
Flask 后端 (app.py)
    │  get_latest_date() → 动态获取数据库最新日期作为"今天"
    │  cached_query()    → 5 分钟 TTL 内存缓存
    │  8 个 /api/* 端点  → 返回 JSON
    ▼
前端 (dashboard.html)
    │  Promise.all() 并行请求所有 API
    │  ECharts 渲染图表
    │  setInterval 10 分钟自动刷新
    ▼
浏览器展示
```

## 看板模块

看板包含 8 个数据模块：

| 模块 | API 端点 | 说明 |
|------|----------|------|
| KPI 卡片 | `/api/overview` | 销售额、毛利额、交易笔数、客单价、毛利率，含日环比 |
| 30 天趋势 | `/api/trend` | 近 30 天销售额（柱）+ 毛利额（线）+ 交易笔数（虚线） |
| 门店排名 | `/api/store_rank` | 各分店当日销售额与毛利额横向对比 |
| 品类分布 | `/api/category` | 生鲜/食品/非食品/耗材 四大品类环形图 |
| 时段分析 | `/api/hourly` | 6:00-22:00 每小时销售额与客流分布 |
| 热销 TOP15 | `/api/top_products` | 当日销售额前 15 的商品表格 |
| 支付方式 | `/api/payment` | 微信/支付宝/现金/会员卡/银行卡 占比 |
| 门店趋势 | `/api/store_trend` | Top10 门店近 7 天销售额折线对比 |

## 数据库核心表

看板主要使用以下 4 张表：

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `tb_o_sg` | 销售明细（主表） | `c_id`, `c_datetime`, `c_amount`, `c_at_cost`, `c_qtty`, `c_gcode`, `c_store_id`, `c_type` |
| `tb_o_sm` | 收款明细 | `c_datetime`, `c_type`, `c_amount` |
| `tb_gds` | 商品档案 | `c_gcode`, `c_adno`, `c_name`, `c_ccode` |
| `tb_store` | 门店信息 | `c_id`, `c_name`, `c_type` |

完整表结构文档见 [db_tables.md](db_tables.md)。

## 运行方式

### 1. 安装依赖

```bash
pip install flask pyodbc
```

系统需安装 [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/zh-cn/sql/connect/odbc/download-odbc-driver-for-sql-server)。

### 2. 配置数据库连接

编辑 `app.py` 顶部的 `DB_CONFIG`：

```python
DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "你的服务器地址,端口",
    "database": "enjoy_shq_test",
    "uid": "用户名",
    "pwd": "密码",
}
```

### 3. 启动

```bash
python app.py
```

### 4. 访问

浏览器打开 http://localhost:5000

## 配置说明

| 配置项 | 位置 | 默认值 | 说明 |
|--------|------|--------|------|
| `CACHE_TTL` | `app.py:40` | `300` | 后端缓存有效期（秒） |
| `port` | `app.py:382` | `5000` | Flask 服务端口 |
| `host` | `app.py:382` | `0.0.0.0` | 监听地址（0.0.0.0 允许局域网访问） |
| `setInterval` | `dashboard.html:513` | `600000` | 前端自动刷新间隔（毫秒，10 分钟） |
| `debug` | `app.py:382` | `True` | Flask 调试模式（生产环境应关闭） |

ngrok authtoken:
3AIDX0j3V3151db0FSJodmvADbV_6wt3yhCe4t5YrozWKGnc4

app.py里面，现在 get_latest_date() 直接返回 "2024-09-08"，原有的动态查询逻辑完整保留在下方，用 # pylint: disable=unreachable 压制 unreachable 警告。
后续正式上线时，只需：
删除 return "2024-09-08" 那一行
删除 # pylint: disable=unreachable 注释
动态查询逻辑自动生效