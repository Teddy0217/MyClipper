---
description: 话题时间线（离线），从已有剪报中按tag筛选并按时间排列
argument-hint: <tag1> [tag2 tag3...]
---

执行话题时间线查询（离线，不联网）。参数：$ARGUMENTS

流程：

1. 获取 tag 池：
   PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/manage_tags.py --action list
   对用户输入的关键词做模糊匹配。匹配不确定时调用 ask_user 列出候选。

2. 搜索匹配剪报：
   PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/search_index.py --keywords "$ARGUMENTS" --limit 50
   多 tag 取交集，结果已按 event_date 排序。

3. 直接在回复中列出，不生成文件，不做二次创作。格式：

📅 「tag1」+「tag2」时间线（共 N 条）

1. 2026-01-15 — 文件名
   🏷️ tag1 / tag2 / tag3
   📂 [打开](obsidian://open?vault=myVault&file=...)

2. 2026-02-03 — 文件名
   🏷️ tag1 / tag2
   📂 [打开](obsidian://open?vault=myVault&file=...)

4. 若无结果：告知用户无匹配剪报，建议使用 /clip 先收集。