# -*- coding: utf-8 -*-
"""
save_clipping.py - 保存剪报元数据
验证 .md 文件存在，更新 index.json 和 tags_pool.json
"""

import argparse
import json
import os
import sys
from urllib.parse import unquote, quote  # 修改：引入 quote，夺回编码控制权

# 添加脚本所在目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    CLIPPINGS_DIR,
    INDEX_PATH,
    TAGS_POOL_PATH,
    encode_obsidian_uri,
    get_today_date,
    validate_date_format,
    load_json,
    atomic_write_json,
    print_json_response,
    print_error
)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="保存剪报元数据到索引")
    parser.add_argument("--file_name", required=True, help="文件名（不含.md），如 '20260227-标题'")
    parser.add_argument("--tags", required=True, help="逗号分隔的 tag 列表，如 'UCI,神经科学,脊髓损伤 治疗'")
    parser.add_argument("--tag_types", required=True, help="逗号分隔的类别，与 tags 一一对应，如 'entity,topic,topic'")
    parser.add_argument("--type", required=True, choices=["clipping", "archive"], help="类型: clipping 或 archive")
    parser.add_argument("--event_date", required=True, help="事件发生日期，YYYY-MM-DD 格式")
    parser.add_argument("--user_comment", default="", help="用户批注（可选）")
    return parser.parse_args()


def validate_params(args) -> tuple:
    """
    验证参数有效性。
    
    Returns:
        (tags_list, tag_types_list) 元组
    
    Raises:
        SystemExit: 参数无效时退出程序（exit code 1）
    """
    # 验证 file_name 不为空
    if not args.file_name or not args.file_name.strip():
        print_error("file_name 不能为空", exit_code=1)
    
    # 验证 event_date 格式
    if not validate_date_format(args.event_date):
        print_error(f"event_date 格式错误: {args.event_date}，应为 YYYY-MM-DD", exit_code=1)
    
    # 解析 tags 和 tag_types
    # 使用 '_'.join(t.split()) 的技巧：
    # 1. 自动去除首尾空格
    # 2. 如果中间有连续的多个空格，也能被优雅地合并为一个下划线（避免 "a   b" 变成 "a___b"）
    tags_list = ['_'.join(t.split()) for t in args.tags.split(",") if t.strip()]
    tag_types_list = [t.strip() for t in args.tag_types.split(",") if t.strip()]
    
    # 验证数量一致
    if len(tags_list) != len(tag_types_list):
        print_error(
            f"tags 和 tag_types 数量不匹配: tags={len(tags_list)}, tag_types={len(tag_types_list)}",
            exit_code=1
        )
    
    # 验证每个 tag_type 必须是 entity 或 topic
    valid_types = {"entity", "topic"}
    for i, tt in enumerate(tag_types_list):
        if tt not in valid_types:
            print_error(f"tag_types 第 {i+1} 项 '{tt}' 无效，必须是 entity 或 topic", exit_code=1)
    
    # 注意：此处已根据要求移除了 tags 数量不能超过 5 个的限制。
    
    return tags_list, tag_types_list


def check_md_file_exists(file_name: str) -> str:
    """
    检查 .md 文件是否存在。
    
    Args:
        file_name: 文件名（不含 .md）
    
    Returns:
        完整的文件路径
    
    Raises:
        SystemExit: 文件不存在时退出程序（exit code 1）
    """
    md_path = os.path.join(CLIPPINGS_DIR, f"{file_name}.md")
    if not os.path.exists(md_path):
        print_error(f"文件不存在，请先写入 .md 文件: {md_path}", exit_code=1)
    return md_path


def check_duplicate(index_data: list, uri: str) -> bool:
    """
    检查索引中是否已存在同名条目。
    
    Args:
        index_data: 当前索引数据
        uri: 要检查的 URI
    
    Returns:
        存在返回 True，否则返回 False
    """
    for item in index_data:
        if item.get("file") == uri:
            return True
    return False


def update_index(index_data: list, uri: str, event_date: str, tags: list, clip_type: str) -> list:
    """
    向索引中添加新条目。
    
    Args:
        index_data: 当前索引数据
        uri: Obsidian URI
        event_date: 事件发生日期
        tags: 标签列表
        clip_type: 类型（clipping 或 archive）
    
    Returns:
        更新后的索引数据
    """
    new_entry = {
        "file": uri,
        "date": get_today_date(),
        "event_date": event_date,
        "tags": tags,
        "type": clip_type
    }
    index_data.append(new_entry)
    return index_data


def update_tags_pool(tags_pool: dict, tags: list, tag_types: list) -> dict:
    """
    更新标签池。
    
    Args:
        tags_pool: 当前标签池数据
        tags: 标签列表
        tag_types: 标签类型列表（与 tags 一一对应）
    
    Returns:
        更新后的标签池数据
    """
    for tag, tag_type in zip(tags, tag_types):
        category_list = tags_pool.get(tag_type, [])
        
        # 查找是否已存在
        found = False
        for item in category_list:
            if item.get("name") == tag:
                item["count"] = item.get("count", 0) + 1
                found = True
                break
        
        # 不存在则新增
        if not found:
            category_list.append({"name": tag, "count": 1})
        
        tags_pool[tag_type] = category_list
    
    return tags_pool


def rollback_index(old_index_data: list) -> None:
    """
    回滚索引到之前的状态。
    
    Args:
        old_index_data: 回滚前的索引数据
    """
    try:
        atomic_write_json(INDEX_PATH, old_index_data)
    except Exception:
        # 回滚失败，记录到 stderr
        print("警告: 回滚 index.json 失败", file=sys.stderr)


def save_clipping(file_name: str, tags: list, tag_types: list, 
                  clip_type: str, event_date: str, user_comment: str = ""):
    """
    保存剪报元数据的主函数。
    """
    # 步骤 2: 验证 .md 文件存在
    md_path = check_md_file_exists(file_name)
    
    # 步骤 3: 生成 obsidian:// URI 【核心修复区】
    # 批判性绕过：鉴于 utils.py 中的 encode_obsidian_uri 对中文存在致命的二次编码 Bug
    # 我们采用“占位符注入”策略，只白嫖它的基础路径模板，自己掌控 URL 编码。
    template_uri = encode_obsidian_uri("__PLACEHOLDER__")
    
    # 我们自己用标准的 urllib.parse.quote 对干净的中文名进行【单次】安全编码
    safe_encoded_name = quote(file_name)
    
    # 将安全编码后的名字注入回模板，彻底斩断乱码的祸根
    uri = template_uri.replace("__PLACEHOLDER__", safe_encoded_name)
    
    # 步骤 4: 原子更新 index.json
    try:
        index_data = load_json(INDEX_PATH, default=[])
        
        # 检查是否已有同名条目
        if check_duplicate(index_data, uri):
            print_error(f"索引中已存在同名条目: {file_name}", exit_code=1)
        
        # 保存旧数据用于可能的回滚
        old_index_data = json.loads(json.dumps(index_data))  # 深拷贝
        
        # 更新索引
        index_data = update_index(index_data, uri, event_date, tags, clip_type)
        atomic_write_json(INDEX_PATH, index_data)
        
    except Exception as e:
        print_error(f"更新 index.json 失败: {str(e)}", exit_code=2)
    
    # 步骤 5: 更新 tags_pool.json（带回滚机制）
    try:
        tags_pool = load_json(TAGS_POOL_PATH, default={"entity": [], "topic": []})
        tags_pool = update_tags_pool(tags_pool, tags, tag_types)
        atomic_write_json(TAGS_POOL_PATH, tags_pool)
    except Exception as e:
        # 回滚 index.json
        rollback_index(old_index_data)
        print_error(f"更新 tags_pool.json 失败，已回滚 index.json: {str(e)}", exit_code=2)
    
    # 返回成功结果
    return {
        "status": "ok",
        "file": f"clippings/{file_name}.md",
        "obsidian_uri": uri
    }


def main():
    """主入口函数"""
    try:
        args = parse_args()
        
        # 🚀 边界防御核心逻辑 1：反编码 URL
        clean_file_name = unquote(args.file_name.strip())
        
        # 🚀 边界防御核心逻辑 2：鲁棒性处理，智能剥离后缀
        # 如果用户（或者自动化脚本）不小心传入了带有 .md 的文件名，在这里直接砍掉，防止变成 .md.md
        if clean_file_name.lower().endswith('.md'):
            clean_file_name = clean_file_name[:-3]
        
        # 将清洗后的值覆盖回去，以防后续函数用到 args.file_name
        args.file_name = clean_file_name
        
        # 步骤 1: 参数校验
        tags_list, tag_types_list = validate_params(args)
        
        # 执行保存操作
        result = save_clipping(
            file_name=clean_file_name,
            tags=tags_list,
            tag_types=tag_types_list,
            clip_type=args.type,
            event_date=args.event_date,
            user_comment=args.user_comment
        )
        
        print_json_response(result)
        sys.exit(0)
        
    except SystemExit:
        raise
    except Exception as e:
        error_response = {"status": "error", "message": f"未知错误: {str(e)}"}
        print(json.dumps(error_response, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()