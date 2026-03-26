# -*- coding: utf-8 -*-
"""
看板首页 API（8 个固定指标 + 页面路由）
"""
from flask import Blueprint, jsonify, render_template

from db import cached_query, get_conn, get_latest_date

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    return render_template("dashboard.html")


@bp.route("/reports")
def reports_page():
    return render_template("reports.html")


@bp.route("/api/overview")
def api_overview():
    """今日核心KPI + 昨日对比"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()

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


@bp.route("/api/trend")
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


@bp.route("/api/store_rank")
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


@bp.route("/api/category")
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


@bp.route("/api/hourly")
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


@bp.route("/api/top_products")
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


@bp.route("/api/daily_flow")
def api_daily_flow():
    """总客流日报（T2）"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        cursor.execute("""
            SELECT CONVERT(varchar(10), a.c_datetime, 23) AS dt,
                   CASE DATEPART(WEEKDAY, a.c_datetime)
                       WHEN 1 THEN N'日' WHEN 2 THEN N'一' WHEN 3 THEN N'二'
                       WHEN 4 THEN N'三' WHEN 5 THEN N'四' WHEN 6 THEN N'五'
                       WHEN 7 THEN N'六' ELSE N''
                   END AS weekday,
                   a.c_store_id AS store_id,
                   b.c_name AS store_name,
                   COUNT(DISTINCT a.c_id) AS flow_count,
                   CASE WHEN COUNT(DISTINCT a.c_id) > 0
                        THEN SUM(a.c_amount) * 1.0 / COUNT(DISTINCT a.c_id)
                        ELSE NULL END AS avg_ticket,
                   SUM(a.c_amount) AS sales,
                   SUM(a.c_amount) - SUM(ISNULL(a.c_pt_cost, 0) * ISNULL(a.c_qtty, 0)) AS profit,
                   CASE WHEN SUM(a.c_amount) = 0 THEN NULL
                        ELSE (SUM(a.c_amount) - SUM(ISNULL(a.c_pt_cost, 0) * ISNULL(a.c_qtty, 0))) * 1.0 / SUM(a.c_amount) END AS profit_rate
            FROM tb_o_sg a
            LEFT JOIN tb_store b ON a.c_store_id = b.c_id
            WHERE CONVERT(varchar(10), a.c_datetime, 23) >= CONVERT(varchar(10), DATEADD(day, -7, ?), 23)
              AND CONVERT(varchar(10), a.c_datetime, 23) <= ?
              AND a.c_id NOT LIKE '-%%'
              AND ISNULL(a.c_adno, '') <> '14'
              AND a.c_computer_id <> 0
            GROUP BY CONVERT(varchar(10), a.c_datetime, 23), DATEPART(WEEKDAY, a.c_datetime),
                     a.c_store_id, b.c_name
            ORDER BY dt DESC, a.c_store_id
        """, latest, latest)
        rows = cursor.fetchall()
        conn.close()
        return {
            "rows": [
                {
                    "date": r[0],
                    "weekday": r[1] or "",
                    "store_id": r[2] or "",
                    "store_name": r[3] or r[2] or "",
                    "flow_count": r[4] or 0,
                    "avg_ticket": round(float(r[5] or 0), 2),
                    "sales": round(float(r[6] or 0), 2),
                    "profit": round(float(r[7] or 0), 2),
                    "profit_rate": round(float(r[8] or 0) * 100, 2) if r[8] is not None else None,
                }
                for r in rows
            ],
            "date_range": [latest, latest],
        }
    return jsonify(cached_query("daily_flow", _query))


@bp.route("/api/store_trend")
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
            series.append({"name": store, "data": [data.get(d, 0) for d in dates]})

        return {"dates": dates, "series": series[:10]}
    return jsonify(cached_query("store_trend", _query))


@bp.route("/api/stores")
def api_stores():
    """门店列表"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT c_id, c_name FROM tb_store WHERE c_type=N'分店' AND c_status=N'正常营业' ORDER BY c_id")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1]} for r in rows]
    return jsonify(cached_query("stores", _query))
