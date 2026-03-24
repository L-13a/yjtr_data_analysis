# -*- coding: utf-8 -*-
"""
宜家天润超市 - 运营决策看板
Flask后端：连接SQL Server，提供数据API
"""
from flask import Flask, jsonify, render_template
import pyodbc
from datetime import datetime, timedelta
from functools import lru_cache
import time

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "tag.qyyjtr.com,6899",
    "database": "enjoy_shq_test",
    "uid": "rou_9999",
    "pwd": "kl87ngG@f",
}


def get_conn():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
        f"TrustServerCertificate=yes;"
        f"LoginTimeout=15;"
    )
    return pyodbc.connect(conn_str, timeout=30)


# 缓存：获取数据库中的最新日期（作为"今天"）
_cache = {}
_cache_time = {}
CACHE_TTL = 300  # 5分钟缓存


def cached_query(key, query_func):
    now = time.time()
    if key in _cache and now - _cache_time.get(key, 0) < CACHE_TTL:
        return _cache[key]
    result = query_func()
    _cache[key] = result
    _cache_time[key] = now
    return result


def get_latest_date():
    # TODO: 测试阶段写死日期，待数据补全后改为动态查询（取消注释 _query 并 return cached_query(...)）
    return "2024-09-08"

    # pylint: disable=unreachable
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        # 找到最近一个完整营业日（跳过不完整天和零星测试/退货记录）
        cursor.execute("""
            SELECT TOP 1 CONVERT(varchar, c_datetime, 23) as dt
            FROM tb_o_sg
            WHERE c_type = N'销售'
            GROUP BY CONVERT(varchar, c_datetime, 23)
            HAVING SUM(c_amount) > 0 AND COUNT(DISTINCT c_id) >= 1000
            ORDER BY dt DESC
        """)
        r = cursor.fetchone()
        conn.close()
        return r[0] if r else "2024-09-08"
    return cached_query("latest_date", _query)


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/overview")
def api_overview():
    """今日核心KPI + 昨日对比"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()

        # 今日销售
        cursor.execute("""
            SELECT COUNT(DISTINCT c_id) as bill_count,
                   SUM(c_amount) as total_sales,
                   SUM(c_amount - ISNULL(c_aet_cost, 0)) as total_profit,
                   COUNT(DISTINCT c_cardno) as member_count
            FROM tb_o_sg
            WHERE CONVERT(varchar, c_datetime, 23) = ?
              AND c_type = N'销售' AND c_amount > 0
        """, latest)
        today = cursor.fetchone()

        # 昨日
        cursor.execute("""
            SELECT COUNT(DISTINCT c_id) as bill_count,
                   SUM(c_amount) as total_sales,
                   SUM(c_amount - ISNULL(c_aet_cost, 0)) as total_profit
            FROM tb_o_sg
            WHERE CONVERT(varchar, c_datetime, 23) = CONVERT(varchar, DATEADD(day, -1, ?), 23)
              AND c_type = N'销售' AND c_amount > 0
        """, latest)
        yesterday = cursor.fetchone()

        conn.close()

        today_sales = float(today[1] or 0)
        today_profit = float(today[2] or 0)
        today_bills = today[0] or 0
        today_members = today[3] or 0
        yest_sales = float(yesterday[1] or 0)
        yest_profit = float(yesterday[2] or 0)
        yest_bills = yesterday[0] or 0

        return {
            "date": latest,
            "sales": round(today_sales, 2),
            "profit": round(today_profit, 2),
            "bills": today_bills,
            "avg_ticket": round(today_sales / today_bills, 2) if today_bills else 0,
            "members": today_members,
            "profit_rate": round(today_profit / today_sales * 100, 2) if today_sales else 0,
            "sales_change": round((today_sales - yest_sales) / yest_sales * 100, 2) if yest_sales else 0,
            "bills_change": round((today_bills - yest_bills) / yest_bills * 100, 2) if yest_bills else 0,
            "profit_change": round((today_profit - yest_profit) / yest_profit * 100, 2) if yest_profit else 0,
        }
    return jsonify(cached_query("overview", _query))


@app.route("/api/trend")
def api_trend():
    """近30天销售趋势"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT CONVERT(varchar, c_datetime, 23) as dt,
                   SUM(c_amount) as sales,
                   COUNT(DISTINCT c_id) as bills,
                   SUM(c_amount - ISNULL(c_aet_cost, 0)) as profit
            FROM tb_o_sg
            WHERE c_datetime >= DATEADD(day, -30, ?)
              AND c_datetime <= DATEADD(day, 1, ?)
              AND c_type = N'销售' AND c_amount > 0
            GROUP BY CONVERT(varchar, c_datetime, 23)
            ORDER BY dt
        """, latest, latest)
        rows = cursor.fetchall()
        conn.close()
        return {
            "dates": [r[0] for r in rows],
            "sales": [round(float(r[1] or 0), 2) for r in rows],
            "bills": [r[2] for r in rows],
            "profit": [round(float(r[3] or 0), 2) for r in rows],
        }
    return jsonify(cached_query("trend", _query))


@app.route("/api/store_rank")
def api_store_rank():
    """门店销售排名"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT s.c_store_id, t.c_name,
                   SUM(s.c_amount) as sales,
                   COUNT(DISTINCT s.c_id) as bills,
                   SUM(s.c_amount - ISNULL(s.c_aet_cost, 0)) as profit
            FROM tb_o_sg s
            LEFT JOIN tb_store t ON s.c_store_id = t.c_id
            WHERE CONVERT(varchar, s.c_datetime, 23) = ?
              AND s.c_type = N'销售' AND s.c_amount > 0
              AND t.c_type = N'分店'
            GROUP BY s.c_store_id, t.c_name
            ORDER BY sales DESC
        """, latest)
        rows = cursor.fetchall()
        conn.close()
        return {
            "stores": [r[1] or r[0] for r in rows],
            "sales": [round(float(r[2] or 0), 2) for r in rows],
            "bills": [r[3] for r in rows],
            "profit": [round(float(r[4] or 0), 2) for r in rows],
        }
    return jsonify(cached_query("store_rank", _query))


@app.route("/api/category")
def api_category():
    """品类销售分布"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT CASE
                     WHEN LEFT(g.c_ccode, 2) = '11' THEN N'生鲜'
                     WHEN LEFT(g.c_ccode, 2) = '22' THEN N'食品'
                     WHEN LEFT(g.c_ccode, 2) = '33' THEN N'非食品'
                     WHEN LEFT(g.c_ccode, 2) = '44' THEN N'耗材/资产'
                     ELSE N'其他'
                   END as category,
                   SUM(s.c_amount) as sales,
                   SUM(s.c_amount - ISNULL(s.c_aet_cost, 0)) as profit
            FROM tb_o_sg s
            JOIN tb_gds g ON s.c_gcode = g.c_gcode AND s.c_adno = g.c_adno
            WHERE CONVERT(varchar, s.c_datetime, 23) = ?
              AND s.c_type = N'销售' AND s.c_amount > 0
            GROUP BY CASE
                       WHEN LEFT(g.c_ccode, 2) = '11' THEN N'生鲜'
                       WHEN LEFT(g.c_ccode, 2) = '22' THEN N'食品'
                       WHEN LEFT(g.c_ccode, 2) = '33' THEN N'非食品'
                       WHEN LEFT(g.c_ccode, 2) = '44' THEN N'耗材/资产'
                       ELSE N'其他'
                     END
            ORDER BY sales DESC
        """, latest)
        rows = cursor.fetchall()
        conn.close()
        return {
            "categories": [r[0] for r in rows],
            "sales": [round(float(r[1] or 0), 2) for r in rows],
            "profit": [round(float(r[2] or 0), 2) for r in rows],
        }
    return jsonify(cached_query("category", _query))


@app.route("/api/hourly")
def api_hourly():
    """时段销售分布"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT DATEPART(hour, c_datetime) as hr,
                   SUM(c_amount) as sales,
                   COUNT(DISTINCT c_id) as bills
            FROM tb_o_sg
            WHERE CONVERT(varchar, c_datetime, 23) = ?
              AND c_type = N'销售' AND c_amount > 0
            GROUP BY DATEPART(hour, c_datetime)
            ORDER BY hr
        """, latest)
        rows = cursor.fetchall()
        conn.close()
        hours = list(range(6, 23))
        sales_map = {r[0]: round(float(r[1] or 0), 2) for r in rows}
        bills_map = {r[0]: r[2] for r in rows}
        return {
            "hours": [f"{h}:00" for h in hours],
            "sales": [sales_map.get(h, 0) for h in hours],
            "bills": [bills_map.get(h, 0) for h in hours],
        }
    return jsonify(cached_query("hourly", _query))


@app.route("/api/top_products")
def api_top_products():
    """热销商品TOP15"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT TOP 15
                   s.c_gcode, g.c_name,
                   SUM(s.c_amount) as sales,
                   SUM(s.c_qtty) as qty,
                   SUM(s.c_amount - ISNULL(s.c_aet_cost, 0)) as profit
            FROM tb_o_sg s
            LEFT JOIN tb_gds g ON s.c_gcode = g.c_gcode AND s.c_adno = g.c_adno
            WHERE CONVERT(varchar, s.c_datetime, 23) = ?
              AND s.c_type = N'销售' AND s.c_amount > 0
            GROUP BY s.c_gcode, g.c_name
            ORDER BY sales DESC
        """, latest)
        rows = cursor.fetchall()
        conn.close()
        return {
            "products": [r[1] or r[0] for r in rows],
            "sales": [round(float(r[2] or 0), 2) for r in rows],
            "qty": [round(float(r[3] or 0), 1) for r in rows],
            "profit": [round(float(r[4] or 0), 2) for r in rows],
        }
    return jsonify(cached_query("top_products", _query))


@app.route("/api/payment")
def api_payment():
    """支付方式分布(基于tb_o_sm)"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT c_type,
                   COUNT(*) as cnt,
                   SUM(c_amount) as total
            FROM tb_o_sm
            WHERE CONVERT(varchar, c_datetime, 23) = ?
            GROUP BY c_type
            ORDER BY total DESC
        """, latest)
        rows = cursor.fetchall()
        conn.close()

        # 合并小类
        merged = {}
        for r in rows:
            pay_type = r[0] or "其他"
            # 简化支付名称
            if "微信" in pay_type:
                key = "微信"
            elif "支付宝" in pay_type:
                key = "支付宝"
            elif "现金" in pay_type:
                key = "现金"
            elif "贵宾" in pay_type or "会员" in pay_type:
                key = "会员卡"
            elif "银联" in pay_type or "信用卡" in pay_type:
                key = "银行卡"
            else:
                key = "其他"
            merged[key] = merged.get(key, 0) + float(r[2] or 0)

        sorted_items = sorted(merged.items(), key=lambda x: -x[1])
        return {
            "types": [i[0] for i in sorted_items],
            "amounts": [round(i[1], 2) for i in sorted_items],
        }
    return jsonify(cached_query("payment", _query))


@app.route("/api/store_trend")
def api_store_trend():
    """各门店近7天趋势"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT t.c_name, CONVERT(varchar, s.c_datetime, 23) as dt,
                   SUM(s.c_amount) as sales
            FROM tb_o_sg s
            JOIN tb_store t ON s.c_store_id = t.c_id
            WHERE s.c_datetime >= DATEADD(day, -7, ?)
              AND s.c_datetime <= DATEADD(day, 1, ?)
              AND s.c_type = N'销售' AND s.c_amount > 0
              AND t.c_type = N'分店'
            GROUP BY t.c_name, CONVERT(varchar, s.c_datetime, 23)
            ORDER BY t.c_name, dt
        """, latest, latest)
        rows = cursor.fetchall()
        conn.close()

        stores_data = {}
        dates_set = set()
        for name, dt, sales in rows:
            if name not in stores_data:
                stores_data[name] = {}
            stores_data[name][dt] = round(float(sales or 0), 2)
            dates_set.add(dt)

        dates = sorted(dates_set)
        series = []
        for store, data in sorted(stores_data.items(), key=lambda x: -sum(x[1].values())):
            series.append({
                "name": store,
                "data": [data.get(d, 0) for d in dates]
            })

        return {"dates": dates, "series": series[:10]}  # Top10门店
    return jsonify(cached_query("store_trend", _query))


if __name__ == "__main__":
    print("=" * 50)
    print("宜家天润超市 运营决策看板")
    print("=" * 50)
    print("正在启动服务...")
    print("打开浏览器访问: http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
