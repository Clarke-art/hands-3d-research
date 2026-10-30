# R2 最终版权与发布准备审核（2026-10-30）

Human 已确认本项目为个人独立开发、持有原创成果相应权利并同意将有权授权的原创成果完全开源。公开署名 Clarke-art，年份 2026。

| 内容 | 生效许可与覆盖范围 |
|---|---|
| 原创代码（逐文件范围表 1,844 项） | MIT；Copyright (c) 2026 Clarke-art |
| 原创研究文档、模型贡献、可授权数据及研究媒体（12,163 项） | CC BY 4.0；Clarke-art (2026)；仅授权原创贡献层，保留上游来源 |
| PianoPlayer 核心（5 项） | 原 MIT，Copyright (c) 2017 Marco Musy，原 LICENSE 不变 |
| Mutopia MIDI（4 项） | 原版本公共领域说明及排版者、来源保留 |
| Blender Human Base Meshes | 原 CC0 来源通知及 Dan Ulrich 等来源署名保留；不将上游成果改称原创 |
| 其他第三方内容 | 遵循原授权；未清权外部运动、权重、训练集及参考数据继续排除 |

范围表共 14,016 项（7,394 个 Git 历史选定项，6,622 个附件成员）；R2 新增原创发布说明采用 CC BY 4.0。现行授权见 LICENSE、COPYRIGHT.md、THIRD_PARTY_NOTICES.md 与 R2_LICENSE_SCOPE.csv。范围表 r1_* 和 sha256 列保留原始证据；current_git_sha256 列记录本轮实际 Git 文件身份。R1 的 owner pending 字段及 ZIP 内说明属于保留的历史记录，由本次明确授权补充，不改写历史研究批准或 FAIL。

## 文件与 SHA256 变化

下列 9 个既有文件发生变化；完整 64 位前后 SHA256 见 [CSV](COPYRIGHT_SHA_CHANGES_2026.csv)。另新增本审核报告及 CSV；新增文件的最终 SHA256 记录于本地最终审计清单，避免报告自哈希循环。

| 文件 | 修改前 SHA256 | 修改后 SHA256 |
|---|---|---|
| COPYRIGHT.md | `2505349785325c7cdacee888a418e662bb900c6ba5830f6a410c6d57c68cb65e` | `8603acce2771407355545de9eebef544566aaa50b7e34e2d6c93af6e2ee1a209` |
| LICENSE | `7e7121e62c7c70719509b5aca9b9fb1ab5d31c879b80f2e04c147782d3d226f2` | `177906c46d160f24bda322f0f5907f6a18803df061a2bc1a341e6fcf38c35624` |
| LICENSES/MIT.txt | `b05785f9f18e6716bab63424b11454513b9943a222595b70411009202fc592b5` | `035be78cb5bdf604d7441e8b7f4d3367b551a6b4a355a15cb2fb2b4b22bd2717` |
| LICENSE_RECOMMENDATION.md | `e85758afdccb68e53978a6471e234aea3081b5dd2a5fff21d813082a8688a53a` | `a67db5e59a0dc3d24f5b74ce677026559a32b81560403e55a4034bd14e878a56` |
| README.md | `e1992d6019c2f82ee814d8f31a68156c0faa04527081a63508d3531fd5bdd61e` | `c09a8e3476dbcf449d982eda0e3b73c9683a90b5b63333a1aa3890532434d40b` |
| THIRD_PARTY_NOTICES.md | `6fda89aed1f270fdb861f2c903979b7d9a8b55d29e0a4608a9b2a1d8b58653a7` | `271b24d6d65e2b3cf5a37a463f4b4808e8af4b21ddb3dfb0ec8e8986a4f8db78` |
| models/README.md | `284b60f0803dba6276df9e46937d16e51b1b2d318c9c0753ad1eaa12e7a2f524` | `aae5e303d957e4ffd068ba3a20aceeb08ee0dd36a175b45a6a5752fc2c436b76` |
| release-assets/R2_LICENSE_SCOPE.csv | `20f793d7a1d9b2ea00454d5ed8bae4cdfce4ed88fee1d48e34bcb65cfe2d8d8c` | `28cfd9ec7dbb65df858eec11ea6772030a706d77a4f2745ae0a0ce6dff2c40ce` |
| release-assets/RELEASE_NOTES_v0.1.0-research.md | `c6d1047111f93fb51b39e335b2091fe59069e52ffb245f8b80a61fa78b7abfb7` | `47dc11dc199a98de8467af34396e6e6f34f7342a5e285003fa391170f679c63c` |

## 核验结果

- README、LICENSE、COPYRIGHT 与 THIRD_PARTY_NOTICES 的署名、年份、许可层级、第三方例外及 Private/Draft 门禁一致。
- 全工作树文本扫描未发现未填写的版权年份/权利人模板；历史研究状态、R1 来源声明和技术占位符不冒充本次版权声明。
- 18 个本地 ZIP 两次 SHA256 核验均与 R1_RELEASE_ASSETS.csv 一致；远端同名附件的 digest、size 也全部一致（7,658,061,482 bytes）。不重打包、不覆盖、不删除。
- 6 个原始受保护 Blender 资产与保护清单 SHA256 一致；本轮未写入原始 hands 工程或正式双钢琴项目。
- 所有源码、测试、历史研究记录、示例、模型二进制、第三方原始许可证与 CC BY 4.0 法律正文保持不变。仅修改 9 项许可/发布元数据，并新增本报告和 SHA 清单。
- git diff --check 通过。本次只改许可元数据，未重新运行运动或几何测试，也未扩大既有技术验收结论。
- 推送前 GitHub API 核验：Clarke-art/hands-3d-research 为 Private；现有 Release ID 428060007、v0.1.0-research 为 Draft，目标 main；18 个附件摘要匹配。最终提交身份与推送后核验保存在本地 copyright_final_20261030 审计目录。

## 公开门禁

原创许可授权已确认；最终切换 Public 和正式发布 Release 尚未批准。完成本轮 Private 推送后停止，等待 Human 最后确认。保留所有历史证据和本地文件。
