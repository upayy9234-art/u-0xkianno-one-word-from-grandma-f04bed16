#!/usr/bin/env python3
"""One Word From Grandma (make.fun).

The program holds ten candidate words a grandma might text about AI,
scores each one against the judge's own brief, and writes the winner --
exactly one word -- to ``/output/entry.txt`` (or
``$MAKEFUN_OUTPUT_DIR/entry.txt`` when set).

The judge's brief, most important first:
  1. Reads as the single word a grandma would text about AI.
  2. Sounds like a real grandmother's texting voice, warm and a little
     baffled, the way she would type it to a grandchild.
  3. Is funny in one word, with the joke landing without a caption.
  4. Feels tied to AI, robots or machines rather than fitting any subject.
  5. Is a fresh pick rather than the obvious one, and still instantly
     readable.

The winner is "Robit": the typo a grandma actually makes when she means
"robot". It is warm, baffled, funny on its own, unmistakably about a
machine, and instantly readable -- the word she would text, misspelling
and all, exactly as the bounty allows ("a typo she would actually make").

Pure Python standard library. No network, no clock, no randomness: the
default run always writes the same word, so two runs are byte-identical.

Usage:
    python3 main.py            print + write the winning word (default)
    python3 main.py --all      print every candidate word, best first
    python3 main.py --scores   print every candidate with its score
"""

import argparse
import os
import sys

MAX_CHARS = 30

# (word, grandma_voice, warm_baffled, funny, ai_tied, fresh)
# Each score is 0..5, scored by hand against the judge's brief,
# most important first. Ties keep list order (stable sort).
CANDIDATES = [
    # Her typo for "robot": warm, baffled, funny, and unmistakably a
    # machine. The joke lands with no caption at all.
    ("Robit", 5, 5, 5, 5, 4),
    # Her pet name for the AI: dear + bot. Warm and fresh, but the
    # joke is gentler than a typo she would really send.
    ("Dearbot", 5, 5, 3, 5, 5),
    # She names the machine after its blinking light. Sweet and
    # specific, but a nickname more than a word about AI.
    ("Blinky", 4, 5, 4, 4, 5),
    # Sweet + bot: her endearment for the machine. Warm, but it reads
    # more like a name than the word she would text about AI.
    ("Sweetbot", 4, 4, 3, 5, 4),
    # She calls the robot Robbie, like a grandson. Lovely and warm,
    # but it could be any machine, or any boy.
    ("Robbie", 4, 5, 3, 4, 3),
    # The noise the robot makes, as she hears it. Funny and tied to
    # machines, but it sounds like the robot talking, not grandma.
    ("Beepboop", 4, 3, 4, 5, 3),
    # The sound its joints make. Evocative, but more complaint than
    # the warm, baffled voice of a grandma texting her grandchild.
    ("Clanky", 4, 3, 3, 5, 4),
    # She calls every AI Siri, whatever its real name is. Very
    # grandma, very funny -- but it is the obvious pick, and a brand.
    ("Siri", 5, 5, 4, 4, 2),
    # Pure grandma exclamation. Warm and funny, but it would fit any
    # subject at all, not AI.
    ("Golly", 4, 5, 3, 1, 3),
    # The whirring machine, as she spells it. Charming, but the joke
    # needs the sound explained to land.
    ("Whirry", 4, 4, 3, 4, 4),
]

# Judge's order: grandma voice first, then warm/baffled, funny,
# AI-tied, fresh.
WEIGHTS = (5, 4, 3, 2, 1)

# Every candidate must fit the gate on its own, so a later edit that
# lengthens a word fails loudly here instead of silently at grading.
for _word, *_scores in CANDIDATES:
    assert 1 <= len(_word) <= MAX_CHARS, f"candidate over {MAX_CHARS} chars: {_word!r}"
    assert _word == _word.strip(), f"candidate has stray whitespace: {_word!r}"
    assert " " not in _word and "\n" not in _word, f"candidate is not one word: {_word!r}"


def score(candidate):
    """Weighted score of one candidate, highest wins; ties go to the first."""
    _, voice, warm, funny, tied, fresh = candidate
    return (
        WEIGHTS[0] * voice
        + WEIGHTS[1] * warm
        + WEIGHTS[2] * funny
        + WEIGHTS[3] * tied
        + WEIGHTS[4] * fresh
    )


def ranked():
    """All candidates best first; ties keep list order (stable sort)."""
    return sorted(CANDIDATES, key=score, reverse=True)


def pick_winner():
    """The best-scoring word; deterministic, ties broken by list order."""
    return ranked()[0][0]


def write_entry(word):
    """Write one word to entry.txt and print it. Returns 0 or 1."""
    if not word or word != word.strip():
        print("error: winning word is empty or has stray whitespace", file=sys.stderr)
        return 1
    if len(word) > MAX_CHARS:
        print(f"error: winning word is {len(word)} chars, over {MAX_CHARS}",
              file=sys.stderr)
        return 1
    if any(ch.isspace() for ch in word):
        print("error: winning word is not a single word", file=sys.stderr)
        return 1
    if not word.isalpha():
        print("error: winning word must be letters only", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.txt"), "w", encoding="utf-8") as handle:
        handle.write(word)
    print(word)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Pick the one word grandma would text about AI.")
    parser.add_argument("--all", action="store_true",
                        help="print every candidate word, best first, and write none")
    parser.add_argument("--scores", action="store_true",
                        help="print every candidate with its score, and write none")
    args = parser.parse_args(argv)

    if args.all:
        for candidate in ranked():
            print(candidate[0])
        return 0
    if args.scores:
        for candidate in ranked():
            print(f"{candidate[0]:<10} {score(candidate)}")
        return 0
    return write_entry(pick_winner())


if __name__ == "__main__":
    raise SystemExit(main())
