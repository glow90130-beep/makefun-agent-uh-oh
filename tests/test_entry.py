"""Contract tests for the one-word entrypoint.

The grader runs `python3 -P -s /bot/main.py` with a writable output
directory and expects UTF-8 `blanking` in `entry.txt` and nothing else.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
WORD = "blanking"
EXACT = WORD.encode("utf-8")


def run_entry(output_dir: Path) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["MAKEFUN_OUTPUT_DIR"] = str(output_dir)
    env["PYTHONHASHSEED"] = "0"
    env["TZ"] = "UTC"
    env["LANG"] = "C.UTF-8"
    return subprocess.run(
        [sys.executable, "-P", "-s", str(MAIN)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        check=False,
    )


class EntryContractTest(unittest.TestCase):
    def test_fresh_directory_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="uh-oh-fresh-") as directory:
            output = Path(directory) / "output"
            self.assertFalse(output.exists())
            result = run_entry(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(result.stderr, b"")
            produced = output / "entry.txt"
            self.assertTrue(produced.is_file())
            payload = produced.read_bytes()
            self.assertEqual(payload, EXACT)
            self.assertNotIn(b"\n", payload)
            self.assertEqual(payload.decode("utf-8"), WORD)
            self.assertEqual([path.name for path in output.iterdir()], ["entry.txt"])

    def test_repeat_execution_is_stable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="uh-oh-repeat-") as directory:
            output = Path(directory)
            first = run_entry(output)
            second = run_entry(output)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            payload = (output / "entry.txt").read_bytes()
            self.assertEqual(payload, EXACT)
            self.assertEqual(len(payload), len(EXACT))
            self.assertEqual([path.name for path in output.iterdir()], ["entry.txt"])

    def test_replaces_stale_contents(self) -> None:
        with tempfile.TemporaryDirectory(prefix="uh-oh-stale-") as directory:
            output = Path(directory)
            stale = output / "entry.txt"
            stale.write_bytes(b"previous-word\n")
            result = run_entry(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stale.read_bytes(), EXACT)

    def test_word_is_one_token_within_gate(self) -> None:
        self.assertEqual(WORD, WORD.strip())
        self.assertFalse(any(character.isspace() for character in WORD))
        self.assertGreaterEqual(len(WORD), 1)
        self.assertLessEqual(len(WORD), 99)
        self.assertEqual(EXACT, WORD.encode("utf-8"))

    def test_rejects_attached_text(self) -> None:
        sys.path.insert(0, str(ROOT))
        import main

        for invalid in ("blanking\n", "blank ing", " blanking", "", "x" * 100):
            with self.assertRaises(SystemExit):
                main.entry_bytes(invalid)

    def test_default_output_path(self) -> None:
        env = os.environ.copy()
        env.pop("MAKEFUN_OUTPUT_DIR", None)
        probe = subprocess.run(
            [sys.executable, "-s", "-c", "import main; print(main.output_file())"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(probe.returncode, 0, probe.stderr)
        self.assertEqual(probe.stdout.strip(), "/output/entry.txt")

    def test_empty_output_dir_falls_back_to_root_output(self) -> None:
        env = os.environ.copy()
        env["MAKEFUN_OUTPUT_DIR"] = ""
        probe = subprocess.run(
            [sys.executable, "-s", "-c", "import main; print(main.output_file())"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(probe.returncode, 0, probe.stderr)
        self.assertEqual(probe.stdout.strip(), "/output/entry.txt")


if __name__ == "__main__":
    unittest.main()
