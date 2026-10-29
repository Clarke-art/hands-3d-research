# 真实运行、模型身份与授权 — R1

采集及执行日期：2026-10-11，Asia/Shanghai。唯一正式推理起始：2026-10-11T22:06:20.840000+08:00。

## 发布身份

实查npm latest为@lumikey/piano-fingering-model **0.3.0**，发布时间2026-01-28T22:33:13.962Z。发布gitHead：`2c1a7806f723f12de35c7f232e452c159e4b4783`，对应2026-01-28提交Bump version to 0.3.0。npm发布记录列出0.1.0和0.3.0，不将未发布版本当作已安装版本。完整元数据、tarball integrity、npm provenance原始记录（未作签名验证）与依赖锁文件保存在NPM_PACKAGE_METADATA.json、evidence/NPM_ATTESTATIONS.json、package-lock.json。没有重新训练或重新导出权重。

来源：[npm注册表](https://registry.npmjs.org/@lumikey%2fpiano-fingering-model)、[固定发布版本package.json](https://github.com/lumikey/piano-fingering-model/blob/2c1a7806f723f12de35c7f232e452c159e4b4783/js/package.json)、[官方Node说明](https://github.com/lumikey/piano-fingering-model/blob/2c1a7806f723f12de35c7f232e452c159e4b4783/js/README.md)。

| 手 | 文件 | 字节 | SHA256 |
|---|---|---|---|
| left | fingering_transformer_left.onnx | 501130 | `246f2fed013c27ca8c32ce9d070002afcc49da4f1dfb0c43e09a4a3f9f2fb86e` |
| right | fingering_transformer_right.onnx | 501130 | `f931288302b87f5eec1c8af29a570ee0213a272a13eeb590991a285e1f1b67eb` |

两文件均来自安装包models目录，与发布gitHead中的js/models同名ONNX文件逐字节一致。核对过程及完整证据保存于collect_provenance.py和evidence/MODEL_PROVENANCE.json。仓库另有左右手.pt文件，但本轮不需要下载或运行PyTorch权重。export_onnx.py描述的来源为各手FingeringTransformer checkpoint，tokens输入[1,26,5]、logits输出5项、opset17；本次CPU会话实际输入输出名称均为tokens/logits。权重训练细节与质量不能由文件哈希推出。

## 环境与执行

| 项目 | 实测值 |
|---|---|
| 系统 | Windows 11 Pro / win32 / x64 |
| CPU | Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz，12逻辑CPU |
| Node | v24.18.0 |
| npm | 11.16.0 |
| ONNX运行时 | onnxruntime-node 1.23.2；onnxruntime-common 1.23.2 |
| MIDI适配 | 已有Python 3.12.1 + 现有只读mido 1.3.3；不是Python模型推理 |
| 模型加载耗时 | 144.1841 ms，左右会话合计墙钟 |
| 正式predictFingerings耗时 | 146.1515 ms，23音，含token构建/顺序ONNX调用/logits记录 |
| 加载+预测 | 290.3356 ms；不包含安装、导入、文件输出和后续审查 |
| 次数 | predictFingerings 1次，内部左7/右16，共23次session.run；未做重复候选或择优 |
| 运行异常 | exception=null；清理无异常；全部logits有限、argmax与1—5返回一致 |
| 加速器 | 仅CPUExecutionProvider；未安装PyTorch/CUDA |

infer_once.mjs先导入onnxruntime-node注册backend，再使用官方loadModels()与predictFingerings(notes, models)。loadModels()没有会话选项参数，因此脚本临时给其共享InferenceSession.create工厂补充executionProviders=['cpu']和profiling选项，加载后立即还原工厂。未编辑包源码、tokens算法或权重。session.run外包装仅记录输入、logits及耗时，原返回值不改。RAW_MODEL_PREDICTIONS.json直接保存官方返回数组，无人工指法或追加ID；身份在单独检查文件中绑定。

两份ONNX profile均实际出现且只出现CPUExecutionProvider。INFERENCE_RUNTIME_RECEIPT.json记录真实时间；OUTPUT_VALIDATION_AND_FEASIBILITY.json记录profile文件名/哈希，RAW_ONNX_LOGITS_AND_TOKENS.json保留逐音直接logits和输入tokens。profiling开启使这里的146ms不能被当作关闭诊断后的稳态性能基准。

安装注意：npm包包含多平台本地二进制，初次下载约8分钟；INSTALL.log保留全记录。npm自动选择了公共接口1.30.0而运行时依赖1.23.2，正式推理前主动将公共接口固定为1.23.2，使官方包与Node backend共用同一工厂；对齐约34秒，期间npm请求曾报ETIMEDOUT，但最终成功。随后离线缓存核查426ms，无新增下载。未经历失败的正式模型调用。boolean依赖弃用警告保留；npm默认没有执行待批准的onnxruntime-node postinstall，Windows CPU二进制已随包提供且实测可运行，无需额外授权脚本或CUDA下载。

复现需在本隔离目录使用锁文件，执行adapt_source.py后再执行infer_once.mjs。推理脚本使用wx保存结果并检测已有RAW_MODEL_PREDICTIONS.json，阻止意外覆盖或重复正式候选；请勿在当前交付上再次运行。所有新增文件仅写在实验目录，现有Hands/Piano工作区、静态姿态、MIDI/音频、Action及候选动画未修改。

## 代码、权重、训练数据商业授权

| 对象 | 已核实证据 | 商业教材状态 |
|---|---|---|
| Lumikey npm/JS代码 | npm元数据及js/package.json声明MIT。但安装包、固定发布仓库树和当前main树均未发现LICENSE/COPYING/NOTICE或许可证正文；GitHub仓库license字段为null | 记录为MIT声明；完整授权证据仍不足。不能给整个仓库、训练代码或商业教材组件作已清权结论 |
| 左右ONNX与.pt权重 | 公开可下载，ONNX包含在npm包中；未发现单独权重许可证、model card或明确商业权重授权。没有证明MIT声明究竟覆盖全部权重/上游权利 | NOT_CLEARED；本轮实测不等于正式商业教材授权 |
| 训练数据来源 | 固定版本train.py把基础数据称Flowkey，并可拼接PIG及scale npz；公开仓库包含这些文件。未提供发布权重实际训练清单或完整来源/授权链 | NOT_CLEARED；不推断上游网站、PIG或生成音阶数据可用于商业权重/教材 |
| ONNX Runtime | 安装包元数据及微软源码声明MIT；本轮未审核全部运行时第三方授权。它是运行环境，不能替代Lumikey权重授权 | 可与模型权重权利分别评估；不能据此替权重清权 |

许可证检索为完整非截断发布树及当前main树，相关路径均为空；它证明本次公开发布未提供这些文件，不能证明作者永远未授予其他授权。源码依据：[训练入口](https://github.com/lumikey/piano-fingering-model/blob/2c1a7806f723f12de35c7f232e452c159e4b4783/python/train.py)、[权重导出入口](https://github.com/lumikey/piano-fingering-model/blob/2c1a7806f723f12de35c7f232e452c159e4b4783/python/export_onnx.py)。完整原始证据在evidence目录。正式商用前需要权利人明确确认代码/权重范围与训练数据链，并保存可追溯授权。本轮结论为隔离技术POC，不将该模型作为已获商业许可的教学组件。
