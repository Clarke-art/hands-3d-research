# STAGE0 R1.3.1 -- R1.3.1.1 HISTORICAL PROVENANCE HYGIENE scan (read-only)
import os, re, json, hashlib

ROOT = r"<HANDS_ROOT>"
F_C1 = ROOT + r"\docs\STAGE1C_C1_ASSET_QUALIFICATION_R1.md"
F_GAC = ROOT + r"\production_spec\stage1c_c1_qualification\stats\GEOMETRY_ANATOMY_CHECK.md"
F_ERRATA = ROOT + r"\docs\STAGE1C_C1_ASSET_QUALIFICATION_R1_ERRATA.md"
F_CLOSURE = ROOT + r"\docs\STAGE0_ROUTE_C_R1_3_1_FINAL_CLOSURE.md"
F_MAN = ROOT + r"\reference_manifest\REFERENCE_MANIFEST_R1.json"

# markers that my earlier patch introduced
MARKERS = ["R1.3.1", "🔴", "CORRECTION RECORD", "ERRATA", "更正框", "HISTORICAL_FILES_RESTORED"]

print("### A. historical-file marker sweep (must be 0)")
for label, p in (("STAGE1C_C1_ASSET_QUALIFICATION_R1.md", F_C1),
                 ("GEOMETRY_ANATOMY_CHECK.md", F_GAC)):
    t = open(p, encoding='utf-8').read()
    hits = {m: t.count(m) for m in MARKERS if t.count(m)}
    print(f"  {label:<40} R1.3.1-correction marker = {sum(hits.values())}  {hits if hits else ''}")
    print(f"  {'':<40} size = {os.path.getsize(p)} bytes")

print()
print("### B. byte-exactness against pre-R1.3.1 directory listing")
EXPECT = {"STAGE1C_C1_ASSET_QUALIFICATION_R1.md": 30563, "GEOMETRY_ANATOMY_CHECK.md": 9208}
for label, p in (("STAGE1C_C1_ASSET_QUALIFICATION_R1.md", F_C1),
                 ("GEOMETRY_ANATOMY_CHECK.md", F_GAC)):
    s = os.path.getsize(p)
    print(f"  {label:<40} {s} bytes  expected {EXPECT[label]}  byte-exact = {s == EXPECT[label]}")
    print(f"  {'':<40} sha256 = {hashlib.sha256(open(p,'rb').read()).hexdigest()}")

print()
print("### C. sidecar")
print(f"  STAGE1C_C1_ASSET_QUALIFICATION_R1_ERRATA.md EXISTS = {os.path.isfile(F_ERRATA)}")
if os.path.isfile(F_ERRATA):
    e = open(F_ERRATA, encoding='utf-8').read()
    for k in ["ERRATA_ID          = C1_Y_AXIS_ANATOMICAL_LABEL_REVERSAL",
              "THIS ERRATA DOES NOT MODIFY THE HISTORICAL C1 QUALIFICATION RESULT",
              "C1_ASSET_QUALIFICATION = UNCHANGED_CONDITIONAL_PASS",
              "diag(1, -1, -1)  =  Rx(180°)",
              "C1_HISTORY_IMMUTABLE = YES"]:
        print(f"    contains {k[:46]!r:<50} = {k in e}")

print()
print("### D. protected technical conclusions still intact in closure doc")
cl = open(F_CLOSURE, encoding='utf-8').read()
for k in ["ASSET_FRAME_CONFLICT                = RESOLVED",
          "SOURCE_TO_CANONICAL_TRANSFORM       = DEFINED",
          "CON_9_ASSET_FRAME_NORMALIZATION     = BOUND_TO_STAGE4",
          "CURRENT_AUTHORITY_CONSISTENCY       = PASS",
          "HISTORICAL_PROVENANCE_HYGIENE       = PASS",
          "STAGE0                              = REFROZEN",
          "STAGE2                              = READY_TO_START_ROUTE_C_BOOTSTRAP"]:
    print(f"  {k.strip():<48} = {k in cl}")

print()
print("### E. manifest")
m = json.loads(open(F_MAN, encoding='utf-8').read())
print("  JSON parses OK")
af = m['asset_frame_authority']
for k in ["C1_HISTORICAL_FILE_MUTATION", "C1_HISTORY_IMMUTABLE", "C1_ERRATA_SIDECAR",
          "C1_ASSET_QUALIFICATION", "HISTORICAL_PROVENANCE_HYGIENE"]:
    print(f"  asset_frame_authority.{k} = {af.get(k)}")
rs = m['review_status']
for k in ["HISTORICAL_PROVENANCE_HYGIENE", "C1_HISTORY_IMMUTABLE", "C1_ERRATA_SIDECAR",
          "ASSET_FRAME_CONFLICT", "SOURCE_TO_CANONICAL_TRANSFORM", "STAGE0_ROUTE_C_R1_3_1"]:
    print(f"  review_status.{k} = {rs.get(k)}")
print()
print("SCAN_DONE")
