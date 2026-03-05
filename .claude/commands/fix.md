---
description: 索引维护（离线），检查索引健康度并修复问题
argument-hint:
---

执行索引健康检查。

1. 执行检查：
   PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/fix_index.py

2. 解读报告：
   - orphan_index（孤立索引：index有记录但.md不存在）→ ask_user 确认后手动删除条目
   - orphan_files（孤立文件：.md存在但index无记录）→ ask_user 确认后从 frontmatter 重建条目
   - missing_tags（index中的tag不在pool中）→ 自动补入 tags_pool
   - missing_dates（event_date缺失）→ 告知用户需手动补充

   所有修改操作需 ask_user 确认后执行。