---
description: 剪报回溯（离线），搜索已有剪报
argument-hint: <关键词1> [关键词2 关键词3...]
---

执行剪报回溯查询（离线）。参数：$ARGUMENTS

流程：

1. 搜索：
   PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/search_index.py --keywords "$ARGUMENTS" --limit 10
   多关键词取交集。

2. 展示结果，格式同 /topic 的输出。

3. 若无结果：告知用户无匹配，询问是否要用 /clip 联网搜索该话题。

4. 若用户要查看某条详情：
   PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/read_clipping.py --file_name "文件名"