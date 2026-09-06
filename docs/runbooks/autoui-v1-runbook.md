# AutoUI v1 运行手册

本文是当前桌面 Web v1 闭环的操作手册。它覆盖本地执行、DesignKit 登录态、Allure Report 3、Playwright Trace、CI 和常见故障；平台调度、性能观测和第二个测试目标不在本手册范围内。

## 1. 当前结果

一次回归运行的职责分工如下：

```text
pytest outcome       权威通过/失败结果
Allure Report 3      业务步骤、环境分组、历史和报告展示
Playwright Trace     Web 技术操作、DOM、网络和截图诊断
JUnit XML            CI 机器可读摘要
```

Allure 业务步骤由产品套件中的 Business Flow 使用原生 `@allure.step` 声明，步骤数量不固定。例如 DesignKit 当前场景明确传入 `点字少年`，不会在测试运行时随机选字体。失败时，pytest-playwright 生成的 `trace.zip` 会作为标准附件出现在同一个 Allure 测试项中。

## 2. 环境准备

项目当前锁定的主要版本：

| 组件 | 版本或来源 |
|---|---|
| Python | 3.12 |
| pytest | `requirements.txt` 锁定 |
| Playwright Python | `1.62.0` |
| pytest-playwright | `0.9.0` |
| allure-pytest | `2.16.0` |
| Allure Report | `3.14.3`，由 `package-lock.json` 锁定 |
| Chromium | 与 Playwright Python 匹配；本机目录为 `.playwright-browsers\chromium-1234` |

所有 Python 验证都使用项目虚拟环境：

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright-browsers"
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -m playwright install chromium
```

如果浏览器已经安装，可以只验证版本和目录，不必重复下载：

```powershell
.venv\Scripts\python.exe -m playwright install --list
```

Node 依赖安装：

```powershell
npm ci
```

## 3. 登录态管理

DesignKit 用 Playwright `storage_state` 注入会员登录态。默认文件为：

```text
.auth\designkit-cn-release.json
```

需要重新登录时，在本机执行一次 codegen，完成人工登录后关闭窗口：

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright-browsers"
.venv\Scripts\python.exe -m playwright codegen `
  --save-storage=".auth\designkit-cn-release.json" `
  "https://www.designkit.cn/"
```

`.auth/` 已被 `.gitignore` 忽略，不能提交到仓库。CI 使用同一个文件的 Base64 内容保存为 GitHub Secret：

```powershell
$encoded = [Convert]::ToBase64String(
  [IO.File]::ReadAllBytes(".auth\designkit-cn-release.json")
)
$encoded | gh secret set DESIGNKIT_STORAGE_STATE_B64 --repo Prectie/AutoUI
gh secret list --repo Prectie/AutoUI
```

测试也支持显式覆盖登录态路径：

```powershell
$env:DESIGNKIT_STORAGE_STATE = "$PWD\.auth\designkit-cn-release.json"
```

登录态过期时，重新生成文件并更新 Secret；不要把账号、密码或 storage state 写入测试代码、日志或 Issue。

## 4. 本地执行

### 4.1 单元测试和收集检查

```powershell
.venv\Scripts\python.exe -m pytest tests/unit_test -o addopts=
.venv\Scripts\python.exe -m pytest --collect-only -q --strict-markers -o addopts=
```

### 4.2 DesignKit 真实回归

默认配置来自 `autoui/core/config/environments/defaults.yaml`（`cn/release`）。可以显式指定目标：

```powershell
.venv\Scripts\python.exe -m pytest `
  tests/web/designkit/test_editor_add_title_vip_font_download.py `
  --site cn `
  --env release `
  --browser chromium `
  --output=artifacts/playwright `
  --tracing=retain-on-failure `
  --screenshot=only-on-failure `
  --alluredir=artifacts/allure-results `
  --clean-alluredir `
  -o addopts=
```

`pyproject.toml` 的本地默认参数包含 `--headed`。无图形界面、脚本化执行或复现 CI 时必须传 `-o addopts=`，再由命令行显式控制浏览器参数。

### 4.3 使用 Allure 3 生成和打开报告

推荐让 Allure 3 包装 pytest，使命令退出码和报告生成保持在同一次运行中：

```powershell
npx allure run `
  --output artifacts/allure-report `
  -- `
  .venv\Scripts\python.exe -m pytest `
  -o addopts= `
  --browser chromium `
  --output=artifacts/playwright `
  --tracing=retain-on-failure `
  --screenshot=only-on-failure `
  --junit-xml=artifacts/junit.xml `
  --alluredir=artifacts/allure-results `
  --clean-alluredir
```

报告生成后可以用以下命令启动本地静态服务：

```powershell
npm run allure:open
```

报告配置位于 `allurerc.mjs`。其中 `historyPath` 指向 `artifacts/allure-history/history.jsonl`，保留最近 30 次运行的历史数据。

## 5. 产物位置与查看顺序

| 产物 | 用途 |
|---|---|
| `artifacts/allure-report/` | Allure Report 3 静态报告，入口为 `index.html` |
| `artifacts/allure-results/` | Allure 原始测试结果和附件索引 |
| `artifacts/allure-history/history.jsonl` | 跨运行趋势历史；本地运行时保留在工作区，CI 由分支缓存恢复/保存 |
| `artifacts/playwright/` | pytest-playwright 为每个测试项生成的截图、Trace、视频和下载目录 |
| `artifacts/junit.xml` | CI 或其他机器消费的 JUnit 摘要 |

失败定位建议按以下顺序：

1. 在 Allure 中先看业务步骤、异常和参数，确认失败发生在哪个业务操作。
2. 在同一个测试项中打开 `Playwright Trace`，查看 Locator、点击/输入、DOM、网络和时间线。
3. 需要下载原始文件时，从 `artifacts/playwright/` 或 CI artifact 获取 `trace.zip`、截图和视频。
4. 用 JUnit XML 判断 CI 门禁结果；不要用报告页面的聚合展示替代 pytest outcome。

## 6. CI 行为

`.github/workflows/autoui-ci.yml` 在 push 和 Pull Request 时执行：

1. 安装锁定的 Python、Node、Allure 3 和 Chromium 依赖。
2. 从 `DESIGNKIT_STORAGE_STATE_B64` 还原会员登录态。
3. 按 `xdist -n 2` 并行运行回归，显式关闭 `pyproject.toml` 的 `--headed`。
4. 由 `allure run` 生成报告，并透传 pytest 退出码。
5. 按分支恢复最近的 Allure history，运行后用唯一 key 保存新 history；缓存异常只影响趋势，不阻断 pytest 门禁。
6. 无论测试成功或失败，都上传 `artifacts/`。

History 使用 GitHub 官方 `actions/cache` 的 restore/save 两步模式；当前 workflow 使用 Node 24 运行时的 `actions/cache@v5`，缓存 key 包含分支、run id 和 run attempt，因此不会覆盖不可变的旧缓存。[官方 actions/cache 文档](https://github.com/actions/cache)

## 7. 常见故障

| 现象 | 检查与处理 |
|---|---|
| `Missing DESIGNKIT_STORAGE_STATE_B64` | 在仓库 `Prectie/AutoUI` 配置同名 Secret；不要把 Secret 值打印到日志。 |
| `登录态文件不存在` | 检查 `.auth/designkit-cn-release.json` 或 `DESIGNKIT_STORAGE_STATE` 路径。 |
| `No XServer` / headed 启动失败 | 使用 `-o addopts=` 覆盖默认 `--headed`。CI 已包含该参数。 |
| `没有找到名称为「点字少年」的可选择 VIP 字体` | 页面字体清单发生变化；更新测试数据中的 `VIP_FONT_NAME`，不要恢复随机选择。 |
| Allure 没有 Trace | `trace` 默认只在失败时保留；先确认 pytest 确实失败，再查看原始 `artifacts/playwright/`。 |
| 历史趋势从零开始 | 检查 `artifacts/allure-history/history.jsonl` 是否在运行前恢复、CI cache 是否命中；单次缓存 miss 不影响当前报告。 |

## 8. 当前验收清单

```text
[ ] .venv\Scripts\python.exe -m pytest tests/unit_test -o addopts= 通过
[ ] --collect-only -q --strict-markers 通过
[ ] DesignKit 真实场景能够应用指定 VIP 字体并下载结果
[ ] 失败测试项可从 Allure 打开 Playwright Trace
[ ] npx allure run 能生成报告并保留 pytest 退出码
[ ] CI Secret 存在且远端 Actions 成功
[ ] 连续运行后 history JSONL 能产生跨运行趋势
```
