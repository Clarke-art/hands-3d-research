# Shared original MIDI clock

Original MIDI SHA256 `fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75`. PPQ 384; tempo 428571 µs/quarter; 3/4, four bars, ticks 0–4608, music duration 5.142852 s. All 23 original identities/pitches/channels/velocities and NOTE_ON/OFF ticks read directly from original MIDI and matched individually against the approved timelines.

Verified report leads: R 0.30 s; L 0.35 s. Common preparation lead 0.35 s. `T_PRESENT = T_MUSIC + 0.35`; `F_SHARED = 1 + 60*T_PRESENT`; R Action origin shifts +3 frames; L +0 frames. No time scaling, interpolation change or musical event alteration. Actual Action curves are checked next.

| ID | Hand/finger | MIDI | Channel | Velocity | ON tick | OFF tick | T_MUSIC ON | T_MUSIC OFF |
|---|---|---|---|---|---|---|---|---|
| R00 | R/5 | 74 | 0 | 90 | 0 | 384 | 0.0000000 | 0.4285710 |
| R01 | R/1 | 67 | 0 | 90 | 384 | 576 | 0.4285710 | 0.6428565 |
| R02 | R/2 | 69 | 0 | 90 | 576 | 768 | 0.6428565 | 0.8571420 |
| R03 | R/3 | 71 | 0 | 90 | 768 | 960 | 0.8571420 | 1.0714275 |
| R04 | R/4 | 72 | 0 | 90 | 960 | 1152 | 1.0714275 | 1.2857130 |
| R05 | R/5 | 74 | 0 | 90 | 1152 | 1536 | 1.2857130 | 1.7142840 |
| R06 | R/1 | 67 | 0 | 90 | 1536 | 1920 | 1.7142840 | 2.1428550 |
| R07 | R/1 | 67 | 0 | 90 | 1920 | 2304 | 2.1428550 | 2.5714260 |
| R08 | R/5 | 76 | 0 | 90 | 2304 | 2688 | 2.5714260 | 2.9999970 |
| R09 | R/3 | 72 | 0 | 90 | 2688 | 2880 | 2.9999970 | 3.2142825 |
| R10 | R/4 | 74 | 0 | 90 | 2880 | 3072 | 3.2142825 | 3.4285680 |
| R11 | R/3 | 76 | 0 | 90 | 3072 | 3264 | 3.4285680 | 3.6428535 |
| R12 | R/4 | 78 | 0 | 90 | 3264 | 3456 | 3.6428535 | 3.8571390 |
| R13 | R/5 | 79 | 0 | 90 | 3456 | 3840 | 3.8571390 | 4.2857100 |
| R14 | R/1 | 67 | 0 | 90 | 3840 | 4224 | 4.2857100 | 4.7142810 |
| R15 | R/1 | 67 | 0 | 90 | 4224 | 4608 | 4.7142810 | 5.1428520 |
| L00 | L/5 | 55 | 1 | 90 | 0 | 768 | 0.0000000 | 0.8571420 |
| L01 | L/3 | 59 | 1 | 90 | 0 | 768 | 0.0000000 | 0.8571420 |
| L02 | L/1 | 62 | 1 | 90 | 0 | 768 | 0.0000000 | 0.8571420 |
| L03 | L/4 | 57 | 1 | 90 | 768 | 1152 | 0.8571420 | 1.2857130 |
| L04 | L/3 | 59 | 1 | 90 | 1152 | 2304 | 1.2857130 | 2.5714260 |
| L05 | L/2 | 60 | 1 | 90 | 2304 | 3456 | 2.5714260 | 3.8571390 |
| L06 | L/3 | 59 | 1 | 90 | 3456 | 4608 | 3.8571390 | 5.1428520 |

Audio is synthesized once from this shared 23-note timeline using the existing Grand sample algorithm; separate source video soundtracks are not mixed. Detailed data: PERFORMANCE_TIMELINE.json.
