# STAGE0 R1.3.1 -- CURRENT_AUTHORITY_CONSISTENCY_SCAN (read-only)
import os, re, json, sys

ROOT = r"<HANDS_ROOT>"
AUTH = [
    r"docs\STAGE0_ROUTE_C_AMENDMENT_R1.md",
    r"docs\PIANO_HAND_PRODUCTION_PIPELINE_R1.md",
    r"docs\PIANO_HAND_MASTER_ASSET_SPEC_R1.md",
    r"docs\MULTIVIEW_REFERENCE_PACK_SPEC_R1.md",
    r"docs\CANONICAL_HAND_POSE_SPEC_R1.md",
    r"reference_manifest\REFERENCE_MANIFEST_R1.json",
]

text = {}
for rel in AUTH:
    p = os.path.join(ROOT, rel)
    text[rel] = open(p, encoding='utf-8').read()

REQUIRED = [
    ("GEOMETRY_SOURCE_PRIMARY", "CC0_AUTHORED_BASE_MESH"),
    ("PROJECT_BLENDER_RUNTIME", r"D:\Blender\blender.exe"),
    ("ROUTE_C_SOURCE_GATE", "PASS"),
    ("REFERENCE_ACQUISITION_GATE", "CONDITIONAL_BRANCH_GATE_FOR_HUNYUAN_MULTIVIEW"),
    ("REAL_HUMAN_8VIEW_REFERENCE", "OPTIONAL_NON_BLOCKING_FOR_ROUTE_C"),
    ("HUNYUAN3D_ROLE", "OPTIONAL_FALLBACK_EXPERIMENT"),
    ("2D_IMAGEGEN_MULTIVIEW_ROUTE", "REJECTED_BASELINE"),
    ("ASSET_FRAME_AUTHORITY", "CONSISTENT"),
    ("SOURCE_TO_CANONICAL_TRANSFORM", "DEFINED"),
    ("CON-9_ASSET_FRAME_NORMALIZATION", "BOUND_TO_STAGE4"),
]

print("### 1. required authority tokens, per file")
for name, val in REQUIRED:
    hits = []
    for rel in AUTH:
        t = text[rel]
        # token must appear with its declared value within a short window
        ok = False
        for m in re.finditer(re.escape(name), t):
            window = t[m.start(): m.start()+200]
            if val.split('\\')[0][:14] in window or val in window:
                ok = True; break
        if ok:
            hits.append(os.path.basename(rel))
    print(f"  {name:<34} = {val:<46} -> {len(hits)} file(s): {', '.join(hits) if hits else '*** MISSING ***'}")

print()
print("### 2. stale-rule sweep (must be 0 as live authority)")
pats = {
    "LowPoly treated as available": r"（若使用 LowPoly 模式）|若使用 LowPoly",
    "unlabelled current '主流水线.*Hunyuan'": r"主流水线：Reference -> Hunyuan",
    "old key amendment_unchanged (live)": r'"amendment_unchanged"',
    "canonical pose spec described as hunyuan-multiview master": r"混元 3D 多视角生成的母版手姿态定义",
    "dorsal=+Y stated as current in canonical spec": r"背侧 \+Y、掌侧 −Y",
}
for label, pat in pats.items():
    tot = 0
    where = []
    for rel in AUTH:
        n = len(re.findall(pat, text[rel]))
        if n:
            where.append(f"{os.path.basename(rel)}:{n}")
            tot += n
    print(f"  {label:<58} occurrences={tot}  {where}")

print()
print("### 3. JSON validity + new fields")
man = json.loads(text[r"reference_manifest\REFERENCE_MANIFEST_R1.json"])
print("  REFERENCE_MANIFEST_R1.json parses OK; top-level keys =", len(man))
af = man.get('asset_frame_authority', {})
for k in ('ASSET_FRAME_AUTHORITY','ASSET_FRAME_CONFLICT','SOURCE_TO_CANONICAL_TRANSFORM',
          'SOURCE_TO_CANONICAL_TRANSFORM_DET','CON_9_ASSET_FRAME_NORMALIZATION'):
    print(f"  asset_frame_authority.{k} = {af.get(k)}")
print("  former field:", 'former_r1_1_amendment_unchanged' in man,
      "| NOT_CURRENT_AUTHORITY =", man.get('former_r1_1_amendment_unchanged', {}).get('NOT_CURRENT_AUTHORITY'))
print("  CON-9 bound stage:", man['c1_conditional_items_binding']['CON-9']['stage'])

print()
print("### 4. CON-9 present in all three binding surfaces")
for rel in [r"docs\STAGE0_ROUTE_C_AMENDMENT_R1.md",
            r"docs\PIANO_HAND_PRODUCTION_PIPELINE_R1.md",
            r"docs\PIANO_HAND_MASTER_ASSET_SPEC_R1.md"]:
    print(f"  {os.path.basename(rel):<42} CON-9 count = {len(re.findall('CON-9', text[rel]))}")
print()
print("SCAN_DONE")
