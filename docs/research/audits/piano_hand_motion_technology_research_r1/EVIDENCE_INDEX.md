# 证据索引

核查日2026-10-11；官方来源优先。报告中的结论分成论文/作者描述、静态事实、实际画面、研究推论和UNKNOWN。

|编号|官方来源|本地证据/说明|
|---|---|---|
|T1|https://tipiano.io/|tipiano_live_page_snapshot.txt / tipiano_release_status.png；动态官网，Code+Dataset TBD|
|T2|https://arxiv.org/html/2604.09692v1|§4输入/级联/输出，§5训练与评价；不把网站增强内容当已发布代码|
|T3|https://tipiano.io/benchmark|实际Top样例id23；完整媒体URL写在视觉报告|
|P1|https://github.com/agnJason/PianoMotion10M|源码提交 `86539e5a16d10ba462005f1f2bd9d72459ac2000`，pianomotion_tree.json|
|P2|https://huggingface.co/agnJason/PianoMotion_models/tree/main|revision de146178457a4f4d262f4f4492597d5fdf76dd23；info/tree和两份配置，未下载ckpt|
|P3|https://agnjason.github.io/PianoMotion-page/|官方生成与数据视频不同；版权NC说明|
|P4|https://arxiv.org/html/2406.09326v2|方法/附录限制；原数据来源为网络俯视演奏视频|
|F1|https://for-elise.github.io/|Code (To be released)；捕获与生成分支分开|
|F2|https://arxiv.org/html/2410.05791v1|§3捕获/后处理，§4联合生成与控制，§5.1训练成本|
|F3|https://huggingface.co/datasets/rcwang/for_elise|revision ea14b581cbc33d8f2d0aca8e609e3e5c62423e50；数据卡/树/下载脚本/查看器，未获取dataset.zip|
|F4|https://for-elise.github.io/static_visualizer/vis.html?id=100|实际短段截图、metadata；motion.json只读两行结构，坐标未保存|
|L1|https://mano.is.tue.mpg.de/license.html|默认非商业及商业许可渠道，mano_license.html|
|L2|https://github.com/agnJason/PianoMotion10M/blob/86539e5a16d10ba462005f1f2bd9d72459ac2000/LICENSE|Apache-2.0仅证明代码层|
|L3|https://creativecommons.org/licenses/by-nc/4.0/|数据NC含义，不能推出商业研发自动获准|
|D1|https://github.com/state-spaces/mamba#installation|Linux要求；当前源码无条件导入Mamba|
|D2|https://huggingface.co/facebook/hubert-base-ls960|第三方音频权重本版本Apache-2.0|

下载记录：SOURCE_FETCH_MANIFEST.json、FOLLOWUP_FETCH_MANIFEST.json；均为小型公共文本/JSON，单项上限512KiB；源码以`.txt`保存而未执行。STATIC_CODE_CHECK.json只做AST语法分析，不是运行成功证据。SMALL_SAMPLE_ACCESS_CHECK.json保存少量预览字段形状，未保存mesh坐标。网页演示由浏览器播放，未下载/另存原视频。

LOCAL_INPUT_HASHES.json记录六个必要接口/时间表/源候选文件的哈希。未重新检查7936个历史文件，未作全项目历史审计。操作写入范围仅本研究目录；选定输入终检见RESEARCH_STATUS.json，不宣称这等于重新认证全部历史资产。
