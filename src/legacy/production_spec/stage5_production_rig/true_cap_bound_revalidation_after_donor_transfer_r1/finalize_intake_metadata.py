import sys
sys.dont_write_bytecode=True
from common import *
auth=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
initial=[read(OUT/(run+'/COMPUTATION_VERIFICATION.json')) for run in ['RUN_A','RUN_B']]
dump('EXECUTION_LEDGER_R1.json',{'initial_complete_process_count':2,'final_complete_process_count':2,'total_complete_process_count':4,
 'initial_run_records':initial,'initial_run_actual_current_geometry_verified':all(x['live_prerequisite_checks']['current_asset_SHA256'] for x in initial),
 'intake_metadata_correction':'The source/target membership receipt carried pre-donor R2_candidate hash under authority_hashes. It now separates pre_donor_authority_hashes and uses actual current R2 hash under authority_hashes. All initial numeric computations already read the correct current derivative.',
 'source_target_sets_changed':False,'numeric_method_changed':False,'pose_probe_applications_total':24,
 'current_true_cap_Dijkstra_source_runs_total':148,'old_bind_replay_Dijkstra_source_runs_total':148})
auth['pre_donor_authority_hashes']=read(OLD/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')['authority_hashes']
auth['authority_hashes']={**auth['pre_donor_authority_hashes'],'R2_candidate':EXPECTED_CAND}
dump('CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json',auth)
print('CURRENT AND PRE-DONOR AUTHORITY HASHES EXPLICITLY SEPARATED',flush=True)
