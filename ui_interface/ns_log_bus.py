# ui_interface/ns_log_bus.py
import logging
import logging.handlers
import queue

# 全局日志队列（线程安全）
LOG_QUEUE: "queue.Queue[logging.LogRecord]" = queue.Queue(maxsize=10000)

# 提供给 NamespaceManager 使用的统一 logger
def get_ns_logger() -> logging.Logger:
    logger = logging.getLogger("NamespaceManager")
    logger.setLevel(logging.DEBUG)   # 放宽等级
    logger.propagate = False
    # 只绑定一次 QueueHandler
    if not any(isinstance(h, logging.handlers.QueueHandler) for h in logger.handlers):
        logger.addHandler(logging.handlers.QueueHandler(LOG_QUEUE))
    return logger
