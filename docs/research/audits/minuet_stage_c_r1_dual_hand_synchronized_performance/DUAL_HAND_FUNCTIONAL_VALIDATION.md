# Joint-scene functional validation

PASS for bounded original-event/Action/audio integration. The original MIDI was parsed independently:23 notes (16R,7L), original track/channel/pitch/velocity, NOTE_ON/OFF tick/type/velocity, PPQ384 and tempo428571µs/quarter. No source music or fingering was edited. Full original event records and source hashes: PERFORMANCE_TIMELINE.json.

Each target key is the matching frozen index MIDI−21. Actual animated frozen-key world parity maximum error:1.39083103899e-05mm. Three opening chord key curves remain exactly synchronous at all inspected down/hold/release samples. Both R06→R07 and R14→R15 G4 partial reset/repress sequences retain the approved shape and event relationship; SHARED_KEY_FUNCTIONAL_READBACK.json records actual angles.

One48kHz stereo Grand mix uses the existing sample manifest, same velocity threshold/pitch ratio/amplitude law/preroll trim/NOTE_OFF release, one common gain1. There are exactly23 unique NOTE_ON voice records and23 preserved NOTE_OFF timings, four simultaneously held notes at the opening chord+melody, no missing chord tone or duplicate scheduling. Max onset schedule quantization0.0101666667ms; audible trimmed sample onset delay0ms; all pitch checks within25cents; zero clipping. Source channels remain bound to the original event identities even though both share one Grand sampler.

The same shared presentation clock drives root, joints, keys, packed WAV and all three videos. Each video contains357frames at60fps; video/audio both5.95s, timestamps start0, full FFmpeg decode PASS. All three AAC tracks decode to identical audio; independent waveform correlation against the shared WAV shows0-sample lag at48kHz. Detailed evidence:MUX_AUDIO_CLOCK_VERIFICATION.json. Music remains5.142852s at1×; common preparation and release tail account for the remainder. There is no manually moved soundtrack or retimed voice.

Active sampled marker/skin contact vertical range:-0.114314 to1.44729mm; maximum horizontal miss:0mm. These are finite measurements. Exact approved-motion and key parity proves no new shared-coordinate contact displacement. Original skin-contact/penetration WARN remain WARN.

New joint-scene review item: the wrists approach around1.13s presentation; whole-hand X envelope overlap reaches4.072mm. This coarse envelope is not a collision finding. Normal teaching, overhead and side evidence shows no obvious interpenetration; no exhaustive geometric collision claim. Human should judge proximity and whether either wrist/contact is obscured.

Human original-speed naturalness remains HUMAN_PENDING. Machine functional PASS does not establish visual approval.
