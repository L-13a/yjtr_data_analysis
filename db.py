# -*- coding: utf-8 -*-
"""
数据库连接、Redis 缓存、公共工具函数
所有路由模块从这里 import，不要重复定义。
"""
import decimal
import json
import time
from datetime import date, datetime

import pyodbc
import redis

# ── 数据库配置 ────────────────────────────────────────────────
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


# ── Redis 缓存 ────────────────────────────────────────────────
CACHE_TTL = 300       # 5 分钟
REDIS_PREFIX = "yjtr:"

try:
    _redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    _redis.ping()
    _redis_available = True
    print("[cache] Redis 连接成功")
except Exception:
    _redis_available = False
    _cache: dict = {}
    _cache_time: dict = {}
    print("[cache] Redis 不可用，降级为内存缓存")


def _run_with_retry(query_func, retries=3, delay=2):
    last_err = None
    for attempt in range(retries):
        try:
            return query_func()
        except pyodbc.OperationalError as e:
            last_err = e
            if attempt < retries - 1:
                print(f"[db] 连接错误，{delay}s 后重试 (attempt {attempt+1}/{retries}): {e}")
                time.sleep(delay)
    raise last_err


def cached_query(key, query_func, ttl=CACHE_TTL):
    rkey = REDIS_PREFIX + key
    if _redis_available:
        cached = _redis.get(rkey)
        if cached:
            return json.loads(cached)
        result = _run_with_retry(query_func)
        _redis.setex(rkey, ttl, json.dumps(result, ensure_ascii=False, default=str))
        return result
    else:
        now = time.time()
        if key in _cache and now - _cache_time.get(key, 0) < ttl:
            return _cache[key]
        result = _run_with_retry(query_func)
        _cache[key] = result
        _cache_time[key] = time.time()
        return result


# ── 日期工具 ──────────────────────────────────────────────────
def get_latest_date():
    def _query():
        conn = get_conn()
        cursor = conn.cursor()
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


def _default_dates():
    latest = get_latest_date()
    return latest, latest


# ── 结果集工具 ────────────────────────────────────────────────
def _rows_to_dicts(cursor):
    """跳过无列描述的结果集（存储过程内的 SET 语句等）"""
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
    """将 Decimal / datetime 转为 JSON 可序列化类型"""
    out = {}
    for k, v in d.items():
        if isinstance(v, decimal.Decimal):
            out[k] = float(v)
        elif isinstance(v, (date, datetime)):
            out[k] = str(v)[:10]
        else:
            out[k] = v
    return out
