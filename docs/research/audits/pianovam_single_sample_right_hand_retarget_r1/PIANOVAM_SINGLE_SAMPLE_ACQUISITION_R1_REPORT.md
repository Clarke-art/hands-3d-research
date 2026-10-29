# PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1

Acquisition succeeded with one solo recording attempt. No entire dataset or directory download.

| Field | Result |
|---|---|
| Dataset/release | PianoVAM/PianoVAM_v1, v1.2 |
| Recording | 2024-03-04_03-46-36 |
| Piece (metadata verbatim) | N/A [Piano Sonata No. 16 in C Major, K.545 (1st Mvt)] |
| Performer | Yonghyun |
| Duration | 22.805 seconds in metadata; video 22.833333 seconds, 1370 frames at 60fps |
| Files downloaded | 5: metadata.json, selected skeleton, MIDI, Fingering, Video |
| Bytes downloaded | 10,679,148 |
| Generated metadata entry | selected_metadata_entry.json, excluded from network file/byte count |
| Window | 11.5–18.5 seconds, 7 seconds, physical right 421/421 valid frames |
| Right note labels | 39 predicted R notes; fingers 1,2,3,4,5 |

The shortest two solo entries are 22.400 s Ravel and 22.805 s Mozart. HEAD requests found Mozart video 7,343,859 bytes versus Ravel 9,052,490 bytes, with richer fingering coverage. Mozart was selected; only that recording was downloaded. The 30 MB video cap was checked before GET. Four-hands was excluded. All source files retain their original bytes and SHA256 in the status manifest.

The actual JSON is keyed by decimal frame strings, with `Left` and `Right` values of null or 21 xyz triplets. Frame count matches the video exactly. Coordinates are normalized image positions and relative depth, not metric world coordinates. Native x/y are near [0,1], so the repository GUI's [-1,1] remapping must not be applied. Aspect-correct y by 1080/1920; retain z's width-normalized scale.

**Important recording-specific correction:** source overlays at frames 300,420,600,780 prove the physical right hand occupies JSON `Left`; JSON `Right` overlays the performer's physical left hand. Original source labels are preserved. The selected window uses physical right, not a left-hand performance mislabeled as right. Its tracking is complete without gap filling. Automated Fingering R labels select musical context and are not manual ground truth. Direct MIDI parsing matches all Fingering onsets within 0.000000334 seconds. MIDI never generates motion.

Dataset and derived motion usage: **CC BY-NC-SA 4.0 / INTERNAL_NONCOMMERCIAL_VALIDATION_ONLY**. **DO_NOT_PROMOTE_DATASET_MOTION_TO_COMMERCIAL_PRODUCT**. Source: [PianoVAM v1.2](https://huggingface.co/datasets/PianoVAM/PianoVAM_v1); reference [PianoVAM-Code](https://github.com/yonghyunk1m/PianoVAM-Code); [license](https://creativecommons.org/licenses/by-nc-sa/4.0/). Attribution: Kim, Yonghyun; Park, Junhyung; Bae, Joonhyung; Kim, Kirak; Kwon, Taegyun; Lerch, Alexander; Nam, Juhan. *PianoVAM: A Multimodal Piano Performance Dataset*, ISMIR 2025. Changes: selected hand-local sequence and skeletal retarget; retain the dataset license on motion adaptations. The frozen product hand's approval is separate from these test motion assets.

Evidence: PIANOVAM_HANDSKELETON_SCHEMA_R1.json, PIANOVAM_SELECTED_WINDOW_R1.json, source_window.mp4, overlay*.png. Acquisition status: PIANOVAM_SINGLE_SAMPLE_ACQUISITION_R1_STATUS.json.
