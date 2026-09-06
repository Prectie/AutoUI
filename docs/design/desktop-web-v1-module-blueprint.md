# 桌面 Web v1 模块设计蓝图

## 1. 结论

桌面 Web v1 以一个真实的 DesignKit 回归场景建立最小闭环：pytest 负责权威测试结果，Allure 负责业务报告，Playwright Trace 负责 Web 诊断。测试业务代码归属于 DesignKit 测试套件，AutoUI 通用框架不持有任何项目专属 Page Object。

本蓝图只确定 Module、Interface、依赖方向、迁移边界和验收标准，不实现测试平台、性能观测、其他测试目标或预设的 Result Manifest。

## 2. 要解决的问题

当前实现将页面操作、业务步骤、JSONL、Allure 和 Trace 绑定在同一调用路径中：

```text
测试 → 注入 WebStepRuntime 的 Page Object → JSONL + Allure + Trace
```

这带来三个直接问题：

1. Page Object 必须了解报告和运行时，无法只表达页面能力。
2. “点击按钮”一类技术动作被当成业务步骤，报告层级受方法拆分方式控制。
3. 同一个事实写入多个输出，生命周期和测试数量随输出种类一起增长。

## 3. 目标结构

```text
autoui/
├── core/
│   └── config/                       # 配置解析与 Settings
└── plugins/
    ├── web.py                        # pytest 与 pytest-playwright 的集成
    └── allure_reporting.py           # 稳定 labels 与测试项附件

tests/
├── resources/                        # 测试素材路径
└── web/
    └── designkit/
        ├── pages/
        │   ├── home_page.py          # DesignKit 首页页面能力
        │   └── editor_page.py        # DesignKit 编辑器页面能力
        ├── flows/
        │   └── image_editor_flow.py  # 可复用业务操作
        └── test_editor_add_title_vip_font_download.py
```

迁移完成后删除 `autoui/platforms/web/pages/`。这里删除的是通用框架中的业务页面实现，不是放弃 Page Object 模式。

## 4. Module 与 Interface

### 4.1 Web pytest plugin

**职责与位置**

复用 pytest-playwright 的生命周期，向桌面 Web 测试提供浏览器配置、`BrowserContext` 和原生产物。它位于 pytest 与 AutoUI Web 能力的 Seam。

**Interface**

- 沿用 pytest-playwright 的 `page`、`context`、`output_path` 等 fixture。
- 只增加 AutoUI 确实需要的配置注入和内部 Adapter 注册。
- 不提供 DesignKit Page Object fixture。
- 不提供业务步骤 runtime。

**当前边界**

- 保留浏览器参数和环境配置接入。
- 复用 pytest-playwright 的截图、视频和 Trace 生命周期。
- 不自行重建一套浏览器产物生命周期。

### 4.2 Allure pytest Integration

**职责与位置**

在 pytest 测试项与 Allure results 之间提供窄的集成层，负责稳定执行 labels 和测试项产物附件。它不定义 Business Step，也不绑定当前 `BrowserContext`。

**Interface**

Business Flow 直接使用 Allure 原生装饰器声明业务语义：

```python
@allure.step("添加标题并应用随机 VIP 字体")
def add_title_with_vip_font(self) -> None:
    ...
```

Allure pytest Integration 在 pytest-playwright 完成测试项产物收集后，将失败 `trace.zip` 以 `application/vnd.allure.playwright-trace` 媒体类型附加到同一个 Allure 测试项。它只使用 pytest、pytest-playwright 和 Allure 的公开 Interface。

**必须隐藏的实现复杂度**

- site、deployment、browser、OS 等稳定 labels 的来源与命名；
- pytest-playwright fixture teardown 后定位当前测试项的 Trace、截图与视频；
- 正确的附件媒体类型与文件扩展名；
- xdist 下测试项产物不得互相覆盖；
- 报告附件失败不得改写 pytest 的权威测试结果。

业务步骤和 Trace 不做步骤级映射：Allure 描述业务过程，Trace 保存 Playwright 原生技术过程，二者只通过同一个 pytest 测试项关联。

### 4.3 DesignKit Page Objects

**职责与位置**

封装 DesignKit 页面元素、页面状态和 Playwright 交互，位于 DesignKit 测试代码中。

**Interface**

- 构造参数只接收所操作的 `Page`。
- 方法使用页面语义命名，并返回调用方继续编排所需的结果。
- 不依赖 Allure、Trace、JSONL、pytest request 或框架 runtime。

不建立 `BasePage` 或所谓通用 `CommonPage`。只有当至少两个真实测试套件出现相同页面行为时，才根据实际重复提取 Module。

### 4.4 DesignKit Business Flow

**职责与位置**

将一个或多个 Page Object 操作组合成可复用的业务操作，是测试场景与页面实现之间的 Seam。

**Interface**

```python
class ImageEditorFlow:
    @allure.step("进入图片编辑器")
    def open_editor(self) -> None: ...

    @allure.step("上传标准图片：{image_path}")
    def upload_standard_image(self, image_path: str) -> None: ...

    @allure.step("添加标题并应用随机 VIP 字体")
    def add_title_with_vip_font(self) -> None: ...

    @allure.step("下载图片编辑结果")
    def download_result(self, output_path: str) -> Path: ...
```

业务步骤数量由测试场景调用的业务操作决定，不设固定个数。一次性且不值得复用的业务步骤可以直接使用 Allure context step，但不是常规写法。

### 4.5 DesignKit tests

**职责与位置**

测试用例只选择业务操作、提供场景数据并完成业务断言。

**Interface 示例**

```python
def test_editor_add_title_vip_font_download(
    image_editor: ImageEditorFlow,
    output_path: str,
) -> None:
    image_editor.open_editor()
    image_editor.upload_standard_image(str(EDITOR_STANDARD_IMAGE))
    image_editor.add_title_with_vip_font()

    downloaded_file = image_editor.download_result(output_path)

    assert downloaded_file.is_file()
    assert downloaded_file.stat().st_size > 0
```

## 5. 依赖与数据流

```text
pytest test
    │
    ├──调用──> DesignKit Business Flow
    │               │
    │               ├──编排──> DesignKit Page Objects ──> Playwright
    │               │
    │               └──声明──> @allure.step ──> Allure Business Report
    │
    └──判定──> pytest Test Outcome
                   ├──> Allure test result
                   └──> pytest-playwright trace.zip
                                  └──标准附件──> 同一个 Allure test result
```

依赖方向必须保持单向：通用框架不知道 DesignKit，Page Object 不知道报告，测试平台不解析 Allure 或 Trace 的内部格式。

## 6. 删除与迁移范围

### 移动并重塑

- `home_page.py`、`editor_page.py` 移入 `tests/web/designkit/pages/`。
- `common_page.py` 的 DesignKit 宣传弹窗行为合并到合适的 DesignKit Page Object，不保留“通用页面”命名。
- 当前测试迁入 `tests/web/designkit/` 并改为调用 `ImageEditorFlow`。
- `autoui/plugins/web.py` 收窄为通用 pytest-playwright 集成。

### 删除

- `autoui/platforms/web/steps.py` 中绑定 JSONL 和 Page Object 的 `WebStepRuntime`。
- 两套 AutoUI 自定义 `business_step` 及其 Trace context 绑定。
- DesignKit 迁移完成后的 `autoui/platforms/web/pages/`。
- Baidu 和 Order Console 演示 Page Object、演示测试及只为演示数据服务的 plugin。
- 仅服务于详细 JSONL 事件链路的 logger、formatter 和对应测试。

### 保留或收窄

- 配置解析与不可变 `Settings`。
- pytest-playwright 已有的浏览器、Context、截图、视频和 Trace 能力。
- pytest 测试结果采集、稳定 Allure labels 和原生产物附件。

## 7. 实施顺序

每个阶段只引入一个主要职责，并保持测试可运行：

1. **验证 Allure 3 契约（已完成，2026-09-06）**：用受控失败证明原生 `@allure.step`、稳定 labels、pytest-playwright `trace.zip` 和 Allure 3 Trace 附件可以形成最小闭环。
2. **业务代码归位（已完成，2026-09-06）**：移动 DesignKit Page Object 和测试，删除通用 Page Object fixture，不改变场景行为。
3. **建立 Business Flow（已完成，2026-09-06）**：把业务编排从技术页面方法中提升到 `ImageEditorFlow`，直接使用原生 `@allure.step`。
4. **移除重复事件链路（已完成，2026-09-06）**：删除 `WebStepRuntime`、两套自定义 `business_step`、详细 JSONL logger/formatter 及其专用测试。
5. **收窄 pytest plugin（本地闭环已完成，2026-09-06）**：只留下配置、结果、稳定 labels 和原生产物附件；CI workflow 已配置，远端运行待代码推送后验证。

## 8. 验收标准

- DesignKit 回归测试只通过 Business Flow 表达主要业务过程。
- Allure 展示数量不固定、语义完整的业务步骤。
- Playwright Trace 仍可打开并用于诊断，可从对应 Allure 测试项进入；不要求与 Allure 显示同名步骤层级。
- Page Object 构造函数只需要 `Page`，不依赖报告 runtime。
- `autoui` 中不存在 DesignKit、Baidu 或 Order Console 的 Page Object。
- 不再生成或维护详细 JSONL 事件流。
- pytest 的通过、失败、跳过和错误是唯一权威测试结果。
- 验证命令统一使用 `.venv\\Scripts\\python.exe -m pytest ...`。

## 9. 后续演进，不在本次实现

- 平台出现真实关联缺口后，是否需要最小 Result Manifest；
- 测试平台及 Viewer 嵌入技术；
- Allure 支持范围内的品牌和配置定制；
- 性能观测采集与独立 Viewer；
- 移动 Web、移动 App、桌面 App 和小程序；
- Business Flow 在多个真实项目之间的复用策略。
