#!/usr/bin/env python3
"""Emit the per-platform how-to-play pages.

Text mirrors HelpContent in the app's SettingsView.swift; keep the two in step.
Run from the repo root: python3 gen_help.py

The site header (brand + menu bar) is defined here in NAV and stamped into every
generated page; index.html and privacy.html carry a hand-pasted copy, so update
those when NAV changes.
"""
import html

NAV = [("index.html", "Support"), ("play-iphone-ipad.html", "iPhone & iPad"),
       ("play-mac.html", "Mac"), ("play-apple-tv.html", "Apple TV"),
       ("privacy.html", "Privacy")]

def site_header(current):
    links = "\n".join(
        f'    <a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{html.escape(label)}</a>'
        for href, label in NAV)
    return f"""<header class="site">
  <a class="brand" href="index.html"><img class="mark" src="icon.png" alt="" width="32" height="32">WordHive Puzzles</a>
  <nav>
{links}
  </nav>
  <script>document.querySelector('.site nav [aria-current]').scrollIntoView({{inline: "center", block: "nearest"}})</script>
</header>"""

TWIST = "On a Twist grid each word bends through neighbouring cells, often folded back on itself and crossing other words. {v} its letters one after another, from either end. The few spare letters are the puzzle's subtheme, scrambled."

PLATFORMS = {
    "ios": dict(
        file="play-iphone-ipad.html", name="iPhone & iPad", icon="📱", help_path="Settings → How to Play",
        select=("Tap or drag a line",
                "Drag your finger from the first letter to the last, or tap the first then the last letter. Correct words lock in and cross off the word list."),
        touch=("Selecting & scrolling",
               "Settings → Touch chooses what one finger does: Drag selects and two fingers scroll; Tap picks words by their first and last letter and one finger scrolls; Auto drags to select, but once you've tapped a first letter one finger scrolls until you tap the last."),
        twist=TWIST.format(v="Trace"),
        move=("Zoom and pan",
              "Pinch to zoom into a large grid and drag with two fingers to pan — or one finger, under the Tap and Auto touch settings. Pinch back out to see the whole board."),
        setup=("Size, shape & level",
               "Pick a grid size (Small, Medium, Large), a shape (Square, Hex or Twist), and a word level — Simple for everyday words, Advanced adds harder ones. Then choose a theme."),
        hold=("Long-press a theme",
              "Press and hold a started or finished theme to continue it, start a new puzzle, or play it again. It also lists any puzzle for that theme left in progress under a different size, shape or level, so you can jump back into it."),
        resume="Your current game is saved automatically and synced across your devices through iCloud. Tap Continue on the menu to jump back in. Settings → Reset all progress deletes every saved puzzle, on every device.",
        define=("Double-tap a word",
                "Double-tap any word in the list to see its dictionary definition."),
        keys=None,
        yours="Tap the gear to open Settings, where you can toggle sound effects and spoken words, pick a voice, switch between light and dark, set your accent colours, choose the menu-to-game transition, and choose how touch selects and scrolls.",
        a11y=[("VoiceOver",
               "Each letter reads as its row, column, and letter, and says whether it is selected or found. Double-tap the first letter of a word, then its last, to select it; the Clear selection action drops a selection you've started. Words in the list read as found or not found — double-tap one to hear it, or use the Define action. Every word you find is announced."),
              ("Reduce Motion",
               "When Reduce Motion is on in Settings → Accessibility, the moving background, menu transitions, and found-word flourishes are switched off."),
              ("Hear a word", "Tap any word in the list to hear it spoken in the voice chosen in Settings.")],
    ),
    "mac": dict(
        file="play-mac.html", name="Mac", icon="💻", help_path="Help → WordHive Help (⌘?)",
        select=("Click or drag a line",
                "Drag from the first letter to the last, or click the first then the last letter. Correct words lock in and cross off the word list."),
        twist=TWIST.format(v="Trace"),
        move=("Zoom and pan",
              "Pinch on the trackpad to zoom into a large grid and scroll to pan. Pinch back out to see the whole board."),
        setup=("Size, shape & level",
               "Pick a grid size (Small, Medium, Large), a shape (Square, Hex or Twist), and a word level — Simple for everyday words, Advanced adds harder ones. Then choose a theme."),
        hold=("Right-click a theme",
              "Right-click (or click and hold) a started or finished theme to continue it, start a new puzzle, or play it again. It also lists any puzzle for that theme left in progress under a different size, shape or level, so you can jump back into it."),
        resume="Your current game is saved automatically and synced across your devices through iCloud. Click Continue on the menu to jump back in. Settings → Reset all progress deletes every saved puzzle, on every device.",
        define=("Double-click a word",
                "Double-click any word in the list to open its definition in the Look Up panel."),
        keys=("Keyboard & menus", [("New Game", "⌘N"), ("Back to Menu", "⇧⌘M"),
                                   ("Settings", "⌘,"), ("Help", "⌘?")]),
        yours="Open Settings (⌘,) to toggle sound effects and spoken words, pick a voice, switch between light and dark, set your accent colours, and choose the menu-to-game transition.",
        a11y=[("VoiceOver",
               "Each letter reads as its row, column, and letter, and says whether it is selected or found. Activate the first letter of a word, then its last, to select it; the Clear selection action drops a selection you've started. Words in the list read as found or not found — activate one to hear it, or use the Define action. Every word you find is announced."),
              ("Reduce Motion",
               "When Reduce Motion is on in System Settings → Accessibility → Display, the moving background, menu transitions, and found-word flourishes are switched off."),
              ("Hear a word", "Click any word in the list to hear it spoken in the voice chosen in Settings.")],
    ),
    "tv": dict(
        file="play-apple-tv.html", name="Apple TV", icon="📺", help_path="Settings → How to Play",
        select=("Aim with the remote",
                "Swipe on the remote's touch surface to glide the cursor across the grid. Click the first letter, then the last letter, to select a word. Correct words lock in and cross off the word list."),
        restart=("Restart a selection",
                 "Press play/pause to clear a selection you've started and aim again."),
        steer=("Steering on hex grids",
               "On Hex and Twist grids, swipe diagonally to step to a diagonal neighbour — the swipe snaps to the nearest of the six directions."),
        twist=TWIST.format(v="Click"),
        move=("It always fits",
              "The whole board stays on screen, so there's nothing to zoom or pan — just aim the cursor with the remote."),
        setup=("Size, shape & level",
               "Choose a grid size (Small, Medium, Large), a shape (Square, Hex or Twist), and a word level — Simple for everyday words, Advanced adds harder ones. Highlight a bar and swipe left or right, or click to step through its options. Then pick a theme."),
        hold=("Hold to choose",
              "Press and hold the remote's click on a started or finished theme to continue it, start a new puzzle, or play it again. It also lists any puzzle for that theme left in progress under a different size, shape or level, so you can jump back into it."),
        resume="Your current game is saved automatically and synced across your devices through iCloud. Select Continue on the menu to jump back in. Settings → Reset all progress deletes every saved puzzle, on every device.",
        wordlist=("Hear a word",
                  "Swipe right past the edge of the grid to move into the word list, then click a word to hear it spoken. Swipe left past the first column to return to the grid."),
        define=None,
        keys=("The remote", [("Move the cursor", "Swipe"), ("Select a letter", "Click"),
                             ("Cancel a selection", "Play/Pause"), ("Back to menu", "Menu")]),
        yours="Open Settings from the gear on the menu to toggle sound effects and spoken words, pick a voice, switch between light and dark, set your accent colours, choose the menu-to-game transition, and turn on the OLED screen saver.",
        a11y=[("VoiceOver",
               "Words in the list read as found or not found, and every word you find is announced. The grid itself is played by aiming the cursor with the remote."),
              ("Reduce Motion",
               "When Reduce Motion is on in Settings → Accessibility → Motion, the moving background, menu transitions, and found-word flourishes are switched off.")],
    ),
}

def row(title, body):
    return f'<div class="row"><strong>{html.escape(title)}</strong><p>{html.escape(body)}</p></div>'

def section(title, rows):
    return f'<h2>{html.escape(title)}</h2>\n<div class="card">\n' + "\n".join(rows) + "\n</div>"

def page(key, p):
    finding = [row(*p["select"])]
    if p.get("touch"):
        finding.append(row(*p["touch"]))
    if p.get("restart"):
        finding.append(row(*p["restart"]))
    if p.get("steer"):
        finding.append(row(*p["steer"]))
    finding.append(row("Any straight line",
        "Words run in straight lines — forwards, backwards, or diagonally. Square grids use 8 directions; hex grids use 6."))
    finding.append(row("Twist grids wind", p["twist"]))
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
            row("Build a combo", "Finding words back-to-back keeps your streak alive for bonus points. Pauses break the chain, but bigger grids give you longer between finds."),
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
    sections.append(section("Accessibility", [row(*pair) for pair in p["a11y"]]))

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WordHive Puzzles — How to Play on {html.escape(p["name"])}</title>
<meta name="description" content="How to play WordHive Puzzles on {html.escape(p["name"])}.">
<link rel="icon" href="icon.png">
<link rel="stylesheet" href="style.css">
</head>
<body>
<main class="help">

{site_header(p["file"])}

<div class="title">
  <div class="mark" aria-hidden="true">{p["icon"]}</div>
  <div>
    <h1>How to play on {html.escape(p["name"])}</h1>
    <p>The same guide is in the app under {html.escape(p["help_path"])}</p>
  </div>
</div>

{chr(10).join(sections)}

<hr>
<footer>© 2026 Rafeek Rahamut</footer>

</main>
</body>
</html>
'''

for key, p in PLATFORMS.items():
    with open(p["file"], "w") as f:
        f.write(page(key, p))
    print("wrote", p["file"])
