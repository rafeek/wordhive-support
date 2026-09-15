# WordHive Puzzles — support site

Public support and privacy pages for the WordHive Puzzles app, served with GitHub Pages
from the root of this repository.

| Page | URL |
| --- | --- |
| Support | `https://rafeek.github.io/wordhive-support/` |
| Privacy policy | `https://rafeek.github.io/wordhive-support/privacy.html` |

Both URLs go in App Store Connect under the app's version information.

`.nojekyll` disables Jekyll processing — these are plain static files.

## Editing

Edit the HTML directly and push; Pages redeploys within a minute or two. The three
how-to-play pages are generated — edit `gen_help.py` and run it, keeping the text in
step with `HelpContent` in the app's `SettingsView.swift`.
