# -*- coding: utf-8 -*-
"""
fix_index.py - 索引健康检查
检查孤立索引、孤立文件、缺失标签、缺失日期等问题
"""

import glob
import json
import os
import sys

# 添加脚本所在目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    CLIPPINGS_DIR,
    INDEX_PATH,
    TAGS_POOL_PATH,
    load_json,
    decode_file_name_from_uri,
    print_json_response
)


def get_all_md_files() -> set:
    """
    获取 clippings 目录下所有 .md 文件名（不含路径和扩展名）。
    
    Returns:
        文件名集合
    """
    md_files = set()
    pattern = os.path.join(CLIPPINGS_DIR, "*.md")
    
    for file_path in glob.glob(pattern):
        # 获取文件名（不含扩展名）
        base_name = os.path.basename(file_path)
        file_name = os.path.splitext(base_name)[0]
        md_files.add(file_name)
    
    return md_files


def get_indexed_file_names(index_data: list) -> set:
    """
    从索引中提取所有文件名（不含路径和扩展名）。
    
    Args:
        index_data: 索引数据
    
    Returns:
        文件名集合
    """
    indexed_files = set()
    
    for record in index_data:
        uri = record.get("file", "")
        file_name = decode_file_name_from_uri(uri)
        if file_name:
            indexed_files.add(file_name)
    
    return indexed_files


def get_all_tags_in_pool(tags_pool: dict) -> set:
    """
    获取标签池中所有标签名称。
    
    Args:
        tags_pool: 标签池数据
    
    Returns:
        标签名称集合
    """
    all_tags = set()
    
    for category in ["entity", "topic"]:
        if category in tags_pool:
            for item in tags_pool[category]:
                tag_name = item.get("name")
                if tag_name:
                    all_tags.add(tag_name)
    
    return all_tags


def get_all_tags_in_index(index_data: list) -> set:
    """
    获取索引中使用的所有标签。
    
    Args:
        index_data: 索引数据
    
    Returns:
        标签名称集合
    """
    all_tags = set()
    
    for record in index_data:
        tags = record.get("tags", [])
        for tag in tags:
            if tag:
                all_tags.add(tag)
    
    return all_tags


def get_files_with_missing_dates(index_data: list) -> list:
    """
    获取缺失 event_date 的文件名列表。
    
    Args:
        index_data: 索引数据
    
    Returns:
        文件名列表
    """
    missing_dates = []
    
    for record in index_data:
        event_date = record.get("event_date")
        uri = record.get("file", "")
        file_name = decode_file_name_from_uri(uri)
        
        # 检查 event_date 是否为空或缺失
        if not event_date or not str(event_date).strip():
            if file_name:
                missing_dates.append(file_name)
    
    return missing_dates


def check_health() -> dict:
    """
    执行健康检查。
    
    检查项：
    a. 孤立索引：index.json 中有记录但对应 .md 文件不存在
    b. 孤立文件：clippings/ 下有 .md 但 index.json 中无对应记录
    c. 缺失标签：index.json 中出现的 tag 不在 tags_pool.json 中
    d. 缺失日期：index.json 中 event_date 为空或缺失的条目
    
    Returns:
        检查结果字典
    """
    # 加载数据
    index_data = load_json(INDEX_PATH, default=[])
    tags_pool = load_json(TAGS_POOL_PATH, default={"entity": [], "topic": []})
    
    # 获取文件集合
    md_files = get_all_md_files()
    indexed_files = get_indexed_file_names(index_data)
    
    # a. 孤立索引：在索引中但不在文件系统中
    orphan_index = sorted(list(indexed_files - md_files))
    
    # b. 孤立文件：在文件系统中但不在索引中
    orphan_files = sorted(list(md_files - indexed_files))
    
    # c. 缺失标签
    pool_tags = get_all_tags_in_pool(tags_pool)
    index_tags = get_all_tags_in_index(index_data)
    missing_tags = sorted(list(index_tags - pool_tags))
    
    # d. 缺失日期
    missing_dates = get_files_with_missing_dates(index_data)
    
    # 判断健康状态
    is_healthy = (
        len(orphan_index) == 0 and
        len(orphan_files) == 0 and
        len(missing_tags) == 0 and
        len(missing_dates) == 0
    )
    
    status = "healthy" if is_healthy else "issues_found"
    
    return {
        "status": status,
        "orphan_index": orphan_index,
        "orphan_files": orphan_files,
        "missing_tags": missing_tags,
        "missing_dates": missing_dates
    }


def main():
    """主入口函数"""
    try:
        result = check_health()
        print_json_response(result)
        
        # 健康时返回 0，有问题返回 0 但 status 不同
        sys.exit(0)
        
    except Exception as e:
        error_response = {"status": "error", "message": f"健康检查失败: {str(e)}"}
        print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
