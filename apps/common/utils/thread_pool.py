# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    thread_pool.py
@date:    2026/10/20
@desc:    线程层"业务完成 vs 取消"并发等待工具
"""

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait


def await_complete_or_cancel(done_event, cancel_event, on_cancel):
    """
    线程层并发等待"业务完成(done_event)"与"取消信号(cancel_event)"任一先到
    :parma done_event: 完成事件
    :param cancel_event: 中断事件
    :param on_cancel: 对应的取消函数
    :return:是否取消
    """

    ex = ThreadPoolExecutor(max_workers=2)
    try:
        f_done = ex.submit(done_event.wait)
        f_cancel = ex.submit(cancel_event.wait)
        wait({f_done, f_cancel}, return_when=FIRST_COMPLETED)
    finally:
        ex.shutdown(wait=False)
    if cancel_event.is_set():
        on_cancel()
        return True
    return False
