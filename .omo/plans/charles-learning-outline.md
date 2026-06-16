# Charles 系统学习大纲：macOS 零基础 14 天标准版

## TL;DR
> **Summary**: 这是一套面向 macOS 零基础用户的 Charles Proxy 14 天系统学习计划，由我提供讲解、示例、练习说明和检查标准；用户本人完成所有实践操作。
> **Deliverables**: 14 天课程路径；每日目标、教学内容、练习、达标标准、常见坑；安全伦理边界；最终综合项目。
> **Effort**: Medium，每天 45-90 分钟。
> **Parallel**: NO，按天顺序学习。
> **Critical Path**: 代理原理 → HTTP 抓包 → HTTPS/证书 → 定位过滤 → 修改请求/响应 → Rewrite/Map → 移动端与排错 → 综合项目。

## Context
### Original Request
用户希望系统性学习 Charles，并明确要求：教学内容由我提供，用户实际行动，不需要指派任何 agent 帮用户完成任务。

### Interview Summary
- 学习场景：全覆盖。
- 当前基础：零基础。
- 操作系统：macOS。
- 学习节奏：14 天标准版，每天约 45-90 分钟。

### Metis Review (gaps addressed)
- 增加安全/伦理边界，避免非授权抓包。
- 使用稳定练习端点，例如 `https://httpbin.org/get`、`https://httpbin.org/post`。
- 将 iPhone/iPad 抓包作为移动端实践内容纳入，但不扩展到 Android-heavy 路线。
- 每天固定包含：目标 / 教学内容 / 练习 / 达标标准 / 常见坑。

## Work Objectives
### Core Objective
让零基础用户能独立使用 Charles 在 macOS 上完成 Web/API/基础移动端抓包、HTTPS 解密、请求定位、断点修改、Rewrite、Map Local/Remote、弱网模拟、会话保存与常见问题排查。

### Deliverables
- 14 天学习路线。
- 每天一组可执行练习。
- 每天一组二元达标标准。
- 最终综合项目：独立完成一次从抓包到定位、修改、替换、导出、复盘的完整流程。

### Definition of Done
- 用户完成 14 天课程练习。
- 用户能解释 Charles 作为 HTTP/SOCKS 代理的基本工作方式。
- 用户能在 macOS 上安装并信任 Charles Root Certificate。
- 用户能对指定 host 启用 SSL Proxying 并查看 HTTPS 明文内容。
- 用户能使用 Filter、Sequence/Structure、Search、Breakpoints、Repeat、Rewrite、Map Local、Map Remote、Throttle、Export。
- 用户能识别并排查：证书未信任、host 未启用 SSL Proxying、VPN/系统代理冲突、证书固定、规则匹配失败等问题。

### Must Have
- 全程使用简体中文教学。
- 每天 45-90 分钟。
- 所有实践均由用户本人完成。
- 示例优先使用自有环境或公开测试接口，避免对第三方隐私流量进行抓取。

### Must NOT Have
- 不安排任何 agent 代用户完成练习。
- 不教授非授权监听、窃取账号、绕过安全保护等用途。
- 不把课程扩展成完整网络协议或 TLS/PKI 深课，只讲 Charles 使用必需概念。
- 不以 Windows/Linux 为主线。

## Verification Strategy
> ZERO HUMAN INTERVENTION for syllabus review; learner practice remains user-executed.
- Test decision: 教学计划文本自检，无代码测试框架。
- QA policy: 每天都有用户可执行练习和达标标准。
- Evidence: 用户可自行保存 Charles session、截图或笔记；不由 agent 代做。

## Execution Strategy
### Learning Waves
Wave 1: Day 1-3，代理/HTTP/基础抓包。
Wave 2: Day 4-6，HTTPS、过滤定位、会话管理。
Wave 3: Day 7-10，断点、重发、Rewrite、Map。
Wave 4: Day 11-14，弱网、移动端、排错、综合项目。

### Dependency Matrix
- Day 2 依赖 Day 1 的安装与代理概念。
- Day 4 依赖 Day 2-3 的 HTTP 请求/响应理解。
- Day 8-10 依赖 Day 5 的精准定位能力。
- Day 13 依赖 Day 4、8、9、10 的常见失败现象。
- Day 14 依赖全部前置能力。

### Agent Dispatch Summary
不派发执行 agent。学习执行者为用户本人；我负责讲解、答疑、复盘和下一课内容提供。

## TODOs
> Implementation + Test = ONE learning day. 每日均由用户本人执行练习。

- [ ] 1. Day 1 — 认识 Charles 与 Web 代理基础

  **What to do**: 学习 Charles 是什么、HTTP/SOCKS 代理是什么、请求从浏览器到服务器再返回的路径；在 macOS 安装 Charles，熟悉主界面 Structure、Sequence、Recording、Clear、Tools 菜单。
  **Must NOT do**: 不抓取登录账号、聊天、支付等隐私流量。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Official: `https://www.charlesproxy.com/documentation/proxying/` - Charles proxying overview.

  **Acceptance Criteria**:
  - [ ] 能用自己的话说明“浏览器 → Charles → 服务器”的代理链路。
  - [ ] 能打开 Charles 并识别 Structure 与 Sequence 两种视图。

  **QA Scenarios**:
  ```
  Scenario: 基础界面识别
    Tool: Charles GUI
    Steps: 打开 Charles，点击 Structure、Sequence、Recording、Clear。
    Expected: 能说出每个按钮/视图的用途。
    Evidence: 用户学习笔记。

  Scenario: 伦理边界
    Tool: 自检
    Steps: 写下 3 类不应抓取的流量。
    Expected: 包含他人账号、支付、聊天/隐私数据。
    Evidence: 用户学习笔记。
  ```

- [ ] 2. Day 2 — macOS 系统代理与第一条 HTTP 请求

  **What to do**: 理解系统代理；确认 Charles 自动配置 macOS 代理；访问 `http://httpbin.org/get`，观察 URL、Method、Status、Request Headers、Response Body。
  **Must NOT do**: 不同时开启多个代理/VPN 干扰练习。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Practice endpoint: `http://httpbin.org/get`.

  **Acceptance Criteria**:
  - [ ] Charles 中能看到 `httpbin.org/get` 请求。
  - [ ] 能指出 method、status code、request headers、response body。

  **QA Scenarios**:
  ```
  Scenario: 抓到 HTTP 请求
    Tool: Browser + Charles
    Steps: 清空 Charles；浏览器访问 http://httpbin.org/get；打开该请求详情。
    Expected: Status 为 200；响应 body 包含 headers/origin/url 字段。
    Evidence: Charles session 或截图。

  Scenario: 无流量排查
    Tool: macOS System Settings + Charles
    Steps: 如果 Charles 无记录，检查 macOS Wi-Fi/Network 代理是否指向 127.0.0.1:8888。
    Expected: 修正后能看到请求。
    Evidence: 用户排查笔记。
  ```

- [ ] 3. Day 3 — HTTP 请求/响应结构

  **What to do**: 学习 URL、query、headers、body、status code、content-type；分别访问 `http://httpbin.org/get?name=charles` 和向 `http://httpbin.org/post` 发送 POST（可用浏览器工具或 API 工具）。HTTPS POST 留到 Day 4 之后再看明文。
  **Must NOT do**: 不把敏感 token、cookie 粘贴到公开测试站点。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Practice endpoints: `http://httpbin.org/get?name=charles`, `http://httpbin.org/post`.

  **Acceptance Criteria**:
  - [ ] 能区分 query parameter 与 request body。
  - [ ] 能解释常见 status code：200、301/302、400、401、403、404、500。

  **QA Scenarios**:
  ```
  Scenario: GET 参数定位
    Tool: Browser + Charles
    Steps: 访问 http://httpbin.org/get?name=charles；查看 Query/String 或 URL。
    Expected: 能定位 name=charles。
    Evidence: 用户笔记。

  Scenario: 错误码识别
    Tool: Browser + Charles
    Steps: 访问 https://httpbin.org/status/404。
    Expected: Charles 中 Status 为 404，用户能说明含义。
    Evidence: 用户笔记。
  ```

- [ ] 4. Day 4 — HTTPS 与 Charles Root Certificate

  **What to do**: 学习 HTTPS 为什么默认看不到明文；安装 Charles Root Certificate 到 macOS Keychain，并设置 Always Trust；为 `httpbin.org` 启用 SSL Proxying；访问 `https://httpbin.org/get`。
  **Must NOT do**: 不启用 `*:*` 全量 HTTPS 解密作为长期默认设置。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Official: `https://www.charlesproxy.com/documentation/proxying/ssl-proxying/` - SSL Proxying and certificate trust.

  **Acceptance Criteria**:
  - [ ] macOS Keychain 中 Charles Root Certificate 被信任。
  - [ ] Charles 能看到 `https://httpbin.org/get` 的明文响应。
  - [ ] 能解释“证书已信任”和“host 已启用 SSL Proxying”是两件事。

  **QA Scenarios**:
  ```
  Scenario: HTTPS 明文查看
    Tool: Charles + Browser + Keychain Access
    Steps: 安装并信任证书；对 httpbin.org 启用 SSL Proxying；访问 https://httpbin.org/get。
    Expected: Response 可读，不再只是 CONNECT 隧道。
    Evidence: Charles session 或截图。

  Scenario: Host 未启用
    Tool: Charles
    Steps: 临时关闭 httpbin.org SSL Proxying 后再次访问。
    Expected: 理解为何看不到 HTTPS 明文。
    Evidence: 用户排查笔记。
  ```

- [ ] 5. Day 5 — 过滤、搜索与快速定位请求

  **What to do**: 学习 Filter、Focus、Search、Structure/Sequence 对比；只关注 `httpbin.org`；按 host、path、status、method 定位请求。
  **Must NOT do**: 不在大量无关请求里盲目查找。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Pattern: Charles GUI filtering/searching workflow.

  **Acceptance Criteria**:
  - [ ] 能在 30 秒内从多条请求中定位指定 host/path。
  - [ ] 能说明 Structure 适合按域名看，Sequence 适合按时间线看。

  **QA Scenarios**:
  ```
  Scenario: 精准定位
    Tool: Charles
    Steps: 连续访问 /get、/headers、/status/404；使用 Filter 搜索 httpbin。
    Expected: 只显示相关请求，并能定位 404 请求。
    Evidence: 用户笔记。

  Scenario: 搜索失败排查
    Tool: Charles
    Steps: 搜索不存在的 path；再改为搜索 host。
    Expected: 理解搜索词过窄会导致误判。
    Evidence: 用户笔记。
  ```

- [ ] 6. Day 6 — 保存、导出与复盘会话

  **What to do**: 学习保存 `.chls` 会话、导出 HAR/文本、清理会话、给请求做 Notes；建立“问题复盘模板”：现象、请求、参数、响应、结论。
  **Must NOT do**: 导出前不应包含敏感 cookie/token/password。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Charles session save/export features.

  **Acceptance Criteria**:
  - [ ] 能保存一份只包含 httpbin 练习流量的 session。
  - [ ] 能导出 HAR，并知道分享前要脱敏。

  **QA Scenarios**:
  ```
  Scenario: 会话保存
    Tool: Charles
    Steps: 清空；访问 3 个 httpbin 地址；保存 session。
    Expected: 重新打开后仍能看到请求记录。
    Evidence: 本地 .chls 文件。

  Scenario: 脱敏检查
    Tool: Charles
    Steps: 导出前检查 headers/cookies。
    Expected: 不包含敏感认证信息。
    Evidence: 用户检查清单。
  ```

- [ ] 7. Day 7 — Breakpoints：拦截并修改请求/响应

  **What to do**: 学习 Breakpoints 的用途；对 `https://httpbin.org/get?role=user` 设置断点，修改 query 或 header；观察服务端回显变化。
  **Must NOT do**: 不对真实生产业务做破坏性修改。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Charles Breakpoints tool.

  **Acceptance Criteria**:
  - [ ] 能拦截指定请求并修改参数。
  - [ ] 能说明请求断点与响应断点的差异。

  **QA Scenarios**:
  ```
  Scenario: 修改请求参数
    Tool: Charles + Browser
    Steps: 对 httpbin.org/get 设置 Breakpoint；访问 ?role=user；拦截后改为 role=admin-test。
    Expected: 响应 args 中显示修改后的测试值。
    Evidence: Charles session 或截图。

  Scenario: 断点过宽
    Tool: Charles
    Steps: 设置过宽匹配导致多个请求被拦截。
    Expected: 能收窄到 host/path 级别。
    Evidence: 用户排查笔记。
  ```

- [ ] 8. Day 8 — Repeat、Compose 与接口复现

  **What to do**: 学习 Repeat 重发请求、Advanced Repeat 多次重发、Compose 编辑请求；用 httpbin 复现实验请求。
  **Must NOT do**: 不对第三方服务高频重放造成压力。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Charles request repeat/compose workflows.

  **Acceptance Criteria**:
  - [ ] 能对一条请求 repeat 并比较两次响应。
  - [ ] 能用 Compose 修改 header 或 query 后发送。

  **QA Scenarios**:
  ```
  Scenario: 请求复现
    Tool: Charles
    Steps: 选中 https://httpbin.org/get 请求；执行 Repeat。
    Expected: 出现新的相同请求记录，响应 200。
    Evidence: Charles session。

  Scenario: 安全重放
    Tool: 自检
    Steps: 写下为什么不能对支付/下单接口随意 Repeat。
    Expected: 答案包含副作用、重复操作、服务压力。
    Evidence: 用户笔记。
  ```

- [ ] 9. Day 9 — Rewrite：自动修改请求与响应

  **What to do**: 学习 Rewrite Set、Location、Rule；先添加一个明显 header，如 `X-Charles-Learn: day9`；再尝试对响应 body 做简单替换。
  **Must NOT do**: 不一次写复杂规则；不使用过宽 location 影响所有网站。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Official: `https://www.charlesproxy.com/documentation/tools/rewrite/` - Rewrite rules and debugging.

  **Acceptance Criteria**:
  - [ ] 能创建只匹配 `httpbin.org` 的 Rewrite Set。
  - [ ] 能在服务端回显中看到新增 header。
  - [ ] 知道 Rewrite 失败时查看 Error Log / Debug。

  **QA Scenarios**:
  ```
  Scenario: Header Rewrite
    Tool: Charles + Browser
    Steps: Location 设为 https://httpbin.org/*；请求 header 添加 X-Charles-Learn: day9；访问 /headers。
    Expected: 响应回显包含 X-Charles-Learn。
    Evidence: Charles session 或截图。

  Scenario: 规则未命中
    Tool: Charles Error Log
    Steps: 故意把 path 写错；访问 /headers；查看未生效现象。
    Expected: 能通过 location/path 修正规则。
    Evidence: 用户排查笔记。
  ```

- [ ] 10. Day 10 — Map Local 与 Map Remote

  **What to do**: 学习 Map Local 用本地文件替代远程响应；学习 Map Remote 将请求映射到另一个远程位置；理解动态服务端脚本不会被 Map Local 执行。
  **Must NOT do**: 不把真实线上关键接口长期映射到错误环境。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Official: `https://www.charlesproxy.com/documentation/tools/map-local/` - local files as remote responses.
  - Official: `https://www.charlesproxy.com/documentation/tools/map-remote/` - remapping requests.

  **Acceptance Criteria**:
  - [ ] 能解释 Map Local 与 Rewrite 的区别。
  - [ ] 能解释 Map Local 与 Map Remote 的区别。
  - [ ] 能完成一次本地 JSON 替换练习。

  **QA Scenarios**:
  ```
  Scenario: Map Local JSON
    Tool: Charles + local file
    Steps: 准备本地 JSON 文件；将某个测试 JSON 请求映射到该文件。
    Expected: 浏览器/客户端看到本地 JSON 内容。
    Evidence: 本地文件与 Charles session。

  Scenario: 映射失败
    Tool: Charles
    Steps: 故意让 path 不匹配；观察仍返回远程响应。
    Expected: 能通过 host/path 修正映射。
    Evidence: 用户排查笔记。

  Scenario: Map Remote 远程映射
    Tool: Charles + Browser
    Steps: 将一个测试路径从原 host 映射到另一个公开测试路径；访问原 URL 并观察实际返回来源。
    Expected: 请求仍从原 URL 发起，但响应由目标远程位置提供；用户能说明这不是浏览器重定向。
    Evidence: Charles session 或用户笔记。
  ```

- [ ] 11. Day 11 — Throttle 弱网与性能观察

  **What to do**: 学习网络延迟、带宽、丢包的基本含义；使用 Throttle 预设模拟慢速网络；观察页面/API 请求耗时变化。
  **Must NOT do**: 不把 Throttle 开着忘记关闭，导致后续误判网络问题。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Charles Throttle tool.

  **Acceptance Criteria**:
  - [ ] 能开启/关闭 Throttle。
  - [ ] 能比较正常网络与弱网下请求耗时差异。

  **QA Scenarios**:
  ```
  Scenario: 弱网观察
    Tool: Charles + Browser
    Steps: 访问 https://httpbin.org/delay/2；开启 Throttle 后再次访问。
    Expected: Timing/Duration 变长，用户能解释原因。
    Evidence: Charles session 或截图。

  Scenario: 忘关弱网
    Tool: Charles
    Steps: 关闭 Throttle；再次访问。
    Expected: 请求耗时恢复，知道排查时先看 Throttle 状态。
    Evidence: 用户笔记。
  ```

- [ ] 12. Day 12 — iPhone/iPad 基础抓包（可选但纳入全覆盖）

  **What to do**: 学习移动设备与 Mac 同 Wi-Fi；在 iPhone/iPad Wi-Fi 中设置 HTTP Proxy 指向 Mac IP 和 Charles 端口；安装并信任 Charles 证书；只抓取自己授权的测试流量。
  **Must NOT do**: 不抓取他人设备或非授权 App 的隐私流量；不尝试绕过证书固定保护。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Official SSL Proxying concepts: `https://www.charlesproxy.com/documentation/proxying/ssl-proxying/`.

  **Acceptance Criteria**:
  - [ ] 能让移动设备 HTTP/HTTPS 流量进入 Charles。
  - [ ] 能说明证书固定 App 为什么可能无法解密。
  - [ ] 能在练习后关闭移动设备代理。

  **QA Scenarios**:
  ```
  Scenario: iOS Safari 抓包
    Tool: iPhone/iPad + Charles
    Steps: 设备与 Mac 同 Wi-Fi；设置代理到 Mac IP:8888；访问 https://httpbin.org/get。
    Expected: Charles 出现移动设备请求；启用 SSL Proxying 后可读。
    Evidence: Charles session 或截图。

  Scenario: 证书固定边界
    Tool: 自检
    Steps: 记录某些 App 无法解密的原因。
    Expected: 答案包含 certificate pinning/证书固定。
    Evidence: 用户笔记。
  ```

- [ ] 13. Day 13 — 常见故障排查与 Error Log

  **What to do**: 系统整理排查路径：Charles 没流量、只有 CONNECT、HTTPS 乱码/不可读、证书不被信任、Rewrite 不生效、Map 不命中、VPN 冲突、浏览器绕过代理；学习查看 Error Log。
  **Must NOT do**: 不凭感觉乱改多个设置；一次只改一个变量。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Official Rewrite debugging mentions Error Log: `https://www.charlesproxy.com/documentation/tools/rewrite/`.

  **Acceptance Criteria**:
  - [ ] 能按“是否有流量 → 是否 HTTPS 明文 → 是否规则命中 → 是否外部冲突”的顺序排查。
  - [ ] 能查看 Error Log 并理解其用途。

  **QA Scenarios**:
  ```
  Scenario: HTTPS 不可读排查
    Tool: Charles + Keychain Access
    Steps: 模拟 host 未启用 SSL Proxying；记录现象；启用后复测。
    Expected: 能明确问题原因不是证书安装本身，而是 host 未启用。
    Evidence: 用户排查笔记。

  Scenario: Rewrite 不生效排查
    Tool: Charles Error Log
    Steps: 检查 Rewrite set 是否启用、location 是否匹配、rule 是否作用于 request/response。
    Expected: 找到至少一个可修正原因。
    Evidence: 用户排查笔记。
  ```

- [ ] 14. Day 14 — 综合项目：从抓包到改包再到复盘

  **What to do**: 完成一个完整闭环：清空会话；抓取 `httpbin` GET/POST；启用 HTTPS SSL Proxying；用 Filter 定位；用 Breakpoint 修改一次请求；用 Rewrite 自动添加 header；用 Map Local 替换一次 JSON；导出 session/HAR；写复盘。
  **Must NOT do**: 不使用真实敏感业务作为综合项目素材。

  **Recommended Agent Profile**: 不使用 agent；用户本人操作。

  **References**:
  - Practice: `https://httpbin.org/get`, `https://httpbin.org/post`, `https://httpbin.org/headers`.

  **Acceptance Criteria**:
  - [ ] 能独立完成抓包、HTTPS 解密、定位、断点、Rewrite、Map Local、导出。
  - [ ] 能写出一页复盘：目标、步骤、现象、问题、解决、结论。
  - [ ] 能列出至少 5 个 Charles 常见坑及对应解决办法。

  **QA Scenarios**:
  ```
  Scenario: 综合成功路径
    Tool: Charles + Browser + local file
    Steps: 按 What to do 完整执行；保存 .chls；导出 HAR；写复盘。
    Expected: 每个关键功能都有可展示证据。
    Evidence: .chls/HAR/用户复盘笔记。

  Scenario: 综合排错路径
    Tool: Charles
    Steps: 任选一个失败点，如 Rewrite 未命中或 HTTPS 不可读；按 Day 13 排查。
    Expected: 能定位原因并修复。
    Evidence: 用户排查笔记。
  ```

## Final Verification Wave
> 本学习计划不派发任何执行 agent。最终检查由文本清单完成；用户学习实践由用户本人完成。
- [ ] F1. 大纲完整性自检：确认正好 14 天，每天都有目标/教学内容/练习/达标标准/常见坑。
- [ ] F2. 范围自检：确认 macOS、零基础、全覆盖、45-90 分钟/天。
- [ ] F3. 安全边界自检：确认包含非授权抓包禁止、敏感信息脱敏、证书固定边界。
- [ ] F4. 功能覆盖自检：确认覆盖 SSL Proxying、Charles Root Certificate、Breakpoints、Rewrite、Map Local、Map Remote、Throttle、Export、Error Log、综合项目。

## Commit Strategy
不涉及代码提交。学习证据建议保存在用户本地笔记、截图、`.chls`、HAR 文件中。

## Success Criteria
- 用户能独立配置 macOS + Charles 抓包环境。
- 用户能看懂 HTTP/HTTPS 请求响应的关键字段。
- 用户能用 Charles 定位问题、修改请求/响应、替换资源、模拟弱网。
- 用户能排查 80% 常见 Charles 初学问题。
- 用户明确知道 Charles 的合法使用边界。
