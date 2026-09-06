# AutoUI UI 自动化框架技术设计

状态：已接受  
决定日期：2026-09-06  
范围：整体 UI 自动化框架方向，以及桌面 Web v1 的可实施设计

## 1. 结论

AutoUI 以 pytest 作为执行内核，以 Allure Report 3 作为测试结果分析与展示中心，但不在 pytest、Playwright、Allure 之上重复建设一套运行时、报告模型或趋势系统。

桌面 Web v1 直接复用：

- pytest：测试发现、fixture、生命周期、并行和权威测试结果；
- pytest-playwright：Browser、BrowserContext、Page、截图、Trace 和测试项产物目录；
- Allure Pytest：业务报告和业务步骤；
- Allure Report 3：环境聚合、历史、稳定性、Known Issues、Quality Gate、报告生成与展示；
- GitHub Actions：持续集成门禁和产物归档。

不同测试目标拥有独立的测试、Business Flow、Page Object 或目标交互对象，以及目标专属诊断证据。AutoUI 不提供 CommonDriver、BasePage 或跨目标业务用例抽象。

桌面 Web 的 Trace、截图和视频作为标准附件进入对应的 Allure 测试项。后续平台优先复用或内嵌 Allure Report 3；只有调度、权限、非 Allure 性能数据等真实需求出现时，才设计额外的平台数据 Interface。

## 2. 是否保留 `business_step`

### 2.1 决定

删除 AutoUI 自定义的 `@business_step`，Business Flow 直接使用 Allure 的 `@allure.step`。

业务步骤（Business Step）作为领域概念继续存在；删除的只是 AutoUI 对 Allure 装饰器的浅封装。

```python
import allure


class ImageEditorFlow:
    @allure.step("上传标准图片：{image_path}")
    def upload_standard_image(self, image_path: str) -> None:
        self.editor_page.upload_image(image_path)
```

### 2.2 删除测试

删除自定义 `business_step` 后：

- 标题和参数格式化仍由 Allure 原生能力提供；
- 步骤状态、耗时、异常和嵌套关系仍由 Allure 原生能力提供；
- Business Flow 只需将 `@business_step` 改成 `@allure.step`；
- Playwright Trace 仍由 pytest-playwright 自动采集完整操作。

复杂度没有重新散落到调用方，因此该 Module 没有形成足够 Depth。

当前只有 Allure 一个业务报告 Adapter。为假设中的第二种报告工具提前建立 Seam，只会增加命名、测试和维护成本。

### 2.3 Allure 与 Trace 的关系

Allure 和 Trace 不做步骤级映射，但在测试项级别建立标准附件关联：

```text
Business Flow ──@allure.step──────────────> Allure test result

Page Object ──Playwright 操作──> trace.zip
                                      │
                                      └──标准 Trace 附件──> 同一个 Allure test result
```

二者共同属于同一个 pytest 测试项，但表达不同层次的信息：

| 产物 | 面向对象 | 表达内容 |
|---|---|---|
| Allure | 业务、产品、测试 | 做了什么、结果如何 |
| Playwright Trace | 开发、测试 | 页面具体发生了什么、为何失败 |

Allure 3 识别 `application/vnd.allure.playwright-trace` 附件，点击后可以在新标签页中使用 Playwright Trace Viewer 打开。AutoUI 只附加原始 zip 和正确媒体类型，不解析或修改 Trace。Python 方案由 Allure Pytest 的字符串媒体类型 Interface 与 Allure 3 的 Trace 附件契约组合而成；2026-09-06 已用真实失败 Trace 完成聚焦验证。

官方默认 Trace Viewer 页面来自 `trace.playwright.dev`。Trace 数据保留在浏览器中，但加载 Viewer 页面需要网络。当前开发环境已验证可打开；CI 和公司其他网络环境仍需在接入阶段分别验证。如果内网不可访问，后续平台再提供内部托管的 Trace Viewer，这不是业务步骤 Module 的职责。

## 3. 设计目标

### 3.1 当前必须达到

- 桌面 Web 用例可重复执行、可并行、可诊断、可接入 CI；
- 测试用例只表达业务场景、数据和断言；
- Business Flow 表达可复用的业务操作；
- Page Object 只表达 DesignKit 页面能力；
- pytest 是唯一权威测试结果；
- Allure 展示数量不固定的业务步骤；
- Playwright Trace 保留完整技术诊断，并可从对应 Allure 测试项进入；
- 运行环境、产品和测试目标使用稳定 Allure labels 描述；
- 优先使用 Allure 3 的环境、历史、Known Issues、Quality Gate 和多阶段汇总；
- 每个 pytest 测试项拥有独立 BrowserContext 和产物目录；
- 通用框架不持有任何具体产品的 Page Object。

### 3.2 明确不做

- 不建设 AutoUI JSONL 详细事件流；
- 不建设自定义业务步骤 runtime；
- 不把 Allure step 映射到 Trace group；
- 不自建报告首页、趋势数据库、Known Issues 或 Quality Gate；
- 不包装 Page、Locator、等待或断言 Interface；
- 不创建 CommonDriver、BasePage、BaseTestCase；
- 不要求同一业务用例跨测试目标复用；
- 不提前创建移动 App、桌面 App 等空 Module；
- 不在 v1 实现测试平台、性能观测和 Result Manifest；
- 不默认启用失败重试，先让 Allure 历史和稳定性分析暴露真实波动。

## 4. 整体架构

```text
                         ┌─────────────────────────┐
                         │       pytest 内核        │
                         │ 发现 / fixture / outcome │
                         └────────────┬────────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
                 ▼                    ▼                    ▼
        ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
        │ 桌面 Web 套件   │   │ 未来移动 App   │   │ 未来桌面 App   │
        │ Flow / Pages    │   │ 独立 Flow/交互  │   │ 独立 Flow/交互  │
        └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
                │                    │                    │
                ▼                    ▼                    ▼
        Playwright Trace         目标专属诊断证据       目标专属诊断证据
                │                    │                    │
                └──────────────标准附件关联───────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Allure results      │
                         │ outcome / step / label   │
                         │ attachment / parameter   │
                         └────────────┬────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │     Allure Report 3      │
                         │ Awesome / Env / History  │
                         │ Known / Gate / Dump      │
                         └────────────┬────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │      后续测试平台         │
                         │ 报告目录 / 调度 / 权限    │
                         │ 独立性能 Viewer           │
                         └─────────────────────────┘
```

Allure Pytest 横切各测试目标生成统一业务报告，各目标的原生诊断证据通过标准附件关联进入报告，但不统一其底层交互模型和文件格式。

## 5. Module 与 Interface

### 5.1 Configuration Module

位置：`autoui/core/config/`

Interface：

```python
settings = resolve_settings(
    cli_site=...,
    cli_env=...,
    cli_base_url=...,
)
```

该 Module 应隐藏：

- YAML 路径和读取；
- 默认值、目标环境与 CLI 的合并顺序；
- 必填字段和类型校验；
- 不可变 Settings 构造。

配置解析必须在浏览器启动前完成。凭据不写入 YAML，通过环境变量或 CI Secrets 注入。

当前只有桌面 Web 时，不为未来所有测试目标设计一个巨型通用 Settings。第二个测试目标落地后，再根据真实重复提取共享配置。

### 5.2 pytest Options Plugin

位置：`autoui/plugins/options.py`

Interface：

- `--site`；
- `--env`；
- pytest-playwright 原生 `--base-url`；
- session scope 的 `settings` fixture。

该 Module 只把 pytest 配置输入适配到 Configuration Module，不读取 Page、不创建浏览器、不处理报告。

### 5.3 Web pytest Plugin

位置：`autoui/plugins/web.py`

Interface：

- 覆盖 pytest-playwright 的 `browser_context_args` fixture；
- 把 Settings 转换为 Playwright BrowserContext 参数；
- 继续使用 pytest-playwright 的 `browser`、`context`、`page` 和 `output_path` fixture。

该 Module 不提供 DesignKit Page Object、Business Flow、业务步骤或报告 fixture。

它隐藏的有效复杂度只有“AutoUI 配置如何进入 BrowserContext”。Browser、Context、Page、Trace 和 screenshot 生命周期继续由 pytest-playwright 管理。

### 5.4 Allure pytest Integration Module

位置：`autoui/plugins/allure_reporting.py`

这个 Module 不包装 `allure.step`，而是处理 pytest、pytest-playwright 与 Allure results 之间真实存在的集成复杂度。

Interface 对测试代码不可见，由 pytest plugin 自动执行：

- 为每个测试项添加稳定的执行标签，例如 `testTarget`、`site`、`deployment` 和 `browser`；
- 在 pytest-playwright 完成产物归档后，将失败截图、视频和 Trace 关联到对应 Allure 测试项；
- 使用 Allure 3 标准媒体类型 `application/vnd.allure.playwright-trace` 附加 `trace.zip`；
- 只读取 pytest-playwright 的公开 `output_path`，不解析 Trace 内容；
- 不改变 pytest outcome，不产生第二套测试结果。

产品、Feature 和 Story 等业务标签不由该 Module 猜测。它们由具体产品测试套件使用 Allure 原生 decorator 或动态 Interface 声明。

这个 Module 通过一个不可见的 pytest plugin Interface 隐藏产物归档时序、标签一致性和附件媒体类型，删除后这些复杂度会重新散落到每个产品套件，因此具有实际 Depth。

### 5.5 Product Test Suite

位置：`tests/web/designkit/`

DesignKit 是业务代码的所有者。其 pages、flows、数据、素材和 pytest fixture 都归属于该套件，而不是 AutoUI 通用框架。

建议目录：

```text
tests/
├── resources/
│   └── images/
└── web/
    └── designkit/
        ├── conftest.py
        ├── pages/
        │   ├── home_page.py
        │   └── editor_page.py
        ├── flows/
        │   └── image_editor_flow.py
        ├── data/
        └── test_editor_add_title_vip_font_download.py
```

### 5.6 Page Object Module

Interface 只包含调用者需要的页面能力：

```python
class EditorPage:
    def upload_image(self, image_path: Path) -> None: ...
    def add_title(self) -> None: ...
    def choose_vip_font(self, font_name: str) -> str: ...
    def download_to(self, output_dir: Path) -> Path: ...
```

约束：

- 构造函数只接收正在操作的 Playwright `Page`；
- Locator 保持为实现细节；
- 可以验证页面操作的技术前置条件和后置状态；
- 不依赖 pytest request、Allure、Trace、logger 或运行时对象；
- 不承担最终业务断言；
- 页面跳转或新 Tab 应返回新的 `Page` 或新的 Page Object。

字体等需要从候选集合选择的页面能力必须接收测试场景提供的稳定名称（例如
`choose_vip_font("点字少年")`），不得在 Page Object 内部随机选择；需要扩大覆盖时由测试数据参数化。

只有两个真实页面实现出现相同且稳定的行为后，才考虑提取共享 Module。

### 5.7 Business Flow Module

Business Flow 位于测试场景与 Page Object 之间的 Seam，将多个页面能力组合为业务操作（Business Operation）。

```python
class ImageEditorFlow:
    def __init__(self, home_page: HomePage) -> None:
        self.home_page = home_page
        self.editor_page: EditorPage | None = None

    @allure.step("进入图片编辑器")
    def open_editor(self) -> None: ...

    @allure.step("上传标准图片：{image_path}")
    def upload_standard_image(self, image_path: Path) -> None: ...

    @allure.step("添加标题并应用 VIP 字体：{font_name}")
    def add_title_with_vip_font(self, font_name: str) -> str: ...

    @allure.step("下载图片编辑结果")
    def download_result(self, output_dir: Path) -> Path: ...
```

Interface 约束：

- 方法以业务意图命名，不以 click、fill 等技术动作命名；
- 一个业务操作可以调用任意数量 Page Object 方法；
- 只有业务读者关心的公开操作使用 `@allure.step`；
- 私有辅助方法不强制生成步骤；
- 场景数据显式传入业务操作，避免随机值破坏重试和 History 聚合；
- 返回测试断言或后续编排真正需要的值；
- 不捕获并改写 Playwright 或断言异常。

Business Flow 属于具体产品和测试目标，不进入 `autoui/` 通用包。

### 5.8 Test Scenario Module

测试用例负责选择 Business Operation、提供场景数据并完成业务断言：

```python
def test_editor_add_title_vip_font_download(
    image_editor: ImageEditorFlow,
    output_path: str,
) -> None:
    image_editor.open_editor()
    image_editor.upload_standard_image(EDITOR_STANDARD_IMAGE)
    selected_font = image_editor.add_title_with_vip_font("点字少年")
    downloaded_file = image_editor.download_result(Path(output_path))

    assert selected_font
    assert downloaded_file.is_file()
    assert downloaded_file.stat().st_size > 0
```

测试不直接处理 Locator，不重复记录步骤，也不自行创建 BrowserContext。

### 5.9 Allure Report 3 Toolchain

不创建 AutoUI Reporting Wrapper 或报告数据模型。Allure Report 3 本身是报告 Toolchain，其配置 Interface 位于项目根目录的 `allurerc.mjs`。

报告链路为：

```text
Business Flow 的 @allure.step
        │
        ▼
allure-pytest==2.16.0
        │
        ▼
allure-results/
        │
        ▼
Allure Report 3（项目级 npm 锁定版本）
        │
        ▼
allure-report/
```

Allure Report 3 的 npm 依赖、配置文件、主题与平台嵌入方式属于报告工具链，不进入 Python `requirements.txt`。

第一阶段采用 Awesome plugin，并由 `allurerc.mjs` 统一管理：

- `groupBy`：按照稳定 labels 组织测试层级；
- `reportLanguage`、theme、logo：完成公司需要的语言和品牌配置；
- `environments`：基于测试结果 labels 区分 site、deployment、browser 和操作系统；
- `historyPath`：保存跨运行历史，用于趋势和稳定性分析；
- `knownIssuesPath`：维护已知失败及其缺陷链接；
- `qualityGate`：执行成功率、失败数量、测试数量和耗时规则；
- plugins：后续按需增加 Dashboard、CSV、Jira 或其他官方 plugin。

采用顺序：

| Allure 3 能力 | AutoUI 设计决定 | 引入阶段 |
|---|---|---|
| Awesome report、分组、过滤、品牌配置 | 直接配置，不修改 Allure 源码或生成文件 | v1 |
| Environments | AutoUI 只提供稳定运行 labels，环境聚合交给 Allure | v1 |
| Trace、截图和视频附件 | Allure pytest Integration Module 负责标准附件关联 | v1 |
| Global errors、stdout、stderr | CI 使用 `allure run -- pytest ...` 捕获 | v1 |
| History、稳定性和趋势 | 使用 `historyPath`，CI 以分支缓存持久化，不自建趋势数据库 | v1 |
| Known Issues | 使用 Allure 文件与缺陷链接，不自建已知问题系统 | v1 CI 稳定后 |
| Quality Gate | 负责发布门禁；不修改单个 pytest outcome | v1 CI 稳定后 |
| Multistage dumps | 多环境或多阶段 CI 出现时合并运行 | 后续 |
| Allure Report Storage | 需要集中报告与历史持久化时先评估 | 平台阶段 |
| 失败重试 | 不默认开启；确有策略后优先评估 Allure 3 rerun | 后续 |

Allure labels 分为两类，避免框架猜测业务、业务代码重复运行信息：

| 类型 | labels | 负责方 |
|---|---|---|
| 运行上下文 | `testTarget`、`site`、`deployment`、`browser`、`os` | Allure pytest Integration Module 自动添加 |
| 业务分类 | `product`、`feature`、`story`、`severity`、issue/testcase link | 产品测试套件显式声明 |

Awesome report 初始使用 `testTarget -> product -> feature -> story` 作为业务浏览层级。pytest 的包和 suite 信息继续保留，供技术人员按代码结构定位。

Allure 的 historyId 依赖稳定的测试身份和参数。时间戳、随机值、运行目录等一次性信息不得作为影响测试身份的参数；site、deployment、browser 等运行差异使用 labels 和 Environments 表达。

pytest 仍负责每个测试项的 passed、failed、skipped 和 error。Quality Gate 可以让 CI 或发布流程失败，但不能把一个 pytest failed 改写为 passed。

报告 UI 定制优先级为：

```text
Awesome 配置（groupBy/theme/logo/language）
    -> 官方 plugin
        -> 确有缺口时开发 Allure 3 plugin
            -> 不 fork Allure，不直接修改生成后的 HTML
```

### 5.10 Diagnostic Evidence

每个测试目标使用自己的原生诊断能力：

| 测试目标 | 诊断证据方向 |
|---|---|
| 桌面 Web | Playwright Trace、screenshot、video、console、network |
| 移动 Web | 根据最终执行工具选择，不预先统一 |
| 移动 App | Appium 日志、设备日志、录屏等 |
| 桌面 App | 由最终驱动工具提供的日志、截图和录屏 |

AutoUI 不把这些证据转换为通用详细事件流。能够被 Allure 3 原生展示或打开的证据，通过标准附件进入测试项；其余证据保持原始文件并在平台阶段按真实需求处理。

## 6. 依赖方向

```text
tests
  └──> product flows
         ├──> product pages
         │      └──> Playwright
         └──> Allure

pytest
  └──> AutoUI pytest plugins
         ├──> Configuration Module
         ├──> pytest-playwright fixtures
         └──> Allure pytest Integration Module
                    └──> allure-pytest
```

禁止的反向依赖：

```text
autoui -> DesignKit pages/flows
Page Object -> pytest plugin/runtime
Page Object -> Allure/Trace
Allure step -> Playwright Trace group
测试平台 -> Allure/Trace 内部数据结构
```

## 7. 执行生命周期

```text
npx allure run 启动 pytest
  -> Allure 3 捕获进程退出码、stdout 和 stderr
  -> pytest 注册 AutoUI CLI
  -> resolve_settings()
  -> 配置失败则在浏览器启动前终止
  -> pytest-playwright 创建 session Browser
  -> 为每个 pytest item 创建独立 BrowserContext
  -> 创建 Page 和独立 output_path
  -> 测试调用 Business Flow
  -> Business Flow 生成 Allure 业务步骤
  -> Page Object 执行 Playwright 操作并进入 Trace
  -> pytest 判定 passed / failed / skipped / error
  -> pytest-playwright 按策略保存 Trace 和 screenshot
  -> Allure pytest Integration Module 附加 Trace、截图和执行 labels
  -> allure-pytest 写入 allure-results
  -> pytest 关闭当前 BrowserContext
  -> Allure 3 应用 Known Issues、History 和 Quality Gate
  -> Awesome plugin 生成报告，或生成供多阶段汇总的 dump archive
```

并行执行时，测试项不得共享 Page、BrowserContext、下载目录或可变业务状态。session Browser 可以由 pytest-playwright 按其原生模型管理。

## 8. 配置设计

桌面 Web v1 的配置来源和优先级：

```text
site：--site > defaults.yaml
deployment：--env > defaults.yaml
base_url：--base-url > targets.yaml
公共 Web Context 参数：target > defaults.yaml
凭据：环境变量 / CI Secrets
```

Settings 创建后不可变，并保留解析后的 `site` 和 `deployment`，供浏览器配置及 Allure 环境 labels 使用。`autoui/plugins/web.py` 和 Allure pytest Integration Module 只消费 Settings，不重复读取 CLI 或 YAML。

登录态属于具体产品测试套件。通用框架只允许产品套件通过 pytest-playwright 支持的 BrowserContext 参数使用 storage state；不在 v1 建设账号池和统一登录中心。

### 8.1 DesignKit 登录态

DesignKit 使用 `tests/web/designkit/auth.py` 解析登录态，通过产品目录下的 `conftest.py` 覆盖上层 `browser_context_args`，只增加 Playwright `storage_state`：

```text
DESIGNKIT_STORAGE_STATE 环境变量
        > .auth/designkit-{site}-{deployment}.json 默认路径
        -> DesignKit browser_context_args
        -> pytest-playwright 独立 BrowserContext
```

登录态是只读的 BrowserContext 初始状态。测试项仍各自创建和关闭 BrowserContext，不共享 Page、下载目录或运行中产生的 cookies。登录态不存在时在 fixture setup 阶段返回明确的 `pytest.UsageError`，不继续执行业务 Flow。

本地使用 Playwright codegen 完成一次人工登录并保存状态：

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$($PWD.Path)\.playwright-browsers"
.venv\Scripts\python.exe -m playwright codegen `
  --save-storage=".auth\designkit-cn-release.json" `
  "https://www.designkit.cn/"
```

CI 使用 `DESIGNKIT_STORAGE_STATE_B64` GitHub Secret 还原文件，并通过 `DESIGNKIT_STORAGE_STATE` 把路径传给测试。账号密码登录、短信、扫码、SSO 和账号池不属于当前 Module；只有实际登录方式要求自动生产状态时，再设计对应 Adapter。

## 9. 结果与产物

### 9.1 当前 v1

```text
pytest outcome       权威结果
JUnit XML            CI 机器可读摘要
allure-results       业务报告原始结果
allure-report        Allure Report 3 生成的展示产物
trace.zip            桌面 Web 失败诊断
screenshot/video     按 pytest-playwright 策略生成
downloads            当前测试项 output_path 下的业务产物
Allure dump           多阶段运行的完整状态归档（需要时启用）
history JSONL         Allure 3 跨运行历史（CI 分支缓存持久化）
```

建议策略：

```text
--tracing=retain-on-failure
--screenshot=only-on-failure
--output=artifacts/playwright
--alluredir=artifacts/allure-results
--junit-xml=artifacts/junit.xml
```

### 9.2 后续平台方向

暂不把 Result Manifest 视为必然需要建设的 Module。Allure 3 已经提供报告、dump archive、历史、环境、Known Issues、Quality Gate 和 Storage 能力，先以这些标准产物作为报告侧 Interface。

后续测试平台第一阶段只需要保存：

- 运行标识和触发信息；
- Allure report 或 dump archive 的位置；
- 独立性能 Viewer 的位置；
- 权限、保留期和调度状态。

只有当平台确实需要关联 Allure 无法表达的多类运行产物时，再设计最小 Result Manifest。它不得复制 Allure step、history、known issues 或 Trace action。

## 10. 依赖管理

Python 依赖与 Allure Report 依赖分开锁定：

```text
requirements.in / requirements.txt
  pytest、pytest-playwright、playwright、allure-pytest 等 Python 依赖

package.json / package-lock.json
  Allure Report 3 及启用的官方 plugins

allurerc.mjs
  报告层级、环境、历史、Known Issues、Quality Gate 和展示配置
```

Playwright Python 包升级后，必须安装匹配版本的 Chromium。CI 与本地均通过当前 Python 环境执行 Playwright 安装命令。

## 11. 测试与验收策略

### 11.1 Configuration Module

- 默认值与 CLI 优先级；
- 未知 site/environment；
- DesignKit 登录态默认路径、环境变量覆盖与缺失错误；
- 缺失字段和类型错误；
- Settings 不可变性。

### 11.2 Product pages 与 flows

- 不为 Locator 和 Playwright 内部实现建立大量 Mock 测试；
- 以真实浏览器 smoke 和回归场景验证页面契约；
- Business Flow 的纯编排逻辑只有在存在真实分支时再使用替代对象测试。

### 11.3 框架闭环

- `pytest --collect-only -q --strict-markers`；
- 代表性桌面 Web smoke；
- DesignKit 真实回归；
- 受控失败时保留 Allure、Trace 和 screenshot；
- Allure 测试项可以打开对应 Playwright Trace 附件；
- site、deployment 和 browser 可以形成 Allure 3 Environments；
- Quality Gate 失败不改写单个 pytest outcome；
- `pytest-xdist -n 2` 下结果和产物互不覆盖；
- GitHub Actions 保留 pytest 非零退出状态并始终上传诊断产物。

### 11.4 Allure 3 Trace 契约验证记录

2026-09-06 先使用独立本地 HTML 页面完成最小契约验证，随后使用正式 pytest plugin、仓库内 Chromium 和真实 DesignKit 场景完成实施验证：

- Allure Pytest 生成三个原生业务步骤，前两步通过、最后一步随断言失败；
- 测试结果包含 `testTarget`、`site`、`deployment`、`browser`、`os` 五个稳定 labels；
- pytest-playwright 在 fixture teardown 后保留真实 `trace.zip`；
- `allure.attach.file(..., attachment_type="application/vnd.allure.playwright-trace")` 正确写入 Allure results；
- Allure Report 3.14.3 成功生成 Awesome report，并把正式插件结果归入 `DesignKit CN · beta · Chromium · Windows` 环境；
- 报告将附件显示为专门的 `Playwright Trace` 分组，提供 `Open Playwright Trace` 与下载操作；
- 报告中的 Trace 操作可打开 `https://trace.playwright.dev/`，页面标题为 `Playwright Trace Viewer`；
- 仓库内 `chromium-1234` 在 `pytest-xdist -n 2` 下完成两个独立浏览器测试项，产物未互相覆盖；
- Allure 3 `allure run` 在受控失败下生成报告并保留 pytest 退出码 `1`；
- DesignKit storage state 注入后，真实场景完成打开编辑器、上传图片、选择 VIP 字体和下载作品，四个 Allure 业务步骤均通过。

正式 `autoui/plugins/allure_reporting.py` 已实现并通过生命周期、附件契约、并行隔离和带有效登录态的 DesignKit 完整回归验证。远端 GitHub Actions 已配置登录态 Secret 并成功运行。

## 12. 实施计划

### 阶段 0：依赖基线

状态：已完成。

- 锁定 Python 直接依赖；
- 单独锁定 Allure Report 3；
- 建立最小 `allurerc.mjs`，使用 Awesome plugin；
- 安装匹配版本的 Playwright Chromium；
- 验证 Allure Pytest 附加标准媒体类型的 Trace 能被 Allure 3 打开；
- 完成 `pip check`、收集和最小浏览器 smoke。

### 阶段 1：业务代码归位

状态：已完成。

- 将 DesignKit Page Object 移入 `tests/web/designkit/pages/`；
- 将 DesignKit 测试和 fixture 移入产品套件；
- 从通用 Web plugin 删除业务 Page Object fixture；
- 保持现有业务行为不变。

### 阶段 2：建立 Business Flow

状态：已完成。

- 创建 `ImageEditorFlow`；
- 用 Allure 原生 `@allure.step` 声明业务步骤；
- 测试通过 Flow 表达场景并保留最终业务断言；
- 不接入 Trace group 映射。

### 阶段 3：删除旧运行时

状态：已完成。

- 删除 `WebStepRuntime` 和两套自定义 `business_step`；
- 删除只服务于 JSONL 的 logger、formatter、identity 和 pytest runtime plugin；
- 删除对应旧测试；
- 收窄根 `conftest.py` 的 plugin 注册。

### 阶段 4：报告、并行与 CI

状态：已完成。本地实现、登录态场景、CI workflow 与远端 GitHub Actions 验证均通过。

- 建立 Allure pytest Integration Module，注入稳定运行 labels；
- 将失败 Trace 以标准媒体类型附加到对应 Allure 测试项；
- 将失败截图和视频作为标准附件；
- 使用 `allure run -- pytest ...` 捕获全局退出码和输出；
- 生成 Awesome report，验证 Trace 可以从报告打开；
- 配置 Allure 3 Environments；
- 验证串行与 `xdist -n 2`；
- 更新 CI 的 Python、Node、Allure 与浏览器安装步骤。

### 阶段 5：Allure 3 运行治理（当前）

- 已启用 `historyPath`，并通过 GitHub Actions 分支缓存跨运行保存 history；
- 引入 Known Issues 文件及缺陷链接流程；
- 从最小规则开始启用 Quality Gate；
- 出现多环境 CI matrix 后使用 dump archive 汇总；
- 需要集中持久化时先评估 Allure Report Storage。

### 阶段 6：后续独立设计

- 测试平台的运行目录、调度和权限；
- 是否仍有必要设计 Result Manifest；
- 性能观测；
- 第二个测试目标。

只有第二个测试目标真正落地后，才根据两个 Adapter 的共同需求提取新的 Seam；不根据猜测提前创建统一 Driver 或目标抽象。

## 13. 决策依据

本设计由以下 ADR 约束：

- [ADR-0001：分离测试执行、公共结果与产物查看](../adr/0001-separate-execution-results-and-artifact-viewers.md) 确定 pytest、业务报告与目标专属诊断证据的职责分离。
- [ADR-0002：以 Allure Report 3 作为报告中心](../adr/0002-adopt-allure-report-3-as-reporting-center.md) 确定原生 `@allure.step`、测试项级 Trace 附件、Allure 3-first 报告能力以及按真实缺口决定 Result Manifest。

若后续实现需要改变以上职责边界，应新增或取代 ADR；目录、类名和局部 Interface 的普通演进直接更新本设计。
