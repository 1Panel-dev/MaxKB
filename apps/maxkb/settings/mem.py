# coding=utf-8
import os
import gc
import threading
from maxkb.const import CONFIG
from common.utils.logger import maxkb_logger
import random
import psutil

CURRENT_PID=os.getpid()
# 1 hour
GC_INTERVAL = 3600

def enable_force_gc():
    before = int(psutil.Process(CURRENT_PID).memory_info().rss / 1024 / 1024)
    collected = gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass
    after = int(psutil.Process(CURRENT_PID).memory_info().rss / 1024 / 1024)
    maxkb_logger.debug(f"(PID: {CURRENT_PID}) Forced GC ({collected} objects and {before - after} MB recycled)")
    t = threading.Timer(GC_INTERVAL - random.randint(0, 900), enable_force_gc)
    t.daemon = True
    t.start()

if CONFIG.get("ENABLE_FORCE_GC", '1') == "1":
    maxkb_logger.info(f"(PID: {CURRENT_PID}) Forced GC enabled")
    enable_force_gc()
