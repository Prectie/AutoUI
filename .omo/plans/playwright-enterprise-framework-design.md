# Playwright 企业级自动化测试框架设计

## TL;DR
> **Summary**: 当前仓库是一个小型 Python `pytest-playwright` 框架，具备基础 UI 自动化能力，但距离企业级可维护、可扩展、易使用、低耦合高内聚还有明显差距。目标设计采用“分层架构 + 显式契约 + 可观测执行 + CI 质量门禁”的 pytest-playwright 企业框架模型。
> **Deliverables**:
> - 当前框架成熟度评估
> - 企业级目标架构蓝图
> - 推荐目录结构与层边界
> - fixture / POM / data / config / reporting / CI 策略
> - 质量门禁、执行命令、风险控制与未来扩展边界
> **Effort**: Medium
> **Parallel**: YES - 3 waves
> **Critical Path**: 架构契约 → fixture/config/data 分层 → CI/reporting/治理标准

## Context

### Original Request
用户需要评估当前 Playwright 框架是否具有企业级的高可维护性、高可扩展性、高可使用性，并且是否遵循低耦合高内聚原则；不局限于当前框架，输出一版更好的框架设计。

### Interview Summary
- 交付深度：仅架构设计，不输出完整迁移实施计划。
- 改造策略：允许重构式升级。
- 文档语言：中文为主；`fixture`、`Page Object Model`、`trace`、`sharding`、`CI` 等中文不好描述的词保留英文。
- 设计优先级：稳定可观测、易用规范、并发扩展、可维护低耦合高内聚全部覆盖。
- 默认假设：面向中大型 QA/研发混合团队、多环境、CI 并行执行，未来可扩展到 UI + API hybrid testing。

### Research Summary
当前仓库关键文件：
- `pyproject.toml`：pytest 入口、`testpaths`、浏览器/截图/trace/headed 参数。
- `conftest.py`：通过 `pytest_plugins` 注册共享 fixture。
- `Fixtures/browser_fixture.py`：当前 browser context/page fixture 与 base URL 设置。
- `Pages/order_console_page.py`：单一 Page Object，使用语义 locator。
- `Tests/test_demo.py`：数据驱动示例测试。
- `Core/data_loader.py`：YAML 加载工具。
- `Config/settings.py`：硬编码环境配置。
- `Data/demo.yaml`：单体测试数据文件。
- `requirements.txt`：已有 `pytest-playwright`、`pytest-xdist`、`pytest-rerunfailures`、`allure-pytest` 等依赖。
- `Readme.md`：空文件，存在使用文档缺口。

### Metis Review (gaps addressed)
- 保持架构设计范围，不把本文档变成完整迁移 backlog。
- 严格基于 Python `pytest-playwright`，不套用 Node Playwright Test 架构。
- 区分“企业级基线”与“未来增强能力”。
- 明确不在范围、质量门禁、执行命令、artifact 安全、并发数据冲突、fixture 隐式状态等边界。

## Work Objectives

### Core Objective
设计一个企业级 Python `pytest-playwright` 自动化测试框架，使测试代码具备：
- 高可维护性：职责分离、依赖方向清晰、变更影响范围可控。
- 高可扩展性：支持多环境、多浏览器、并行、分组、未来 UI+API 扩展。
- 高可使用性：测试作者只关注业务动作和断言，框架提供统一入口、模板、文档和命令。
- 低耦合高内聚：测试、fixture、页面对象、数据、配置、报告各自独立，禁止跨层泄漏。
- 稳定可观测：失败时自动保留 trace/screenshot/video/log/report，并能快速定位原因。

### Current Maturity Assessment
| 维度 | 当前状态 | 企业级判断 | 主要证据 |
|---|---|---|---|
| 可维护性 | 初级 | 不达标 | 仅有单一 POM 示例，config/data/fixture 边界尚未成体系 |
| 可扩展性 | 初级 | 不达标 | 无 tags、sharding、parallel policy、环境矩阵、CI 策略 |
| 可使用性 | 初级 | 不达标 | README 为空，无命令规范、测试模板、贡献规范 |
| 低耦合高内聚 | 部分具备 | 不稳定 | Page Object 初步分离，但配置硬编码、YAML import-time 加载、fixture 扩展边界不清晰 |
| 稳定可观测 | 部分具备 | 不达标 | trace/screenshot 已启用，但无报告发布、日志关联、artifact 留存与脱敏策略 |

### Target Architecture: 分层模型
目标框架采用 8 层结构，自上而下依赖，禁止下层反向依赖上层：

1. **Test Layer**：只描述业务场景、marker、测试数据引用、断言意图。
2. **Flow / Task Layer**：封装跨页面业务流程，如登录、下单、查询订单。
3. **Page / Component Layer**：封装页面与组件动作；集中 locator；不读取环境，不管理数据，不启动浏览器。
4. **Fixture Layer**：统一管理 browser/context/page、登录态、trace/video、artifact、test metadata。
5. **Data Layer**：提供测试数据 schema、factory、seed、cleanup；不在 import 阶段加载大型 YAML。
6. **Config Layer**：统一读取环境、浏览器、base URL、账号、feature flags、超时、artifact 策略。
7. **Observability Layer**：统一日志、Allure/JUnit/HTML、trace/screenshot/video、失败归因。
8. **Execution Layer**：统一本地/CI 命令、marker、xdist、rerun、sharding、质量门禁。

### Recommended Directory Structure
```text
autoui/
  config/                 # 环境配置、schema、secrets 引用，不放真实密钥
  fixtures/               # pytest-playwright fixture 分层
  pages/                  # Page Object / Component Object
  flows/                  # 业务流程编排，复用 pages/components
  data/
    schemas/              # 测试数据 schema
    factories/            # 动态数据 factory
    static/               # 小规模静态测试数据
  clients/                # Optional: API client / service client
  assertions/             # 业务断言 helper，避免断言散落
  observability/          # logger、report adapter、artifact policy
  utils/                  # 纯函数工具，禁止依赖 Playwright page/context
tests/
  smoke/
  regression/
  e2e/
  visual/                 # Optional advanced capability
docs/
  framework-guide.md
  authoring-guide.md
  troubleshooting.md
```

说明：这是目标设计结构，不要求本计划阶段立即实施。若未来执行，应按现有仓库命名逐步落地或一次性重构到小写目录。

### Required Baseline Architecture
- 使用 `pytest-playwright` 作为唯一 runner 基线。
- `browser` 允许 session scope；`context/page` 默认 function scope，保障隔离。
- 所有环境参数通过 Config Layer 读取，不允许测试文件直接读取硬编码 base URL / account / timeout。
- Page Object 只封装页面交互与 locator，不负责测试数据准备、不负责环境判断、不负责跨业务流程编排。
- Flow Layer 负责编排多页面业务动作，防止 Page Object 变成 god class。
- 测试数据必须有 schema；大型 YAML 不允许 import-time 全量加载。
- 所有测试必须有 marker：至少 `smoke`、`regression`、`e2e`、`critical`、`flaky`、`serial`。
- CI 默认 headless；失败保留 trace + screenshot；video 作为高价值场景或失败重跑时启用。
- 报告必须至少输出 JUnit XML；推荐 Allure 作为可视化报告；trace/video/screenshot 作为受控 artifact 上传。
- 质量门禁包含 `pytest --collect-only`、lint、typecheck、marker 校验、artifact 生成校验。

### Recommended Enterprise Upgrades
- 引入 `pytest-xdist`：默认 `-n auto`，对共享状态场景使用 `serial` marker 或 group 策略。
- 引入 `pytest-rerunfailures`：仅对标记为 `flaky` 的测试启用有限重试，禁止全局无差别重试掩盖缺陷。
- 使用 `pydantic` 或等价 schema 工具校验 config/data。
- 使用 `ruff` 统一 lint/format；使用 `mypy` 或 `pyright` 做关键层 typecheck。
- 使用 Allure labels/steps/attachments 关联业务模块、测试数据 ID、trace、screenshot、log。
- 为测试作者提供场景模板、Page Object 模板、数据 factory 模板、命令清单。

### Optional Future Enhancements
- API client / service client 层，用于 UI 前置数据准备、状态校验、cleanup。
- Visual regression：只对稳定页面区域启用，避免全量截图导致维护成本暴涨。
- Contract testing / DB validation：只在业务需要时作为独立能力接入。
- 测试治理 dashboard：统计 flaky rate、失败分类、平均修复时间、耗时趋势。

### 不在本次架构设计范围内
- 不直接修改源代码或测试代码。
- 不生成完整迁移实施 backlog。
- 不切换到 Node Playwright Test。
- 不强制引入 API/DB/visual/contract testing 作为基线。
- 不设计真实密钥管理方案细节，只定义框架侧引用和脱敏原则。

### Definition of Done (verifiable conditions with commands)
- [ ] 设计文档存在：`Test-Path -LiteralPath ".omo\plans\playwright-enterprise-framework-design.md"`
- [ ] 文档以中文为主，英文技术术语仅在必要处保留。
- [ ] 文档包含当前评估、目标架构、目录结构、层边界、fixture 策略、POM 策略、数据/配置策略、并发/重试/tag 策略、报告/CI 策略、质量门禁、范围边界。
- [ ] 文档明确区分 baseline、recommended upgrade、optional future enhancement。
- [ ] 文档不包含 Node Playwright Test 专属架构作为主方案。

### Must Have
- 当前框架企业级成熟度评估。
- 一版明确的目标框架分层架构。
- 可执行命令示例。
- artifact 安全与可观测策略。
- 低耦合高内聚规则。

### Must NOT Have
- 不将 fixture 设计成隐藏全局状态中心。
- 不将 Page Object 设计成同时负责数据、断言、流程、环境的 god class。
- 不使用全局 sleep 作为等待策略。
- 不让 retry 掩盖真实缺陷。
- 不让 trace/video/log 泄露敏感信息。

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: architecture-only design; future implementation应采用 tests-after + framework quality gates。
- QA policy: 每个未来执行任务都包含 agent-executed 场景。
- Evidence: `.omo/evidence/task-{N}-{slug}.{ext}`

建议未来实现后的核心命令：
```bash
pytest --collect-only
pytest -m smoke --browser chromium -n auto --tracing retain-on-failure
pytest -m "regression and not flaky" --browser chromium --browser firefox -n auto
pytest --last-failed --failed-first
ruff check .
mypy autoui tests
```

## Execution Strategy

### Parallel Execution Waves
Wave 1: 架构契约与配置/fixture 基线（Tasks 1-3）
Wave 2: Page/Flow/Data/Execution 策略（Tasks 4-6）
Wave 3: Observability/UX/Governance 与验收（Tasks 7-8）

### Dependency Matrix (full, all tasks)
| Task | Blocked By | Blocks |
|---|---|---|
| 1 架构契约 | none | 2,3,4,5,6,7,8 |
| 2 Config/Env | 1 | 3,5,6,7 |
| 3 Fixture 生命周期 | 1,2 | 4,6,7 |
| 4 POM/Flow 边界 | 1,3 | 8 |
| 5 Data 策略 | 1,2 | 6,8 |
| 6 并发/marker/retry | 2,3,5 | 7,8 |
| 7 Reporting/CI 可观测 | 2,3,6 | 8 |
| 8 Usability/Governance | 4,5,6,7 | final verification |

### Agent Dispatch Summary
| Wave | Task Count | Categories |
|---|---:|---|
| 1 | 3 | deep, unspecified-high |
| 2 | 3 | deep, unspecified-high |
| 3 | 2 | writing, unspecified-high |

## TODOs
> Implementation + Test = ONE task. Never separate.
> 这些 TODO 是未来执行该架构设计时的高层任务，不是本次规划阶段的代码改动。

- [ ] 1. 定义框架架构契约与依赖方向

  **What to do**: 产出架构契约：8 层模型、依赖方向、禁止跨层调用规则、baseline/recommended/optional 分类；明确 Python `pytest-playwright` 为主方案。
  **Must NOT do**: 不引入 Node Playwright Test 作为主架构；不写具体业务测试代码。

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: 需要架构推理和约束定义。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 本任务不需要浏览器交互。

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 2,3,4,5,6,7,8 | Blocked By: none

  **References**:
  - Pattern: `Fixtures/browser_fixture.py` - 当前 fixture 基线。
  - Pattern: `Pages/order_console_page.py` - 当前 POM 基线。
  - External: `https://playwright.dev/python/docs/test-runners` - pytest fixture 模型。

  **Acceptance Criteria**:
  - [ ] 架构契约列出每层职责、允许依赖、禁止依赖。
  - [ ] 明确 baseline / recommended / optional 三类能力。
  - [ ] 明确“架构设计，不实施代码”的范围。

  **QA Scenarios**:
  ```
  Scenario: 架构边界完整
    Tool: Bash
    Steps: Search the design artifact for "Target Architecture", "Required Baseline Architecture", "Optional Future Enhancements", "不在本次架构设计范围内".
    Expected: All sections exist exactly once and mention Python pytest-playwright.
    Evidence: .omo/evidence/task-1-architecture-contract.txt

  Scenario: 防止 Node runner 混入主方案
    Tool: Bash
    Steps: Search for "Node Playwright Test" and inspect surrounding text.
    Expected: It appears only as out-of-scope/non-primary wording, not as the main runner.
    Evidence: .omo/evidence/task-1-node-runner-guard.txt
  ```

  **Commit**: YES | Message: `docs(architecture): define playwright framework contracts` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 2. 设计 Config/Env/Secrets 策略

  **What to do**: 定义配置来源优先级：CLI/env vars → environment profile → default config；定义 base URL、browser、viewport、locale、timezone、account、timeout、artifact policy 的 schema；说明 secrets 只引用不落盘。
  **Must NOT do**: 不保存真实账号密码；不让测试文件直接读取硬编码配置。

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: 需要结合测试执行和安全策略。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 不需要 UI 操作。

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 3,5,6,7 | Blocked By: 1

  **References**:
  - Pattern: `Config/settings.py` - 当前硬编码配置风险来源。
  - External: `https://playwright.dev/python/docs/test-runners` - CLI/fixture 参数约束。

  **Acceptance Criteria**:
  - [ ] 配置策略包含环境、浏览器、账号、超时、artifact、feature flags。
  - [ ] 明确配置读取优先级和 secrets 脱敏原则。
  - [ ] 明确测试代码禁止直接依赖具体环境值。

  **QA Scenarios**:
  ```
  Scenario: 配置项覆盖完整
    Tool: Bash
    Steps: Verify the config section contains base URL, browser, viewport, locale, timezone, account, timeout, artifact policy.
    Expected: Every required config class is mentioned.
    Evidence: .omo/evidence/task-2-config-coverage.txt

  Scenario: Secrets 不落盘
    Tool: Bash
    Steps: Search for "真实密码", "secret", "token", "脱敏" in the design section.
    Expected: Document states secrets are referenced from CI/env/secret manager and masked in logs/artifacts.
    Evidence: .omo/evidence/task-2-secret-policy.txt
  ```

  **Commit**: YES | Message: `docs(config): define env and secret strategy` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 3. 设计 fixture 生命周期与隔离模型

  **What to do**: 定义 `browser` session scope、`context/page` function scope、`new_context` 多用户场景、登录态 fixture、artifact fixture、marker-driven context options。
  **Must NOT do**: 不在 fixture 中隐藏业务流程；不让 fixture 持有跨测试可变状态。

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: fixture 生命周期直接影响稳定性、并发和低耦合。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 架构设计阶段无需真实浏览器。

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4,6,7 | Blocked By: 1,2

  **References**:
  - Pattern: `Fixtures/browser_fixture.py` - 当前 fixture 入口。
  - External: `https://playwright.dev/python/docs/browser-contexts` - BrowserContext 隔离。
  - External: `https://playwright.dev/python/docs/test-runners` - pytest-playwright fixture。

  **Acceptance Criteria**:
  - [ ] 明确 browser/context/page/new_context 的 scope 和用途。
  - [ ] 明确登录态、artifact、marker options 的 fixture 边界。
  - [ ] 明确禁止 fixture 隐式共享业务状态。

  **QA Scenarios**:
  ```
  Scenario: 生命周期定义完整
    Tool: Bash
    Steps: Verify fixture section mentions browser=session, context/page=function, new_context=multi-user.
    Expected: All lifecycle rules are explicit.
    Evidence: .omo/evidence/task-3-fixture-lifecycle.txt

  Scenario: 隐式状态风险被约束
    Tool: Bash
    Steps: Search fixture section for "隐藏全局状态" and "跨测试可变状态".
    Expected: Both are explicitly forbidden.
    Evidence: .omo/evidence/task-3-fixture-state-guard.txt
  ```

  **Commit**: YES | Message: `docs(fixtures): define lifecycle and isolation model` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 4. 设计 Page/Object、Component、Flow 边界

  **What to do**: 定义 Page Object 只做页面动作和 locator；Component Object 处理复用组件；Flow 处理跨页面业务流程；Assertions 层处理业务断言。
  **Must NOT do**: 不让 Page Object 读取测试数据、环境变量或执行 cleanup；不让测试直接散落复杂 locator。

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: 低耦合高内聚核心设计。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 不需要浏览器交互。

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8 | Blocked By: 1,3

  **References**:
  - Pattern: `Pages/order_console_page.py` - 当前 POM 示例。
  - External: `https://playwright.dev/python/docs/pom` - POM 官方定位。
  - External: `https://playwright.dev/python/docs/locators` - 语义 locator 推荐。

  **Acceptance Criteria**:
  - [ ] 明确 Page / Component / Flow / Assertions 四者职责。
  - [ ] 明确 locator 优先级：role/label/test_id/text > CSS/XPath。
  - [ ] 明确禁止 god class。

  **QA Scenarios**:
  ```
  Scenario: POM 边界清晰
    Tool: Bash
    Steps: Verify section contains Page Object, Component Object, Flow Layer, Assertions Layer.
    Expected: Each has responsibilities and forbidden responsibilities.
    Evidence: .omo/evidence/task-4-pom-boundaries.txt

  Scenario: Locator 策略可执行
    Tool: Bash
    Steps: Verify locator priority mentions get_by_role/get_by_label/get_by_test_id and CSS/XPath fallback.
    Expected: Priority order is explicit.
    Evidence: .omo/evidence/task-4-locator-policy.txt
  ```

  **Commit**: YES | Message: `docs(pom): define page component flow boundaries` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 5. 设计 Data Layer 与并发安全数据策略

  **What to do**: 定义 static data、factory data、seeded account、cleanup、schema validation、test data ID；禁止 import-time 大型 YAML 加载；定义并行 worker 数据隔离策略。
  **Must NOT do**: 不让多个并发测试共用可变账号/订单/客户数据；不把数据准备塞入 Page Object。

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: 数据策略影响并行稳定性和可维护性。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 不需要浏览器交互。

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 6,8 | Blocked By: 1,2

  **References**:
  - Pattern: `Data/demo.yaml` - 当前单体 YAML 数据。
  - Pattern: `Core/data_loader.py` - 当前 YAML loader。

  **Acceptance Criteria**:
  - [ ] 明确三类数据：static、factory、seeded accounts。
  - [ ] 明确 schema validation 和 cleanup policy。
  - [ ] 明确 xdist worker 隔离与数据命名规则。

  **QA Scenarios**:
  ```
  Scenario: 数据分类完整
    Tool: Bash
    Steps: Verify data section mentions static data, factory data, seeded accounts, cleanup, schema validation.
    Expected: All required data categories exist.
    Evidence: .omo/evidence/task-5-data-taxonomy.txt

  Scenario: 并发数据冲突有防护
    Tool: Bash
    Steps: Verify data section mentions worker_id/test_id namespacing or equivalent isolation.
    Expected: Parallel data conflict prevention is explicit.
    Evidence: .omo/evidence/task-5-parallel-data-isolation.txt
  ```

  **Commit**: YES | Message: `docs(data): define schema and parallel data strategy` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 6. 设计 marker、parallel、sharding、retry 策略

  **What to do**: 定义 marker taxonomy、默认并行命令、serial/group 场景、flaky 标记准入、rerun 限制、失败优先本地调试命令。
  **Must NOT do**: 不启用全局无条件 retry；不让共享状态测试默认并行。

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: 需要兼顾速度、稳定性和失败诊断。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 不需要浏览器交互。

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 7,8 | Blocked By: 2,3,5

  **References**:
  - External: `https://pytest-xdist.readthedocs.io/en/stable/distribution.html` - xdist 分发策略。
  - External: `https://docs.pytest.org/en/stable/how-to/cache.html` - failed-first/last-failed。

  **Acceptance Criteria**:
  - [ ] 定义 `smoke/regression/e2e/critical/flaky/serial` marker。
  - [ ] 定义 `pytest -m smoke --browser chromium -n auto` 等目标命令。
  - [ ] 定义 CI sharding：`SHARD_INDEX`、`SHARD_TOTAL`、manifest/hash 分配、report merge、artifact 命名。
  - [ ] 定义 retry 只服务 flaky 管控，不掩盖真实失败。

  **QA Scenarios**:
  ```
  Scenario: Marker 分类可用
    Tool: Bash
    Steps: Run `pwsh -NoProfile -Command "Select-String -Path '.omo/plans/playwright-enterprise-framework-design.md' -Pattern 'smoke','regression','e2e','critical','flaky','serial'"`.
    Expected: Command returns matches for all six markers in the execution strategy.
    Evidence: .omo/evidence/task-6-marker-taxonomy.txt

  Scenario: Sharding 策略可执行
    Tool: Bash
    Steps: Run `pwsh -NoProfile -Command "Select-String -Path '.omo/plans/playwright-enterprise-framework-design.md' -Pattern 'SHARD_INDEX','SHARD_TOTAL','manifest','hash','report merge','junit-shard','allure-results/shard'"`.
    Expected: Command returns matches proving the design covers CI shard inputs, deterministic allocation, report merge, and shard-specific artifacts.
    Evidence: .omo/evidence/task-6-sharding-policy.txt

  Scenario: Retry 不掩盖缺陷
    Tool: Bash
    Steps: Run `pwsh -NoProfile -Command "Select-String -Path '.omo/plans/playwright-enterprise-framework-design.md' -Pattern '全局无条件 retry','flaky','失败 nodeid'"`.
    Expected: Command returns matches showing global unconditional retry is forbidden and rerun is limited to flaky governance or failed nodeids.
    Evidence: .omo/evidence/task-6-retry-guard.txt
  ```

  **Commit**: YES | Message: `docs(execution): define marker parallel retry strategy` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 7. 设计 Reporting、Observability、CI Artifact 策略

  **What to do**: 定义 JUnit XML、Allure、trace/screenshot/video/log 产物、失败分类、artifact retention、脱敏、CI upload、headless/Xvfb 策略。
  **Must NOT do**: 不上传包含密钥/个人敏感信息的 trace/video/log；不无限期保留大型 artifact。

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: 涉及 CI、可观测性和安全边界。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 不需要浏览器交互。

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 8 | Blocked By: 2,3,6

  **References**:
  - Pattern: `nb_log_config.py` - 当前日志配置入口。
  - Pattern: `test-results/.../trace.zip` - 当前 trace artifact 示例。
  - External: `https://playwright.dev/python/docs/ci` - CI 指南。
  - External: `https://playwright.dev/python/docs/trace-viewer` - trace 诊断。
  - External: `https://playwright.dev/python/docs/videos` - video artifact。

  **Acceptance Criteria**:
  - [ ] 报告策略包含 JUnit XML + Allure + trace/screenshot/video/log。
  - [ ] 明确 artifact retention 和脱敏策略。
  - [ ] 明确 CI 中 headless 默认、headed Linux 需 Xvfb。

  **QA Scenarios**:
  ```
  Scenario: 可观测产物完整
    Tool: Bash
    Steps: Verify observability section mentions JUnit XML, Allure, trace, screenshot, video, log.
    Expected: All artifact types are covered with retention guidance.
    Evidence: .omo/evidence/task-7-observability-artifacts.txt

  Scenario: Artifact 安全边界明确
    Tool: Bash
    Steps: Verify observability section mentions sensitive data, masking, retention, upload permissions.
    Expected: Security and retention rules are explicit.
    Evidence: .omo/evidence/task-7-artifact-security.txt
  ```

  **Commit**: YES | Message: `docs(observability): define reporting and artifact policy` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

- [ ] 8. 设计开发者体验、文档与治理规范

  **What to do**: 定义 README、authoring guide、troubleshooting、PR checklist、命名规范、测试模板、Page Object 模板、数据模板、review gates。
  **Must NOT do**: 不用口头约定替代文档和自动检查；不把规范写成无法执行的愿望清单。

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: 需要清晰中文文档结构和治理规范。
  - Skills: [] - 不需要额外技能。
  - Omitted: [`playwright`] - 不需要浏览器交互。

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: final verification | Blocked By: 4,5,6,7

  **References**:
  - Pattern: `Readme.md` - 当前文档缺口。
  - Pattern: `Tests/test_demo.py` - 当前测试作者体验示例。

  **Acceptance Criteria**:
  - [ ] 明确至少三份文档：framework guide、authoring guide、troubleshooting。
  - [ ] 明确 PR checklist 和 review gates。
  - [ ] 明确命名规范与模板清单。

  **QA Scenarios**:
  ```
  Scenario: 文档体系完整
    Tool: Bash
    Steps: Verify usability section mentions framework guide, authoring guide, troubleshooting, PR checklist.
    Expected: Each document has purpose and target user.
    Evidence: .omo/evidence/task-8-doc-system.txt

  Scenario: 规范可执行
    Tool: Bash
    Steps: Verify governance section mentions lint/typecheck/collect-only/marker validation as gates.
    Expected: Governance is backed by executable checks, not only prose.
    Evidence: .omo/evidence/task-8-governance-gates.txt
  ```

  **Commit**: YES | Message: `docs(governance): define authoring and review standards` | Files: [`.omo/plans/playwright-enterprise-framework-design.md`]

## Detailed Design Decisions

### 1. Config Layer
配置必须从测试代码中剥离。目标读取顺序：
1. CLI 参数 / pytest option。
2. 环境变量 / CI secrets。
3. 环境 profile：`dev`、`test`、`staging`、`prod-readonly`。
4. 默认配置。

必须覆盖：`base_url`、`browser`、`headless`、`viewport`、`locale`、`timezone`、`timeout`、`account_pool`、`artifact_policy`、`feature_flags`。

### 2. Fixture Layer
- `browser`: session scope，复用浏览器进程。
- `context`: function scope，每个测试隔离。
- `page`: function scope，仅由 context 创建。
- `new_context`: 多用户/多角色场景使用。
- `authenticated_context`: 可选 fixture，只负责提供登录态，不执行业务流程。
- `artifact_context`: 统一收集 trace/screenshot/video/log。

禁止：fixture 执行业务流程、跨测试共享可变对象、在 fixture 中吞掉异常。

### 3. Page / Component / Flow Layer
- Page Object：封装页面元素和页面级动作。
- Component Object：封装可复用组件，如弹窗、表格、导航栏。
- Flow：封装跨页面业务流程。
- Assertions：封装业务断言，避免测试文件散落复杂判断。

Locator 优先级：`get_by_role` / `get_by_label` / `get_by_test_id` / `get_by_text` > CSS > XPath。XPath 只能作为最后 fallback，并需要说明原因。

### 4. Data Layer
数据分三类：
- Static data：少量稳定枚举和只读数据。
- Factory data：每个测试/worker 动态生成，避免冲突。
- Seeded accounts：预置账号池，按 worker 或 test id 分配。

并发规则：所有可变数据必须包含 `worker_id` 或唯一 test run id；cleanup 必须可重复执行；数据 schema 校验失败应在测试执行前暴露。

### 5. Execution Layer
推荐命令：
```bash
pytest -m smoke --browser chromium -n auto --tracing retain-on-failure
pytest -m "regression and not flaky" --browser chromium --browser firefox -n auto
pytest -m serial --browser chromium -n 0
pytest --last-failed --failed-first
```

Marker 策略：
- `smoke`: 每次 PR 必跑。
- `regression`: nightly 或 release 前执行。
- `e2e`: 端到端完整链路。
- `critical`: 关键业务高优先级。
- `flaky`: 需要治理的非稳定用例，必须关联原因。
- `serial`: 不允许并行的共享状态场景。

Retry 策略：仅对 `flaky` 或外部依赖不稳定场景限次重跑；全局无条件 retry 禁止。

Sharding 策略：Python `pytest-playwright` 没有 Node Playwright Test 的内建 `--shard` 语义，企业框架应在 CI 层实现 pytest-compatible sharding：
- CI matrix 提供 `SHARD_INDEX`、`SHARD_TOTAL`、`TEST_BROWSER`、`TEST_ENV`。
- shard 分配以测试 nodeid 为输入，使用稳定 hash 或预生成 test manifest，保证同一提交下分片可复现。
- 每个 shard 内仍可使用 `pytest-xdist -n auto` 做 worker 并行；shard 负责“跨机器切分”，xdist 负责“机器内并行”。
- `serial` marker 测试默认进入独立 shard 或在 shard 内 `-n 0` 执行，避免共享状态被并发破坏。
- 每个 shard 的报告与 artifact 必须带 shard 后缀：`junit-shard-{index}.xml`、`allure-results/shard-{index}`、`trace-shard-{index}`。
- CI 最后增加 report merge job：合并 JUnit/Allure，汇总失败 nodeid、shard index、worker id、artifact path。
- rerun 只针对失败 shard 或失败 nodeid，不重新跑全部 shard；`flaky` retry 仍受治理规则限制。
- shard 的数据隔离必须结合 `worker_id + shard_index + test_run_id`，避免跨 shard 账号/订单冲突。

### 6. Observability Layer
每次 CI 执行至少生成：
- JUnit XML：供 CI test summary 使用。
- Allure results：供趋势、步骤、附件查看。
- trace.zip：失败时保留。
- screenshot：失败时保留。
- video：默认关闭；失败重跑、高价值链路或调试时启用。
- framework log：关联 test id、worker id、browser、environment、data id。

安全规则：trace/video/screenshot/log 均视为敏感 artifact；上传前脱敏；设置保留期；限制访问权限。

### 7. Developer Usability
必须提供：
- Framework Guide：框架结构、运行命令、环境配置。
- Authoring Guide：如何写测试、Page Object、Flow、Data Factory。
- Troubleshooting：trace 分析、常见等待问题、并发冲突、artifact 查看。
- PR Checklist：marker、数据隔离、locator、fixture、报告、lint/typecheck。

### 8. Quality Gates
建议未来 CI gates：
```bash
pytest --collect-only
pytest -m smoke --browser chromium -n auto --tracing retain-on-failure
ruff check .
mypy autoui tests
```

额外 gate：
- 禁止未注册 marker。
- 禁止测试文件直接使用 `time.sleep`。
- 禁止测试文件直接使用硬编码 base URL。
- 禁止 Page Object 读取 secrets/env。
- 检查失败 artifact 是否上传。

## Final Verification Wave (MANDATORY — after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- 本设计文档阶段：仅提交 `.omo/plans/playwright-enterprise-framework-design.md`。
- 未来实施阶段：按架构层分批提交，避免一次性大爆炸提交。
- 推荐 commit scope：`config`、`fixtures`、`pages`、`data`、`execution`、`observability`、`docs`。

## Success Criteria
- 文档能让后续执行者不再询问“采用哪种架构”。
- 所有核心设计决策均有当前仓库证据或官方文档依据。
- 明确当前框架不满足企业级标准的原因。
- 明确目标架构如何提升维护性、扩展性、易用性、低耦合高内聚和稳定可观测性。
- 明确哪些是基线、哪些是推荐升级、哪些是未来增强。

## Reference Sources
- Current repo: `pyproject.toml`, `conftest.py`, `Fixtures/browser_fixture.py`, `Pages/order_console_page.py`, `Tests/test_demo.py`, `Core/data_loader.py`, `Config/settings.py`, `Data/demo.yaml`, `requirements.txt`, `Readme.md`。
- Playwright Python intro: `https://playwright.dev/python/docs/intro`
- pytest-playwright runner fixtures: `https://playwright.dev/python/docs/test-runners`
- BrowserContext isolation: `https://playwright.dev/python/docs/browser-contexts`
- Locators: `https://playwright.dev/python/docs/locators`
- Page Object Model: `https://playwright.dev/python/docs/pom`
- CI: `https://playwright.dev/python/docs/ci`
- Trace Viewer: `https://playwright.dev/python/docs/trace-viewer`
- Videos: `https://playwright.dev/python/docs/videos`
- pytest-xdist distribution: `https://pytest-xdist.readthedocs.io/en/stable/distribution.html`
- pytest cache / failed-first: `https://docs.pytest.org/en/stable/how-to/cache.html`
