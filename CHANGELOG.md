# Changelog

## v1.1 — Aggressive Duels

The movement, passing, shooting, heading, and goalkeeper settings from v1.0 are unchanged. This update modifies **10 defensive/contact timing parameters** across two physics variants (20 numeric values in total).

| Parameter | v1.0 | v1.1 |
|---|---:|---:|
| `min_delay_for_ball_lunge_do` | 1500 | 1460 |
| `min_delay_for_ball_lunge_receive` | 770 | 790 |
| `min_delay_for_block_tackle_do` | 500 | 470 |
| `min_delay_for_block_tackle_receive` | 775 | 800 |
| `min_delay_for_force_opponent_to_lose_ball_do` | 500 | 470 |
| `min_delay_for_force_opponent_to_lose_ball_receive` | 500 | 525 |
| `min_delay_for_shoulder_charge_do` | 500 | 470 |
| `min_delay_for_shoulder_charge_receive` | 2050 | 2130 |
| `min_delay_for_slide_tackle_do` | 1500 | 1450 |
| `min_delay_for_slide_tackle_receive` | 780 | 815 |

**Design intent:** Moderately shorten certain minimum intervals before challenge actions and slightly extend selected post-contact response intervals. These settings do **not** guarantee more successful tackles or an increase in fouls.

**Not changed in v1.1:** Movement and ball-speed settings, turning, passing, shooting, heading, goalkeeper parameters, injury thresholds, two-footed tackle settings, violent-conduct settings, or the foul/card decision algorithms. No new animations or AI routines have been added.

**Testing status:** Archive integrity checks passed. Extensive in-game testing and balance validation are still pending.
