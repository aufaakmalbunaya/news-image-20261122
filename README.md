# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/aufaakmalbunaya/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/aufaakmalbunaya/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Gulf in Flames: a dense newspaper front page summing up Sunday 22 November 2026 in one image. 46 stories, all of which happened or were first reported that day: three hero panels (Iran strikes a US air base in Kuwait as the Gulf burns, the capture of cartel kingpin El Chapo Isidro in Sinaloa, and a magnitude 6.9 earthquake in the Peruvian Andes), twelve illustrated leads (drones hitting a Russian ship in the Baltic, the barrage on Kryvyi Rih, Estonia's border closure, Trump landing in Shenzhen, Israel's coalition talks, Bolsonaro in intensive care, the COP31 impasse, France's shrinking protests, England thrashing the All Blacks, France reaching the Nations Championship final, Australia's first T20 win, and Verstappen's Las Vegas pole), a seven-number strip, a sketch world map with fifteen numbered pins, region and field counts that add to 46, 31 more stories in brief, and a date-check footer naming the big 19 November stories deliberately left out (the ICJ Myanmar ruling, the Shenzhen trilateral, the Anthropic debut).

## How it is built

`main.py` draws the whole page (1024x1024 PNG) with the Python standard library only: its own canvas, a 5x7 bitmap font, fourteen flat-vector scene painters, and a PNG encoder written with `zlib` and `struct`. No third-party packages, no network, no clock, no randomness, so the graded run is deterministic and both runs write the same bytes.

## Run it

```sh
python3 main.py          # write entry.png to $MAKEFUN_OUTPUT_DIR
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
