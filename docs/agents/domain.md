# 领域文档

工程技能在探索代码库时，应按照以下规则读取本项目的领域文档。

## 开始探索前读取

- 如果根目录存在 `CONTEXT.md`，读取它；或者
- 如果根目录存在 `CONTEXT-MAP.md`，读取它指向的、与当前主题相关的各个 `CONTEXT.md`；
- 读取与当前工作区域相关的 `docs/adr/` 中的 ADR。在 multi-context 仓库中，还要检查对应 context 下的 `src/<context>/docs/adr/`。

如果这些文件不存在，静默继续即可。不要专门提示它们缺失，也不要提前建议创建。`/domain-modeling` skill（由 `/grill-with-docs` 和 `/improve-codebase-architecture` 使用）会在真正解决术语或架构决策时按需创建这些文件。

## 文件结构

本仓库采用 single-context 布局（大多数仓库都适用）：

```text
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

如果以后变成 multi-context，布局如下：

```text
/
├── CONTEXT-MAP.md                  ← 指向各个 context 的 CONTEXT.md
├── docs/adr/                       ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/               ← ordering 专属决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用术语表中的词汇

在 Issue 标题、重构提案、假设或测试名称中命名领域概念时，使用 `CONTEXT.md` 定义的术语。如果需要的概念尚未出现在术语表中，这通常说明：要么正在创造项目没有使用的语言（应重新考虑），要么项目确实存在领域术语缺口，应记录给 `/domain-modeling`。

## 标记 ADR 冲突

如果输出内容与现有 ADR 冲突，应明确指出，而不是静默覆盖：

> _与 ADR-0007（event-sourced orders）冲突，但值得重新讨论，因为……_
