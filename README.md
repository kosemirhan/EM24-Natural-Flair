# EM24 Natural Flair — v1

**An experimental match-physics mod for Football Manager 2024.**

EM24 Natural Flair adjusts selected parameters in FM24's existing match engine to experiment with player movement, ball physics, physical challenges, and goalkeeping. It is designed to offer a different feel on the pitch without favoring one specific tactic.

> **Important:** This is a physics modification, **not a new match engine**. It does not add new animations or guarantee more rabonas, trivelas, bicycle kicks, fake shots, or fake passes. The changes have passed archive-integrity checks, but extensive gameplay and balance testing is still in progress.

## Features

- **Player movement:** Adjustments to acceleration, deceleration, turning, and direction changes.
- **Passing and shooting:** Adjustments to selected kick-speed and heading parameters.
- **Physical duels:** Revised timing for shoulder challenges, tackles, and certain post-contact actions, intended to make challenges feel more physical.
- **Goalkeepers:** Adjustments to selected diving and recovery parameters.

The mod does **not** directly change the referee's decisions, foul or card probabilities, injury logic, tactical AI, or the frequency of individual skill animations.

## Download — choose one installation method

The **ready-to-install version** and the **build-it-yourself version** are published as **separate releases/tags**. Choose **one**; you do not need both.

**[View all releases and downloads](https://github.com/kosemirhan/EM24-Natural-Flair/releases)**

| Option | Who is it for? | What you download | Additional software |
| --- | --- | --- | --- |
| **A. Ready-to-install** | Players who want to replace one game file | The release ZIP containing `simatch.fmf` | None |
| **B. Build it yourself** | Players who want to patch their own original FM24 file | The separate build/patch release ZIP | Python 3.9+ and `zstandard` |

### Option A — ready-to-install (`simatch.fmf`)

1. Download the **ready-to-install** ZIP from its release on the [Releases page](https://github.com/kosemirhan/EM24-Natural-Flair/releases).
2. Extract the ZIP and locate `simatch.fmf`.
3. **Close Football Manager 2024.** In Steam, right-click FM24 and select **Properties → Installed Files → Browse**.
4. Open the `data` folder. **Copy its original `simatch.fmf` to a safe location outside the game folder.**
5. Copy the mod's `simatch.fmf` into the game's `data` folder and replace the existing file.
6. Start FM24 and try a friendly match or a separate save.

**No Python, terminal, or additional mod manager is needed for this method.** Only one replacement `simatch.fmf` can be active at a time.

### Option B — build it yourself (patch your own file)

Use this method if you prefer generating the modified archive from your **own legally obtained, compatible FM24 installation**. The public build package does not need to contain the game's original archive.

**Requirements:** Windows, Python 3.9 or newer, and the Python package `zstandard`.

1. Download the **build/patch** ZIP from its separate release on the [Releases page](https://github.com/kosemirhan/EM24-Natural-Flair/releases) and extract it to a folder.
2. Close FM24. Find your original `simatch.fmf` in the game's `data` folder and **back it up outside the game folder**.
3. Open **PowerShell** in the extracted build folder and install the dependency:

   ```powershell
   py -m pip install zstandard
   ```

4. Run the included build script. The command below finds the Python build script in the extracted folder, so its filename does not matter. Adjust the FM24 installation path if your Steam library is elsewhere:

   ```powershell
   $script = Get-ChildItem -File -Filter "*build.py" | Select-Object -First 1
   py $script.FullName "C:\Program Files (x86)\Steam\steamapps\common\Football Manager 2024\data\simatch.fmf" --out-dir ".\output"
   ```

5. Open the new `output` folder. Find the generated `.fmf` file, **copy it**, and rename that copy to `simatch.fmf`.
6. Put the renamed copy in FM24's `data` folder, replacing the original only **after** confirming you have a backup.
7. Start FM24 and test the mod.

The builder checks the source physics file and may reject unknown game builds or archives modified by other mods. If it does, restore a compatible original FM24 file; do not bypass the check. The script does not overwrite its input file.

## Uninstall / restore the original

1. Close FM24.
2. Replace the modded `simatch.fmf` in the game's `data` folder with the original copy you backed up.
3. Restart the game.

Steam game-file verification or a game update may also restore original files and disable the mod.

## Compatibility and testing

- Made for **Football Manager 2024**. Compatibility with other editions or every FM24 game build is **not guaranteed**.
- Existing saves can be used for initial testing, but keeping a separate test save is recommended.
- The archive passed technical checks intended to preserve the original resources outside the modified physics data. **This does not establish gameplay balance or universal compatibility.**
- To report an issue, open a [GitHub Issue](https://github.com/kosemirhan/EM24-Natural-Flair/issues) and include your FM24 game version, installation method, and a short description or video of the problem.

See [CHANGELOG.md](CHANGELOG.md) for technical changes and [TEST_PLAN.md](TEST_PLAN.md) for suggested match tests.

## License and distribution

The project's original build script and documentation are available under the [MIT License](LICENSE). This license **does not cover Football Manager 2024 or any Sports Interactive / SEGA assets**. A ready-to-install archive made from game files may require the rights holders' permission to distribute publicly; the build-it-yourself package is the alternative that lets users patch their own legally obtained files.

*Unofficial community project. Not affiliated with, endorsed by, or sponsored by Sports Interactive or SEGA.*
