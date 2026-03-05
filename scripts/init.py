# -*- coding: utf-8 -*-
"""
init.py - 初始化脚本
创建目录结构和初始数据文件
"""

import os
import sys

# 添加脚本所在目录到路径，确保可以导入 utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    CLIPPINGS_DIR,
    LOGS_DIR,
    SCRIPTS_DIR,
    INDEX_PATH,
    TAGS_POOL_PATH,
    ensure_dir_exists,
    atomic_write_json,
    print_json_response
)


def init():
    """
    初始化目录和数据文件。
    
    创建以下目录（若不存在）：
    - clippings/    # 剪报文件存放目录
    - logs/         # 运行日志
    - scripts/      # 脚本目录
    
    创建以下文件（若不存在，不覆盖已有文件）：
    - index.json    # 剪报索引，初始内容 []
    - tags_pool.json # 标签池，初始内容 {"entity": [], "topic": []}
    """
    created_items = []
    existing_items = []
    
    # 创建目录
    dirs_to_create = [
        (CLIPPINGS_DIR, "剪报目录"),
        (LOGS_DIR, "日志目录"),
    ]
    
    for dir_path, desc in dirs_to_create:
        if not os.path.exists(dir_path):
            ensure_dir_exists(dir_path)
            created_items.append(desc)
        else:
            existing_items.append(desc)
    
    # 创建 index.json（若不存在）
    if not os.path.exists(INDEX_PATH):
        atomic_write_json(INDEX_PATH, [])
        created_items.append("索引文件 (index.json)")
    else:
        existing_items.append("索引文件 (index.json)")
    
    # 创建 tags_pool.json（若不存在）
    if not os.path.exists(TAGS_POOL_PATH):
        atomic_write_json(TAGS_POOL_PATH, {"entity": [], "topic": []})
        created_items.append("标签池文件 (tags_pool.json)")
    else:
        existing_items.append("标签池文件 (tags_pool.json)")
    
    # 构建响应消息
    if created_items and existing_items:
        message = f"初始化完成。新建: {', '.join(created_items)}; 已存在: {', '.join(existing_items)}"
    elif created_items:
        message = f"初始化完成。新建: {', '.join(created_items)}"
    else:
        message = "所有文件已存在，无需初始化"
    
    return {"status": "ok", "message": message}


def main():
    """主入口函数"""
    try:
        result = init()
        print_json_response(result)
        sys.exit(0)
    except Exception as e:
        error_response = {"status": "error", "message": f"初始化失败: {str(e)}"}
        print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    import json
    main()
