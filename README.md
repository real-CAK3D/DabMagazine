# Dab Magazine

The Garden's monthly humor magazine: every comic strip drawn that month, bound into one issue behind a painted cover starring Clydius, the Garden's goofy pit bull mascot (in the spirit of the classic humor magazines — its own logo and mascot, no borrowed characters).

Part of the Garden's papers, all read through **[The Corner Chronicle](https://github.com/real-CAK3D/NewsStand)** — one home-screen app that mounts every paper under one private (Tailscale-only) HTTPS address: [The Double Wide](https://github.com/real-CAK3D/TheDoubleWide) (daily), [The Re-Up](https://github.com/real-CAK3D/TheRe-Up) (want ads), [The Sunday Smoke](https://github.com/real-CAK3D/TheSundaySmoke) (Sundays), [Roach Clips](https://github.com/real-CAK3D/RoachClips) (Tuesdays), [The Green Thumb](https://github.com/real-CAK3D/TheGreenThumb) (the directory), [Dime Bags](https://github.com/real-CAK3D/DimeBags), [Trail Mix](https://github.com/real-CAK3D/TrailMix), [Dab Magazine](https://github.com/real-CAK3D/DabMagazine), [Hashish](https://github.com/real-CAK3D/Hashish), [The Perennial](https://github.com/real-CAK3D/ThePerennial), [Baked Goods](https://github.com/real-CAK3D/BakedGoods) and [Extra! Extra!](https://github.com/real-CAK3D/ExtraExtra). The papers are written by [Hermes](https://github.com/NousResearch/hermes-agent) agents running on a small Oracle VM called The Garden.

## Files

| File | What it does |
|---|---|
| `build_dab.py` | Collects the month's strips, draws the cover once (gpt-image-2 via the Codex login) and binds the issue. |
| `gardenweb.py` | The small shared web-server kit every Garden paper carries its own copy of. |

## Running

This month's issue grows nightly; the finished issue lands on the 1st. Served at `/dab/`. Each project is Linux-first (`%-d` date formatting) and expects a Hermes install on the same machine.
