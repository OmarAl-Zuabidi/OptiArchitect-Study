"""Launchers for the browser interfaces (need ``pip install "optiarchitect[web]"``).

``optiarchitect-web``          the normal web application
``optiarchitect-study``        the student-study application (questionnaires + tool + report)
``optiarchitect-study-admin``  the researcher dashboard (password protected)
"""
import subprocess
import sys
from pathlib import Path


def _launch(relative_path: str) -> int:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("The web interface needs Streamlit:  pip install \"optiarchitect[web]\"", file=sys.stderr)
        return 1
    script = Path(__file__).parent / relative_path
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(script), *sys.argv[1:]])


def main() -> int:
    return _launch("app.py")


def study_main() -> int:
    return _launch("study/app_study.py")


def study_admin_main() -> int:
    return _launch("study/admin.py")


if __name__ == "__main__":
    sys.exit(main())
