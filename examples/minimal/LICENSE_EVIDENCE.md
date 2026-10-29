# LICENSE EVIDENCE · Blender Human Base Meshes v1.4.1

> 目录：`references/licenses/blender_human_base_meshes/`
> 用途：为 `STAGE1C_C1_ASSET_QUALIFICATION` 提供 **CC0 授权链证据**（对应 `LIC-03`）。
> 记录人：WorkBuddy　记录日期：**2026-09-27**（访问日期同上）

---

## 1. 结论（先给结论）

| 项 | 值 |
| --- | --- |
| **LICENSE** | **CC0 1.0 Universal（Public Domain Dedication）** |
| 授权性质 | 可修改 / 可商用 / 可再发布 / 无需署名 / 无需额外商业授权 |
| 与本项目交付场景冲突 | **无**。CC0 不含"禁止再分发模型文件"条款 → 与"Web 交付必然把 GLB 送达终端用户"**不冲突**（对比 A-2 商业素材市场的 `LIC-01`） |
| 证据强度 | 官方页面明示 CC0 + 官方镜像下载 URL + 文件哈希 + 第三方权威镜像（Wikimedia Commons）记录作者与 CC0 |

---

## 2. 官方来源记录

| 项 | 记录 |
| --- | --- |
| 资产包名称 | **Human Base Meshes v1.4.1** |
| 官方页面（Asset Bundles） | `https://www.blender.org/download/demo-files/` |
| **官方页面原始授权标记** | 页面条目原文：**"49 MB – CC0"**；条目署名原文：**"by Blender Studio and community contributions."** |
| 官方页面其他标记 | **"Updated: Jan 20, 2025"**；**"Requires Blender 4.2 LTS or newer"** |
| 页面下载入口 | `https://www.blender.org/download/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip` |
| 该入口的实际返回 | HTTP 302 → Blender 官方 "Thanks!" 中间页（HTML），页内给出真实文件地址 |
| **实际下载 URL（官方 mirror）** | `https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip` |
| 来源合规性 | `mirror.blender.org` 与 `download.blender.org` 均为 Blender Foundation 官方域；**未使用任何第三方转载站** |
| 版本号 | **v1.4.1** |
| 下载日期 | **2026-09-27** |
| 最低 Blender 版本要求 | **Blender 4.2 LTS 或更新**（实际检查所用版本：Blender 4.5.9 LTS，`hash 8bf95cbd38d1`） |

### 2.1 第三方权威镜像（交叉印证作者与授权，非母文件来源）

Wikimedia Commons（Wikimedia Foundation 运营）分类页 `Human Base Meshes (Blender)` 收录了源自上述官方 URL 的官方资产再发布副本，其中：

| 条目 | 记录内容 |
| --- | --- |
| `Hand realistic by Dan Ulrich (CC0).stl` | 文件名直接标注 **作者 = Dan Ulrich**、**许可 = CC0** |
| `Body male realistic by Dan Ulrich (CC0).stl` 元数据 | 作者原文列举：**"Blender Studio; Dan Ulrich; Paul Kotelevets; Tonatiuh de San Julián; Julien Kaspar"**；许可原文为 **CC0 1.0 Universal Public Domain Dedication** 全文 |
| 来源字段 | `https://www.blender.org/download/demo-files/`（即本文件 §2 的官方页面） |

> 📌 **用途限定**：该镜像**仅用于印证作者与授权**。本项目的实际母文件**只从官方域下载**（见 §3），
> 未从 Commons 或任何转载站获取 `.blend`。

---

## 3. 文件哈希（唯一标识，可复核）

| 文件 | 大小（bytes） | SHA-256 |
| --- | --- | --- |
| `human-base-meshes-bundle-v1.4.1.zip` **（下载归档，保存于本目录）** | **50,643,039** | `811f43accbb31a88266d932f8f5563b2d13586fca0ba2693aad1f5fe582b3515` |
| `human_base_meshes_bundle.blend`（解压后母文件） | **49,420,489** | `3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137` |
| `blender_assets.cats.txt`（资产目录定义） | 713 | 见包内（未单独校验，内容已存档于 `stats/pass1_inventory.json` 的 `catalog_file` 字段） |

解压后目录结构（完整清单见 `stats/pass1_inventory.json`）：

```
human-base-meshes-bundle-v1.4.1/
├── blender_assets.cats.txt
├── human_base_meshes_bundle.blend      ← 唯一母文件（49.4 MB）
└── thumbnails/                          ← 26 张官方缩略图（含 realistic_hand.png）
```

---

## 4. ⚠ 文件内部未内嵌授权元数据（诚实记录）

对 `.blend` 内部的实际检查结果（`stats/pass1_inventory.json`）：

| 检查点 | 实际结果 |
| --- | --- |
| 资产级 author 元数据 | **空**（`asset_metadata = {}`） |
| 资产级 license 元数据 | **空** |
| 资产标签 `asset_tags` | **空** |
| 包内独立 `LICENSE` / `README` 文件 | **不存在**（包内仅 `blender_assets.cats.txt` + `.blend` + `thumbnails/`） |
| 文件级自定义属性 | 无 |

> **结论**：CC0 的授权声明**不在文件内部**，而**在官方分发页面**上（§2）。
> 因此本项目保存的证据链构成为：
> **① 官方页面原文（授权标记）＋ ② 官方下载 URL ＋ ③ 文件哈希 ＋ ④ 第三方权威镜像的作者/授权交叉印证**。
> 任何后续复用/发布母版时，应一并保存本文件与本目录下的 `human-base-meshes-bundle-v1.4.1.zip` 原始归档。

---

## 5. 与 `HR-09` 的关系（不修改冻结文档，仅声明）

`HR-09` 原文约束："CC0 模型图只能作内部 QC，不得作 Hunyuan3D 正式输入"。
本文件**不修改**该条；仅记录事实：本阶段把该 CC0 资产作为**资格审查对象（母体候选）**，
未将其任何渲染图送交 Hunyuan3D（`HUNYUAN3D_CALLED = NO`）。
其是否由"参考图"升级为"母体来源"，属 `STAGE0_ROUTE_C_AMENDMENT` 议题，**本轮不裁定**。

---

## 6. 证据文件清单（本目录）

| 文件 | 说明 |
| --- | --- |
| `LICENSE_EVIDENCE.md` | 本文件 |
| `human-base-meshes-bundle-v1.4.1.zip` | 官方下载归档原件（50,643,039 bytes，SHA-256 见 §3） |
| `extracted/human-base-meshes-bundle-v1.4.1/` | 解压后的官方内容（含母文件与官方缩略图） |

**访问日期：2026-09-27　记录人：WorkBuddy　状态：`C1_LICENSE = CC0`（已验证）**
