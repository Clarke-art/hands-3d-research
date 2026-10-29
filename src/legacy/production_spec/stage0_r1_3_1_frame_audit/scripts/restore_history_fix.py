import hashlib
p = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\GEOMETRY_ANATOMY_CHECK.md"
c = open(p, 'rb').read()
anchor = "> 视角约定：手指 −Z；**背侧 +Y**；**掌侧 −Y**；拇指侧（桡侧）+X。".encode('utf-8')
start = c.find(anchor) + len(anchor)
print("size now:", len(c), " (original was 9208)")
print("context:", c[start-20:start+30])
c2 = c[:start] + b"\n" + c[start:]
open(p, 'wb').write(c2)
print("size after +1 NL:", len(c2), " byte-exact:", len(c2) == 9208)
print("sha256 =", hashlib.sha256(c2).hexdigest())
