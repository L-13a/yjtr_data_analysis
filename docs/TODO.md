# 上线前需要修改的地方

## T1 自动加载 — 切换为当天日期

### 1. 前端：`templates/reports.html`

找到以下两行（在 `// T1 开页自动加载配置` 注释下方）：

```js
const T1_AUTO_STORE = '倾城';
const T1_TEST_DATES = { start: '2024-09-08', end: '2024-09-09' };
```

改为：

```js
const T1_AUTO_STORE = '倾城';
const T1_TEST_DATES = null;  // null → 自动使用当天日期
```

### 2. 后端预热：`app.py`

找到 `_warmup_t1()` 函数中的固定日期：

```python
start = "2024-09-08"
end   = "2024-09-09"
```

改为：

```python
from datetime import date
today = date.today().strftime("%Y-%m-%d")
start = today
end   = today
```
