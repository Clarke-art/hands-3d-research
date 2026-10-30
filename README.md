# 3D Hands — open research publication candidate

本项目研究如何把MIDI音符、时钟和指法转换为可解释、可验证的钢琴手部运动，欢迎全球开发者共同研究、改进和贡献。**双手连续自然运动仍未完成；这不是成熟自动演奏产品。** 本提交处于Private发布准备阶段。Human已于2026-10-30确认原创权属及开源授权，公开署名为Clarke-art、版权年份为2026；仓库保持Private，Release保持Draft，等待Human最后确认正式公开。

已完成冻结左右手模型、MIDI结构读取、短指法接口、局部接触/几何算法及其测试，并保留重要失败实验和验证结果。真实动作数据的授权、Rig/坐标/时钟对齐，以及持音、释放、掌腕协同、双手复音和穿模仍有未解决问题。最小测试通过只证明列明的输入、接口、模型身份与几何fixture，不代表历史算法或连续动作研发全部通过。

从[研究总览](RESEARCH_OVERVIEW.md)了解已完成结果及失败边界，使用[研究索引](RESEARCH_INDEX.md)和148份研究卡定位源码、输入、输出与失败证据。六个核心Blender模型见[模型说明](models/README.md)及[SHA清单](ASSET_MANIFEST.csv)。

## 最小示例

Python 3.12，在仓库根目录执行（Linux/macOS把`.venv/Scripts/python`改为`.venv/bin/python`）：

```sh
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python src/midi_inspect.py examples/minimal/anna-magdalena-04.mid
.venv/Scripts/python src/fingering_demo.py examples/minimal/fingering_smoke.json
.venv/Scripts/python -m pip install -r requirements-geometry.txt
.venv/Scripts/python -B -m unittest discover -s tests -v
```

基本示例只需标准库；NumPy用于第六项几何测试，未安装会跳过该项。六项全通过要求没有skip。不要把`src/legacy`中的历史优化、下载、清理脚本当成安装步骤。[完整环境说明](environment/REBUILD.md)不保证所有旧求解器ABI可直接复现。Blender打开模型时禁用自动执行脚本。

## 下载18个研究附件

拟定版本为`v0.1.0-research`，尚未发布。真实上传完成后，按[18包下载与恢复索引](release-assets/DOWNLOADS.md)获取ZIP；逐包、逐成员核验方法见[恢复说明](release-assets/RESTORE.md)。附件不使用LFS。R0的22个ZIP不上传。[原始路径映射](release-assets/ORIGINAL_PATH_MAP.csv)及[R1精确清单](release-assets/R1_PUBLICATION_MANIFEST.csv)保留原路径、原SHA、公开SHA和排除决定。

原创代码采用MIT（Copyright (c) 2026 Clarke-art）；原创研究文档、模型贡献和可授权研究数据采用CC BY 4.0，署名Clarke-art。第三方内容保留原许可和来源。约1.974GB外部运动及参考数据不直接分发；版本、来源、原始SHA、原创适配和研究结论保留。两组中间PNG由编码视频、关键帧、科学数据和代码代替，不承诺无损逐帧重建。[许可层级](LICENSE)、[版权与署名](COPYRIGHT.md)、[第三方来源](THIRD_PARTY_NOTICES.md)约束全部公开文件及附件。

## Issues、Discussions与贡献

通过[贡献说明](CONTRIBUTING.md)提交可复现Issue、研究讨论或PR。仓库公开后使用GitHub的Issues/Discussions入口，当前未启用或验证。请附提交SHA、包SHA、环境、预期/实际结果和最小反例；保留历史FAIL及冻结资产身份。请勿上传未授权外部数据、权重、个人信息或凭据。贡献者需说明其贡献来源和授权范围。
