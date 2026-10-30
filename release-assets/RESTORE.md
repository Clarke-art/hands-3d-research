# Independently restore the published research

The repository is Public. [v0.1.0-research](https://github.com/Clarke-art/hands-3d-research/releases/tag/v0.1.0-research) is formally published with 18 public research ZIPs totaling 7,658,061,482 bytes. Restore from GitHub into a new, empty directory on your own machine; no original Hands workspace, local audit copies, authentication or paid LFS is needed.

## Obtain the repository and attachments

1. Clone `https://github.com/Clarke-art/hands-3d-research.git` with Git long-path support where required: `git -c core.longpaths=true clone https://github.com/Clarke-art/hands-3d-research.git`. Record `git rev-parse HEAD`. The original licensing/research baseline is `01cfab7263c98acb3da832a902de96f5e2c6b66f`; later main revisions may update publication documentation.
2. Use the 18 exact public URLs in [DOWNLOADS.md](DOWNLOADS.md), or the public API `https://api.github.com/repos/Clarke-art/hands-3d-research/releases/tags/v0.1.0-research` and each asset's `browser_download_url`. GitHub's automatic source-code ZIP/tarball is not a substitute for these research attachments.
3. Check all filenames, exact byte counts and SHA256 hashes against [R1_RELEASE_ASSETS.csv](R1_RELEASE_ASSETS.csv) and [SHA256SUMS.txt](SHA256SUMS.txt) from the repository. For example, use PowerShell `Get-FileHash -Algorithm SHA256` or `sha256sum`. Reject missing/extra research ZIPs, unexpected sizes or mismatched hashes. Never execute downloaded historical code merely to validate an archive.

## Restore the selected payload

Each archive contains `PUBLIC_FILE_INDEX.json`, `README.txt` and `payload/` members. Extract verified payload members into a separate logical history root, preserving their relative paths. Before extraction reject duplicate names, absolute paths, path traversal, symlinks and unexpected members. The root README and index are archive metadata, not historical payload files. A fresh independent integrity audit can compare member sizes/hashes with the per-archive index and [R1_PUBLICATION_MANIFEST.csv](R1_PUBLICATION_MANIFEST.csv).

[ORIGINAL_PATH_MAP.csv](ORIGINAL_PATH_MAP.csv) records original paths, canonical aliases, transformations and intentional exclusions. The six core Blender models remain in the repository's `models/`; scientific history lives under the restored payload tree. Normalized public text may differ from original private source bytes. Excluded external motion/reference data, private records, installed dependency trees and two sets of intermediate PNGs cannot all be reconstructed byte for byte. The retained videos, keyframes, scientific data and sources do not promise lossless frame-by-frame PNG recovery.

## Rebuild the minimal environment

Follow the repository [README](../README.md) and [environment/REBUILD.md](../environment/REBUILD.md), installing dependencies independently. The existing six unittest cases require zero failures and zero skips for a six-case PASS. Open Blender models with factory startup and autoexec disabled; record the actual Blender version and missing linked libraries/images. Model opening and minimal tests do not certify all historical solvers or the visual quality of animations. **Continuous natural dual-hand motion remains unfinished; this is not a mature automatic performance product.**

Original software uses MIT (Copyright (c) 2026 Clarke-art); original research documents, model contributions and authorized research data/media use CC BY 4.0, attributed to Clarke-art. Retain [LICENSE](../LICENSE), [COPYRIGHT.md](../COPYRIGHT.md), [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md), the full license texts and [R2_LICENSE_SCOPE.csv](R2_LICENSE_SCOPE.csv) with restored research. Third-party terms remain unchanged: PianoPlayer MIT/Marco Musy, Blender Human Base Meshes CC0 source notices, Mutopia saved public-domain edition provenance, and other upstream terms.

The prior remote download audit already verified all 18 ZIPs and 6,622 payload members. This documentation closeout checks anonymous public access and GitHub metadata with HEAD/limited Range requests; it does not repeat the full 7.658 GB download, member verification, environment rebuild or Blender acceptance, and does not claim a new full independent restore run. Public access and prior integrity evidence are separate checks. Local cleanup requires a separate exact-path inventory and Human deletion approval.
