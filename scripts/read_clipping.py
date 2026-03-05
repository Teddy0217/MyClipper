# -*- coding: utf-8 -*-
"""
read_clipping.py - 读取剪报内容
读取指定 .md 文件的全部内容
"""

import argparse
import json
import os
import sys

# 添加脚本所在目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    CLIPPINGS_DIR,
    print_json_response,
    print_error
)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="读取剪报文件内容")
    parser.add_argument("--file_name", required=True, help="文件名（不含.md）")
    return parser.parse_args()


def read_clipping(file_name: str) -> dict:
    """
    读取剪报文件内容。
    
    Args:
        file_name: 文件名（不含 .md 后缀）
    
    Returns:
        包含文件内容的字典
    
    Raises:
        SystemExit: 文件不存在时退出程序（exit code 1）
    """
    # 构建完整文件路径
    md_path = os.path.join(CLIPPINGS_DIR, f"{file_name}.md")
    
    # 检查文件是否存在
    if not os.path.exists(md_path):
        print_error(f"文件不存在: {md_path}", exit_code=1)
    
    # 读取文件内容
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print_error(f"读取文件失败: {str(e)}", exit_code=2)
    
    return {
        "status": "ok",
        "content": content
    }


def main():
    """主入口函数"""
    try:
        args = parse_args()
        
        # 验证 file_name 不为空
        if not args.file_name or not args.file_name.strip():
            print_error("file_name 不能为空", exit_code=1)
        
        # 读取文件
        result = read_clipping(args.file_name.strip())
        
        print_json_response(result)
        sys.exit(0)
        
    except SystemExit:
        raise
    except Exception as e:
        error_response = {"status": "error", "message": f"读取失败: {str(e)}"}
        print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
