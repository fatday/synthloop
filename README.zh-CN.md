# synthloop

[English](README.md) | **简体中文**

<img width="1536" height="1024" alt="synthloop 项目示意图" src="https://github.com/user-attachments/assets/b84fdbea-c99a-419a-ac46-51603c1507c7" />

**一套由 agent 执行的操作手册，用于构建、审核和迭代 LLM 数据生成器。**

synthloop 不是数据生成库，而是围绕数据生成库的一套*工作流程*：通过分阶段的
操作手册和可填写的模板，让 coding agent 在人参与的情况下，把合成数据生成器
从想法推进到大规模发布。整个过程有明确的质量检查、可恢复的状态记录，以及
可追溯的人工审批节点。

这套手册**不依赖特定 agent**：任何 coding agent 或人都可以阅读 `playbook/`
并执行。同时，它通过 `.claude/skills/` 中的斜杠技能**原生支持 Claude Code**，
通过 `.agents/skills/` 中的仓库技能**原生支持 Codex**。选择你的使用方式：
[Claude Code](#path-a-claude-code)、
[Codex](#path-b-codex)，或
[其他 agent](#path-c-any-other-agent)。

```text
了解背景 → 设计 → 实现 → [ 小规模生成 → 自动化质检 → 修复 ]* → 扩量与发布
                               ↑ 日常反复执行的循环 ↑
```

## 为什么需要它

合成数据项目经常以相似的方式出问题：指标通过了，数据却是错的；自动修复循环
不断修补表面问题，数据分布却悄悄收窄；设计好的能力从未被触发，也没人发现；
六周后，没人说得清哪些代码生成了哪些数据。每种问题都有对应的应对方法。
这个仓库把它们整理成 agent 可以执行、人可以审查的检查清单。

核心原则：

1. **双轨质检**：agent 审核与确定性规则检查能发现不同类型的问题，每轮都需要两者。
2. **阅读原始数据是最有价值的质检活动。** 评判模型和规则可能存在共同盲区；
   人或 agent 直接阅读分层抽样的原始数据，能发现其他方式遗漏的问题。
3. **先诊断，再修复。** 在已批准的范围内，自主修复可以修改提示词、代码和常量，
   但不能收紧验收标准。代码修复需要书面诊断，以及一个在修复前会失败的测试。
4. **防回归机制（ratchet）**：每次事故都要转化为永久的确定性检查，防止质量悄悄退步。
5. **来源追踪和运行统计是生成过程的一部分。** 每次启动前提交代码；从一开始就
   为每项设计行为记录触发次数。

## 仓库结构

```text
CLAUDE.md                  统一操作指南（不依赖 agent 类型；Claude Code 自动加载）
AGENTS.md                  其他 agent 的入口，指向 CLAUDE.md 和操作手册
playbook/
  survey.md                识别工作区目录的用途（首次使用或目录变化时执行）
  00_context.md            阶段 0：了解领域和目标
  01_design.md             阶段 1：设计规格、覆盖要求、现实条件核验
  02_implement.md          阶段 2：生成器、离线回放和运行统计
  03_quality_loop.md       阶段 3：小规模生成、质检和修复循环
  04_scale.md              阶段 4：扩量、监控、发布和复盘
  principles.md            核心规则，优先阅读
  review_rubric.md          数据审核方法和报告要求
  review_backends.md        保留原生 agent harness 的可选审核 API 配置
  workflows.md             两个平台共用的命令流程
  recovery.md              会话恢复、记录和并行协调
  platforms.md             Claude Code 和 Codex 执行适配说明
templates/
  environment.md           工作区共享背景：基础设施、生成器目录、评测目标
                           每个工作区实例化一次，保存为 data_projects/ENVIRONMENT.md
                           注意大小写：模板小写，实例大写
  design_spec.md           每个生成器的设计规格（包含必答问题）
  review_instruction.md    带版本的数据审核指令
  progress.md              可读的进度记录
  project_memory.md        每个生成器的长期记忆（决策和经验）
  data_projects_README.md  创建 data_projects/ 时复制进去的初始 README
.claude/agents/            独立 reviewer 和 refuter 的角色定义
.claude/skills/            斜杠技能：/survey /design /smoke /review /repair
                           /cycle /scale /status
.agents/skills/            Codex 仓库技能：$sl-survey $sl-design
                           $sl-smoke $sl-review $sl-repair
                           $sl-cycle $sl-scale $sl-status
data_projects/             你的工作区状态（本仓库忽略此目录；通常也可作为独立私有仓库）
                           每个生成器一个文件夹
LICENSE                    MIT 许可证
```

## 工作区准备

synthloop 与你的数据生成代码库**并列放置**，生成器代码不放在 synthloop 中：

```text
~/work/
  my-data-infra/    # 你的代码库：生成器代码、模型引擎、CLI、测试
  synthloop/        # 本仓库：操作手册、技能、各生成器的状态
```

Agent 在 synthloop 中读取操作手册和技能，在你的基础设施仓库中操作代码、测试
和生成数据。职责划分始终保持一致：**生成器代码、测试和数据放在你的仓库里；
设计规格、进度记录、记忆和审核历史放在这里。** Agent 使用你现有的基础设施执行
流程，代码 PR 不会混入流程记录，新会话也能通过进度记录接着工作。

接下来选择：**方式 A（Claude Code）**使用斜杠技能，**方式 B（Codex）**使用
仓库技能，或**方式 C（其他 agent）**直接阅读手册并执行同一套流程。

<a id="path-a-claude-code"></a>

## 方式 A：Claude Code

从 synthloop 目录启动 Claude Code，并授予它访问基础设施仓库的权限：

```bash
cd ~/work/synthloop
claude --add-dir ~/work/my-data-infra
```

如果工作区涉及多个仓库，例如评测集、种子数据目录或另一个基础设施仓库，
可以重复使用 `--add-dir`：

```bash
claude --add-dir ~/work/my-data-infra --add-dir ~/work/some-benchmark
```

如果不想每次输入路径，可以把它们保存在 `synthloop/.claude/settings.local.json`
中。此文件属于个人配置，不提交到仓库；每位成员使用自己的本地路径。
之后直接运行 `claude` 即可：

```json
{
  "permissions": {
    "additionalDirectories": ["~/work/my-data-infra", "~/work/some-benchmark"]
  }
}
```

也可以在正在运行的会话中使用 `/add-dir <path>` 添加目录。

你不需要逐个解释目录的用途：`/survey` 会检查提供的工作区根目录，依据实际内容
将其归类为 data-infra、benchmark、seed-corpus、vendored-reference 等，把结果
写入 `data_projects/ENVIRONMENT.md`，只对含义不明确的目录向你确认。
首次执行 `/design` 时会自动进行这一步；添加新目录后可以重新运行。

唯一必需的目录角色是 **data-infra**，即你的数据生成代码库。缺少它时，agent 会
在开始实现前停下来请你提供。评测集、种子语料等属于可选背景，提供后有助于完善设计。

### 首次会话

输入 `/design <your-first-generator>`。技能发现 `data_projects/ENVIRONMENT.md`
不存在时，会先创建它：少量信息通过提问获取，大部分来自阅读基础设施仓库，
包括 CLI、生成器模式、可复用的已有生成器和评测目标。后续项目和会话都能复用这些信息。

### 每个生成器的工作循环

```text
/design my-generator     # 了解需求、制定带覆盖指标的规格 → 你批准（审批节点 1）
                         # agent 按规格在你的基础设施仓库中实现
/smoke my-generator      # 提交代码、小批量生成、统计覆盖、阅读原始数据
/review my-generator     # 双轨质检、独立反驳审核结论 → 最终判定
/repair my-generator     # 先诊断再修复，补充防回归测试
                         # 重复 smoke → review → repair，直到连续两轮通过
                         # → 你批准（审批节点 2）
/scale my-generator      # 启动前检查、启动、监控、发布
/status                  # 查看所有生成器的进度总览
```

你需要参与两个审批节点、处理待确认的问题，也可以随时抽查原始数据。
请持续做抽查，这是最有价值的质检方式之一。

### 自动执行内部循环

`/cycle` 执行有边界的 smoke → review → repair 循环，与 Codex 使用相同的流程。
还可以通过可选的 `/loop` 调度再次调用它：

```text
/cycle my-generator          # 执行到连续两轮通过，或遇到必须停止的条件
/loop /cycle my-generator    # 可选调度；到达终止条件时取消后续唤醒
```

经批准的基线会确定联合通过率目标（建议默认值为 95%）、各分组最小样本量、
覆盖率下限、分布漂移限制，以及轮次、成本和时间预算。轨道 A 检查所有生成的行，
包括被拒绝的行；轨道 B 使用固定版本的审核标准。两个轨道各自达到 95%，
不代表联合通过率达到 95%。语义审核如果采用抽样，不能把未审核的行默认为通过。

极小规模的功能 smoke 用于检查指定路径是否可用，不用于估计总体频率。
质量验证使用经批准的样本量。随机采样造成的正常覆盖波动不自动视为回归，
应结合固定下限、分布漂移和配对回放来判断。

首次完整通过后，在同一个已验证版本上换一个随机种子生成确认批次。
连续两轮完整通过后停止，交由人审查具体扩量方案。任何修改或失败都会打断连续通过
计数。遇到必须人工批准的事项、已确认的回归、尚未核清的基础设施故障，或预算上限时，
循环会提前停止。收紧验收标准、削弱评判或防回归检查、修改固定基线、扩大范围，
仍然需要人工批准。循环不会自动扩量。

### 日常使用

- **恢复工作**：新建会话 → `/status` → 选择项目。Agent 读取 `progress.md`，
  核对其中引用的任务和产物，确认运行状态，再从已保存的数据块继续未完成的审核。
- **同时开发多个生成器**：每个生成器使用独立会话、基础设施 worktree 和输出前缀，
  每个项目同一时间只有一个写入方。共享环境和手册的修改按顺序进行；仅分开项目文件夹，
  无法隔离同一个基础设施仓库的 HEAD。批次元数据中也要记录框架版本。
- **团队协作**：克隆两个仓库，执行相同的启动命令，即可复用环境文件、操作手册
  和各项目的状态。

<a id="path-b-codex"></a>

## 方式 B：Codex

从 synthloop 目录启动 Codex，并让数据基础设施仓库在同一工作区或会话中可访问：

```bash
cd ~/work/synthloop
codex --add-dir ~/work/my-data-infra
```

Codex 会自动读取 `AGENTS.md`，并发现 `.agents/skills/` 中的仓库技能。
通过 `/skills` 或直接提及技能名称来调用 synthloop 流程：

```text
$sl-design my-generator
$sl-smoke my-generator
$sl-review my-generator
$sl-repair my-generator
$sl-cycle my-generator
$sl-status
```

`sl-*` 前缀是有意保留的：Codex 自带 `/status`、`/review` 等斜杠命令，
它们属于 Codex 会话命令，不是 synthloop 的工作流命令。

### 首次会话

从 `$sl-design <your-first-generator>` 开始。如果 `data_projects/ENVIRONMENT.md`
不存在，技能会先执行 `$sl-survey`，识别可访问目录的用途，并创建共享环境文件。

### 每个生成器的工作循环

```text
$sl-design my-generator     # 设计规格和覆盖指标 → 你批准
$sl-smoke my-generator      # 提交代码、小批量生成、统计覆盖、阅读原始数据
$sl-review my-generator     # 双轨质检、独立反驳审核结论 → 最终判定
$sl-repair my-generator     # 先诊断再修复，补充防回归测试
$sl-cycle my-generator      # 重复 smoke → review → repair，直到检查节点
$sl-scale my-generator      # 仅在明确批准扩量后执行
$sl-status                  # 所有生成器的进度总览
```

其余约定与 Claude Code 相同：`CLAUDE.md` 是统一操作指南，`playbook/` 定义实际
规则，人工审批节点不能跳过，每个工作会话都更新 `progress.md`。
独立审核与自动化的执行细节见[平台适配说明](playbook/platforms.md)。

<a id="path-c-any-other-agent"></a>

## 方式 C：其他 agent

按前文的工作区准备方式，将两个仓库并列克隆。Claude Code 和 Codex 的技能都只是
便捷入口，核心内容在 `playbook/`（阶段、原则、审核标准）和 `templates/` 中。
这些都是普通 Markdown，任何 coding agent 或人都能阅读执行。

使用其他工具（Cursor、Gemini CLI、Aider 或自定义 harness）时：

1. 让 agent 访问本仓库。支持 `AGENTS.md` 的工具会自动读取入口指南；
   否则，先要求 agent 阅读 `AGENTS.md`。
2. `AGENTS.md` 会指向 `CLAUDE.md` 中不依赖平台的统一操作规则，以及 `playbook/`
   中的各阶段。它还提供一张映射表，解释不使用技能时该做什么，包括没有独立编号
   阶段文件的工作区调查（survey）和状态查看（status）。
3. 首次使用时，按 `AGENTS.md` 的 “First time” 一节完成初始化：创建
   `data_projects/`，复制 `templates/data_projects_README.md` 到其中，执行
   `playbook/survey.md`，并由 `templates/environment.md` 创建
   `data_projects/ENVIRONMENT.md`。之后逐步阅读相应阶段文件
   （`playbook/00_context.md`、`01_design.md`、`03_quality_loop.md`、`04_scale.md`），
   遵循检查清单和退出条件。同样需要经过两个主要人工审批节点。

核心阶段规则和模板不依赖平台。两套技能都指向[共享工作流](playbook/workflows.md)，
平台特定的执行细节则放在[平台适配说明](playbook/platforms.md)中。

审核 agent 可以选择使用用户提供的模型 API，同时保留 Codex 或 Claude Code 的
harness。在工作区的 `ENVIRONMENT.md` 中记录选择即可；配置方式、协议要求，
以及原生子 agent 与独立 CLI worker 会话的区别，见[审核后端说明](playbook/review_backends.md)。
没有明确选择时，独立审核 agent 默认使用当前会话的模型、provider 和认证，
不会要求额外配置 API。用户明确选择的 API 如果配置不完整或调用失败，会报告问题，
不会悄悄换回当前会话的模型。

## 公开框架，私有状态

本仓库只保存框架。工作区专属内容，包括实例化的 `ENVIRONMENT.md`、各项目文件夹
和运行脚本，都放在 `data_projects/` 中；**本仓库通过 gitignore 忽略此目录**。
普通的 `git add .` 不会包含它。也不要把私有细节复制进受版本控制的模板或手册中。
Gitignore 无法防止强制添加文件，也无法防止将私有内容复制到公开文件。

这也是远端仓库里看不到 `data_projects/` 的原因：它在首次使用前并不存在。
`/design` 会在本地创建它，之后保留在本地或你的私有仓库中，而不是提交到公开框架仓库。

工作区状态有两种管理方式：

```bash
# 1. 仅保存在本地（个人使用）：直接使用，不纳入版本控制。
/design my-generator          # 首次使用时创建 data_projects/

# 2. 独立私有仓库（推荐团队使用）：单独对状态做版本管理。
cd ~/work/synthloop
git clone git@your-host:your-org/synthloop-projects.git data_projects
```

采用第二种方式时，agent 会在工作过程中把进度、规格和记忆等流程状态提交到私有仓库。
团队成员克隆同一对仓库，即可共享状态，同时保持公开框架仓库不包含私有信息。

## 持续工作与恢复

Agent 直接使用现有基础设施的命令和记录来执行手册。将运行中的任务、审核进度、
批次结果和下一步行动保存在 `progress.md` 中。[恢复指南](playbook/recovery.md)
说明了如何避免重复执行，以及如何跨会话复用适用的已有授权。
不需要额外的框架运行时、强制 JSON 状态文件或框架测试套件。

## 人的职责

你负责最终批准和方向选择。循环把你的注意力留给两件事：判断数据是否*真正符合
你的需求*，以及用 agent 无法控制的来源核实它的结论，例如你的监控面板和亲自抽查的
数据。其余执行工作交给 agent。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
