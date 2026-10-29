# Restore selected research

After public publication: anonymously clone the verified repository main commit into an empty short directory (`git -c core.longpaths=true clone https://github.com/Clarke-art/hands-3d-research.git`). Obtain the exact 18 real ZIP assets from the verified v0.1.0-research GitHub Release, using the remote release API and browser_download_url. Do not use local objects, prior ZIPs, cached files or an original workspace. Do not enable paid LFS.

Verify every ZIP against SHA256SUMS.txt and R1_RELEASE_ASSETS.csv obtained from the remote commit. Reject missing/extra archive assets, mismatched sizes and hashes. Compare PUBLIC_FILE_INDEX.json against R1_PUBLICATION_MANIFEST.csv for every member; verify uncompressed member size and SHA. Reject duplicate, absolute or traversal paths, symlinks and unexpected members (only README.txt and PUBLIC_FILE_INDEX.json are container metadata).

Extract verified payload/ members into a separate logical history root under this isolated environment. Preserve each relative path; do not execute archived code. ORIGINAL_PATH_MAP.csv records canonical aliases, transformations and intentionally unshared inputs; these exclusions cannot be recovered byte for byte from the public release. The six models in Git remain at models/; scientific history lives under the restored payload tree.

Run the README examples and existing six unittest cases in a fresh environment with independently installed dependencies. Require zero failures and zero skips for the six-case check. Open all six core Blender models with factory startup and autoexec disabled, recording actual Blender version, linked libraries/images and missing dependencies. Model opening is not visual approval of animations.

Check README, all 18 actual download links, research overview, index, 148 cards, local Markdown targets, license forms, scope, upstream notices and dataset provenance. Record every check separately. Remote recovery PASS requires all checks; otherwise PARTIAL, no local retirement. Current status: NOT RUN, no public release exists.
