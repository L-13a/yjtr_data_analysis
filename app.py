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


if __name__ == "__main__":
    import atexit
    import subprocess

    subprocess.run(["redis-server", "--daemonize", "yes"], check=False)
    atexit.register(lambda: subprocess.run(["redis-cli", "shutdown", "nosave"], check=False))

    print("=" * 50)
    print("宜家天润超市 运营决策看板")
    print("=" * 50)
    print("正在启动服务...")
    print("打开浏览器访问: http://localhost:5001")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5001, debug=True)
