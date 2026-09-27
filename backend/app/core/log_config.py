import sys
from pathlib import Path

from loguru import logger

from app.config.path_conf import BASE_DIR

# 日志目录：基于项目根目录（backend/），而不是"当前工作目录"。
# 之前写的是相对路径 "../../log/blog_log.log"，它取决于进程的工作目录（cwd）：
#   - 从 backend/ 启动 -> backend/../log -> 项目根/log（跑到项目外面去了）
#   - 从 backend/app 启动 -> 又是另一个位置
# 更严重的是 loguru 会主动创建目录，一旦该目录不可写就抛 PermissionError；
# 而这个模块被 exceptions.py 顶层导入，等于"导入即崩"，整个应用起不来。
LOG_DIR = BASE_DIR / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    LOG_DIR / "blog_log.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
    level="INFO",
    rotation="10 MB",
    retention="14 days",
    encoding="utf-8",
)

# 同时也输出到控制台，否则本地开发和 systemd 的 journalctl 里什么都看不到
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)
