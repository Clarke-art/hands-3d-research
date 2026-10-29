# Omitted reinstallable SciPy runtime

R1 incremental vendor-package correction intentionally excluded the Python 3.13 SciPy 1.18.1 installation at `_deps313/scipy/`. Its installed source files and fft/_duccfft/LICENSE.md are not distributed in the research release. The six old research-card links now resolve to this explicit exclusion note instead of missing files. No deleted runtime file is silently reintroduced.

Obtain the pinned historical runtime independently from the official package registry and retain its original third-party notices: [SciPy 1.18.1 on PyPI](https://pypi.org/project/scipy/1.18.1/). Availability and historical ABI replay are not certified by this note. The minimal geometry smoke uses the separately documented NumPy dependency and does not require this entire SciPy installation.

See [environment rebuilding](REBUILD.md) and [original path decisions](../release-assets/ORIGINAL_PATH_MAP.csv). R1 references remain preserved in the immutable R1 candidate and audit; R2 changes only this navigation mapping.
