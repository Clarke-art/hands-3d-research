# one-off read-only query: arc positions of the frozen-boundary vertices
import bpy, sys, os, json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
S5B = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "..", "stage5_production_rig",
                                   "stage5b_r1b", "scripts"))
sys.path.append(S5B)
import r1b_common as C
RC = C.RC

ctx = C.build_context()
NV, ARC, MED = ctx["NV"], ctx["ARC"], ctx["MED"]
s_MCP, s_IP = ctx["s_MCP"], ctx["s_IP"]
NAIL, CAP, WEB, own = ctx["nail"], ctx["cap"], ctx["first_web"], ctx["thumb_own"]
P_MCP = sorted(i for i in own if abs(ARC[i] - s_MCP) <= 2 * MED)
P_IP = sorted(i for i in own if abs(ARC[i] - s_IP) <= 2 * MED)

print("MED=%.6f  s_MCP=%.4f s_IP=%.4f" % (MED, s_MCP, s_IP))
for nm, S in (("NAIL", NAIL), ("CAP", CAP), ("FIRST_WEB", WEB)):
    a = sorted(ARC[i] for i in S)
    print("%-10s n=%2d  arc=[%.3f, %.3f]  median=%.3f" % (nm, len(S), a[0], a[-1], a[len(a)//2]))
    print("           members:", sorted(S))

nail_in_ip = sorted(i for i in NAIL if i in set(P_IP))
nail_in_mcp = sorted(i for i in NAIL if i in set(P_MCP))
web_in_ip = sorted(i for i in WEB if i in set(P_IP))
web_in_mcp = sorted(i for i in WEB if i in set(P_MCP))
print("NAIL inside IP patch core:", len(nail_in_ip), "arcs",
      [round(ARC[i], 3) for i in nail_in_ip])
print("NAIL inside MCP patch core:", len(nail_in_mcp))
print("WEB  inside IP patch core:", len(web_in_ip), "arcs",
      [round(ARC[i], 3) for i in web_in_ip])
print("WEB  inside MCP patch core:", len(web_in_mcp), "arcs",
      [round(ARC[i], 3) for i in web_in_mcp])
print("IP patch core size=%d ; MCP patch core size=%d" % (len(P_IP), len(P_MCP)))

# lateral radius distribution of the IP patch core (palmar vs dorsal side proxy)
lat = sorted((ctx["dth"][i], i) for i in P_IP)
print("IP patch core lateral radius min=%.3f max=%.3f" % (lat[0][0], lat[-1][0]))

# which of the worst-case faces' vertices are frozen?
for cid in ("TH_IP_30", "TH_IP_45", "TH_MCP_45"):
    pass
print("QUERY_DONE")
