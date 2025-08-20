# 安装单个包
pip install --target /opt/maxkb-data/maxkb-python-packages numpy

# 安装多个包
pip install --target /opt/maxkb-data/maxkb-python-packages numpy pandas requests scikit-learn

# 从requirements.txt安装
pip install --target /opt/maxkb-data/maxkb-python-packages -r requirements.txt



# 查看已安装的包
ls -la /opt/maxkb-data/maxkb-python-packages/

# 重启容器测试持久化
docker restart gs-backend


现在当您更新容器版本时：
停止旧容器：docker stop gs-backend
运行新版本部署脚本：./deploy-interactive.sh
依赖自动保留：所有在 /opt/maxkb-data/maxkb-python-packages 中的依赖包会自动挂载到新容器

# MaxKB 工具脚本开发规范

## 脚本要求

MaxKB 的工具执行器对 Python 脚本有特定的格式要求，必须遵循以下规范：

### 1. 基本要求

- ✅ **必须定义至少一个函数**
- ✅ **函数语法必须正确**
- ✅ **函数必须是可调用的**
- ✅ **使用正确的 Python 缩进**

### 2. 正确的脚本格式

#### 基本函数定义
```python
def my_tool():
    return "Hello World"
```

#### 带参数的函数
```python
def calculate(a, b):
    result = a + b
    return result
```

#### 带默认参数的函数
```python
def process_text(text="", option="default"):
    processed = text.upper()
    return f"{processed} - {option}"
```

#### 复杂工具示例
```python
def data_processor(input_data, config="{}"):
    import json

    # 解析配置
    settings = json.loads(config) if config else {}

    # 处理数据
    result = {
        "original": input_data,
        "processed": input_data.strip().upper(),
        "config": settings
    }

    return result
```

#### 带错误处理的工具
```python
def safe_operation(data):
    try:
        # 执行可能出错的操作
        result = risky_function(data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def risky_function(data):
    # 辅助函数
    return data / 0  # 示例：可能出错的操作
```

### 3. 错误的脚本格式

#### ❌ 只有变量赋值（没有函数定义）
```python
# 错误：这样的代码会失败
result = "Hello World"
```

#### ❌ 语法错误
```python
# 错误：缺少冒号
def my_function()
    return "hello"

# 错误：缩进问题
def my_function():
return "hello"
```

#### ❌ 定义的不是函数
```python
# 错误：定义的是变量，不是函数
my_variable = "hello world"
```

### 4. 执行流程说明

MaxKB 工具执行器的工作流程：

1. **代码执行**：在 sandbox 环境中执行用户代码
2. **函数提取**：从执行结果中提取定义的函数
3. **函数调用**：调用提取的函数并传入参数
4. **结果返回**：返回函数的执行结果

### 5. 调试技巧

如果工具执行失败，检查以下几点：

1. **确保定义了函数**：代码中必须有 `def function_name():`
2. **检查语法**：确保没有语法错误，特别是冒号和缩进
3. **验证函数可调用**：确保定义的是函数，不是变量
4. **测试参数匹配**：确保函数参数与传入的参数匹配

### 6. 可用的 Python 包

工具脚本可以使用以下路径中的 Python 包：
- `/opt/py3/lib/python3.11/site-packages` - 系统预装包
- `/opt/maxkb-app/sandbox/python-packages` - Sandbox 专用包
- `/opt/maxkb/python-packages` - 用户安装的包

### 7. 缓存和持久化

工具可以使用以下目录进行数据持久化：
- `/opt/maxkb/cache` - 缓存目录
- `/opt/maxkb/local` - 本地存储目录

示例：
```python
def cached_operation(data):
    import os
    import pickle

    cache_dir = "/opt/maxkb/cache"
    cache_file = os.path.join(cache_dir, f"cache_{hash(data)}.pkl")

    # 检查缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # 执行计算
    result = expensive_computation(data)

    # 保存缓存
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)

    return result

def expensive_computation(data):
    # 模拟耗时操作
    return data.upper()
```

### 8. 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `popitem(): dictionary is empty` | 代码执行后没有定义函数 | 确保代码中定义了至少一个函数 |
| `定义的对象不是可调用函数` | 定义的是变量而不是函数 | 使用 `def` 关键字定义函数 |
| `SyntaxError` | 语法错误 | 检查代码语法，特别是冒号和缩进 |
| `FileNotFoundError` | 缓存目录不存在 | 使用 `os.makedirs(dir, exist_ok=True)` 创建目录 |