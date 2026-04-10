# 权限系统：企微扫码登录 + 三级角色控制

## Context
当前系统完全无认证，任何人访问都能看到全部数据。
需要加入登录验证 + 三级角色（超管/部门部长/店长）区分数据访问范围。
用户规模 <10 人，内网部署，有内部域名可在企微后台注册回调。

---

## 技术选型

| 项目 | 选择 | 原因 |
|------|------|------|
| 登录方式 | 企微扫码登录 | 无需密码管理，员工已有企微账号，支持普通浏览器 |
| 用户/角色存储 | SQLite（单文件） | <10人，无需额外服务器，管理简单 |
| Session | Flask server-side session | 加 secret_key 即可，简单可靠 |
| 权限执行 | Flask before_request + 装饰器 | 集中管理，不依赖前端 |

---

## 三级角色设计

| 角色 | 门店筛选 | 报表访问 | 品类限制 |
|------|---------|---------|---------|
| `admin` | 全部门店可选 | 全部报表 | 无 |
| `dept` 部门部长 | 全部门店可选 | 全部报表 | API 自动注入 ccode 前缀过滤 |
| `store` 店长 | 锁定为自己的门店 | 全部报表 | 无 |

> 部门部长的品类过滤：生鲜部长 → ccode 前缀 `11`，食品 → `22`，非食 → `33`。
> 不缩减报表入口，只过滤数据，避免前端维护复杂白名单。

---

## 企微扫码登录流程

```
用户访问系统
  → session 无效 → 跳转 /login
  → 显示企微扫码 iframe（WWLogin JS SDK）
  → 用户手机企微 扫码授权
  → 企微回调 /auth/callback?code=xxx
  → 后端用 code 换 access_token → 换 userid
  → 查 SQLite users 表 → 写 session（userid/role/store_id/dept_code）
  → 跳转回原始页面
```

**企微需要配置：**
- corpid（企业ID）
- agentid（自建应用ID）
- corpsecret（应用密钥）
- 回调域名在企微后台"网页授权及JS-SDK"中注册

---

## 文件改动清单

### 新增文件
- `routes/auth.py` — 登录/回调/登出路由，企微 API 调用
- `templates/login.html` — 扫码登录页面
- `auth_db.py` — SQLite 用户表初始化 + 查询（独立于 db.py）
- `users.db` — SQLite 数据库（运行时自动创建）

### 修改文件
- `app.py` — 注册 auth 蓝图，设置 `app.secret_key`，从环境变量读企微配置
- `routes/dashboard.py` — 所有路由加 `@login_required`；API 按角色注入 store_id/ccode 过滤
- `routes/reports.py` — 同上
- `templates/dashboard.html` — header 加用户名 + 退出按钮
- `templates/reports.html` — 同上

---

## auth_db.py 用户表结构

```sql
CREATE TABLE users (
    userid      TEXT PRIMARY KEY,   -- 企微 userid
    name        TEXT NOT NULL,
    role        TEXT NOT NULL,      -- admin / dept / store
    dept_code   TEXT,               -- 部门部长：'11'/'22'/'33'（品类ccode前缀）
    store_id    TEXT                -- 店长：门店ID
);
```

初始数据手动 INSERT，超管通过命令行维护（<10人不需要管理界面）。

---

## 权限执行方式

**装饰器**（放在 `auth_db.py`）：
```python
def login_required(f):
    # 检查 session，未登录 → redirect /login
```

**API 过滤注入**（在各路由函数开头）：
```python
role      = session['role']
store_id  = session.get('store_id')
dept_code = session.get('dept_code')

# store 角色：覆盖前端传来的 store 参数
if role == 'store':
    store_id = session['store_id']   # 锁死，忽略前端传参

# dept 角色：注入 ccode 过滤（仅对 category/product 类 API）
if role == 'dept' and not ccode:
    ccode = dept_code
```

---

## 企微配置存放

放在环境变量（不写进代码）：
```
WXWORK_CORPID=xxx
WXWORK_AGENTID=xxx
WXWORK_SECRET=xxx
FLASK_SECRET_KEY=xxx
```

`app.py` 用 `os.environ.get()` 读取。

---

## 验证方式

1. 未登录访问 `/` → 跳转 `/login`，显示扫码页
2. 扫码登录后 → 回到首页，header 显示用户名和退出
3. 店长账号：门店筛选器被锁定，只显示自己的门店
4. 部门部长：品类相关 API 只返回本部门数据
5. 超管：无任何限制
6. 点击退出 → session 清除 → 跳回登录页
