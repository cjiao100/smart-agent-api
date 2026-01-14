import logging
import os

def get_logger(name: str) -> logging.Logger:
    """创建并返回一个日志记录器"""

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename=os.path.join("logs", "app.log"),
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    )

    return logging.getLogger(name)