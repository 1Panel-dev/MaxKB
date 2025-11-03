"""
交互式问答客户端
用于在 MaxKB 工作流中调用，向服务端发送问题并等待人工回复

使用示例：
    result = ask_human_support(
        question="如何配置知识库?",
        context="用户正在设置向量数据库",
        timeout=180
    )
"""


def ask_human_support(
    question="",
    context="",
    priority="normal",
    timeout=300,
    server_url="http://localhost:5678"
):
    """
    向人工支持服务发送问题并等待回复

    参数:
    - question: 用户的问题内容（必需）
    - context: 问题的上下文信息，帮助人工更好理解问题（可选）
    - priority: 优先级，可选值: low/normal/high（默认 normal）
    - timeout: 等待回复的超时时间（秒），默认 300 秒（5分钟）
    - server_url: 服务端地址（默认 http://localhost:5678）

    返回:
    - 包含问题和回复的字典结果，结构如下：
      {
          "status": "成功",
          "question": "原始问题",
          "response": "人工回复内容",
          "elapsed_time": "1.2 秒"
      }
    """
    import requests
    import time

    # 参数验证
    if not question or not question.strip():
        return {
            "error": "问题不能为空",
            "status": "参数错误"
        }

    # 验证优先级参数
    valid_priorities = ["low", "normal", "high"]
    if priority not in valid_priorities:
        priority = "normal"

    try:
        print(f"📤 正在发送问题到人工支持...")
        print(f"   问题: {question}")
        if context:
            print(f"   上下文: {context}")
        print(f"   优先级: {priority}")
        print(f"⏳ 等待人工回复中（超时: {timeout}秒）...")

        start_time = time.time()

        # 构建请求数据
        request_data = {
            "question": question,
            "context": context,
            "priority": priority,
            "timeout": timeout
        }

        # 发送 POST 请求到服务端
        response = requests.post(
            f"{server_url}/ask",
            json=request_data,
            timeout=timeout
        )

        elapsed_time = time.time() - start_time

        # 检查响应状态
        response.raise_for_status()

        result = response.json()

        if result.get('status') == 'success':
            print(f"✅ 收到人工回复 (耗时 {elapsed_time:.1f} 秒)")
            return {
                "status": "成功",
                "question": result.get('question', question),
                "response": result.get('response', ''),
                "elapsed_time": f"{elapsed_time:.1f} 秒"
            }
        else:
            return {
                "error": result.get('error', '未知错误'),
                "status": "服务端返回错误",
                "question": question
            }

    except requests.Timeout:
        return {
            "error": f"等待人工回复超时（{timeout}秒）",
            "status": "超时",
            "question": question,
            "timeout": timeout
        }

    except requests.ConnectionError:
        return {
            "error": f"无法连接到服务端 {server_url}，请确保服务端已启动",
            "status": "连接失败",
            "question": question
        }

    except requests.RequestException as e:
        return {
            "error": f"请求失败: {str(e)}",
            "status": "请求错误",
            "question": question
        }

    except Exception as e:
        return {
            "error": f"未知错误: {str(e)}",
            "status": "异常",
            "question": question
        }


# 测试函数（可选）
if __name__ == '__main__':
    import sys

    # 测试调用
    print("🧪 开始测试客户端功能...\n")

    # 测试1: 基础调用
    print("测试1: 基础调用")
    result1 = ask_human_support(
        question="MaxKB 如何配置知识库？"
    )
    print("结果:", result1)
    print()

    # 测试2: 带上下文和优先级
    print("\n测试2: 带上下文和优先级")
    result2 = ask_human_support(
        question="向量数据库连接失败",
        context="用户正在使用 PostgreSQL + pgvector，已确认数据库服务正常运行",
        priority="high",
        timeout=180  # 3分钟超时
    )
    print("结果:", result2)
    print()

    print("\n✅ 测试完成!")
