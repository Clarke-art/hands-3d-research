# Source and license — MIDI driven dual hand POC R1

Retrieved / checked 2026-10-08. Source files are retained in `source/`; hashes and score/MIDI checks are in `SOURCE_MIDI_AUDIT_R1.json`.

## Score and MIDI

- Work: Musette, BWV Anh.126. Credit follows the supplied Mutopia edition; this audit does not independently adjudicate historical attribution.
- Official page: https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=79
- MIDI: https://www.mutopiaproject.org/ftp/BachJS/BWVAnh126/anna-magdalena-22/anna-magdalena-22.mid
- PDF: https://www.mutopiaproject.org/ftp/BachJS/BWVAnh126/anna-magdalena-22/anna-magdalena-22-a4.pdf
- LilyPond: https://www.mutopiaproject.org/ftp/BachJS/BWVAnh126/anna-magdalena-22/anna-magdalena-22.ly
- Mutopia labels this edition Public Domain. The PDF carries the typesetter's public-domain notice; maintainer/typesetter Allen Garvin, edition Mutopia-2013/01/06-79, source Bach-Gesellschaft.
- Used excerpt: measures 1–2, first occurrence, without adding repeat playback. No notes, duration, tempo or velocity changed. The 0.7-second preparation offset is shared by all output systems.
- Staff one/voiceone is the treble/right part; staff two/voicetwo is the bass/left part. The first two bars were checked in the rendered PDF and compared exactly against the LilyPond and MIDI pitch/tick sequences.
- No finger numbers are supplied in the official score or MIDI. This POC's 5–4–3–2–1 right descent and 5/1 left octave alternation are designed provisional fingering, requiring Human review.

## Piano audio

- Existing product source: `piano/release/grand-piano-v1.1-rc-candidate/assets/audio/vcsl-kawai-grand/` and its `data/V1_1D_PIANO_SAMPLE_MANIFEST.json`.
- Upstream: https://github.com/sgossner/VCSL
- Instrument: `Chordophones/Zithers/Grand Piano, Kawai`.
- Publisher: Versilian Studios LLC / VCSL contributors.
- License: CC0-1.0, confirmed by the existing source notice and upstream repository. https://github.com/sgossner/VCSL/blob/master/LICENSE
- Library page: https://versilian-studios.com/vcsl-keys/
- Source Ogg files are read in place and checked against the approved manifest SHA256. No source audio file is modified. The local copy of the manifest and license notice is under `source/`.
- Offline adapter uses the existing zone root MIDI, pitchRatio, velocity-layer threshold, amplitude law and release-envelope concept. A per-asset leading recording-silence trim is documented in `KEY_AUDIO_SYNC_R1.json`; all MIDI times remain unchanged. No oscillator is used.
- Filename octaves use sampler notation C3=MIDI60; the timeline/UI use scientific notation C4=MIDI60. The manifest's numerical MIDI mapping, not filename octaves, is authoritative.

## Hands, keyboard and new motion

- Hands use the user-approved frozen R2 and L1 canonical assets. Their ownership/license is inherited from the project; no broader license grant is inferred here.
- Keyboard geometry, dimensions and press pivots come from the accepted frozen Grand 88-key authority. This POC renders those keys without altering their source files.
- New joint rotations are computed from these rest rigs and the current MIDI/design plan. No PianoVAM Action, fitted root motion, landmark trajectory, or noncommercial source-derived animation is loaded into the candidate or audio/video execution path.
- Prior audit code contributes only canonical asset metadata, fixed marker definitions and keyboard geometry measurement helpers. It contributes no performance motion.
- The candidate contains only new `NEW_MIDI_PROCEDURAL_*` hand actions and timeline-generated key actions. This is an experimental audit artifact, not a commercial release or production approval.
