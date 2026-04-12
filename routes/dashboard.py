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


@bp.route("/sales")
def sales_page():
    return render_template("sales.html")


@bp.route("/stores")
def stores_page():
    return render_template("stores.html")


@bp.route("/category")
def category_page():
    return render_template("category.html")


@bp.route("/products")
def products_page():
    return render_template("products.html")


@bp.route("/supply")
def supply_page():
    return render_template("supply.html")


# ============================================================
# Query functions（模块级，供路由和预热共用）
# ============================================================

def _query_overview():
    """今日核心KPI + 昨日对比"""
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
    yest_avg_ticket = yest_sales / yest_bills if yest_bills else 0
    yest_profit_rate = yest_profit / yest_sales * 100 if yest_sales else 0
    today_avg_ticket = today_sales / today_bills if today_bills else 0
    today_profit_rate = today_profit / today_sales * 100 if today_sales else 0

    return {
        "date": latest,
        "sales": round(today_sales, 2),
        "profit": round(today_profit, 2),
        "bills": today_bills,
        "avg_ticket": round(today_avg_ticket, 2),
        "members": today_members,
        "profit_rate": round(today_profit_rate, 2) if today_sales else 0,
        "sales_change": round((today_sales - yest_sales) / yest_sales * 100, 2) if yest_sales else 0,
        "bills_change": round((today_bills - yest_bills) / yest_bills * 100, 2) if yest_bills else 0,
        "profit_change": round((today_profit - yest_profit) / yest_profit * 100, 2) if yest_profit else 0,
        "avg_ticket_change": round((today_avg_ticket - yest_avg_ticket) / yest_avg_ticket * 100, 2) if yest_avg_ticket else 0,
        "profit_rate_change": round(today_profit_rate - yest_profit_rate, 2) if yest_sales else 0,
    }


def _query_trend():
    """近30天销售趋势"""
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


def _query_store_rank():
    """门店销售排名"""
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


def _query_category(store_id=None):
    """品类销售分布，可按门店筛选"""
    conn = get_conn()
    cursor = conn.cursor()
    latest = get_latest_date()
    store_filter = "AND s.c_store_id = ?" if store_id else ""
    params = (latest, store_id) if store_id else (latest,)
    cursor.execute(f"""
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
          {store_filter}
        GROUP BY CASE
                   WHEN LEFT(g.c_ccode, 2) = '11' THEN N'生鲜'
                   WHEN LEFT(g.c_ccode, 2) = '22' THEN N'食品'
                   WHEN LEFT(g.c_ccode, 2) = '33' THEN N'非食品'
                   WHEN LEFT(g.c_ccode, 2) = '44' THEN N'耗材/资产'
                   ELSE N'其他'
                 END
        ORDER BY sales DESC
    """, *params)
    rows = cursor.fetchall()
    conn.close()
    return {
        "categories": [r[0] for r in rows],
        "sales": [round(float(r[1] or 0), 2) for r in rows],
        "profit": [round(float(r[2] or 0), 2) for r in rows],
    }


def _query_hourly():
    """时段销售分布"""
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
    avg_ticket_map = {
        r[0]: round(float(r[1] or 0) / r[2], 2) if r[2] else 0
        for r in rows
    }
    return {
        "hours": [f"{h}:00" for h in hours],
        "sales": [sales_map.get(h, 0) for h in hours],
        "bills": [bills_map.get(h, 0) for h in hours],
        "avg_ticket": [avg_ticket_map.get(h, 0) for h in hours],
    }


def _query_top_products(store_id=None):
    """热销商品TOP15，可按门店筛选"""
    conn = get_conn()
    cursor = conn.cursor()
    latest = get_latest_date()
    if store_id:
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
              AND s.c_store_id = ?
            GROUP BY s.c_gcode, g.c_name
            ORDER BY sales DESC
        """, latest, store_id)
    else:
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


def _query_daily_flow(start=None, end=None):
    """总客流日报（T2），支持自定义日期范围"""
    conn = get_conn()
    cursor = conn.cursor()
    latest = get_latest_date()
    date_end   = end   if end   else latest
    date_start = start if start else None
    if date_start is None:
        # 默认近7天
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
        """, date_end, date_end)
    else:
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
            WHERE CONVERT(varchar(10), a.c_datetime, 23) >= ?
              AND CONVERT(varchar(10), a.c_datetime, 23) <= ?
              AND a.c_id NOT LIKE '-%%'
              AND ISNULL(a.c_adno, '') <> '14'
              AND a.c_computer_id <> 0
            GROUP BY CONVERT(varchar(10), a.c_datetime, 23), DATEPART(WEEKDAY, a.c_datetime),
                     a.c_store_id, b.c_name
            ORDER BY dt DESC, a.c_store_id
        """, date_start, date_end)
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


def _query_store_trend():
    """各门店近7天趋势"""
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


def _query_stores():
    """门店列表"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT c_id, c_name FROM tb_store WHERE c_type=N'分店' AND c_status=N'正常营业' ORDER BY c_id")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]


# ============================================================
# Routes
# ============================================================

@bp.route("/api/overview")
def api_overview():
    return jsonify(cached_query("overview", _query_overview))


@bp.route("/api/trend")
def api_trend():
    return jsonify(cached_query("trend", _query_trend))


@bp.route("/api/store_rank")
def api_store_rank():
    return jsonify(cached_query("store_rank", _query_store_rank))


@bp.route("/api/category")
def api_category():
    from flask import request
    store_id = request.args.get('store_id', '').strip()
    if store_id:
        return jsonify(_query_category(store_id=store_id))
    return jsonify(cached_query("category", _query_category))


# L2 品类代码 -> 名称映射
_L2_CODE_MAP = {
    # 生鲜 L2
    '110': '熟食', '111': '水产', '112': '水果', '113': '面包',
    '114': '精肉', '116': '生鲜场外专柜', '117': '蔬菜', '118': '蛋品',
    # 食品 L2
    '220': '烟酒饮料', '221': '休闲食品', '222': '营养冲调',
    '223': '粮油调料', '224': '食品场外专柜', '225': '冷冻冷藏',
    '226': '散装休闲/南北干货',
    # 非食品 L2
    '330': '洗化清洁', '331': '家用百货', '332': '文体休闲',
    '333': '家电电器', '334': '针织针纺', '335': '非食场外专柜',
}
_L1_NAME_TO_CODE = {'生鲜': '11', '食品': '22', '非食品': '33', '耗材/资产': '44'}


def _query_category_l2(l1_name, store_id=None):
    """L2品类销售分布（按L1名称过滤）"""
    l1_code = _L1_NAME_TO_CODE.get(l1_name)
    if not l1_code:
        return {"categories": [], "codes": [], "sales": [], "profit": []}
    conn = get_conn()
    cursor = conn.cursor()
    latest = get_latest_date()
    store_filter = "AND s.c_store_id = ?" if store_id else ""
    params = [latest, l1_code] + ([store_id] if store_id else [])
    cursor.execute(f"""
        SELECT LEFT(g.c_ccode, 3) as l2_code,
               SUM(s.c_amount) as sales,
               SUM(s.c_amount - ISNULL(s.c_aet_cost, 0)) as profit
        FROM tb_o_sg s
        JOIN tb_gds g ON s.c_gcode = g.c_gcode AND s.c_adno = g.c_adno
        WHERE CONVERT(varchar, s.c_datetime, 23) = ?
          AND s.c_type = N'销售' AND s.c_amount > 0
          AND LEFT(g.c_ccode, 2) = ?
          {store_filter}
        GROUP BY LEFT(g.c_ccode, 3)
        ORDER BY sales DESC
    """, *params)
    rows = cursor.fetchall()
    conn.close()
    return {
        "categories": [_L2_CODE_MAP.get(r[0], r[0]) for r in rows],
        "codes": [r[0] for r in rows],
        "sales": [round(float(r[1] or 0), 2) for r in rows],
        "profit": [round(float(r[2] or 0), 2) for r in rows],
    }


def _query_category_hourly(category=None, ccode=None, store_id=None):
    """某品类各时段客流分布。ccode（2或3位前缀）优先于 category 名称。"""
    conn = get_conn()
    cursor = conn.cursor()
    latest = get_latest_date()
    if ccode:
        clen = len(ccode)
        ccode_filter = f"AND LEFT(g.c_ccode, {clen}) = ?"
        base_params = [latest, ccode]
        display_name = _L2_CODE_MAP.get(ccode, category or ccode)
    else:
        ccode_prefix = _L1_NAME_TO_CODE.get(category or '')
        if ccode_prefix:
            ccode_filter = "AND LEFT(g.c_ccode, 2) = ?"
            base_params = [latest, ccode_prefix]
        else:
            ccode_filter = "AND LEFT(g.c_ccode, 2) NOT IN ('11','22','33','44')"
            base_params = [latest]
        display_name = category or ''
    store_filter = "AND s.c_store_id = ?" if store_id else ""
    params = base_params + ([store_id] if store_id else [])
    cursor.execute(f"""
        SELECT DATEPART(hour, s.c_datetime) as hr,
               COUNT(DISTINCT s.c_id) as bills,
               SUM(s.c_amount) as sales
        FROM tb_o_sg s
        JOIN tb_gds g ON s.c_gcode = g.c_gcode AND s.c_adno = g.c_adno
        WHERE CONVERT(varchar, s.c_datetime, 23) = ?
          AND s.c_type = N'销售' AND s.c_amount > 0
          {ccode_filter}
          {store_filter}
        GROUP BY DATEPART(hour, s.c_datetime)
        ORDER BY hr
    """, *params)
    rows = cursor.fetchall()
    conn.close()
    hours = list(range(6, 23))
    bills_map = {r[0]: r[1] for r in rows}
    sales_map = {r[0]: round(float(r[2] or 0), 2) for r in rows}
    return {
        "category": display_name,
        "hours": [f"{h}:00" for h in hours],
        "bills": [bills_map.get(h, 0) for h in hours],
        "sales": [sales_map.get(h, 0) for h in hours],
    }


@bp.route("/api/hourly")
def api_hourly():
    return jsonify(cached_query("hourly", _query_hourly))


@bp.route("/api/category_l2")
def api_category_l2():
    from flask import request
    l1 = request.args.get('l1', '').strip()
    store_id = request.args.get('store_id', '').strip() or None
    if not l1:
        return jsonify({"categories": [], "codes": [], "sales": [], "profit": []})
    return jsonify(_query_category_l2(l1, store_id))


@bp.route("/api/category_hourly")
def api_category_hourly():
    from flask import request
    category = request.args.get('category', '').strip() or None
    ccode = request.args.get('ccode', '').strip() or None
    store_id = request.args.get('store_id', '').strip() or None
    if not category and not ccode:
        return jsonify({"error": "category or ccode required", "hours": [], "bills": [], "sales": []})
    return jsonify(_query_category_hourly(category=category, ccode=ccode, store_id=store_id))


@bp.route("/api/top_products")
def api_top_products():
    from flask import request
    store_id = request.args.get('store_id', '').strip()
    if store_id:
        return jsonify(_query_top_products(store_id=store_id))
    return jsonify(cached_query("top_products", _query_top_products))


@bp.route("/api/daily_flow")
def api_daily_flow():
    from flask import request
    start = request.args.get('start', '').strip() or None
    end   = request.args.get('end',   '').strip() or None
    if start or end:
        return jsonify(_query_daily_flow(start=start, end=end))
    return jsonify(cached_query("daily_flow", _query_daily_flow))


@bp.route("/api/store_trend")
def api_store_trend():
    return jsonify(cached_query("store_trend", _query_store_trend))


@bp.route("/api/stores")
def api_stores():
    return jsonify(cached_query("stores", _query_stores))


# ============================================================
# Cache warmup（供 app.py 启动时调用）
# ============================================================

def warmup():
    """并行预热所有看板查询缓存。"""
    from concurrent.futures import ThreadPoolExecutor
    # 先单独预热 latest_date，避免后续并行查询各自重复建连接查它
    try:
        get_latest_date()
    except Exception as e:
        print(f"[warmup] latest_date 预热失败: {e}")
        return

    jobs = [
        ("overview",     _query_overview),
        ("trend",        _query_trend),
        ("store_rank",   _query_store_rank),
        ("category",     _query_category),
        ("hourly",       _query_hourly),
        ("top_products", _query_top_products),
        ("daily_flow",   _query_daily_flow),
        ("store_trend",  _query_store_trend),
        ("stores",       _query_stores),
    ]
    # max_workers=3 限制同时打开的数据库连接数
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(cached_query, key, fn): key for key, fn in jobs}
        for future, key in futures.items():
            try:
                future.result()
            except Exception as e:
                print(f"[warmup] 看板 {key} 预热失败: {e}")
    print("[warmup] 看板缓存预热完成")
