from common import *
import numpy as np
targetcheck=read(OUT/'TARGETED_READONLY_WEB_CHECK.json')['states']
code=(OUT/'package_evidence.py').read_text(encoding='utf8').split('# Reproducible plots, not generated or retouched anatomy.')[1]
exec(compile(code,'<evidence_plots_only>','exec'))
