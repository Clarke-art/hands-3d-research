# VCSL Kawai Grand Piano — source and license notice

- Library: Versilian Community Sample Library (VCSL)
- Instrument: `Chordophones/Zithers/Grand Piano, Kawai`
- Publisher/maintainer: Versilian Studios LLC / VCSL contributors
- Upstream repository: https://github.com/sgossner/VCSL
- Instrument source directory: https://github.com/sgossner/VCSL/tree/master/Chordophones/Zithers/Grand%20Piano%2C%20Kawai
- Library information: https://versilian-studios.com/vcsl-keys/
- License: CC0 1.0 Universal
- Redistribution: permitted
- Commercial/product use: permitted
- Attribution: not required by CC0; this notice is retained for provenance.

## Product transformation

The 18 files in this directory are transcoded from the upstream 44.1 kHz, stereo, 16-bit PCM WAV files to Ogg Vorbis quality 4. No synthesis, pitch correction, or content substitution was applied. The exact upstream path, product byte count, and SHA-256 digest of every file are recorded in `data/V1_1D_PIANO_SAMPLE_MANIFEST.json`.

The product bundles two source velocity layers (`v2` and `v4`) at nine root notes. Every MIDI note 21–108 resolves to a bounded zone. Source release samples exist, but V1.1D does not bundle them; note release is handled by a gain envelope. No oscillator fallback exists.
