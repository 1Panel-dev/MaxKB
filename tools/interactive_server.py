"""
交互式问答服务端
用于接收工作流发送的问题，并在命令行中人工回复

运行方式：
    python interactive_server.py

默认监听地址：http://localhost:5678
"""

from flask import Flask, request, jsonify
import threading
import queue
import sys

app = Flask(__name__)

# 使用队列来处理问题和回复
question_queue = queue.Queue()
response_queue = queue.Queue()


@app.route('/ask', methods=['POST'])
def ask_question():
    """
    接收问题的 API 端点
    """
    try:
        data = request.json
        question = data.get('question', '')
        context = data.get('context', '')
        priority = data.get('priority', 'normal')
        timeout = data.get('timeout', 300)

        if not question:
            return jsonify({
                'error': '问题不能为空',
                'status': 'error'
            }), 400

        # 在服务端显示问题和额外信息
        print("\n" + "="*60)
        print("📩 收到新问题:")
        print(f"\n问题: {question}")
        if context:
            print(f"上下文: {context}")

        # 优先级显示
        priority_emoji = {"low": "🟢", "normal": "🟡", "high": "🔴"}
        print(f"优先级: {priority_emoji.get(priority, '🟡')} {priority.upper()}")
        print(f"超时时间: {timeout}秒")
        print("="*60)
        print("请输入回复 (直接输入文本后按回车): ", end='', flush=True)

        # 将问题放入队列，等待人工回复
        question_queue.put(question)

        # 等待回复（阻塞直到有回复）
        response = response_queue.get()

        return jsonify({
            'status': 'success',
            'question': question,
            'response': response
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


def input_thread():
    """
    独立线程用于处理命令行输入
    """
    print("🚀 交互式问答服务端已启动!")
    print("📡 监听地址: http://localhost:5678")
    print("⏳ 等待接收问题...\n")

    while True:
        try:
            # 等待问题到来
            question_queue.get()

            # 获取用户输入作为回复
            user_response = input()

            if user_response.strip():
                response_queue.put(user_response.strip())
                print(f"✅ 回复已发送: {user_response.strip()}\n")
                print("⏳ 等待接收下一个问题...\n")
            else:
                response_queue.put("未提供回复")
                print("⚠️ 空回复已发送\n")
                print("⏳ 等待接收下一个问题...\n")

        except Exception as e:
            print(f"❌ 输入处理错误: {e}")
            response_queue.put(f"服务端错误: {str(e)}")


if __name__ == '__main__':
    # 启动输入处理线程
    input_thread_obj = threading.Thread(target=input_thread, daemon=True)
    input_thread_obj.start()

    # 启动 Flask 服务
    app.run(host='0.0.0.0', port=5678, debug=False, use_reloader=False)
