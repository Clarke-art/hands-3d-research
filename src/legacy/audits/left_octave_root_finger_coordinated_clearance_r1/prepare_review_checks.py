from pathlib import Path
P=Path(__file__).resolve().parent;LAST=P.parent/'left_little_finger_moving_key_reachability_r1'
(P/'review_server.cjs').write_text((LAST/'review_server.cjs').read_text(encoding='utf8').replace('port=8851','port=8863'),encoding='utf8')
(P/'06_review_check.cjs').write_text((LAST/'08_review_check.cjs').read_text(encoding='utf8').replace(':8851',':8863'),encoding='utf8')
print('LOCAL_REVIEW_CHECKS_PREPARED')
