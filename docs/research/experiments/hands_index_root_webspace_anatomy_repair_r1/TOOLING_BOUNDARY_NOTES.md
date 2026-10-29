# 工具边界记录

Blender MCP持久Python会话保留了上一隔离实验的审计钩子。新任务重新绑定其内存中的输出根目录至本次授权隔离目录后，才写入本次文件；历史磁盘文件未改动。首次边界探测在文件创建前被审计钩子拒绝。

`package_evidence.py`首次执行已生成并排对照和ROI图、定向只读检查JSON，随后matplotlib尝试创建默认用户缓存目录，被实验写入保护主动拒绝（WRITE_OUTSIDE_EXPERIMENT）。未发生缓存越界写入。设置MPLCONFIGDIR到本隔离目录后，`render_evidence_plots.py`仅续做尚未生成的剖面图，不覆盖此前证据。这不属于姿态修改轮次。

所有因素隔离均为临时诊断副本；未保存关闭变形器或修改权重的修复候选。诊断完成后，原网格数据引用、modifier状态及evaluated坐标已精确恢复。之后保存的诊断Blend默认是原C1动作与原变形器。
