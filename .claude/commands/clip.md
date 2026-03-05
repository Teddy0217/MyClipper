---
description: 链接剪报（联网），读取URL或粘贴正文，扩展搜索，生成阅读稿
argument-hint: [URL1 URL2... 或留空等待粘贴正文]
---

执行链接剪报任务。参数：$ARGUMENTS

流程：

1. 内容获取
   - 若有 URL：尝试read_url读取正文。失败则告知用户手动粘贴。多 URL 逐个读取，视为同一话题多信源。
   - 若无参数：等待用户粘贴正文。

2. 扩展搜索（中英双语必搜）
   使用 web_search_exa：
   - 第一轮：中文关键词
   - 第二轮：英文关键词
   - 可追加第三轮补充反方观点
   对高价值搜索结果调用 fetch_markdown 深读。

3. 提取 metadata
   先获取 tag 池：
   PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/manage_tags.py --action list
   从内容中提取 tag（遵循【Tag 体系铁律】），推断 event_date，生成文件名。

4. 生成阅读稿，格式如下：

---
date: YYYY-MM-DD
event_date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
type: clipping
created_by: newsClipper
---

# 文件名（不含.md）

## ⚡ TLDR
一到两句话极简总结。

## 📰 核心事实
- 按重要度排列的关键事实
- 每条标注信源 [来源名](URL)
- 实体用 [[双链]] 包裹

## 🌐 背景上下文
这件事为什么重要？前因后果？

## 🔭 观点光谱
| 立场   | 来源 | 核心论点 |
| ------ | ---- | -------- |
| 🟢 支持 | ...  | ...      |
| 🟡 中立 | ...  | ...      |
| 🔴 反对 | ...  | ...      |
（信源不足时注明"单一信源，观点光谱暂缺"）

## ✏️ 批注
> 用户批注或"暂无批注"

5. 预览确认（遵循【预览确认铁律】）

6. 保存（遵循【保存操作标准流程】，type 为 clipping）

7. 回复：文件名 + tag + obsidian:// 链接