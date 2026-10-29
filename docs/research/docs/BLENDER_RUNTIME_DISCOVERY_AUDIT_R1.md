# BLENDER RUNTIME DISCOVERY AUDIT · R1

> `docs/BLENDER_RUNTIME_DISCOVERY_AUDIT_R1.md`
> 项目：钢琴教学双手 3D 交互资产
> 阶段：`BLENDER_RUNTIME_DISCOVERY_AUDIT`（**只读审计**，非生产阶段）
> 日期：2026-09-27　状态：**`READY_FOR_HUMAN_REVIEW`**
>
> **本审计为纯只读**：未卸载、未覆盖、未修改 PATH、未修改 Blender 配置、未切换项目运行时、未删除任何文件。

---

## 0. 一句话结论

> ## 本机**原本就装有 Blender**：`Blender 5.1.2`（MSI 安装到 **`D:\blender\`**，2026-06-27 安装，且有 06-27 / 06-30 实际使用痕迹）。
> ## 上一轮 C1 资格审查**没有使用它**，而是使用了本轮新下载的 portable **Blender 4.5.9 LTS**。
> ## 当时之所以"没检测到"，是因为检查方法不充分：只查了 PATH（`where blender`）与两个**默认安装路径**，未查注册表 / 开始菜单 / 非系统盘 / 用户配置痕迹。

---

## 1. 审计方法（以及"未改动"的证明）

| 检查手段 | 具体做法 |
| --- | --- |
| PATH 解析 | `where blender`、`command -v blender`、`type -a blender`、逐条打印 `PATH` 条目、检查 `App Paths\blender.exe` |
| 常见安装目录 | 逐一探测 `C:\Program Files\Blender Foundation`、`C:\Program Files (x86)\Blender Foundation`、`C:\Program Files\WindowsApps`、`%LOCALAPPDATA%\Programs`、`%LOCALAPPDATA%\Microsoft\WindowsApps`、`C:\ProgramData\chocolatey\bin`、`%USERPROFILE%\scoop\apps`、Steam common、`D:\Blender`、`D:\Program Files\Blender Foundation` |
| Start Menu / 桌面 | 递归查找 Start Menu（用户 + 全局）与桌面中含 `blender` 的 `.lnk`，并**解析 .lnk 二进制**取出目标路径 |
| 注册表 | `HKLM/HKCU\SOFTWARE\Blender Foundation`、`...\CurrentVersion\App Paths\blender.exe`、三处 `...\CurrentVersion\Uninstall\*`（扫描全部条目匹配 `blender`）、`.blend` 文件关联（HKLM/HKCU `Classes`） |
| 应用安装记录（Store） | `Get-AppxPackage` 匹配 blender；`%LOCALAPPDATA%\Microsoft\WindowsApps` 别名目录；`winget list` |
| 可执行文件搜索 | 在 `C:\Program Files`、`C:\Program Files (x86)`、`%LOCALAPPDATA%`、`%APPDATA%`、`C:\ProgramData`、`D:\`、`E:\`、`C:\Program Files\WindowsApps` 内**受限深度搜索 `blender.exe`** |
| 用户配置痕迹（关键旁证） | 列出 `%APPDATA%\Blender Foundation\`、`%LOCALAPPDATA%\Blender Foundation\` 的全部文件与时间戳 |
| 版本 / build | 对既有安装执行 **`D:\Blender\blender.exe --version --factory-startup`**（仅打印版本后退出）；对两个 exe 读取 **PE VERSIONINFO 资源**（`version.dll`，不执行） |
| 只读性证明 | 运行 `--version` **前后各做一次用户配置目录全量快照（文件数 34、路径 + 大小 + mtime）并 diff** → **完全一致**；并检查 `D:\Blender` 下**是否存在今日被修改的文件** → **一个都没有** |

> PowerShell 工具在本会话持续不回传 stdout，故注册表读取改用 Python `winreg`、PE 版本资源改用 Python `ctypes + version.dll` 完成，结果等价且可复现。

---

## 2. 发现记录（共 **2** 个 Blender）

| # | 精确路径 | 版本 | build | 是否 portable | 是否 WorkBuddy 调用 | Python | user config path | scripts / addons path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **B-1（既有）** | **`D:\Blender\blender.exe`**（安装根 `D:\blender\`） | **5.1.2** | hash **`ec6e62d40fa9`**；build date **2026-05-19**；commit date 2026-05-18 13:43；branch `blender-v5.1-release`；platform Windows | ❌ **不是 portable**（**MSI 安装器安装**，见 §2.1） | ❌ **否**（上一轮从未调用） | **CPython 3.13**（随包 `D:\Blender\5.1\python\bin\python313.dll`） | `%APPDATA%\Blender Foundation\Blender\5.1\config`（**已存在**，`userpref.blend` 最后写入 2026-06-30 22:40） | scripts：`%APPDATA%\Blender Foundation\Blender\5.1\scripts`（含 `addons\addon.py`）；extensions：`...\5.1\extensions\{blender_org, lab_blender_org}`；缓存：`%LOCALAPPDATA%\Blender Foundation\Blender\Cache\*` |
| **B-2（本轮新增）** | **`<USER_HOME>\.workbuddy\binaries\blender\blender-4.5.9-windows-x64\blender.exe`** | **4.5.9 LTS** | hash **`8bf95cbd38d1`**；build date **2026-04-21**；commit time 14:24；branch `blender-v4.5-release`；platform Windows | ✅ **是 portable**（官方 zip 解压，无安装器、无注册表项、未入 PATH） | ✅ **是**（上一轮 C1 实际使用的就是它） | **CPython 3.11.11**（随包 `python311.dll`） | bpy 报告 `%APPDATA%\Blender Foundation\Blender\4.5\config`，但**该目录不存在**（实测 `AppData\Roaming\Blender Foundation\Blender\` 下**只有 `5.1`**）→ 说明 4.5.9 的运行**未落任何用户配置** | 同上规则（`...\4.5\scripts\addons`，**不存在**）；本地资源目录 `<安装目录>\4.5`；exe 旁**无 `config` 目录**（故未处于就地 portable 配置模式） |

### 2.1 B-1 的安装性质证据（判定"非 portable"的依据）

| 证据 | 内容 |
| --- | --- |
| 注册表卸载项 | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{9CB8CCE7-F0F8-418C-9FA1-B09BEE912FD0}` → `DisplayName = Blender`、**`DisplayVersion = 5.1.2`**、`Publisher = Blender Foundation`、**`InstallLocation = D:\blender\`**、`UninstallString = MsiExec.exe /X{9CB8CCE7-…}`、**`InstallDate = 20260627`** |
| 安装器痕迹 | `HKCU\SOFTWARE\Blender Foundation\Blender` → **`Blender_installed = 1`**、**`Blender_installed_desktop = 1`** |
| 文件关联 | `HKLM\SOFTWARE\Classes\.blend` → `blender.5.1`（随 5.1 安装注册；`HKCU\...\FileExts\.blend\UserChoice` 不存在） |
| 快捷方式 | `…\Start Menu\Programs\Blender\Blender 5.1.lnk` 与 `%USERPROFILE%\Desktop\Blender 5.1.lnk`，二者 TargetPath = **`D:\blender\blender-launcher.exe`**，WorkingDir = `D:\blender\` |
| 目录时间戳 | `D:\Blender` 目录 mtime **2026-06-27 08:19**；`blender.exe` mtime 2026-05-19 03:40（构建时间）；用户配置 `5.1` 目录 2026-06-27 08:48，`userpref.blend` **2026-06-30 22:40** |

> 📌 结论：B-1 是**用户用官方 MSI 安装器安装、并主动把安装目录改到 `D:\blender`** 的正式安装，**不是**免安装 zip。
> 该"**非默认安装盘 + 非默认路径**"正是后续检测失败的直接原因（见 §4）。

### 2.2 本机**未**发现的其他形态

| 形态 | 结果 |
| --- | --- |
| `C:\Program Files\Blender Foundation` / `(x86)` | **不存在** |
| Store/AppX 版 Blender | **不存在**（无匹配包、`WindowsApps` 无 blender 别名） |
| Chocolatey / Scoop / Steam | **不存在** |
| `App Paths\blender.exe` | **不存在**（→ `where blender` 必然为空） |
| PATH 中的 blender 条目 | **无**；`BLENDER*` 环境变量 | **无** |
| 全盘 `blender.exe` 命中数 | **恰好 2 个**（即 B-1 与 B-2），无第三个副本 |

---

## 3. 逐项回答指定问题

### A. 在本轮 C1 资产资格审查之前，电脑上是否已经存在 Blender？

> ## ✅ **YES**
> **`Blender 5.1.2`**，路径 `D:\Blender\blender.exe`（安装根 `D:\blender\`），
> **安装日期 2026-06-27**（注册表 `InstallDate = 20260627`），
> 且**有实际使用痕迹**：用户配置 `5.1\config\userpref.blend` 最后写入 **2026-06-30 22:40**、
> `bookmarks.txt` **2026-06-30 22:37**、`extensions\{blender_org, lab_blender_org}` 与 `scripts\addons\addon.py` 均存在。
> 桌面与开始菜单均有其快捷方式。

### B. 为什么当时没有检测到它？

见 §4 根因分析（一句话：**只用 PATH + 两个默认路径去查，且单项失败无可见信号，未做交叉验证**）。

### C. 本轮新安装的 Blender 4.5.9 LTS portable 具体位置？

```
<USER_HOME>\.workbuddy\binaries\blender\blender-4.5.9-windows-x64\blender.exe
```
- 下载归档：`<USER_HOME>\.workbuddy\binaries\blender\blender-4.5.9-windows-x64.zip`（399,051,129 B）
- 官方来源：`https://download.blender.org/release/Blender4.5/blender-4.5.9-windows-x64.zip`
- 解压时间：2026-09-27 20:58～20:59（exe mtime `2026-09-27 20:58:57`）
- **未加入 PATH**；**未创建注册表项**；**未生成用户配置目录**（`AppData\Roaming\Blender Foundation\Blender\` 下只有 `5.1`）

### D. 上一轮真实用于无头检查和渲染的 blender.exe 是哪一个？

> ## ✅ **就是 C 里的那个**：`<USER_HOME>\.workbuddy\binaries\blender\blender-4.5.9-windows-x64\blender.exe`
- 脚本证据：`production_spec/stage1c_c1_qualification/scripts/` 中共 **3 处** 硬编码该绝对路径（`render_all.sh` / `render_closeups.sh` / `render_extra.sh`）；**全项目脚本对 `D:\Blender` 的引用数 = 0**。
- 运行时证据：上一轮实际输出的 banner 为 `Blender 4.5.9 LTS (hash 8bf95cbd38d1 built 2026-04-21 01:33:45)`，与本次审计读取的 build hash **完全一致**。
- **`D:\Blender\blender.exe` 在上一轮**从未被执行**（`D:\Blender` 下无任何 2026-09-26 之后被修改的文件）。**

---

## 4. `ROOT_CAUSE_OF_FALSE_NOT_FOUND`（根因分析）

上一轮的第一步环境检查是这条命令：

```bash
where blender 2>/dev/null; ls "/c/Program Files/Blender Foundation" 2>/dev/null; \
ls "/c/Program Files (x86)/Blender Foundation" 2>/dev/null; echo "---"; python --version
```

其输出仅有 `---` 与 Python 版本号，于是被判定为"本机未安装 Blender"。根因共 **5 条**：

| # | 根因 | 说明 |
| --- | --- | --- |
| **RC-1** | **只查了 PATH** | `where blender` 仅搜索 `PATH`。该安装**不在 PATH**（`App Paths\blender.exe` 缺失、`PATH` 无 blender 条目），其唯一入口是 `.lnk` 快捷方式 → **必然查不到** |
| **RC-2** | **只探测了"官方安装器默认路径"** | 硬编码只查 `C:\Program Files\Blender Foundation` 与 `C:\Program Files (x86)\Blender Foundation`；而实际安装被用户**改到非系统盘 `D:\blender`** → **必然查不到** |
| **RC-3** | **完全没有查"第二类证据源"** | 未查注册表（Uninstall / `HKCU\SOFTWARE\Blender Foundation`）、未查开始菜单与桌面 `.lnk`、未查 `%APPDATA%\Blender Foundation` 用户配置痕迹、未搜索非系统盘 → **错过全部旁证** |
| **RC-4** | **复合命令把失败信号掩盖了** | 命令未用 `set -e`、未逐项 `echo` 结果，`where blender` 的"未找到"被 `2>/dev/null` 吞掉，且**整条命令的退出码取自最后一条命令**（`python --version` → 0），于是**工具层看不到任何失败** |
| **RC-5** | **由单点结果直接下了结论，未做交叉验证** | 在"1 条 PATH 查询 + 2 条硬编码路径"的基础上直接断言"未安装"，未按"找不到 ≠ 不存在"的原则继续确认（本次审计证明该结论是错的） |

> ✅ 本轮据此修正：**不得根据 `where blender` 单项结果判断"没有安装 Blender"**（已按要求写入本文件 §1 方法表）。

---

## 5. 当前状态与影响

| 项 | 结论 |
| --- | --- |
| 并存安装 | 现为"**两个并存**"：用户 MSI 版 **5.1.2**（`D:\blender`）＋ WorkBuddy portable **4.5.9 LTS**（`.workbuddy\binaries\blender`）。**本轮未做任何删改** |
| 是否互相污染 | **否**。二者配置目录按版本号隔离（`...\Blender\5.1` vs `...\Blender\4.5`，后者不存在）；4.5.9 未写任何用户配置 |
| 本轮是否改动既有安装 | **否**（已验证）：`D:\Blender` 下**无**今日修改的文件；用户配置目录运行前后快照 **34 个文件完全一致（diff 为空）** |
| 是否改动 PATH / 注册表 / 文件关联 | **否**。未新增 PATH 条目、未新增注册表项、未改动 `.blend` 关联 |
| 对 C1 结论的影响 | **无实质影响**。C-1 资产的官方最低要求为 **Blender 4.2 LTS 或更新**，**4.5.9 与 5.1.2 均满足**；C1 的全部数据（几何统计、拓扑枚举、渲染）来自 4.5.9，过程已记录、可复现 |
| 潜在风险（仅记录，不处理） | 若未来某次运行**保存了偏好设置**，4.5.9 会在 `%APPDATA%\Blender Foundation\Blender\4.5\` 新建配置目录；当前**未发生**。另：若日后需要严格复核，可选用 5.1.2 复跑同一批脚本（**本轮不做**） |

---

## 6. 本轮未做（合规确认）

- 🚫 未卸载任何 Blender（`D:\Blender` 原样保留）
- 🚫 未覆盖/移动/重命名任何 Blender 文件
- 🚫 未修改 `PATH` 或任何环境变量
- 🚫 未修改 Blender 配置（未创建/未写入 `userpref.blend`；未改动既有 5.1 配置——已用快照 diff 证明）
- 🚫 未修改注册表、未改动文件关联
- 🚫 未切换项目运行时（后续脚本仍指向 4.5.9，**未做任何改动**）
- 🚫 未进入任何生产阶段（未 re-pose / 未 Retopo / 未 Rig / 未调用 Hunyuan3D / 未进入 Three.js）
- ✅ 已完成：PATH / 安装目录 / 开始菜单与桌面快捷方式 / 注册表 / Store 记录 / 全盘 `blender.exe` 搜索 / 配置痕迹 / 版本与 build / Python 版本 / 配置与脚本路径 / 调用归属确认 / 只读性验证

---

## 7. 最终状态输出

```
PRE_EXISTING_BLENDER          = YES
PRE_EXISTING_BLENDER_PATH     = D:\Blender\blender.exe          (install root: D:\blender\)
PRE_EXISTING_BLENDER_VERSION  = 5.1.2                            (build ec6e62d40fa9, 2026-05-19, blender-v5.1-release)
PRE_EXISTING_BLENDER_INSTALL  = MSI installer, InstallDate 20260627, NOT portable, NOT in PATH
PRE_EXISTING_BLENDER_USED     = NO                               (上一轮未被调用)

WORKBUDDY_PORTABLE_BLENDER_PATH    = <USER_HOME>\.workbuddy\binaries\blender\blender-4.5.9-windows-x64\blender.exe
WORKBUDDY_PORTABLE_BLENDER_VERSION = 4.5.9 LTS                   (build 8bf95cbd38d1, 2026-04-21, blender-v4.5-release)

C1_QUALIFICATION_RUNTIME      = WORKBUDDY_PORTABLE_BLENDER 4.5.9 LTS  (证据：脚本 3 处硬编码该路径；D:\Blender 引用数 0；banner hash 一致)

ROOT_CAUSE_OF_FALSE_NOT_FOUND = 只查 PATH（不在 PATH，仅 .lnk 入口）
                              + 只探测 C:\Program Files[ (x86)]\Blender Foundation 两个默认路径（实际装在 D:\blender）
                              + 未查注册表 / 开始菜单 / 用户配置痕迹 / 非系统盘
                              + 复合命令未逐项回显且退出码取自末条命令（失败信号被吞）
                              + 由单点结果直接下结论，未做交叉验证

SYSTEM_STATE                  = 未卸载 / 未覆盖 / 未改 PATH / 未改配置 / 未改注册表（均已验证）
AUDIT_MODE                    = READ-ONLY
```

**等待 Human Review。本轮在此停止，不进入下一生产阶段。**

**文档状态：`READY_FOR_HUMAN_REVIEW`**
