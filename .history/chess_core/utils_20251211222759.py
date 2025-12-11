"""工具函数"""
import time
import psutil
import os

def get_cpu_usage():
    """获取CPU使用率"""
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    """获取内存使用情况"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024  # MB

def format_time(seconds: float) -> str:
    """格式化时间"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:05.2f}"