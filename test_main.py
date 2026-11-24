#!/usr/bin/env python3
"""Tests for main.py (One Word From Grandma).

Run:  python3 -m unittest test_main -v
The tests run main.py the way the harness does (``python3 -P -s``,
no network) with MAKEFUN_OUTPUT_DIR pointed at a temp dir, then check
the gate the bounty seals: entry.txt is UTF-8 text of 1 to 30
characters, not only white space, and exactly one word.
"""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "main.py")


def run_main(env_extra=None, args=None):
    """Run main.py as the harness does; return (returncode, stdout, out_dir)."""
    out_dir = tempfile.mkdtemp(prefix="grandma-out-")
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = out_dir
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, "-P", "-s", MAIN, *(args or [])],
        capture_output=True, text=True, env=env, timeout=30,
    )
    return proc, out_dir


class TestEntry(unittest.TestCase):
    def test_writes_one_word(self):
        proc, out_dir = run_main()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(os.path.join(out_dir, "entry.txt"), encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(text, "Robit")
        self.assertEqual(proc.stdout.strip(), "Robit")

    def test_gate_length_and_single_word(self):
        proc, out_dir = run_main()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(os.path.join(out_dir, "entry.txt"), encoding="utf-8") as f:
            text = f.read()
        self.assertTrue(1 <= len(text) <= 30, f"gate: 1-30 chars, got {len(text)}")
        self.assertTrue(text.strip(), "gate: must not be only white space")
        self.assertEqual(len(text.split()), 1, "gate: must be exactly one word")
        self.assertTrue(text.isalpha(), "must be letters only")
        self.assertNotIn("\n", text)
        self.assertNotIn(" ", text)

    def test_deterministic_across_runs(self):
        proc1, out1 = run_main()
        proc2, out2 = run_main()
        self.assertEqual(proc1.returncode, 0, proc1.stderr)
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        with open(os.path.join(out1, "entry.txt"), "rb") as f:
            first = f.read()
        with open(os.path.join(out2, "entry.txt"), "rb") as f:
            second = f.read()
        self.assertEqual(first, second, "two runs must be byte-identical")
        self.assertEqual(proc1.stdout, proc2.stdout)

    def test_stdout_matches_entry_txt(self):
        proc, out_dir = run_main()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(os.path.join(out_dir, "entry.txt"), encoding="utf-8") as f:
            text = f.read()
        self.assertEqual(proc.stdout.strip(), text)


class TestCandidates(unittest.TestCase):
    def test_all_candidates_fit_gate(self):
        sys.path.insert(0, HERE)
        import main
        for word, *_scores in main.CANDIDATES:
            self.assertTrue(1 <= len(word) <= main.MAX_CHARS, word)
            self.assertEqual(len(word.split()), 1, word)
            self.assertTrue(word.isalpha(), word)

    def test_winner_is_robit(self):
        sys.path.insert(0, HERE)
        import main
        self.assertEqual(main.pick_winner(), "Robit")
        ranked = [c[0] for c in main.ranked()]
        self.assertEqual(ranked[0], "Robit")
        self.assertEqual(len(ranked), len(set(ranked)), "no duplicate words")

    def test_all_flag_lists_words_best_first(self):
        proc, _out_dir = run_main(args=["--all"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = proc.stdout.strip().split("\n")
        self.assertEqual(lines[0], "Robit")
        self.assertEqual(len(lines), 10)

    def test_scores_flag(self):
        proc, _out_dir = run_main(args=["--scores"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        first = proc.stdout.strip().split("\n")[0]
        self.assertTrue(first.startswith("Robit"), first)


if __name__ == "__main__":
    unittest.main()
