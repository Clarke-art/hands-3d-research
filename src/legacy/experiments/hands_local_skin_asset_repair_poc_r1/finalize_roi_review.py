from roi_localization_tools import *
p=OUT/'CONFIRMED_ROI_PROPOSAL.json';data=read(p)
_,_,ido=raster(V,row('OVERHEAD'))
_,_,idc=raster(CAND,row('OVERHEAD','CURRENT_BEST'))
_,_,ids=raster(V,row('AUX_INDEX_SIDE'))
maps={'A':idc,'B':ido,'S':ids}
for k,r in data['regions'].items():
    movable=set(r['maximum_proposed_movable_vertex_ids']);support=set(r['core_face_ids']+r['transition_face_ids'])
    affected=[int(i) for i,f in enumerate(F) if set(map(int,f))&movable]
    assert set(affected)<=support
    assert all(set(r['face_vertices'][str(i)])&movable for i in r['core_face_ids'])
    assert set(r['core_face_ids'])<=set(np.unique(maps[k]))
    assert all(len(r['face_vertices'][str(i)])==4 for i in support)
    r['faces_potentially_affected_by_maximum_movable_set']=affected
    r['outside_support_faces_affected']=[]
    r['maximum_movable_count']=len(movable)
    r['core_has_visible_pixels_in_selection_view']=True
    r['core_has_visible_pixels_in_C1_overhead']=all(i in ido for i in r['core_face_ids'])
    tip=data['registration'][k]['tip_native_xy'];x,y=np.rint(tip).astype(int)
    r['arrow_tip_frontmost_native_face_at_rounded_pixel']=int(maps[k][y,x])
data['side_vs_B']['shared_transition_face_ids']=sorted(set(data['regions']['B']['transition_face_ids'])&set(data['regions']['S']['transition_face_ids']))
data['side_vs_B']['shared_core_vertex_ids']=sorted(set(data['regions']['B']['core_vertex_ids'])&set(data['regions']['S']['core_vertex_ids']))
data['selection_proposal_method']={
 'A':{'view':'CURRENT_BEST OVERHEAD','native_y_rows_inclusive':[232,252],'native_x_range_used_to_find_index_silhouette':[680,714],'visible_strip_width_native_pixels':7,'method':'Select frontmost real native polygons touching the thumb-facing index silhouette strip near the arrow; keep the edge-connected component; transfer native IDs to C1.'},
 'B':{'view':'ORIGINAL OVERHEAD','ellipse_radius_native_pixels':[7,8],'method':'Arrow-tip neighbourhood on first-web lower connector, keep frontmost edge-connected native faces; this neighbourhood is a proposed review extent, not a measured defect mask.'},
 'S':{'view':'ORIGINAL AUX_INDEX_SIDE','ellipse_radius_native_pixels':[20,18],'method':'Independent arrow-tip neighbourhood, keep frontmost edge-connected native faces.'},
 'transition':'Exactly one edge-neighbour ring restricted to visible polygons in selection view. All outer boundary vertices fixed. No vertices incident to outside support may move.'}
data['registration_uncertainty_note']='The 2px registration and 5px arrow interpretation tolerances are conservative review allowances, not statistical confidence intervals. RGB fit residual is a raster agreement metric, not a 3D defect validation.'
data['joint_scope_note']='A is between MCP and PIP on the thumb-facing index side; no extra joint is inferred from the contour. Actual projected joints are shown. No judgement that all highlighted normal soft tissue must change.'
data['piano_directory_accessed']=False
data['historical_evidence_preserved']=True
with p.open('w',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
before=read(OUT/'ROI_INPUT_SHA256_BEFORE.json')
checks=[{'path':r['path'],'before':r['sha256'],'after':sha(r['path'])} for r in before]
for r in checks:r['unchanged']=r['before']==r['after']
assert all(r['unchanged'] for r in checks)
write('ROI_PROTECTED_SHA256_BEFORE_AFTER.json',{'all_unchanged':True,'count':len(checks),'piano_directory_accessed':False,'files':checks})
report='''# ROI 提案待 Human 审核

状态：**ROI_PROPOSED — STOP — HUMAN REVIEW**。本轮没有修改任何模型资产，也没有生成修补候选。`CONFIRMED_ROI_PROPOSAL.json` 是请求指定的文件名，`human_confirmed=false`。

1. **ROI-A：位置对应，范围待确认。** 原始上方箭头只出现在右栏候选图；已根据原合成脚本、同机位渲染和像素配准找回该处，再将真实原生面 ID 映射至原 C1。青色核心覆盖食指近节靠拇指／虎口侧的局部轮廓，不包含整根食指、PIP 关节区域或历史背侧拱形。不能据此断言核心内每个面都有缺陷；正常轻微曲率应保留。
2. **ROI-B：位置对应，饱满度边界待确认。** 橙色核心位于原 C1 下方箭头落点的第一指蹼下部、食指根部—掌部连接皮肤；未把整个正常虎口凹面纳入。图中同时保留候选栏与原 C1 的 B 原始箭头局部。
3. **侧视 S：暂不与 B 合并。** 原 C1 侧视箭头落在紫色指根面片。S 与 B 核心无共用面或顶点，最近核心面中心约 7.97 mm；两者过渡面有 1244、1247 重叠，属于相邻皮肤，不能仅凭二维箭头认定为同一片异常。距离为面中心间欧氏距离，不是皮肤最短路径或缺陷大小。
4. **实际修改为零；未来拟可动上限如下。** 白线外皮肤及白线上的固定外围顶点保持原状；过渡面并不表示必须修改。全部核心、过渡、固定邻面、边界边、顶点编号及 Basis／求值后局部坐标、世界坐标都在 JSON 中，单位米，编号从 0 开始。
5. **最小不确定性。** 原图能与既有真实渲染配准，非红色像素 RGB RMSE 分别约 A 2.22、B 1.29、S 2.71／255。配准按约 ±2 屏幕像素、箭头落点解释按约 ±5 屏幕像素保守留量；它们不是统计置信区间。箭头只指出位置，没有定义编辑边界。A 的跨姿态范围、B 的正常凹面与疑似欠饱满边界、S 是否应作为独立修补目标，仍由 Human 确认。没有扩大诊断。

| 区域 | 核心面 | 过渡面 | 拟可动顶点上限（其余固定） |
|---|---|---|---|
| A | 356, 384, 385, 386, 387, 390, 391, 444, 445 | 9 面，详见 JSON | 158, 656, 1074, 1075, 1076, 2073, 2192, 2576, 2577, 2591 |
| B | 1248, 1249, 1250, 1251, 1253, 1254, 1255, 1274 | 12 面，详见 JSON | 294, 337, 1375, 1376, 1377, 1444, 1445, 2792, 2793 |
| S | 1245, 1246, 2728, 2729 | 8 面，详见 JSON | 627, 628, 2057, 2791, 3162 |

## 证据与保护

- 综合审核图：`HUMAN_ROI_CONFIRMATION.png`。颜色仅覆盖真实原生面，使用实际求值坐标与相机矩阵做前后深度测试；遮挡面不作 X-ray 彩色填充。黄虚线为另行标明的真实皮下骨轴参考。两张原始附件按原字节保存为 `hands_original_red_arrows_overhead.png` 与 `hands_original_red_arrows_side.png`。
- Blender MCP 只读核验当前原 C1 状态：第157帧，60fps，t=(frame−1)/fps=2.600000秒；右手3300顶点／3298原生面，逐顶点与前轮 ORIGINAL 快照误差为0，面编号和顶点序列完全一致。实际对象、骨轴、相机和配准记录见 JSON／`ROI_READONLY_BLENDER_RECEIPT.json`。拇指、食指通过真实命名骨链和各自指尖方向交叉核验，未调整任何 Pose Bone。
- 原 C1 源文件 SHA256 仍为 `d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7`。71项受保护输入及既有证据在本轮前后哈希全部不变，见 `ROI_PROTECTED_SHA256_BEFORE_AFTER.json`。独立 piano 目录未访问。历史报告、FAIL及旧 RESULT 均未覆盖；本轮状态另存 `ROI_RESULT.json`。
- 本轮没有 Blender 保存，没有 Basis、权重、corrective、Action、冻结 Rig、正式 MIDI 变化；没有 A/B 修补、多姿态回归或候选。有限的配准工作图和首版排版草稿保留在本实验目录作为过程证据，不是额外修复结果。

请在综合图上确认 A、B 的核心与过渡边界，以及 S 是否保留为独立区域。只有 Human 明确确认这些 ROI 后，才能进入此前授权的隔离单因素修补实验。
'''
with (OUT/'ROI_HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(report)
write('ROI_RESULT.json',{'status':'ROI_PROPOSED — STOP — HUMAN REVIEW','human_confirmed':False,'asset_modifications':0,'repair_candidates':0,'core_faces':{k:len(r['core_face_ids']) for k,r in data['regions'].items()},'all_protected_inputs_unchanged':True,'protected_input_count':len(checks),'piano_access':False,'required_human_review':['A core and transition boundary','B core and transition boundary','S independent region and boundary'],'historical_result_not_overwritten':True})
delivery=['HUMAN_ROI_CONFIRMATION.png','CONFIRMED_ROI_PROPOSAL.json','ROI_HUMAN_REVIEW.md','ROI_RESULT.json','ROI_READONLY_BLENDER_RECEIPT.json','ROI_PROTECTED_SHA256_BEFORE_AFTER.json']
write('ROI_DELIVERY_SHA256.json',[{'path':str(OUT/n),'sha256':sha(OUT/n)} for n in delivery])
print(json.dumps({'protected_inputs':len(checks),'all_unchanged':True,'status':'ROI_PROPOSED — STOP — HUMAN REVIEW','support_boundaries_validated':True}))
