# 最终Q1–Q12

|问题|回答|
|---|---|
|Q1|02_generate_once.py第46行；修正量PCHIP后叠加R2角度、输出采样完成时，在np.savez及Action烘焙前检查827×20DOF。|
|Q2|没有。现有R3未保存fit.x、latent、输出q或违规mask；FINAL_FAILED_TRAJECTORY=UNAVAILABLE。|
|Q3|原动态手指/关节/时刻/实际值/超限量全部UNKNOWN；人工反例与静态预算差额均不能替代。|
|Q4|确认输出曲线域保障与静态/正式修正预算表示不一致；未发现左右手、单位、轴或关节索引转换错误。guard拒绝本身正确。|
|Q5|最有支持的是验证管线不一致，尤其分别PCHIP后相加未保持总q域；还存在静态预算到正式latent预算的不一致。具体原失败归因仍SUPPORTED。|
|Q6|不是已证实的限制；固定root静态任务实际可达，完整动态root冲突UNKNOWN。|
|Q7|当前没有证据要求开放。先保留R2 root，修复输出域与诊断管线。|
|Q8|不需要修改冻结Rig；无这类证据或授权。|
|Q9|固定root静态证据支持有可能，但完整动态与Human自然动作保持仍未验证，不能承诺。|
|Q10|唯一推荐GUARD_FIX：统一actual/latent预算、总角度域保持评价与输出检查，在guard前保存现场；不同时开放root或调安全区。|
|Q11|优化器返回立即保存真实nfev/status及支持点/latent；guard前分阶段保存全部时间/角度/身份/边界/超限/非有限值，异常后保留checkpoint。|
|Q12|YES：8336个保护文件哈希一致，含原8294文件及全部42个R3文件；无历史修改、动态求解或新候选。|

诊断完成不等于动态演奏通过。STOP — HUMAN REVIEW。
