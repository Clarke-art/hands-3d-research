from pathlib import Path
O=Path(__file__).resolve().parent;p=O/'bake_and_validate.py';s=p.read_text(encoding='utf-8-sig')
old="""   pts=fc.keyframe_points
   assert len(pts)==len(TRACK['times'])"""
new="""   # keyframe_insert merges very close event +/-100us keys; populate RNA directly.
   if ob==rt:values=TRACK['root_location'][:,fc.array_index] if fc.data_path=='location' else TRACK['root_quat'][:,fc.array_index]
   else:values=TRACK['bone_quat'][:,names.index(n),fc.array_index]
   fc.keyframe_points.clear();fc.keyframe_points.add(len(TRACK['times']))
   for ii,kp in enumerate(fc.keyframe_points):kp.co=(1+60*float(TRACK['times'][ii]),float(values[ii]))
   pts=fc.keyframe_points
   assert len(pts)==len(TRACK['times'])"""
assert old in s;s=s.replace(old,new)
p.write_text(s,encoding='utf8')
