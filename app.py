# -*- coding: utf-8 -*-
"""
宜家天润超市 - 运营决策看板
入口文件：创建 Flask app，注册蓝图，启动服务。
"""
from flask import Flask

from routes.dashboard import bp as dashboard_bp
from routes.reports import bp as reports_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reports_bp)


def _warmup():
    """启动时并行预热看板和 T1 报表缓存。"""
    import time
    from concurrent.futures import ThreadPoolExecutor
    from db import _clean_row, _rows_to_dicts, cached_query, get_conn
    from routes.dashboard import warmup as warmup_dashboard
    time.sleep(2)  # 等 Redis 和数据库连接就绪

    def _warmup_t1():
        store = "11021"
        start = "2024-09-08"
        end   = "2024-09-09"
        dept = ""
        bhour, ehour = 0, 23
        ccode = ""
        ccodelen = ""
        key = f"t1:{store}:{start}:{end}:{dept}:{bhour}:{ehour}:{ccode}:{ccodelen}"
        def _query():
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("exec up_rpt_io_sale_bytime ?,?,?,?,?,?,?,?,1",
                           start, end, store, dept, bhour, ehour, ccode, ccodelen)
            result = _rows_to_dicts(cursor)
            conn.close()
            return [_clean_row(r) for r in result]
        try:
            cached_query(key, _query)
            print("[warmup] T1 按时段销售缓存预热完成")
        except Exception as e:
            print(f"[warmup] T1 预热失败: {e}")

    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.submit(warmup_dashboard)
        pool.submit(_warmup_t1)


if __name__ == "__main__":
    import atexit
    import subprocess
    import threading

    subprocess.run(["redis-server", "--daemonize", "yes"], check=False)
    atexit.register(lambda: subprocess.run(["redis-cli", "shutdown", "nosave"], check=False))

    threading.Thread(target=_warmup, daemon=True).start()

    def _schedule_warmup():
        import time
        from routes.dashboard import warmup as warmup_dashboard
        while True:
            time.sleep(240)  # 每4分钟刷新，TTL是5分钟
            warmup_dashboard()
            print("[warmup] 看板缓存定时刷新完成")

    threading.Thread(target=_schedule_warmup, daemon=True).start()

    print("=" * 50)
    print("宜家天润超市 运营决策看板")
    print("=" * 50)
    print("正在启动服务...")
    print("打开浏览器访问: http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
