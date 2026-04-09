"""环境配置加载。"""

import os
from pathlib import Path

# 默认配置文件路径：脚本所在目录的 .env 文件
DEFAULT_ENV_FILE = Path(__file__).parent / ".env"

# 必需变量
REQUIRED_VARS = ["USER_MAIL", "TOKEN"]
# 可选变量
OPTIONAL_VARS = ["DEFALT_PIPELINE_ID"]
ALL_VARS = REQUIRED_VARS + OPTIONAL_VARS


def load_env(env_file: str | None = None) -> dict:
    """从配置文件加载配置，环境变量作为回退。

    优先级：
    1. 显式指定的 env_file（必须存在）
    2. ~/.env（如果存在）
    3. 环境变量（补充缺失值）

    Args:
        env_file: 配置文件路径。如果指定则必须存在。

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 指定的配置文件不存在
    """
    config = {}
    path = Path(env_file) if env_file else DEFAULT_ENV_FILE

    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    if key.startswith("export "):
                        key = key[7:].strip()
                    config[key] = value.strip().strip('"').strip("'")
    elif env_file:
        raise FileNotFoundError(f"配置文件未找到: {path}")

    # 用环境变量补充缺失值
    for var in ALL_VARS:
        if var not in config and var in os.environ:
            config[var] = os.environ[var]

    return config


def validate_config(config: dict) -> list:
    """验证配置是否包含所有必需变量。

    Args:
        config: 配置字典

    Returns:
        验证错误列表（空表示有效）
    """
    errors = []

    for var in REQUIRED_VARS:
        if var not in config or not config[var]:
            errors.append(f"缺少必需变量: {var}")

    return errors
