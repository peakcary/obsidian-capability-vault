---
type: index
tags:
  - skills
---

# Codex Skill 索引

Obsidian 保存能力来源、证据和设计；实际 Skill 安装在用户确认的位置，并通过 `skill-creator` 创建和验证。

```dataview
TABLE WITHOUT ID
  file.link AS "能力",
  status AS "状态",
  skill_path AS "安装路径",
  last_verified AS "最近验证"
FROM "capabilities"
WHERE contains(list("skill-candidate", "skill"), status)
SORT file.name ASC
```

## 晋级检查

- [ ] 至少两次独立成功执行
- [ ] 输入、输出和触发语句明确
- [ ] 工具和环境前提明确
- [ ] 验证步骤可重复
- [ ] 失败模式和回退方案明确
- [ ] 不包含密码、令牌或私人原始数据
- [ ] 已确认 Skill 安装位置
- [ ] 已运行 `quick_validate.py`
