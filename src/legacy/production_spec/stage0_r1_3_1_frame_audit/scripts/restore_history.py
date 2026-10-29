import hashlib

ROOT = r"<HANDS_ROOT>"
ORIG_SIZE_1 = 30563   # STAGE1C_C1_ASSET_QUALIFICATION_R1.md, from the pre-R1.3.1 directory listing

# ---------- 1. STAGE1C_C1_ASSET_QUALIFICATION_R1.md : drop appended section 15 ----------
p1 = ROOT + r"\docs\STAGE1C_C1_ASSET_QUALIFICATION_R1.md"
b = open(p1, 'rb').read()
marker = "**文档状态：`READY_FOR_HUMAN_REVIEW`**".encode('utf-8')
i = b.find(marker)
assert i != -1, "doc-status marker not found"
end = i + len(marker)
print("current size      :", len(b))
print("size w/o trailing NL:", end, "    size w/ trailing NL:", end + 1)
print("target original   :", ORIG_SIZE_1)
assert end in (ORIG_SIZE_1, ORIG_SIZE_1 - 1), "revert is not byte-exact -> investigate"
b2 = b[:end] if end == ORIG_SIZE_1 else b[:end] + b"\n"
open(p1, 'wb').write(b2)
print("RESTORED size     :", len(b2), " byte-exact:", len(b2) == ORIG_SIZE_1)
print("removed tail head :", b[end:end+80])
print()

# ---------- 2. GEOMETRY_ANATOMY_CHECK.md : drop inserted correction box ----------
p2 = ROOT + r"\production_spec\stage1c_c1_qualification\stats\GEOMETRY_ANATOMY_CHECK.md"
c = open(p2, 'rb').read()
anchor = "> 视角约定：手指 −Z；**背侧 +Y**；**掌侧 −Y**；拇指侧（桡侧）+X。".encode('utf-8')
j = c.find(anchor)
assert j != -1, "anchor not found"
start = j + len(anchor)
k = c.find(b"\n---\n", start)
assert k != -1, "separator not found"
print("GAC before :", len(c))
print("GAC removed:", k - start, "bytes")
print("GAC head of removed:", c[start:k][:70])
c2 = c[:start] + c[k:]
open(p2, 'wb').write(c2)
print("GAC after  :", len(c2))
print()
print("sha256 STAGE1C_C1_ASSET_QUALIFICATION_R1.md      =", hashlib.sha256(b2).hexdigest())
print("sha256 GEOMETRY_ANATOMY_CHECK.md                 =", hashlib.sha256(c2).hexdigest())
