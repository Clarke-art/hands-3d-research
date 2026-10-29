from pathlib import Path
import json,re,urllib.request,hashlib
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf8'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
a=read('ACTUAL_STATIC_COMPARISON.json');center=a['poses'][5];hit=center['local_white_keys']['77']['pairs'][0]
assert hit['digit']=='LITTLE' and hit['penetration']['max_depth_mm']>1
extra=f'''\n\n## 补充：局部白键安全核查\n\n复用同一批静态姿态追加实际D5/E5/F5键体测量，没有再次求解。中心B小指/F5为20面对、19个内部采样顶点，最大采样深度{hit['penetration']['max_depth_mm']:.4f} mm；原R1与A均无该命中。前邻居3.750 s虽清除邻指相交，但无名指进入非目标E5的内部见证深度由3.0873增加到4.3084 mm；后邻居3.850 s中指/D5约1.3014→1.4193 mm，主动E5浅层内部见证约0.1289→0.1654 mm。它们不能因为主动指腹锚点gap合格就被当作整体可行姿态。检查仅限这三个相邻白键及既有七黑键，未扩大到全88键。\n'''
for n in ['LATE_CONFLICT_GEOMETRY.md','FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md','NATURAL_POSTURE_ASSESSMENT.md']:
 s=(P/n).read_text(encoding='utf8')
 if '## 补充：局部白键安全核查' not in s:(P/n).write_text(s+extra,encoding='utf8')
answers='''# 最终Q1–Q14

Q1：在指定局部范围内已定位实际交线、内部采样深度、E5运动键面和D♯5干涉，并保存世界坐标见证；不宣称全曲或全手诊断。

Q2：固定root结果能保持E5并清除中心D♯5，但不能同时满足中指/无名指分离与自然释放。中指DIP、无名指PIP接近伸直下限，其他自由度仍有余量。R4局部非光滑距离引导和释放约束表达值得复评，未证明固定root全局不可行。

Q3：两个邻居静态样本的邻指相交改善，但中心失败且有新增键体风险，尚不能支持有限root方案进入动态阶段。

Q4：测试了world X/Y/Z平移±3/±5/±3 mm及腕点pitch/yaw各±2°；中心实际−2.267/+0.454/−2.349 mm、−1.965/+1.480°。这些是测试自由度，不是已经证明必要的自由度；自然度HUMAN_PENDING。

Q5：是，在3.825/3.850秒E5静态指腹接触gap约0.8605/0.4987 mm，水平越界0；不是持续动态接触认证。3.750秒仍应保持D5，未提前强制E5。

Q6：中心没有实质改善：原R1/A/B相交面对93/92/83；最大内部采样见证深度7.267/6.695/6.651 mm。前后邻居的相交消失，但不能替代中心失败。

Q7：相对原R1中心0.7274 mm内部顶点穿入，B采样内部顶点为0，但仍有11面对交叉；A已经无命中。因此D♯5相对原始姿态改善，相对固定root A没有优势。

Q8：是。中心新增小指/F5：20面对、19个内部采样顶点、约1.2706 mm深度；邻居原有非目标白键穿入部分恶化。没有新增食指/中指或无名指/小指相交，但不能报告无新增冲突。

Q9：中心明显穿插仍在，释放指偏直与小指下沉存在风险；未取得自然度PASS。没有连续动作，不能评价抽动或原速自然度。

Q10：没有证据需要修改冻结Rig。

Q11：唯一建议先复评非冻结局部接触、释放准备、稳定表面分离约束及root带动闲置指的安全保护。取得中心与邻域可靠静态依据后，再单独授权有限事件窗口内的联合动态验证；root不预设为必需。

Q12：没有证据要求整段重规划；有限D5→E5→后续交接事件窗口是下一轮最小研究范围，但尚未证明足够或边界连续可行。

Q13：没有。正式动态求解0、动态候选0、新Action0、新完整Blend0、新视频0；仅一个三状态静态比较批次，固定root未重优化。

Q14：保持不变。6563个受保护文件哈希一致，四个批准静态姿态相关20文件也一致。

CURRENT_LOCAL_FEASIBILITY = NOT_ESTABLISHED。可行性比较工作完成，可提交Human审核静态证据；不是修复成功或动态生成批准。

STOP — HUMAN REVIEW
'''
(P/'FINAL_ANSWERS.md').write_text(answers,encoding='utf8')
page=P/'STATIC_REVIEW.html';s=page.read_text(encoding='utf8');s=s.replace('出现小指/F5新增面交叉','出现小指/F5新增约1.271 mm内部采样穿入')
if 'href="FINAL_ANSWERS.md"' not in s:s=s.replace('<h2>证据与报告</h2>','<h2>证据与报告</h2><p><a href="FINAL_ANSWERS.md">最终Q1–Q14</a></p>')
page.write_text(s,encoding='utf8')
refs=re.findall(r'(?:src|href)="([^"#]+)"',s);missing=[r for r in refs if not (P/r).is_file()];assert not missing,missing
required=['LATE_CONFLICT_GEOMETRY.md','FIXED_VS_BOUNDED_ROOT_FEASIBILITY.md','NATURAL_POSTURE_ASSESSMENT.md','NEXT_MOTION_PLANNING_DECISION.md','FINAL_STATUS.json'];assert all((P/n).is_file() for n in required)
url='http://127.0.0.1:53518/'+P.name+'/STATIC_REVIEW.html'
with urllib.request.urlopen(url,timeout=5) as response:
 status=response.status;assert response.read().decode('utf8').replace('\r\n','\n')==s
save('FINAL_DELIVERY_VERIFICATION.json',dict(required_reports=required,all_present=True,relative_links_checked=len(refs),missing_links=missing,HTTP_status=status,review_url=url,source_preservation=read('ASSET_PRESERVATION.json'),actual_skin_parity=read('BOUNDED_ACTUAL_SKIN_PARITY.json'),static_B_states=len(read('BOUNDED_STATIC_RESULTS.json')['poses']),new_dynamic_solves=0,new_dynamic_candidates=0,no_range_expansion=True))
print('VERIFIED',status,len(refs),'links',url)
