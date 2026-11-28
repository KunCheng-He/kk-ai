# kk-ai 仓库说明

本文件是本仓库的运行手册，**新会话开始时会被自动加载**。写它是为了让任何 agent 在动手之前知道：这个仓库是什么、东西该放哪、怎么用、按什么规矩改。

---

## 1. 这是什么

一个**跨 harness 的 AI 资源仓库**：存放通用 skill 与各 AI 编码工具的专属资源，供不同项目按需链接使用。

适配的 harness 包括 DeepSeek Harness（DSH）、OpenCode、Pi，以及以后可能出现的其他工具。

**仓库本身不是可运行的项目**，没有构建、没有依赖安装、没有测试套件。它是一堆会被别的项目"取用"的资产。

## 2. 目录结构

```
kk-ai/
├── skills/                  通用层：任何 harness 都能用的 skill
│   └── <name>/              SKILL.md 必需；references/ scripts/ assets/ 按需
├── opencode/                OpenCode 专属层
│   ├── agents/              agent 定义（markdown + frontmatter）
│   ├── cmds/                command 定义
│   └── skills/              OpenCode 专属 skill
├── pi/                      Pi 专属层
│   └── extends/             扩展源码（pi-k-subagent、pi-agent-switcher）
└── AGENTS.md                本文件
```

### 两层的划分依据

判断一个资源放哪，只问一句：

> **把它单独拷给另一个项目、换一个 harness，还能不能用？**

- **能**（纯指令、纯脚本、纯模板）→ `skills/`
- **不能**（用到某工具专属的目录约定、frontmatter 字段、运行时 API）→ `<harness>/`

`<harness>/` 目录的内容只对该工具有意义。不要把 OpenCode 专属的东西放进 `skills/`，也不要让 `skills/` 里的技能硬依赖某个平台。

## 3. 通用与项目级的关系

**通用 skill 是"货"，harness 目录是"货架"，符号链接是"取货"。**

- 全局要用的 skill → 链到各 harness 的用户级目录
- 某个项目要用的 skill → 链到 `<项目>/.opencode/skills/`、`<项目>/.dsh/skills/` 等
- 链接一律用**绝对路径**，指向本仓库源目录；仓库改一处，所有项目同步生效

因此**链接目录不进 git**，换机器重新链即可。初始化这类工作由 `skills/project-init` 负责。

## 4. 有哪些内容：用命令看，不要在这里列

**本文件不列举当前有哪些 skill、哪些 agent。** 那些内容会变，写死在文档里就必然过期，还得手动维护两遍——违反「一个事实只写一处」。

需要知道当前有什么，一律现查：

```bash
skills/project-init/scripts/init.sh index            # 仓库现在有什么
skills/project-init/scripts/init.sh discover <项目>   # 某个项目现在接了什么
```

`index` 会列出：

- `skills/` 下每个通用 skill 及其 `description`
- 注册表里每个 harness 的项目级目录约定与核实状态
- 该 harness 目录下 `agents/`、`cmds/`、`skills/` 里的全部资源

`<harness>/` 下的资源由**扫目录**得到，增删文件后立刻可见，不需要改任何登记文件。

唯一的例外是 `pi/extends/` 这类扩展源码：它不参与链接，`index` 不列，需要时直接看目录。

## 5. 使用方式

### 给项目接上 skill

```bash
# 看仓库现在有什么、项目现在接了什么
skills/project-init/scripts/init.sh index
skills/project-init/scripts/init.sh discover <项目路径>

# 预览后执行
skills/project-init/scripts/init.sh plan <项目路径> --harness opencode --skill mermaid --agent 诸葛亮
skills/project-init/scripts/init.sh init <项目路径> --harness opencode --skill mermaid --agent 诸葛亮
```

参数写法：通用 skill 用 `--skill <name>`，harness 专属用 `--skill opencode/herdr`；agent 同理支持 `--agent opencode/诸葛亮`。

详细工作流见 `skills/project-init/SKILL.md`。

### 手工等价操作

```bash
ln -s ~/Code/kk-ai/skills/<name> ~/.dsh/skills/<name>              # 全局
ln -s ~/Code/kk-ai/skills/<name> <项目>/.opencode/skills/<name>    # 项目级
```

## 6. 维护原则

### 6.1 如无必要，勿增实体 ⭐

**这是本仓库最重要的原则。**

- 不为"以后可能用到"提前加结构：不加空目录、不加预留字段、不加没人用的抽象层
- 基于某个需求要加一个字段，就**只加这一个字段**，不要顺手补齐一堆"看起来对称"的字段
- 能删就删：过时的 skill、被新 skill 覆盖的旧文件、不再使用的脚本，确认无引用后删除，而不是留着注释掉

判断标准：**现在就有东西在读它 / 用它吗？** 没有就不加。

### 6.2 一个事实只写一处

- 目录约定、路径、参数说明，写在唯一的地方，别处引用而不是复制
- 文档里出现的事实（路径、命令、开关）必须与代码实际行为一致；改了代码要同步文档

### 6.3 会变的东西，写"怎么查"而不是"是什么"

- **不在文档里列清单**：有哪些 skill、有哪些 agent、有哪些 harness、各版本号——这些都在变，写死一处就要维护两处
- 正确做法是记录**命令或入口**：`init.sh index` 看仓库内容，`discover` 看项目现状，`ls` 看目录
- 判断标准：**这段内容会不会因为别人正常干活而变化？** 会 → 只写怎么查；不会（结构约定、划分依据、操作步骤）→ 可以写

### 6.4 不臆造未核实的能力

- 没在真机上确认过的路径、字段、工具名，**不要写成确定事实**
- 不确定就标"未核实"，或者直接问用户

### 6.5 改动要可验证

- 改 `project-init` 这类有脚本的技能，**改完必须实际跑一遍**（至少 `index` + 一个临时项目的 `plan`/`init`）
- 提交前确认没有残留的旧路径、旧名称

### 6.6 不乱动仓库以外的东西

- 全局配置目录（`~/.dsh`、`~/.config/opencode`、`~/.agents`、`~/.pi`）属于用户的个人环境
- 除非用户明确要求，不要修改、不要删除其中的链接或文件

## 7. 新增一个 skill

1. 判断归属：`skills/` 还是 `<harness>/skills/`（按 §2 的依据）
2. 建目录，写 `SKILL.md`，frontmatter 至少含 `name` + `description`
   - `description` 写清"做什么 + 什么时候用"，多数平台只靠它触发
3. 加 `upstream.json` 记录来源与版本（与现有 skill 保持一致；字段按需写，不要预先铺满）
4. 如果 skill 跨平台且含平台专属用法，正文用平台无关表述，另建 `harness/<平台>.md`
5. 确认 `init.sh index` 能看到它（不用改任何登记文件）
6. 若要同步到某个工具，在对应项目里重新建链接

## 8. 新增一个 harness

前提：仓库里真的有这个工具的专属资源，或用户明确要求接入。

1. 建 `<harness>/` 目录，放好它的资源（`agents/`、`cmds/`、`skills/` 按需）
2. 在 `skills/project-init/scripts/init.sh` 的「harness 注册表」段：
   - `ALL_HARNESSES` 加名字
   - 补 `h_skills_dir` / `h_agent_dirs` / `h_instructions` 分支
   - 补 `harness_status`
   - 路径没核实过就让 `h_skills_verified` 返回 `false`
3. 在 `skills/project-init/references/harnesses.md` 表格补一行，标注验证状态
4. **只注册"该工具的项目级目录约定"，不要登记资源清单**——`<harness>/` 里的文件由脚本扫目录即得

### 什么情况**不需要**改注册表

往 `opencode/agents/`、`opencode/cmds/`、`opencode/skills/`、`skills/` 里增删文件，**什么都不用改**，脚本自动发现。

## 9. 提交规范

采用 Conventional Commits，摘要用中文：

```
<type>(<scope>): <摘要>

<正文：说明动机与要点>
```

- `type`：`feat` / `fix` / `refactor` / `docs` / `chore` / `move`
- `scope`：受影响的 skill 名或目录名，多个用逗号分隔，如 `refactor(skillify, workflow-designer)`
- 正文说明**为什么改**，而不只是改了什么

## 10. 注意事项

1. **本仓库没有根级 README**，本文件是唯一的入口说明；新增全局性约定写在这里，但**不要往这里列清单**（见 §6.3）
2. `skills/woaile-gzh` 与 `skills/kk-obsidian` 有明确适用范围限制，不要把它们的规则套到别的场景
3. `project-init` 是其他所有 skill 进入项目的方式，改动它会波及其它项目
4. `.venv/`、`__pycache__/` 等已被 `.gitignore` 忽略，不要提交
5. 拿不准的结构取舍，先问用户，不要凭感觉加东西——回到 §6.1