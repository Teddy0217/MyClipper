# -*- coding: utf-8 -*-
"""
search_index.py - 搜索剪报索引
根据关键词搜索 index.json 中的记录
"""

import argparse
import json
import os
import sys

# 添加脚本所在目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    INDEX_PATH,
    load_json,
    decode_file_name_from_uri,
    print_json_response,
    print_error
)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="搜索剪报索引")
    parser.add_argument("--keywords", required=True, help="空格分隔的关键词，如 '特朗普 贸易战'")
    parser.add_argument("--limit", type=int, default=10, help="最大返回条数，默认 10")
    return parser.parse_args()


def match_keywords(record: dict, keywords: list) -> bool:
    """
    检查记录是否匹配所有关键词（交集）。
    
    匹配范围：
    - tags 数组中的任意 tag
    - 从 URI 解码出的文件名
    
    匹配规则：不区分大小写
    
    Args:
        record: 索引记录
        keywords: 关键词列表
    
    Returns:
        所有关键词都匹配返回 True，否则返回 False
    """
    # 获取 tags 数组
    tags = record.get("tags", [])
    tags_lower = [str(t).lower() for t in tags]
    
    # 从 URI 解码文件名
    uri = record.get("file", "")
    file_name = decode_file_name_from_uri(uri)
    file_name_lower = file_name.lower()
    
    # 检查每个关键词
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # 检查是否在 tags 中
        in_tags = any(keyword_lower in tag for tag in tags_lower)
        
        # 检查是否在文件名中
        in_file_name = keyword_lower in file_name_lower
        
        # 当前关键词必须至少在一个地方匹配
        if not (in_tags or in_file_name):
            return False
    
    return True


def sort_by_event_date(records: list) -> list:
    """
    按 event_date 降序排列（最新的在前）。
    
    Args:
        records: 记录列表
    
    Returns:
        排序后的记录列表
    """
    def get_event_date(record):
        date_str = record.get("event_date", "")
        # 空日期排到最后
        if not date_str:
            return "0000-00-00"
        return date_str
    
    return sorted(records, key=get_event_date, reverse=True)


def search_index(keywords_str: str, limit: int) -> list:
    """
    搜索索引的主函数。
    
    Args:
        keywords_str: 空格分隔的关键词字符串
        limit: 最大返回条数
    
    Returns:
        匹配的记录列表
    """
    # 解析关键词（空格分隔）
    keywords = [k.strip() for k in keywords_str.split() if k.strip()]
    
    if not keywords:
        print_error("关键词不能为空", exit_code=1)
    
    # 加载索引
    index_data = load_json(INDEX_PATH, default=[])
    
    if not index_data:
        return []
    
    # 筛选匹配的记录
    matched_records = []
    for record in index_data:
        if match_keywords(record, keywords):
            matched_records.append(record)
    
    # 按 event_date 降序排列
    matched_records = sort_by_event_date(matched_records)
    
    # 截取 limit 条
    return matched_records[:limit]


def main():
    """主入口函数"""
    try:
        args = parse_args()
        
        # 验证 limit 参数
        if args.limit <= 0:
            print_error("limit 必须大于 0", exit_code=1)
        
        # 执行搜索
        results = search_index(args.keywords, args.limit)
        
        # 输出结果（直接输出数组）
        print(json.dumps(results, ensure_ascii=False, indent=2))
        sys.exit(0)
        
    except SystemExit:
        raise
    except Exception as e:
        error_response = {"status": "error", "message": f"搜索失败: {str(e)}"}
        print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
