---
description: 知识存档（离线），保存用户粘贴的文本或文件，不联网搜索
argument-hint: （无参数，等待用户粘贴内容）
---

## 流程（严格按序执行，禁止跳步）

1. 等待用户粘贴文本或发送文件。

2. 【必须先执行】提取 metadata：
   - 调用 manage_tags.py --action list 获取 tag 池
   - 确定文件名（YYYYMMDD-简要中文）
   - 提取 tag，推断 event_date

3. 【必须执行 tool call】复制原文副本：

   - 如果用户提供的是粘贴文本, 则用 Bash 将用户原文以 markdown 格式写入：
     E:/myVault/AgentInbox/myClipper/clippings/save/{文件名}.md
     比如: cat << 'ENDOFFILE' > "E:/myVault/AgentInbox/myClipper/clippings/save/test.md"
     [这里填入用户提供的完整原始文本]
     ENDOFFILE
   - 如果用户提供的文件, 则将该文件复制到E:/myVault/AgentInbox/myClipper/clippings/save/ , 比如:
     cp "C:\Users\Administrator\Desktop\中美地缘政治与AI博弈论综述.md" "E:/myVault/AgentInbox/myClipper/clippings/save/20260227-中美AI博弈论综述.md"

4. 生成存档稿，原文链接使用步骤3已保存的文件路径：
   obsidian://open?vault=myVault&file=AgentInbox%2FmyClipper%2Fclippings%2Fsave%2F{URL编码的文件名}
   ⚠️ 如果步骤3未成功保存，此处标注"原文未自动保存，请手动归档"。


   存档稿，格式如下：

---
date: YYYY-MM-DD
event_date: YYYY-MM-DD
tags: [tag1, tag2]
type: archive

created_by: newsClipper
---

# 文件名（不含.md）

## 📄 原文
用户原文简要归纳总结，轻度 markdown 格式化, 附上原文的链接便于访问, 形如: [原文链接](obsidian://open?vault=myVault&file=AgentInbox%2FmyClipper%2Fclippings%2Fsave%2Ftest)。

## 🏷️ 归档说明
一句话说明 tag 选择理由和内容核心价值。

## ✏️ 批注
> 用户批注或"暂无批注"

4. 预览确认（遵循【预览确认铁律】）

5. 保存（遵循【保存操作标准流程】，type 为 archive）注意, 这里的保存和步骤3的保存不要混淆, 步骤3是保存原文副本, 这里是保存存档稿. 

6. 回复：文件名 + tag + obsidian:// 链接