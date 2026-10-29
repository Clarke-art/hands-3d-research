from pathlib import Path
p=Path(r'<HANDS_ROOT>_contact_derivative_feasibility_recovery_r1')
s=(p/'extra_probe.py').read_text();s=s[:s.index('# Stage node')]+"\nnp.savez_compressed(O/'ORIGINAL_JACOBIAN.npz',jac=jold,x=x);ns['gfun'].save(str(O/'ORIGINAL_G.casadi'));save('ORIGINAL_DIRECT_BUDGET.json',dict(charged_seconds=time.monotonic()-start))\n"
(p/'direct_original.py').write_text(s)
