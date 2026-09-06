---
status: accepted
date: 2026-09-03
---

# 分离测试执行、公共结果与产物查看

AutoUI 先建设可靠的桌面 Web 自动化框架，未来再逐步接入移动 Web、移动 App、桌面 App 和测试平台。各测试目标拥有独立业务用例，只共享执行、配置、公共结果和产物管理能力；不建立统一跨端 Driver，也不要求不同目标产生统一的详细操作事件流。

测试框架提供权威测试结果以及结果与产物的稳定关联。Allure 作为面向人的业务报告，Playwright Trace 作为桌面 Web 的专属诊断证据；未来的 App、桌面 App 和性能观测使用各自适合的产物及查看方式。测试平台统一展示公共结果摘要，并可在同一使用体验中内嵌这些彼此隔离的 Viewer，但不解析或重建 Viewer 的内部数据模型。性能观测后置建设，且不与 Trace action 建立时间联动。

业务步骤由目标专属的 Business Flow 通过 AutoUI `@business_step` 装饰器声明一次；装饰器使用 Allure 的公开步骤 Interface 生成业务报告，并在桌面 Web 执行上下文中使用 Playwright 的公开 Trace Interface 建立同名 group。Page Object 不记录业务步骤，测试代码也不重复声明 Allure 与 Trace。

选择这种方向，是为了同时保留平台扩展性和专业工具的诊断能力，避免当前 `自定义详细事件 + Allure + Trace` 同步写入同一业务执行路径所造成的重复语义、生命周期耦合和维护负担。Result Manifest 的字段、现有 JSONL 的迁移方式以及 Viewer 的具体嵌入技术均属于后续设计，不在本 ADR 中决定。

## 后继决定

[ADR-0002](./0002-adopt-allure-report-3-as-reporting-center.md) 延续本 ADR 对执行、业务报告与目标专属诊断证据的职责分离，同时取代其中“自定义 `@business_step` 映射 Allure step 与 Trace group”的实现决定，并明确 Result Manifest 不再作为预设必备 Module。
