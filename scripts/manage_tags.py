# -*- coding: utf-8 -*-
"""
manage_tags.py - 标签池管理
支持 list/add/delete/rename 操作
"""

import argparse
import json
import os
import sys

# 添加脚本所在目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    INDEX_PATH,
    TAGS_POOL_PATH,
    load_json,
    atomic_write_json,
    print_json_response,
    print_error
)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="管理标签池")
    parser.add_argument("--action", required=True, 
                       choices=["list", "add", "delete", "rename"],
                       help="操作类型: list | add | delete | rename")
    parser.add_argument("--category", help="类别: entity 或 topic（add 时必填）")
    parser.add_argument("--name", help="标签名称（add/delete/rename 时必填）")
    parser.add_argument("--new_name", help="新标签名称（rename 时必填）")
    return parser.parse_args()


def validate_params(args) -> None:
    """
    验证参数有效性。
    
    Raises:
        SystemExit: 参数无效时退出程序（exit code 1）
    """
    valid_categories = {"entity", "topic"}
    
    if args.action == "add":
        if not args.category:
            print_error("add 操作需要 --category 参数", exit_code=1)
        if args.category not in valid_categories:
            print_error(f"category 必须是 entity 或 topic，当前: {args.category}", exit_code=1)
        if not args.name or not args.name.strip():
            print_error("add 操作需要 --name 参数", exit_code=1)
    
    elif args.action == "delete":
        if not args.name or not args.name.strip():
            print_error("delete 操作需要 --name 参数", exit_code=1)
    
    elif args.action == "rename":
        if not args.name or not args.name.strip():
            print_error("rename 操作需要 --name 参数", exit_code=1)
        if not args.new_name or not args.new_name.strip():
            print_error("rename 操作需要 --new_name 参数", exit_code=1)


def sort_tags_pool(tags_pool: dict) -> dict:
    """
    对标签池中的每个类别按 count 降序排列。
    
    Args:
        tags_pool: 标签池数据
    
    Returns:
        排序后的标签池数据
    """
    result = {}
    for category in ["entity", "topic"]:
        if category in tags_pool:
            sorted_list = sorted(
                tags_pool[category],
                key=lambda x: x.get("count", 0),
                reverse=True
            )
            result[category] = sorted_list
        else:
            result[category] = []
    return result


def find_tag_in_pool(tags_pool: dict, name: str) -> tuple:
    """
    在标签池中查找标签。
    
    Args:
        tags_pool: 标签池数据
        name: 标签名称
    
    Returns:
        (category, index) 元组，未找到返回 (None, -1)
    """
    for category in ["entity", "topic"]:
        if category in tags_pool:
            for i, item in enumerate(tags_pool[category]):
                if item.get("name") == name:
                    return category, i
    return None, -1


def tag_exists_anywhere(tags_pool: dict, name: str) -> bool:
    """
    检查标签是否存在于任意类别中。
    
    Args:
        tags_pool: 标签池数据
        name: 标签名称
    
    Returns:
        存在返回 True，否则返回 False
    """
    category, _ = find_tag_in_pool(tags_pool, name)
    return category is not None


def action_list() -> dict:
    """
    列出所有标签。
    
    Returns:
        排序后的标签池数据
    """
    tags_pool = load_json(TAGS_POOL_PATH, default={"entity": [], "topic": []})
    return sort_tags_pool(tags_pool)


def action_add(category: str, name: str) -> dict:
    """
    添加新标签。
    
    Args:
        category: 类别（entity 或 topic）
        name: 标签名称
    
    Returns:
        操作结果字典
    
    Raises:
        SystemExit: 标签已存在或写入失败
    """
    tags_pool = load_json(TAGS_POOL_PATH, default={"entity": [], "topic": []})
    
    # 检查是否已存在（任意类别）
    if tag_exists_anywhere(tags_pool, name):
        print_error(f"标签 '{name}' 已存在", exit_code=1)
    
    # 添加到指定类别
    if category not in tags_pool:
        tags_pool[category] = []
    
    tags_pool[category].append({"name": name, "count": 0})
    
    try:
        atomic_write_json(TAGS_POOL_PATH, tags_pool)
    except Exception as e:
        print_error(f"写入 tags_pool.json 失败: {str(e)}", exit_code=2)
    
    return {"status": "ok", "message": f"标签 '{name}' 已添加到 {category}"}


def action_delete(name: str) -> dict:
    """
    删除标签。
    注意：不修改 index.json 和 .md 文件。
    
    Args:
        name: 标签名称
    
    Returns:
        操作结果字典
    
    Raises:
        SystemExit: 标签不存在或写入失败
    """
    tags_pool = load_json(TAGS_POOL_PATH, default={"entity": [], "topic": []})
    
    # 查找标签
    category, index = find_tag_in_pool(tags_pool, name)
    
    if category is None:
        print_error(f"标签 '{name}' 不存在", exit_code=1)
    
    # 从对应类别中删除
    tags_pool[category].pop(index)
    
    try:
        atomic_write_json(TAGS_POOL_PATH, tags_pool)
    except Exception as e:
        print_error(f"写入 tags_pool.json 失败: {str(e)}", exit_code=2)
    
    return {"status": "ok", "message": f"标签 '{name}' 已从 {category} 中删除"}


def action_rename(name: str, new_name: str) -> dict:
    """
    重命名标签。
    同步更新 index.json 中所有 tags 数组。
    注意：不修改 .md 文件。
    
    Args:
        name: 原标签名称
        new_name: 新标签名称
    
    Returns:
        操作结果字典
    
    Raises:
        SystemExit: 标签不存在、新名称已存在或写入失败
    """
    # 加载数据
    tags_pool = load_json(TAGS_POOL_PATH, default={"entity": [], "topic": []})
    index_data = load_json(INDEX_PATH, default=[])
    
    # 检查原标签是否存在
    category, index = find_tag_in_pool(tags_pool, name)
    if category is None:
        print_error(f"标签 '{name}' 不存在", exit_code=1)
    
    # 检查新名称是否已存在
    if tag_exists_anywhere(tags_pool, new_name):
        print_error(f"新标签名 '{new_name}' 已存在", exit_code=1)
    
    # 在 tags_pool 中重命名
    old_count = tags_pool[category][index].get("count", 0)
    tags_pool[category][index]["name"] = new_name
    
    # 在 index.json 中同步更新
    updated_count = 0
    for record in index_data:
        tags = record.get("tags", [])
        if name in tags:
            # 替换为新的标签名
            record["tags"] = [new_name if t == name else t for t in tags]
            updated_count += 1
    
    # 原子写入
    try:
        atomic_write_json(TAGS_POOL_PATH, tags_pool)
    except Exception as e:
        print_error(f"写入 tags_pool.json 失败: {str(e)}", exit_code=2)
    
    try:
        atomic_write_json(INDEX_PATH, index_data)
    except Exception as e:
        # 尝试回滚 tags_pool
        try:
            tags_pool[category][index]["name"] = name
            atomic_write_json(TAGS_POOL_PATH, tags_pool)
        except Exception:
            pass
        print_error(f"写入 index.json 失败，已回滚 tags_pool: {str(e)}", exit_code=2)
    
    return {
        "status": "ok", 
        "message": f"标签 '{name}' 已重命名为 '{new_name}'，更新了 {updated_count} 条索引记录"
    }


def main():
    """主入口函数"""
    try:
        args = parse_args()
        
        # 验证参数
        validate_params(args)
        
        # 执行对应操作
        if args.action == "list":
            result = action_list()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        elif args.action == "add":
            result = action_add(args.category, args.name.strip())
            print_json_response(result)
        
        elif args.action == "delete":
            result = action_delete(args.name.strip())
            print_json_response(result)
        
        elif args.action == "rename":
            result = action_rename(args.name.strip(), args.new_name.strip())
            print_json_response(result)
        
        sys.exit(0)
        
    except SystemExit:
        raise
    except Exception as e:
        error_response = {"status": "error", "message": f"操作失败: {str(e)}"}
        print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
