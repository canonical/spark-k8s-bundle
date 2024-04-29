import os
from pathlib import Path

IE_TEST_DIR = Path(os.path.dirname(__file__))

RELEASE_DIR = IE_TEST_DIR / ".." / ".." / "releases" / "3.4"
