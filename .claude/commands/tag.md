---
description: 标签管理（离线），查看/增加/删除/重命名标签池
argument-hint: [add|delete|rename] [entity|topic] [name] [new_name]
---

执行标签管理操作。参数：$ARGUMENTS

根据参数判断操作：

无参数 → 列出所有 tag：
PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/manage_tags.py --action list

add <entity|topic> <name> → 添加 tag：
PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/manage_tags.py --action add --category "$1" --name "$2"

delete <name> → 删除 tag（不改 index.json 和 .md）：
PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/manage_tags.py --action delete --name "$1"

rename <old> <new> → 重命名（同步更新 index.json，不改 .md）：
PYTHONIOENCODING=utf-8 python E:/myVault/AgentInbox/myClipper/scripts/manage_tags.py --action rename --name "$1" --new_name "$2"