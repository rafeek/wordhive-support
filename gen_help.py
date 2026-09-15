#!/usr/bin/env python3
"""Emit the per-platform how-to-play pages.

Text mirrors HelpContent in the app's SettingsView.swift; keep the two in step.
Run from the repo root: python3 gen_help.py
"""
import html

PLATFORMS = {
    "ios": dict(
        file="play-iphone-ipad.html", name="iPhone & iPad", icon="📱",
        select=("Tap or drag a line",
                "Drag your finger from the first letter to the last, or tap the first then the last letter. Correct words lock in and cross off the word list."),
        move=("Zoom and pan",
              "Pinch to zoom into a large grid and drag with two fingers to pan. Double-tap to snap back to the full board."),
        setup=("Size, shape & level",
               "Pick a grid size (Small, Medium, Large), a shape (Square or Hex), and a word level — Simple for shorter everyday words, Advanced for a tougher mix. Then choose a theme."),
        hold=("Long-press a theme",
              "Press and hold a started or finished theme to continue it, start a new puzzle, or play it again."),
        resume="Your current game is saved automatically and synced across your devices through iCloud. Tap Continue on the menu to jump back in. Settings → Reset all progress deletes every saved puzzle, on every device.",
        define=("Double-tap a word",
                "Double-tap any word in the list to see its dictionary definition."),
        keys=None,
        yours="Tap the gear to open Settings, where you can toggle sound effects and spoken words, pick a voice, switch between light and dark, and set your accent colours.",
    ),
    "mac": dict(
        file="play-mac.html", name="Mac", icon="💻",
        select=("Click or drag a line",
                "Drag from the first letter to the last, or click the first then the last letter. Correct words lock in and cross off the word list."),
        move=("Zoom and pan",
              "Pinch on the trackpad to zoom into a large grid and scroll to pan. Double-click the board to fit it back to the window."),
        setup=("Size, shape & level",
               "Pick a grid size (Small, Medium, Large), a shape (Square or Hex), and a word level — Simple for shorter everyday words, Advanced for a tougher mix. Then choose a theme."),
        hold=("Right-click a theme",
              "Right-click (or click and hold) a started or finished theme to continue it, start a new puzzle, or play it again."),
        resume="Your current game is saved automatically and synced across your devices through iCloud. Click Continue on the menu to jump back in. Settings → Reset all progress deletes every saved puzzle, on every device.",
        define=("Double-click a word",
                "Double-click any word in the list to open its definition in the Look Up panel."),
        keys=("Keyboard & menus", [("New Game", "⌘N"), ("Back to Menu", "⇧⌘M"),
                                   ("Settings", "⌘,"), ("Help", "⌘?")]),
        yours="Open Settings (⌘,) to toggle sound effects and spoken words, pick a voice, switch between light and dark, and set your accent colours.",
    ),
    "tv": dict(
        file="play-apple-tv.html", name="Apple TV", icon="📺",
        select=("Aim with the remote",
                "Swipe on the remote's touch surface to glide the cursor across the grid. Click the first letter, then the last letter, to select a word. Correct words lock in and cross off the word list."),
        restart=("Restart a selection",
                 "Press play/pause to clear a selection you've started and aim again."),
        move=("It always fits",
              "The whole board stays on screen, so there's nothing to zoom or pan — just aim the cursor with the remote."),
        setup=("Size, shape & level",
               "Highlight a grid size (Small, Medium, Large), a shape (Square or Hex), and a word level — Simple for shorter everyday words, Advanced for a tougher mix — and click to choose. Then pick a theme."),
        hold=("Hold to choose",
              "Press and hold the remote's click on a started or finished theme to continue it, start a new puzzle, or play it again."),
        resume="Your current game is saved automatically and synced across your devices through iCloud. Select Continue on the menu to jump back in. Settings → Reset all progress deletes every saved puzzle, on every device.",
        wordlist=("Hear a word",
                  "Swipe right past the edge of the grid to move into the word list, then click a word to hear it spoken. Swipe left past the first column to return to the grid."),
        define=None,
        keys=("The remote", [("Move the cursor", "Swipe"), ("Select a letter", "Click"),
                             ("Cancel a selection", "Play/Pause"), ("Back to menu", "Menu")]),
        yours="Open Settings from the gear on the menu to toggle sound effects and spoken words, pick a voice, switch between light and dark, set your accent colours, and turn on the OLED screen saver.",
    ),
}

def row(title, body):
    return f'<div class="row"><strong>{html.escape(title)}</strong><p>{html.escape(body)}</p></div>'

def section(title, rows):
    return f'<h2>{html.escape(title)}</h2>\n<div class="card">\n' + "\n".join(rows) + "\n</div>"

def page(key, p):
    others = " ".join(f'<a href="{q["file"]}">{q["icon"]} {html.escape(q["name"])}</a>'
                      for k, q in PLATFORMS.items() if k != key)
    finding = [row(*p["select"])]
    if p.get("restart"):
        finding.append(row(*p["restart"]))
    finding.append(row("Any straight line",
        "Words run in straight lines — forwards, backwards, or diagonally. Square grids use 8 directions; hex grids use 6."))
    if p.get("wordlist"):
        finding.append(row(*p["wordlist"]))
    if p.get("define"):
        finding.append(row(*p["define"]))

    sections = [
        section("The goal", [row("Find every hidden word",
            "Each puzzle hides a list of themed words in a grid of letters. Find them all to finish the puzzle — the honeycomb bar at the top fills as you go.")]),
        section("Finding words", finding),
        section("Moving the grid", [row(*p["move"])]),
        section("Scoring", [
            row("Be quick", "Each word starts at a high value that ticks down the longer it takes to find. The faster you spot it, the more points it adds to your score."),
            row("Build a combo", "Finding words back-to-back keeps your streak alive for bonus points. Pauses break the chain."),
        ]),
        section("Setting up a puzzle", [
            row(*p["setup"]),
            row("Theme badges", "A tick means you finished that theme with the current size, shape, and level; a count (e.g. 3/12) marks a puzzle in progress."),
            row(*p["hold"]),
        ]),
        section("Saving & resuming", [row("Picks up where you left off", p["resume"])]),
    ]
    if p["keys"]:
        title, pairs = p["keys"]
        sections.append(section(title, [
            f'<div class="row keys"><span>{html.escape(a)}</span><kbd>{html.escape(b)}</kbd></div>' for a, b in pairs]))
    sections.append(section("Make it yours", [row("Sound & looks", p["yours"])]))

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WordHive Puzzles — How to Play on {html.escape(p["name"])}</title>
<meta name="description" content="How to play WordHive Puzzles on {html.escape(p["name"])}.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<main class="help">

<header>
  <div class="mark">{p["icon"]}</div>
  <div>
    <h1>How to play on {html.escape(p["name"])}</h1>
    <p>WordHive Puzzles</p>
  </div>
</header>

<p class="switch">Other platforms: {others}</p>

{chr(10).join(sections)}

<hr>
<footer>
  <span>© 2026 Rafeek Rahamut</span>
  <nav>
    <a href="index.html">Support</a>
    <a href="privacy.html">Privacy</a>
  </nav>
</footer>

</main>
</body>
</html>
'''

for key, p in PLATFORMS.items():
    with open(p["file"], "w") as f:
        f.write(page(key, p))
    print("wrote", p["file"])
