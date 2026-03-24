# 总看板首次加载慢 —— 性能优化方案

## 根本原因

每次重启服务后刷新总看板慢，三个问题叠加：

1. **Flask 单线程**：前端 `Promise.all` 同时发出 7 个 API 请求，但后端默认 `threaded=False`，请求串行排队处理，总耗时 ≈ 7 个 API 之和（约 6-7 秒）
2. **无连接池**：每个 API 调用 `get_conn()` 都新建一条数据库连接（+500ms/次），7 个请求 = 7 次握手
3. **冷启动无预热**：服务刚启动缓存为空，第一批 7 个请求全部穿透到数据库

---

## 修改文件

`app.py`

---

## Step 1 — 启用多线程（改 1 行，收益最大）

**位置**：`app.py` 末尾 `app.run(...)` 处

```python
# 改前
app.run(host="0.0.0.0", port=5001, debug=True)

# 改后
app.run(host="0.0.0.0", port=5001, debug=True, threaded=True)
```

**效果**：7 个请求真正并发处理，总耗时从 ∑t_i 降至 max(t_i)，预计节省 5-6 秒。

---

## Step 2 — 线程安全连接池（替换 get_conn）

用 `threading.local()` 实现每线程复用单条连接，避免重复握手。

```python
import threading
_local = threading.local()

def get_conn():
    conn = getattr(_local, 'conn', None)
    if conn is None:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['uid']};"
            f"PWD={DB_CONFIG['pwd']};"
            "LoginTimeout=15;"
        )
        conn = pyodbc.connect(conn_str, timeout=30)
        _local.conn = conn
    return conn
```

> 注意：各 `api_xxx` 函数中**不再调用 `conn.close()`**，让连接在线程内复用。

**效果**：连接建立从 7 次降至线程数次，节省约 2-3 秒冷启动开销。

---

## Step 3 — 启动时后台预热缓存

在 `app.run()` 之前启动后台线程，提前调用各 API 的内部 `_query` 填充缓存：

```python
import threading

def _warmup():
    import time
    time.sleep(2)  # 等待 Flask 完成端口绑定
    keys_and_funcs = [
        ("overview",    _query_overview),
        ("trend",       _query_trend),
        ("store_rank",  _query_store_rank),
        ("category",    _query_category),
        ("hourly",      _query_hourly),
        ("top_products",_query_top_products),
        ("store_trend", _query_store_trend),
    ]
    for key, fn in keys_and_funcs:
        try:
            cached_query(key, fn)
        except Exception as e:
            print(f"[warmup] {key} 失败: {e}")

if __name__ == "__main__":
    threading.Thread(target=_warmup, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=True, threaded=True)
```

**实际做法**：将每个 API 路由内部的 `_query` 函数提升为模块级函数（目前已是局部函数，只需移出即可）。

**效果**：用户打开浏览器时缓存已就绪，首屏响应 < 300ms。

---

## 优先级汇总

| 步骤 | 改动量 | 预期收益 | 推荐顺序 |
|------|--------|---------|--------|
| Step 1 多线程 | 1 行 | ★★★★★ | 必做，最先 |
| Step 2 连接池 | ~15 行 | ★★★★ | 必做 |
| Step 3 预热 | ~30 行 | ★★★ | 建议做 |

---

## 验证方法

1. 重启服务 `python app.py`
2. 打开浏览器 DevTools → Network 面板
3. 刷新 `http://localhost:5001`
4. 观察 7 个 API 请求是否**并行发出且并行完成**（瀑布图应对齐，而非阶梯状）
5. 目标：冷启动 < 2 秒，缓存命中 < 500ms
