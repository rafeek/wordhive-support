# WordHive Puzzles — support site

Public support and privacy pages for the WordHive Puzzles app, served with GitHub Pages
from the root of this repository, in English at the root and in the app's other
languages under `fr/`, `es/` and `zh-Hans/`.

| Page | URL |
| --- | --- |
| Support | `https://rafeek.github.io/wordhive-support/` |
| Privacy policy | `https://rafeek.github.io/wordhive-support/privacy.html` |

Both URLs go in App Store Connect under the app's version information. Each translated
listing can take its own language's pages, e.g. `https://rafeek.github.io/wordhive-support/fr/`.

`.nojekyll` disables Jekyll processing — these are plain static files.

## Editing

Every page is generated. Edit `gen_site.py`, run `python3 gen_site.py` (it expects the app
repo at `../WordSearch`, or takes its path), and push. Pages redeploys within a minute or two.

The how-to-play pages are read from `HelpContent` in the app's `SettingsView.swift` and
translated with its `Localizable.xcstrings`, so change the guide in the app and regenerate.
A guide string the app hasn't translated stops the run. The support and privacy pages are
written in `TEXT` in `gen_site.py`, one entry per language, and the menu paths they name
come from the app's catalog.

Every page opens with the same site header, the brand plus a menu bar linking all five
pages (`NAV`), and ends with links to the same page in each language. The English support
page sends a first visit on to the reader's language, unless they have picked one.
