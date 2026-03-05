# -*- coding: utf-8 -*-
"""
utils.py - 公共函数库
供其他脚本 import 使用
"""

import json
import os
import tempfile
from datetime import datetime, timezone, timedelta
from urllib.parse import quote, unquote

# 基础路径配置
BASE_DIR = "E:/myVault/AgentInbox/myClipper"
CLIPPINGS_DIR = os.path.join(BASE_DIR, "clippings")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
INDEX_PATH = os.path.join(BASE_DIR, "index.json")
TAGS_POOL_PATH = os.path.join(BASE_DIR, "tags_pool.json")

VAULT_NAME = "myVault"
FILE_PREFIX = "AgentInbox/myClipper/clippings"


def atomic_write_json(filepath: str, data) -> None:
    """
    原子写入 JSON 文件：先写入临时文件，再用 os.replace() 替换。
    确保在写入失败时不会损坏原文件。
    
    Args:
        filepath: 目标文件路径
        data: 要写入的 JSON 数据
    
    Raises:
        IOError: 写入失败时抛出
    """
    # 获取目标文件的目录
    dir_name = os.path.dirname(filepath) or "."
    
    # 创建临时文件（在同一目录下，确保 rename 原子性）
    fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # 原子替换
        os.replace(temp_path, filepath)
    except Exception as e:
        # 清理临时文件
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise IOError(f"原子写入失败: {e}")


def load_json(filepath: str, default=None):
    """
    加载 JSON 文件，文件不存在时返回默认值。
    
    Args:
        filepath: JSON 文件路径
        default: 文件不存在时返回的默认值
    
    Returns:
        解析后的 JSON 数据，或默认值
    """
    if not os.path.exists(filepath):
        return default
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析错误 ({filepath}): {e}")
    except Exception as e:
        raise IOError(f"读取文件失败 ({filepath}): {e}")


def encode_obsidian_uri(file_name: str) -> str:
    """
    生成 Obsidian URI。
    
    Args:
        file_name: 文件名（不含 .md 后缀）
    
    Returns:
        obsidian://open?vault=myVault&file=AgentInbox%2FmyClipper%2Fclippings%2F{URL编码的file_name}
    """
    # URL 编码文件名（中文会被编码）
    encoded_name = quote(file_name, safe='')
    # 构建完整路径
    full_path = f"{FILE_PREFIX}/{encoded_name}"
    # 构建 URI
    uri = f"obsidian://open?vault={VAULT_NAME}&file={quote(full_path, safe='')}".replace('%2F', '/')
    return uri


def decode_file_name_from_uri(uri: str) -> str:
    """
    从 Obsidian URI 中提取并解码文件名（不含路径前缀和 .md 后缀）。
    
    Args:
        uri: Obsidian URI，如 obsidian://open?vault=myVault&file=AgentInbox%2FmyClipper%2Fclippings%2Fxxx
    
    Returns:
        解码后的文件名（不含 .md 后缀）
    """
    # 解析 URI 参数
    if "?" not in uri:
        return ""
    
    query = uri.split("?", 1)[1]
    params = {}
    for param in query.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)
            params[key] = unquote(value)
    
    file_path = params.get("file", "")
    if not file_path:
        return ""
    
    # 移除前缀路径
    prefix = f"{FILE_PREFIX}/"
    if file_path.startswith(prefix):
        file_name = file_path[len(prefix):]
    else:
        # 尝试从最后一个 / 提取
        file_name = file_path.split("/")[-1]
    
    # URL 解码
    return unquote(file_name)


def get_today_date() -> str:
    """
    返回东八区今天的日期。
    
    Returns:
        YYYY-MM-DD 格式的日期字符串
    """
    tz = timezone(timedelta(hours=8))  # 东八区
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d")


def validate_date_format(date_str: str) -> bool:
    """
    验证日期字符串格式是否为 YYYY-MM-DD。
    
    Args:
        date_str: 日期字符串
    
    Returns:
        格式正确返回 True，否则返回 False
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def ensure_dir_exists(dir_path: str) -> None:
    """
    确保目录存在，不存在则创建。
    
    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def print_json_response(data: dict) -> None:
    """
    以 JSON 格式输出响应到 stdout。
    
    Args:
        data: 要输出的字典数据
    """
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_error(message: str, exit_code: int = 1) -> None:
    """
    输出错误信息到 stderr 并退出程序。
    
    Args:
        message: 错误信息
        exit_code: 退出码
    """
    import sys
    error_response = {"status": "error", "message": message}
    print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
    sys.exit(exit_code)
