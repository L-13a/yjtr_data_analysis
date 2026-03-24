# -*- coding: utf-8 -*-
"""
宜家天润超市 - 运营决策看板
Flask后端：连接SQL Server，提供数据API
"""
from flask import Flask, jsonify, render_template, request
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
    _cache_time[key] = time.time()
    return result


def get_latest_date():
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
        return r[0] if r else "2024-09-09"
    return cached_query("latest_date", _query)


@app.route("/")
def index():
    return render_template("dashboard.html")


# @app.route("/report2")
# def report2_page():
#     """第二份报表页：总客流日报（basic.sql T2 提取方式）"""
#     return render_template("report2.html")


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

@app.route("/api/daily_flow")
def api_daily_flow():
    """
    总客流日报（basic.sql T2 提取方式）。
    按日期、机构汇总：客流、客单、销售额、毛利额、毛利率。
    """
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        latest = get_latest_date()
        # 默认查询最近 7 天
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


@app.route("/reports")
def reports_page():
    return render_template("reports.html")


@app.route("/api/stores")
def api_stores():
    """获取门店列表"""
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT c_id, c_name FROM tb_store WHERE c_type=N'分店' AND c_status=N'正常营业' ORDER BY c_id")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1]} for r in rows]
    return jsonify(cached_query("stores", _query))


def _default_dates():
    latest = get_latest_date()
    return latest, latest


def _rows_to_dicts(cursor):
    # Skip result sets with no columns (e.g. SET statements inside stored procs)
    while cursor.description is None:
        if not cursor.nextset():
            return []
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def _safe_float(val):
    if val is None:
        return None
    try:
        return round(float(val), 4)
    except (ValueError, TypeError):
        return None


def _clean_row(d):
    """Convert Decimal/datetime values to JSON-serializable types."""
    import decimal
    from datetime import date, datetime as dt_type
    out = {}
    for k, v in d.items():
        if isinstance(v, decimal.Decimal):
            out[k] = float(v)
        elif isinstance(v, (date, dt_type)):
            out[k] = str(v)[:10]
        else:
            out[k] = v
    return out


@app.route("/api/t1_sale_bytime")
def api_t1():
    """T1: 销售客单按时段"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    dept = request.args.get('dept', '')
    bhour = int(request.args.get('bhour', '0'))
    ehour = int(request.args.get('ehour', '23'))
    ccode = request.args.get('ccode', '')
    ccodelen = request.args.get('ccodelen', '')
    if not start:
        start, _ = _default_dates()
    if not end:
        end = start
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("exec up_rpt_io_sale_bytime ?,?,?,?,?,?,?,?,1",
                       start, end, store, dept, bhour, ehour, ccode, ccodelen)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t3_category_analysis")
def api_t3():
    """T3: 品类销售分析表"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    ccode = request.args.get('ccode', '')
    clevel = request.args.get('clevel', '')
    if not start:
        start, _ = _default_dates()
    if not end:
        end = start
    sql = """
    DECLARE @pclevel int, @pstart datetime, @pend datetime, @pccode varchar(1000), @pstore varchar(max)
    SELECT @pclevel=?, @pstart=?, @pend=?, @pstore=?, @pccode=?;
    WITH temp00 AS(
        SELECT gc.c_ccode, gc.c_level, gc.c_name,
            COUNT(DISTINCT g.c_gcode) AS c_kind,
            COUNT(DISTINCT CASE WHEN ISNULL(g.c_sale,0)<>0 THEN g.c_gcode ELSE NULL END) AS dongxiao,
            ROUND(CAST(COUNT(DISTINCT CASE WHEN ISNULL(g.c_sale,0)<>0 THEN g.c_gcode ELSE NULL END) AS dec(12,2))/COUNT(DISTINCT g.c_gcode),4) AS dongxiaov,
            COUNT(DISTINCT g.c_gcode)-COUNT(DISTINCT CASE WHEN ISNULL(g.c_sale,0)<>0 THEN g.c_gcode ELSE NULL END) AS budongxiao
        FROM tb_gdsclass gc
        CROSS APPLY dbo.io_get_gds_gcode_cnt(@pstore, gc.c_ccode, @pstart, @pend) g
        WHERE (ISNULL(@pclevel,'')='' OR gc.c_level=@pclevel)
            AND (ISNULL(@pccode,'')='' OR gc.c_ccode = @pccode)
            AND gc.c_ccode NOT LIKE '44%'
            AND g.c_sale_status NOT IN ('暂停销售')
            AND NOT (g.c_number=0 AND g.c_status IN ('暂停进货'))
            AND gc.c_ccode=g.c_ccode_pre
        GROUP BY gc.c_ccode, gc.c_level, gc.c_name
    ),
    temp01 AS(
        SELECT gc.c_ccode, gc.c_name AS pinlei_name, SUM(ds.c_sale) AS sale, SUM(ds.c_sale)-SUM(ds.c_at_sale) AS maoli,
            CASE WHEN SUM(ds.c_sale)=0 THEN NULL ELSE (SUM(ds.c_sale)-SUM(ds.c_at_sale))/SUM(ds.c_sale) END AS maoliv,
            SUM(ds.c_sale_count) AS laike, CASE WHEN SUM(ds.c_sale_count)=0 THEN NULL ELSE SUM(ds.c_sale)/SUM(ds.c_sale_count) END AS kd,
            SUM(ds.c_at_sale) AS c_at_sale
        FROM tb_gdsclass gc
        LEFT JOIN tbs_d_supp ds ON ds.c_type=N'品类' AND ds.c_dt>=@pstart AND ds.c_dt<=@pend AND ds.c_id=gc.c_ccode
            AND ds.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(@pstore,',','store',1,default))
        WHERE (ISNULL(@pclevel,'')='' OR gc.c_level=@pclevel)
            AND (ISNULL(@pccode,'')='' OR gc.c_ccode=@pccode)
            AND gc.c_ccode NOT LIKE '44%'
        GROUP BY gc.c_ccode, gc.c_name
    ),
    temp02 AS(
        SELECT a.c_ccode, a.pinlei_name, a.sale, a.maoli, a.maoliv, a.laike, a.kd,
            b.c_kind, b.dongxiao, b.dongxiaov, b.budongxiao, c.c_sale AS c_sale_par, c.c_maoli AS c_maoli_par,
            (SELECT SUM(c_sale) FROM tbs_d_supp WHERE c_type=N'机构' AND c_dt>=@pstart AND c_dt<=@pend
                AND c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(@pstore,',','store',1,default))) AS c_store_sale,
            (SELECT SUM(c_sale)-SUM(c_at_sale) FROM tbs_d_supp WHERE c_type=N'机构' AND c_dt>=@pstart AND c_dt<=@pend
                AND c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(@pstore,',','store',1,default))) AS c_store_maoli
        FROM temp01 a
        LEFT JOIN temp00 b ON a.c_ccode=b.c_ccode
        LEFT JOIN (
            SELECT c_id, SUM(c_sale) AS c_sale, SUM(c_sale-c_at_sale) AS c_maoli FROM tbs_d_supp
            WHERE c_type=N'品类' AND c_dt>=@pstart AND c_dt<=@pend
                AND c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(@pstore,',','store',1,default))
            GROUP BY c_id
        ) c ON CASE WHEN LEN(a.c_ccode)=3 THEN SUBSTRING(a.c_ccode,1,LEN(a.c_ccode)-1) ELSE SUBSTRING(a.c_ccode,1,LEN(a.c_ccode)-2) END=c.c_id
    )
    SELECT a.c_ccode AS 品类号码, LEN(a.c_ccode) AS 品类长度, a.pinlei_name AS 品类名称, a.sale AS 销售额, a.maoli AS 毛利额, a.maoliv AS 毛利率,
        a.laike AS 来客数, a.kd AS 客单价, a.c_kind AS 品项数, a.dongxiao AS 动销数, a.dongxiaov AS 动销率, a.budongxiao AS 不动销数,
        CASE WHEN a.c_sale_par=0 THEN NULL ELSE a.sale/a.c_sale_par END AS 销售额占比_课占部,
        CASE WHEN a.c_store_sale=0 THEN NULL ELSE a.sale/a.c_store_sale END AS 销售额占比_课占店,
        CASE WHEN a.c_maoli_par=0 THEN NULL ELSE a.maoli/a.c_maoli_par END AS 毛利额占比_课占部,
        CASE WHEN a.c_store_maoli=0 THEN NULL ELSE a.maoli/a.c_store_maoli END AS 毛利额占比_课占店
    FROM temp02 a WHERE 1=1 AND (ISNULL(@pccode,'')='' OR a.c_ccode=@pccode) ORDER BY a.c_ccode
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        lev = None if not clevel else int(clevel)
        cursor.execute(sql, lev, start, end, store, ccode)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t4_sale_compare")
def api_t4():
    """T4: 销售时段对比"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    cmp_start = request.args.get('cmp_start', '')
    cmp_end = request.args.get('cmp_end', '')
    if not start:
        start, _ = _default_dates()
    if not end:
        end = start
    if not cmp_start:
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        cmp_start = (d - td(days=7)).strftime('%Y-%m-%d')
    if not cmp_end:
        from datetime import timedelta as td
        d = datetime.strptime(end, '%Y-%m-%d')
        cmp_end = (d - td(days=7)).strftime('%Y-%m-%d')
    sql = """
    WITH temp00 AS (
        SELECT a.c_hour AS 时段,
            a.c_amount AS 销售额, a.count_id AS 客流, a.kd AS 客单,
            b.c_amount AS 对比销售额, b.count_id AS 对比客流, b.kd AS 对比客单,
            a.c_amount-b.c_amount AS 销售差,
            CASE WHEN a.c_amount=0 THEN NULL ELSE (a.c_amount-ISNULL(b.c_amount,0))/a.c_amount END AS 销售对比率,
            a.count_id-b.count_id AS 客流差, a.kd-b.kd AS 客单差
        FROM (
            SELECT FORMAT(c_datetime,'HH') AS c_hour, SUM(c_amount) AS c_amount, COUNT(DISTINCT c_id) AS count_id,
                SUM(c_amount)/CASE WHEN COUNT(DISTINCT c_id)=0 THEN NULL ELSE COUNT(DISTINCT c_id) END AS kd
            FROM tb_o_sg WHERE c_computer_id<>0 AND CONVERT(char(10),c_datetime,20)>=? AND CONVERT(char(10),c_datetime,20)<=?
                AND (ISNULL(?,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
                AND c_id NOT LIKE '-%' AND (c_adno<>'14')
            GROUP BY FORMAT(c_datetime,'HH')
        ) a LEFT JOIN (
            SELECT FORMAT(c_datetime,'HH') AS c_hour, SUM(c_amount) AS c_amount, COUNT(DISTINCT c_id) AS count_id,
                SUM(c_amount)/CASE WHEN COUNT(DISTINCT c_id)=0 THEN NULL ELSE COUNT(DISTINCT c_id) END AS kd
            FROM tb_o_sg WHERE c_computer_id<>0 AND CONVERT(char(10),c_datetime,20)>=? AND CONVERT(char(10),c_datetime,20)<=?
                AND (ISNULL(?,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
                AND c_id NOT LIKE '-%' AND (c_adno<>'14')
            GROUP BY FORMAT(c_datetime,'HH')
        ) b ON a.c_hour=b.c_hour
    )
    SELECT 时段,销售额,客流,客单,对比销售额,对比客流,对比客单,销售差,销售对比率,客流差,客单差 FROM (
        SELECT 时段,销售额,客流,客单,对比销售额,对比客流,对比客单,销售差,销售对比率,客流差,客单差 FROM temp00
        UNION ALL
        SELECT NULL AS 时段, SUM(销售额), SUM(客流),
            CASE WHEN SUM(客流)=0 THEN NULL ELSE SUM(销售额)/SUM(客流) END,
            SUM(对比销售额), SUM(对比客流),
            CASE WHEN SUM(对比客流)=0 THEN NULL ELSE SUM(对比销售额)/SUM(对比客流) END,
            SUM(销售额)-SUM(对比销售额),
            CASE WHEN SUM(销售额)=0 THEN NULL ELSE (SUM(销售额)-SUM(对比销售额))/SUM(销售额) END,
            SUM(客流)-SUM(对比客流),
            CASE WHEN SUM(客流)=0 THEN NULL ELSE SUM(销售额)/SUM(客流) END - CASE WHEN SUM(对比客流)=0 THEN NULL ELSE SUM(对比销售额)/SUM(对比客流) END
        FROM temp00
    ) a ORDER BY CASE WHEN a.时段 IS NULL THEN 9999 ELSE a.时段 END
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, start, end, store, store, cmp_start, cmp_end, store, store)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t5_stockout")
def api_t5():
    """T5: 畅销商品缺货"""
    store = request.args.get('store', '11021')
    ccode = request.args.get('ccode', '')
    supplier = request.args.get('supplier', '')
    supplier_type = request.args.get('supplier_type', '')
    warn_days = int(request.args.get('warn_days', '7'))
    freq = request.args.get('freq', '全部')
    sql = """
    SELECT gs.c_gcode AS 商品编码, g.c_name AS 商品名称, g.c_barcode AS 商品条码, g.c_model AS 规格, g.c_basic_unit AS 单位,
        gs.c_status AS 商品状态, gs.c_pro_status AS 促销状态, gs.c_sale_frequency AS 销售频率,
        gs.c_pt_cost AS 进价, CASE WHEN gs.c_price_disc=0 THEN gs.c_price ELSE gs.c_price_disc END AS 售价,
        CASE WHEN gs.c_price_disc=0 THEN gs.c_price-gs.c_pt_cost ELSE gs.c_price_disc-gs.c_pt_cost END AS 毛利,
        CASE WHEN (CASE WHEN gs.c_price_disc=0 THEN gs.c_price ELSE gs.c_price_disc END)=0 THEN NULL
            ELSE ROUND(CAST(CASE WHEN gs.c_price_disc=0 THEN gs.c_price-gs.c_pt_cost ELSE gs.c_price_disc-gs.c_pt_cost END AS FLOAT)/
            CAST(CASE WHEN gs.c_price_disc=0 THEN gs.c_price ELSE gs.c_price_disc END AS FLOAT),4) END AS 毛利率,
        gs.c_number AS 库存, gs.c_at_cost AS 库存金额, gs.c_lastsale_dt AS 最后销售日期, gs.c_sn_perday AS 日均销售,
        gs.c_onway AS 在途, gc.c_ccode AS 品类编码, gc.c_name AS 品类名称,
        gs.c_provider AS 主供应商编码, p.c_name AS 供应商名称, p.c_category AS 供应商类型
    FROM tb_gdsstore gs
    LEFT JOIN tb_gds g ON g.c_gcode=gs.c_gcode
    LEFT JOIN tb_gdsclass gc ON g.c_ccode=gc.c_ccode
    LEFT JOIN tb_partner p ON gs.c_provider=p.c_no
    WHERE (ISNULL(?,'')='' OR gs.c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''   ),',')))
        AND (ISNULL(?,'')='' OR gc.c_ccode LIKE ?+'%')
        AND (ISNULL(?,'')='' OR gs.c_provider=?)
        AND (ISNULL(?,'')='' OR p.c_category LIKE '%'+?+'%')
        AND gs.c_number<gs.c_sn_perday*?
        AND gs.c_adno NOT IN ('13','14')
        AND gs.c_type LIKE N'自营%'
        AND gs.c_status NOT IN (N'作废')
        AND NOT (gs.c_status IN (N'暂停进货') AND ISNULL(gs.c_number,0)=0)
        AND (ISNULL(?,'')='' OR ISNULL(?,'')=N'全部' OR gs.c_sale_frequency=?)
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, store, store, ccode, ccode, supplier, supplier, supplier_type, supplier_type, warn_days, freq, freq, freq)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t6_product_sales")
def api_t6():
    """T6: 商品销售分析"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    dept = request.args.get('dept', '')
    ccode = request.args.get('ccode', '')
    gcode = request.args.get('gcode', '')
    supplier = request.args.get('supplier', '')
    if not start:
        start, _ = _default_dates()
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        start = (d - td(days=30)).strftime('%Y-%m-%d')
    if not end:
        _, end = _default_dates()
    sql = """
    SELECT dg.c_gcode AS 商品编码, g.c_name AS 商品名称, g.c_barcode AS 商品条码, g.c_model AS 规格, g.c_basic_unit AS 单位,
        dg.c_number_sale AS 销售数量, dg.c_sale AS 销售额, dg.c_at_sale AS 成本, dg.maoli AS 毛利, dg.maoliv AS 毛利率,
        gc.c_ccode AS 品类编码, gc.c_name AS 品类名称, p.c_no AS 供应商编码, p.c_name AS 供应商名, gs.c_number AS 当前库存
    FROM (
        SELECT c_store_id, c_gcode, SUM(c_number_sale) AS c_number_sale, SUM(c_sale) AS c_sale, SUM(c_at_sale) AS c_at_sale,
            SUM(c_sale-c_at_sale) AS maoli, CASE WHEN SUM(c_sale)=0 THEN NULL ELSE SUM(c_sale-c_at_sale)/SUM(c_sale) END AS maoliv
        FROM tbs_d_gds WHERE CONVERT(char(10),c_dt,20)>=? AND CONVERT(char(10),c_dt,20)<=?
            AND (ISNULL(?,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
            AND c_adno NOT IN ('13','14')
        GROUP BY c_store_id, c_gcode
    ) dg
    LEFT JOIN (SELECT c_store_id, c_gcode, c_provider, c_number FROM tb_gdsstore
        WHERE (ISNULL(?,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
    ) gs ON dg.c_store_id=gs.c_store_id AND dg.c_gcode=gs.c_gcode
    LEFT JOIN tb_gds g ON dg.c_gcode=g.c_gcode
    LEFT JOIN tb_gdsclass gc ON g.c_ccode=gc.c_ccode
    LEFT JOIN tb_partner p ON gs.c_provider=p.c_no
    WHERE 1=1
        AND (ISNULL(?,'')='' OR dg.c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
        AND (ISNULL(?,'')='' OR dg.c_gcode=?)
        AND (ISNULL(?,'')='' OR g.c_adno=?)
        AND (ISNULL(?,'')='' OR g.c_ccode=?)
        AND (ISNULL(?,'')='' OR p.c_no=?)
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, start, end, store, store, store, store, store, store, gcode, gcode, dept, dept, ccode, ccode, supplier, supplier)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t7_supplier_delivery")
def api_t7():
    """T7: 供应商到货率汇总"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    supplier = request.args.get('supplier', '')
    if not start:
        start, _ = _default_dates()
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        start = (d - td(days=30)).strftime('%Y-%m-%d')
    if not end:
        _, end = _default_dates()
    sql = """
    WITH temp00 AS (
        SELECT p.c_no, p.c_name, SUM(dg.c_sale) AS c_sale, SUM(dg.c_sale-dg.c_at_sale) AS c_maoli,
            CASE WHEN SUM(dg.c_sale)=0 THEN NULL ELSE 1.00*SUM(dg.c_sale-dg.c_at_sale)/SUM(dg.c_sale) END AS c_maoliv,
            gp.count_gcode AS kind_count,
            COUNT(DISTINCT dg.c_gcode) AS dongxiao,
            CASE WHEN SUM(gp.count_gcode)=0 THEN NULL ELSE 1.00*COUNT(DISTINCT dg.c_gcode)/gp.count_gcode END AS dongxiaov
        FROM tbs_d_gds dg
        LEFT JOIN tb_contract c ON dg.c_con_no=c.c_con_no
        LEFT JOIN tb_partner p ON c.c_provider=p.c_no
        LEFT JOIN (
            SELECT c_provider, COUNT(DISTINCT c_gcode) count_gcode FROM tb_gdsprovider WHERE c_status_gp=N'正常进货'
                AND (ISNULL(?,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(?,',','store',1,default)))
                AND (ISNULL(?,'')='' OR c_provider=?)
            GROUP BY c_provider
        ) gp ON p.c_no=gp.c_provider
        WHERE 1=1 AND CONVERT(char(10),dg.c_dt,20)>=? AND CONVERT(char(10),dg.c_dt,20)<=?
            AND (ISNULL(?,'')='' OR dg.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(?,',','store',1,default)))
            AND (ISNULL(?,'')='' OR p.c_no=?)
        GROUP BY p.c_no, p.c_name, gp.count_gcode
    ),
    temp_oi AS (
        SELECT a.c_provider, SUM(ISNULL(b.c_order_n,0)) AS c_order_n, SUM(ISNULL(b.c_order_n,0)*ISNULL(c_pt_in,0)) AS c_order_am,
            SUM(ISNULL(c_rec_n,0)) AS c_rec_n, SUM(ISNULL(c_rec_n,0)*ISNULL(c_pt_in,0)) AS c_rec_am
        FROM tb_o_i a, tb_o_ig b WHERE a.c_id=b.c_id
            AND CONVERT(char(10),a.c_rec_au_dt,20)>=? AND CONVERT(char(10),a.c_rec_au_dt,20)<=?
            AND (ISNULL(?,'')='' OR a.c_provider=?)
            AND a.c_rec_type=N'有订单收货' AND a.c_rec_status=N'收货已审核' AND c_at_order<>0
        GROUP BY a.c_provider
    )
    SELECT a.c_no AS 供应商号, a.c_name AS 供应商名称, a.c_sale AS 销售额, a.c_maoli AS 毛利, a.c_maoliv AS 毛利率,
        a.kind_count AS 品项数, a.dongxiao AS 动销数, a.dongxiaov AS 动销率,
        b.c_order_n AS 订货量, b.c_order_am AS 订货额, b.c_rec_n AS 到货量, b.c_rec_am AS 到货额,
        CASE WHEN b.c_order_n=0 THEN NULL ELSE 1.00*b.c_rec_n/b.c_order_n END AS 到货量率,
        CASE WHEN b.c_order_am=0 THEN NULL ELSE 1.00*b.c_rec_am/b.c_order_am END AS 到货额率
    FROM temp00 a, temp_oi b WHERE a.c_no=b.c_provider
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, store, store, supplier, supplier, start, end, store, store, supplier, supplier, start, end, supplier, supplier)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t8_negative_margin")
def api_t8():
    """T8: 负毛利"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    dept = request.args.get('dept', '')
    ccode = request.args.get('ccode', '')
    if not start:
        start, _ = _default_dates()
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        start = (d - td(days=7)).strftime('%Y-%m-%d')
    if not end:
        _, end = _default_dates()
    sql = """
    SELECT dg.c_store_id AS 机构编码, s.c_name AS 机构名称, dg.c_name AS 商品名称, g.c_gcode AS 商品编码, g.c_barcode AS 条码,
        g.c_model AS 规格, g.c_basic_unit AS 单位, dg.c_dt AS 销售日期,
        dg.c_number_sale AS 销售数量, dg.c_sale AS 销售金额,
        dg.c_sale-(dg.c_at_sale) AS 毛利额,
        dg.c_pt_cost AS 进价, dg.c_price AS 售价, gs.c_number AS 库存,
        CASE WHEN ISNULL(dg.c_sale,0)=0 THEN NULL ELSE (dg.c_sale-dg.c_at_sale)/(dg.c_sale) END AS 毛利率,
        gs.c_lastin_dt AS 最后收货日期, gs.c_lastsale_dt AS 最后销售日期, gc.c_name AS 分类, p.c_name AS 供应商
    FROM tbs_d_gds dg
    LEFT JOIN tb_gds g ON g.c_gcode=dg.c_gcode
    LEFT JOIN tb_gdsstore gs ON gs.c_store_id=dg.c_store_id AND gs.c_gcode=dg.c_gcode
    LEFT JOIN tb_gdsclass gc ON gc.c_ccode=g.c_ccode
    LEFT JOIN tb_partner p ON p.c_no=gs.c_provider
    LEFT JOIN tb_store s ON dg.c_store_id=s.c_id
    WHERE CONVERT(char(10),dg.c_dt,20)>=? AND CONVERT(char(10),dg.c_dt,20)<=?
        AND (ISNULL(?,'')='' OR dg.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(?,',','store',1,default)))
        AND (ISNULL(?,'')='' OR gs.c_adno=?)
        AND (ISNULL(?,'')='' OR g.c_ccode LIKE ?+'%')
        AND gs.c_type LIKE N'%自营%'
        AND (dg.c_sale-dg.c_at_sale)<0
        AND ISNULL(dg.c_sale,0)<>0
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, start, end, store, store, dept, dept, ccode, ccode)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t9_high_inventory")
def api_t9():
    """T9: 高库存(低周转)"""
    store = request.args.get('store', '11021')
    ccode = request.args.get('ccode', '')
    formula = request.args.get('formula', '基于周转天数')
    sql = """
    SELECT g.c_ccode AS 品类, g.c_name AS 品名, g.c_barcode AS 条码, g.c_model AS 规格, gs.c_introduce_date AS 新品日,
        gs.c_status AS 商品品态, gs.c_pro_status AS 促销, gs.c_sale_frequency AS 畅销, gs.c_pt_cost AS 进价, gs.c_price AS 售价,
        CASE WHEN gs.c_price=0 THEN NULL ELSE (gs.c_price-gs.c_pt_cost)/gs.c_price END AS 毛利率,
        gs.c_number AS 库存数量, gs.c_at_cost AS 库存成本, gs.c_sn_perday AS 日均销量,
        gs.c_dnlmt_day AS 安全库存天数, gs.c_lastin_dt AS 最后收货日期, gs.c_lastsale_dt AS 最后销售日期,
        gc.c_name AS 分类名称, p.c_name AS 主供应商名称, g.c_adno AS 部门,
        dg.c_sale AS 最近年销售, dg.c_sale_day AS 年平均销售,
        CASE WHEN dg.c_sale_day=0 THEN NULL ELSE gs.c_at_cost/dg.c_sale_day END AS 计算值
    FROM tb_gdsstore gs
    LEFT JOIN tb_gds g ON g.c_gcode=gs.c_gcode
    LEFT JOIN tb_gdsclass gc ON gc.c_ccode=g.c_ccode
    LEFT JOIN tb_partner p ON p.c_no=gs.c_provider
    LEFT JOIN (
        SELECT c_store_id, c_gcode, SUM(c_sale) AS c_sale, SUM(c_sale)/12/30 AS c_sale_day FROM tbs_d_gds
        WHERE CONVERT(char(10),c_dt,20) BETWEEN DATEADD(year,-1,CONVERT(char(10),GETDATE()-1,20)) AND CONVERT(char(10),GETDATE()-1,20)
        GROUP BY c_store_id, c_gcode
    ) dg ON dg.c_store_id=gs.c_store_id AND dg.c_gcode=gs.c_gcode
    WHERE (ISNULL(?,'')='' OR gs.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(?,',','store',1,default)))
        AND (ISNULL(?,'')='' OR g.c_ccode LIKE ?+'%')
        AND g.c_ccode NOT LIKE '44%'
        AND gs.c_type LIKE N'自营%'
        AND gs.c_status NOT IN (N'作废')
        AND NOT (gs.c_status IN (N'暂停进货') AND gs.c_number=0)
        AND (1=0
            OR (?=N'基于周转天数'
                AND CASE WHEN g.c_adno=13 AND CASE WHEN dg.c_sale_day=0 THEN NULL ELSE gs.c_at_cost/dg.c_sale_day END >5 THEN 1
                        WHEN g.c_adno=11 AND CASE WHEN dg.c_sale_day=0 THEN NULL ELSE gs.c_at_cost/dg.c_sale_day END>30 THEN 1
                        WHEN g.c_adno=12 AND CASE WHEN dg.c_sale_day=0 THEN NULL ELSE gs.c_at_cost/dg.c_sale_day END>60 THEN 1
                    ELSE 0 END=1)
            OR (?=N'基于安全天数'
                AND CASE WHEN gs.c_sn_perday=0 THEN NULL ELSE gs.c_number/gs.c_sn_perday END < 3)
        )
    ORDER BY gs.c_number
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, store, store, ccode, ccode, formula, formula)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t10_new_products")
def api_t10():
    """T10: 新品报表"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    if not start:
        start, _ = _default_dates()
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        start = (d - td(days=30)).strftime('%Y-%m-%d')
    if not end:
        _, end = _default_dates()
    sql = """
    SELECT g.c_gcode AS 商品编码, g.c_name AS 商品名, g.c_barcode AS 条码, g.c_model AS 规格, g.c_basic_unit AS 单位,
        gs.c_introduce_date AS 新品日, gs.c_first_order_dt AS 首次进货日期, gs.c_firstsale_dt AS 首次销售日期,
        gs.c_test_day AS 新品天数, gs.c_status AS 商品品态, gs.c_pro_status AS 促销, gs.c_sale_frequency AS 畅销,
        gs.c_provider AS 供应商编码,
        dg.c_number_sale AS 销售数量, dg.c_sale AS 销售金额, dg.c_maoli AS 销售毛利, dg.c_maoliv AS 销售毛利率,
        gs.c_number AS 库存数量, gs.c_at_cost AS 库存成本, gs.c_sn_perday AS 日均销售, gs.c_onway AS 在途数量,
        gs.c_dnlmt_day AS 库存天数, gc.c_name AS 分类名称
    FROM tb_gdsstore gs
    LEFT JOIN tb_gds g ON g.c_gcode=gs.c_gcode
    LEFT JOIN tb_gdsclass gc ON g.c_ccode=gc.c_ccode
    LEFT JOIN (
        SELECT c_store_id, c_gcode, SUM(c_number_sale) AS c_number_sale, SUM(c_sale) AS c_sale,
            SUM(c_sale-c_at_sale) AS c_maoli,
            CASE WHEN SUM(c_sale)=0 THEN NULL ELSE SUM(c_sale-c_at_sale)/SUM(c_sale) END AS c_maoliv
        FROM tbs_d_gds WHERE CONVERT(char(10),c_dt,20)>=? AND CONVERT(char(10),c_dt,20)<=?
            AND (ISNULL(?,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
        GROUP BY c_store_id, c_gcode
    ) dg ON dg.c_store_id=gs.c_store_id AND dg.c_gcode=gs.c_gcode
    WHERE 1=1
        AND (ISNULL(?,'')='' OR gs.c_store_id IN (SELECT c_str FROM dbo.uf_split_string(ISNULL(?,''),',')))
        AND gs.c_status NOT IN (N'暂停进货',N'正常流转',N'作废')
        AND ISNULL(gs.c_test_day,0)<>0
        AND gs.c_type LIKE N'%自营%'
        AND DATEDIFF(day,gs.c_introduce_date,GETDATE())<g.c_od_day
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, start, end, store, store, store, store)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t11_supplier_movement")
def api_t11():
    """T11.1: 供应商动销率"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    supplier = request.args.get('supplier', '')
    ccode = request.args.get('ccode', '')
    if not start:
        start, _ = _default_dates()
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        start = (d - td(days=30)).strftime('%Y-%m-%d')
    if not end:
        _, end = _default_dates()
    sql = """
    SELECT gdsp.c_store_id AS 机构, s.c_sname AS 机构名称, gdsp.c_provider AS 供应商号, p.c_name AS 供应商名称,
        COUNT(DISTINCT gdsp.c_gcode) AS 单品数,
        COUNT(CASE WHEN dg.c_sale IS NULL THEN NULL ELSE 1 END) AS 动销数,
        COUNT(CASE WHEN dg.c_sale IS NOT NULL THEN NULL ELSE 1 END) AS 不动销数,
        CAST(COUNT(CASE WHEN dg.c_sale IS NULL THEN NULL ELSE 1 END) AS FLOAT)/CAST(COUNT(DISTINCT gdsp.c_gcode) AS FLOAT) AS 动销率
    FROM tb_gdsprovider gdsp
    LEFT JOIN (
        SELECT dg.c_store_id, dg.c_gcode, SUM(dg.c_at_sale) AS c_at_sale, SUM(dg.c_sale) AS c_sale FROM tbs_d_gds dg
        WHERE CONVERT(char(10),dg.c_dt,20)>=? AND CONVERT(char(10),dg.c_dt,20)<=?
        GROUP BY dg.c_store_id, dg.c_gcode
    ) dg ON dg.c_gcode=gdsp.c_gcode AND dg.c_store_id=gdsp.c_store_id
    INNER JOIN tb_store s ON s.c_id=gdsp.c_store_id AND s.c_status=N'正常营业'
    LEFT JOIN tb_partner p ON gdsp.c_provider=p.c_no
    LEFT JOIN tb_gds g ON g.c_gcode=gdsp.c_gcode AND (ISNULL(?,'')='' OR g.c_ccode LIKE ?+'%')
    LEFT JOIN tb_gdsclass gc ON gc.c_ccode=g.c_ccode
    LEFT JOIN tb_gdsstore gs ON gs.c_store_id=gdsp.c_store_id AND gs.c_gcode=gdsp.c_gcode
    WHERE gdsp.c_status_gp=N'正常进货' AND gs.c_status NOT IN (N'暂停销售')
        AND (ISNULL(?,'')='' OR gdsp.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(?,',','store',1,default)))
        AND (ISNULL(?,'')='' OR gdsp.c_provider=?)
        AND (ISNULL(?,'')='' OR g.c_ccode LIKE ?+'%')
    GROUP BY gdsp.c_store_id, s.c_sname, gdsp.c_provider, p.c_name
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, start, end, ccode, ccode, store, store, supplier, supplier, ccode, ccode)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t11_2_category_movement")
def api_t11_2():
    """T11.2: 品类动销率"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    ccode = request.args.get('ccode', '')
    clevel = request.args.get('clevel', '')
    if not start:
        start, _ = _default_dates()
    if not end:
        end = start
    sql = """
    DECLARE @pstore varchar(max), @pstart datetime, @pend datetime, @pccode varchar(1000), @pclevel int
    SELECT @pstore=?, @pstart=?, @pend=?, @pccode=?, @pclevel=?
    SELECT gc.c_ccode AS 分类号码, gc.c_name AS 分类名称,
        COUNT(DISTINCT g.c_gcode) AS 单品数,
        COUNT(DISTINCT CASE WHEN ISNULL(g.c_sale,0)<>0 THEN g.c_gcode ELSE NULL END) AS 动销数,
        ROUND(CAST(COUNT(DISTINCT CASE WHEN ISNULL(g.c_sale,0)<>0 THEN g.c_gcode ELSE NULL END) AS dec(12,2))/COUNT(DISTINCT g.c_gcode),4) AS 动销率,
        COUNT(DISTINCT g.c_gcode)-COUNT(DISTINCT CASE WHEN ISNULL(g.c_sale,0)<>0 THEN g.c_gcode ELSE NULL END) AS 不动销数
    FROM tb_gdsclass gc
    CROSS APPLY dbo.io_get_gds_gcode_cnt(@pstore, gc.c_ccode, @pstart, @pend) g
    WHERE 1=1
        AND (ISNULL(@pclevel,'')='' OR gc.c_level=@pclevel)
        AND (ISNULL(@pccode,'')='' OR gc.c_ccode LIKE @pccode+'%')
        AND g.c_sale_status NOT IN (N'暂停销售')
        AND NOT (g.c_number=0 AND g.c_status IN (N'暂停进货'))
        AND gc.c_ccode NOT LIKE '44%'
        AND gc.c_ccode=g.c_ccode_pre
    GROUP BY gc.c_ccode, gc.c_name
    ORDER BY gc.c_ccode
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        lev = None if not clevel else int(clevel)
        cursor.execute(sql, store, start, end, ccode, lev)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t12_abnormal_status")
def api_t12():
    """T12: 品态异常"""
    store = request.args.get('store', '11021')
    sql = """
    SELECT g.c_name AS 品名, g.c_barcode AS 条码, g.c_model AS 规格, g.c_basic_unit AS 单位, gs.c_introduce_date AS 新品日,
        gs.c_store_status AS 库存状态,
        p.c_name AS 主供应商名称, gs.c_number AS 库存数量, gs.c_sn_perday AS 日均销量,
        gs.c_lastin_dt AS 最后收货日期, gs.c_lastsale_dt AS 最后销售日期, gc.c_name AS 分类名称, gs.c_provider AS 主供应商
    FROM tb_gdsstore gs
    LEFT JOIN tb_gds g ON g.c_gcode=gs.c_gcode
    LEFT JOIN tb_gdsclass gc ON gc.c_ccode=g.c_ccode
    LEFT JOIN tb_partner p ON p.c_no=gs.c_provider
    WHERE (ISNULL(?,'')='' OR gs.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(?,',','store',1,default)))
        AND gs.c_status NOT LIKE N'作废' AND gs.c_store_status<>N'正常商品'
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, store, store)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


@app.route("/api/t13_slow_moving")
def api_t13():
    """T13: 滞销商品"""
    store = request.args.get('store', '11021')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    dept = request.args.get('dept', '')
    ccode = request.args.get('ccode', '')
    clevel = request.args.get('clevel', '第三层')
    calc_method = request.args.get('calc', '以上全部')
    if not start:
        start, _ = _default_dates()
        from datetime import timedelta as td
        d = datetime.strptime(start, '%Y-%m-%d')
        start = (d - td(days=14)).strftime('%Y-%m-%d')
    if not end:
        _, end = _default_dates()
    sql = """
    DECLARE @codelen int, @pstore varchar(max), @pstart datetime, @pend datetime, @pdept varchar(1000),
            @pccode varchar(1000), @psupplier varchar(max), @pcalc varchar(100)
    SELECT @pstore=?, @pstart=?, @pend=?, @pdept=?, @pccode=?, @pcalc=?
    SELECT @codelen=codelen FROM io_ccode WHERE name=?
    ;WITH temp AS (
        SELECT c_store_id, c_gcode, c_ccode, SUM(c_number_sale) AS c_number_sale, SUM(c_sale) AS c_sale,
            DENSE_RANK() OVER (PARTITION BY c_store_id,SUBSTRING(c_ccode,1,@codelen) ORDER BY SUM(c_sale)) AS sortby_sum_sale,
            DENSE_RANK() OVER (PARTITION BY c_store_id,SUBSTRING(c_ccode,1,@codelen) ORDER BY SUM(c_number_sale)) AS sortby_sum_number,
            COUNT(*) OVER (PARTITION BY c_store_id,SUBSTRING(c_ccode,1,@codelen)) AS allcount
        FROM tbs_d_gds WHERE 1=1
            AND CONVERT(char(10),c_dt,20) BETWEEN @pstart AND @pend
            AND (ISNULL(@pstore,'')='' OR c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(@pstore,',','store',1,default)))
        GROUP BY c_store_id, c_gcode, c_ccode
    ), temp01 AS (
        SELECT c_store_id, c_gcode, c_ccode, c_number_sale, c_sale,
            sortby_sum_sale, 1.00*sortby_sum_sale/allcount AS sortby_sum_sale_percent,
            sortby_sum_number, 1.00*sortby_sum_number/allcount AS sortby_sum_number_percent, allcount
        FROM temp
    ), temp02 AS (
        SELECT * FROM temp01 WHERE 1=1
            AND (@pcalc=N'销量6%' OR sortby_sum_sale_percent<=0.06)
            AND (@pcalc=N'销额1%' OR sortby_sum_number_percent<=0.01)
            AND (@pcalc=N'以上全部' OR (sortby_sum_sale_percent<=0.06 AND sortby_sum_number_percent<=0.01))
    )
    SELECT gs.c_store_id AS 机构编码, s.c_name AS 机构名称, gs.c_gcode AS 商品编码, g.c_name AS 商品名称,
        g.c_barcode AS 条码, g.c_model AS 规格, gstore.c_status AS 商品品态, gstore.c_sale_frequency AS 畅销,
        gstore.c_pt_cost AS 进价, gstore.c_price AS 售价,
        CASE WHEN gstore.c_price=0 THEN NULL ELSE (gstore.c_price-gstore.c_pt_cost)/gstore.c_price END AS 毛利率,
        gstore.c_number AS 库存数量, gstore.c_at_cost AS 库存成本, gstore.c_sn_perday AS 日均销量,
        gstore.c_lastin_dt AS 最后收货日期, gstore.c_lastsale_dt AS 最后销售日期,
        gc.c_ccode AS 分类编码, gc.c_name AS 分类名称, p.c_name AS 主供应商名称,
        c_number_sale AS 销售数量, c_sale AS 销售金额,
        sortby_sum_number AS 销量排名, sortby_sum_sale AS 销额排名,
        sortby_sum_number_percent AS 销量排名率, sortby_sum_sale_percent AS 销额排名率
    FROM temp02 gs
    LEFT JOIN tb_gds g ON g.c_gcode=gs.c_gcode
    LEFT JOIN tb_gdsstore gstore ON gs.c_store_id=gstore.c_store_id AND gs.c_gcode=gstore.c_gcode
    LEFT JOIN tb_gdsclass gc ON gc.c_ccode=g.c_ccode
    LEFT JOIN tb_gdsprovider gp ON gs.c_store_id=gp.c_store_id AND gs.c_gcode=gp.c_gcode AND gp.c_status=N'主供应商'
    LEFT JOIN tb_partner p ON p.c_no=gp.c_provider
    LEFT JOIN tb_store s ON gs.c_store_id=s.c_id
    WHERE (ISNULL(@pstore,'')='' OR gs.c_store_id IN (SELECT c_str FROM dbo.uf_io_split_string(@pstore,',','store',1,default)))
        AND (ISNULL(@pdept,'')='' OR gstore.c_adno=@pdept)
        AND (ISNULL(@pccode,'')='' OR gc.c_ccode LIKE @pccode+'%')
        AND gstore.c_number<>0 AND gstore.c_adno<>'14'
        AND ISNULL(gstore.c_sn_perday,0)<>0
    ORDER BY gs.c_store_id, SUBSTRING(gs.c_ccode,1,@codelen)
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, store, start, end, dept, ccode, calc_method, clevel)
        result = _rows_to_dicts(cursor)
        conn.close()
        return jsonify({"rows": [_clean_row(r) for r in result]})
    except Exception as e:
        return jsonify({"error": str(e), "rows": []})


if __name__ == "__main__":
    print("=" * 50)
    print("宜家天润超市 运营决策看板")
    print("=" * 50)
    print("正在启动服务...")
    print("打开浏览器访问: http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
