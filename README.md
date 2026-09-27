# EM24 Natural Flair v1 

**Experimental match-physics modification for Football Manager 2024.**

EM24 Natural Flair adjusts selected physics parameters in FM24's existing match engine. Version 1.1 retains the v1.0 movement, passing, shooting, heading, and goalkeeper settings and fine-tunes ten timing parameters related to defensive challenges and physical contact.

> **Important:** This is **not** a replacement match engine. It does not add animations, skills, tactical AI, new dribble types, referee logic, or guaranteed changes to foul/card rates. Results may vary; v1.1 has not been fully validated in gameplay.

## Features and scope

- **Player movement:** Adjusted acceleration, deceleration, turning, and direction-change thresholds inherited from v1.0.
- **Ball physics:** Adjusted kick-speed and heading parameters inherited from v1.0.
- **Physical challenges:** v1.1 tweaks the timing of shoulder challenges, slide tackles, blocked tackles, and certain ball challenges.
- **Goalkeepers:** Preserves the v1.0 diving and save-recovery settings.

For exact v1.0-to-v1.1 changes, see [CHANGELOG.md](CHANGELOG.md). For suggested in-game checks, see [TEST_PLAN.md](TEST_PLAN.md).

## Installation: public patch

This repository **does not include** FM24's copyrighted `simatch.fmf`. You must use your own legally obtained, compatible game file to generate the patched archive.

**Requirements:** Python 3.9+ and the Python package `zstandard` (or a compatible system `libzstd`).

1. Back up your original `simatch.fmf` before doing anything else.
2. Download these repository files and open a terminal in this directory.
3. Install the dependency:

   ```powershell
   py -m pip install zstandard
   ```

4. Run the patch script, replacing the example path with the location of your **own** FM24 game installation:

   ```powershell
   py em24_v1_1_duels_build.py "C:\Program Files (x86)\Steam\steamapps\common\Football Manager 2024\data\simatch.fmf" --out-dir .
   ```

5. The script produces `EM24_Natural_Flair_v1.1_Duels.fmf`. Close FM24 and copy that output into your game's `data` directory, renaming the copy to `simatch.fmf`. Keep the original backup outside that folder.
6. Start FM24 and test in a friendly or a separate save. Restore the backed-up file if you encounter unexpected behavior.

**Compatible inputs:** Only the recognized original FM24 physics build used to develop this patch, EM24 v0.1, and EM24 v1.0. Other game versions and third-party physics mods are intentionally rejected. An updated or differently packaged installation may not be recognized.

This is a **manual installation**, not a Steam Workshop one-click subscription. Use only one replacement `simatch.fmf` at a time. Steam's game-file verification or updates may restore the original.

## Verification and limitations

- Build-time archive checks reported **109 preserved resources** with only the intended physics file changed.
- v1.1 changes **10 contact-timing parameters** compared with v1.0; the full patch has **28 modified physics parameters**.
- These are technical integrity checks, **not evidence of gameplay balance**. See [VERIFICATION.json](VERIFICATION.json) for build metadata.
- No new rabona, trivela, bicycle-kick, fake-shot, or fake-pass animation is included.

## Publishing

This repository includes the patch script and documentation, **not game archives**. Do not upload the ready-to-install `simatch.fmf` produced from a game installation. The original patch script and accompanying documentation are released under the [MIT License](LICENSE). The `LICENSE_NOTE.txt` is a separate distribution note; neither file grants rights to Sports Interactive / SEGA game assets.

*Unofficial community project. Not affiliated with Sports Interactive or SEGA.*
