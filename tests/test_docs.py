"""docs/api.md must match the docstrings; every relative link in the docs must resolve."""
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Docs(unittest.TestCase):
    def test_api_reference_is_current(self):
        env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src") + os.pathsep + os.environ.get("PYTHONPATH", ""))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "docs", "generate_api.py"), "--check"], env=env)
        self.assertEqual(r.returncode, 0, "run: python docs/generate_api.py")

    def test_relative_links_resolve(self):
        files = [os.path.join(ROOT, "README.md")] + \
                [os.path.join(ROOT, "docs", f) for f in os.listdir(os.path.join(ROOT, "docs")) if f.endswith(".md")]
        for path in files:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                full = os.path.normpath(os.path.join(os.path.dirname(path), target))
                self.assertTrue(os.path.exists(full), f"{os.path.relpath(path, ROOT)} -> {target}")


if __name__ == "__main__":
    unittest.main()
