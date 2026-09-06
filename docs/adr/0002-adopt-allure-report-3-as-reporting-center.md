---
status: accepted
date: 2026-09-06
---

# 以 Allure Report 3 作为报告中心

## Context

ADR-0001 已决定分离 pytest 权威结果、业务报告与目标专属诊断证据，但当时设计了 AutoUI `@business_step`，让一次业务步骤声明同时生成 Allure step 与 Playwright Trace group，并预留 Result Manifest。进一步验证表明，Allure Report 3 已能承担业务步骤、环境聚合、历史、Known Issues、Quality Gate、多阶段汇总和报告展示；Playwright Trace 也可以作为其识别的标准附件进入对应测试项。

业务步骤与 Trace action 面向不同读者、表达不同粒度。维持步骤级映射会引入当前 Web Context 绑定、嵌套栈和异常降级等生命周期复杂度，却不会提高测试结果的权威性或 Trace 的诊断能力。

## Decision

- pytest 继续产生唯一权威 Test Outcome。
- Business Flow 直接使用 Allure 原生 `@allure.step` 描述数量不固定的业务步骤；删除 AutoUI 自定义 `business_step` Module。
- Page Object 只封装产品页面能力，不依赖 Allure、pytest runtime 或 Trace。
- pytest-playwright 负责采集 Playwright Trace；AutoUI 在测试项级别以 `application/vnd.allure.playwright-trace` 媒体类型附加 `trace.zip`，不建立 Allure step 与 Trace group 的映射。
- Allure Report 3 优先负责业务报告、环境、历史、Known Issues、Quality Gate、多阶段汇总和报告展示。当前使用 Allure 3 Awesome UI；未来平台优先复用或内嵌报告，并从测试项进入目标专属 Viewer。
- 性能观测保持独立，不要求与业务步骤或 Trace action 建立时间关联。
- Result Manifest 不作为预设必备 Module。只有未来平台出现 Allure 标准产物无法表达的真实运行关联需求时，才设计最小契约。

本决定取代 ADR-0001 中关于自定义 `@business_step`、步骤级 Allure/Trace 映射和预设 Result Manifest 的内容；ADR-0001 的其余职责分离原则继续有效。

## Considered Options

### 保留自定义 `@business_step` 并同步 Trace group

优点是两个 Viewer 可以显示同名分组。缺点是浅封装需要承担跨工具生命周期、当前 Context、嵌套与异常降级，维护成本高于它隐藏的业务复杂度。

### 自建统一事件模型与平台报告

能够完全控制展示，但会重复实现 Allure 3 和 Playwright Trace 已有的数据模型、历史与查看能力，并让执行路径同时维护三套语义。

## Consequences

- Business Flow 依赖 Allure 的公开步骤 Interface；这是有意接受的直接依赖。
- Allure 和 Trace 只在同一个 pytest 测试项上关联，二者的步骤数量和层级可以不同。
- Python 侧需维护一个窄的 Allure pytest Integration Module，负责稳定 labels 与产物附件，不负责业务步骤。
- Allure Report 3 作为 Node 工具链独立锁定；Python 测试依赖仍由 Python 依赖文件管理。
- 默认 Trace Viewer 需要加载 `trace.playwright.dev`；公司网络不可访问时，由后续平台提供内部托管 Viewer，不改变本 ADR 的产物边界。
