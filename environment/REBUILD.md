# Environment boundaries

Base: Python 3.12, standard library only; the MIT PianoPlayer core subset is included with license. `python -m venv .venv`, then `.venv/Scripts/python -m pip install -r requirements.txt`. No model weights required.

Optional geometry: `python -m pip install --only-binary=:all: -r requirements-geometry.txt`. Historical solvers require the per-environment exact-version lists; these are inventories, not proof that all old ABI combinations still install or execute.

The original fingering npm package-lock is retained as historical metadata. To study that optional route, obtain packages directly from the recorded registry/version and run `npm ci --ignore-scripts` in a fresh directory after separately reviewing weight/data terms. This project does not redistribute Lumikey weights or certify their rights.

Installed Python package files were compared with distribution RECORD: 11096 match, 0 mismatches, 20 have no content hash, 10 are unrecorded non-Python installation metadata. The latter are not classified as modified programs. npm content was not re-downloaded to prove tarball byte identity; the lockfile records its original integrity and package sources. Never assume a package license grants training-data/model rights.

Blender is an external tool. Use factory startup and disable autoexec when reading models; do not run archival solve, delete, fetch or render scripts to test restoration.
