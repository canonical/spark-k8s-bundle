import os
from pathlib import Path

IE_TEST_DIR = Path(os.path.dirname(__file__))

RELEASE_DIR = IE_TEST_DIR / ".." / ".." / "releases" / "3.4"

BUNDLE_FILE = RELEASE_DIR / "bundle.small.yaml.j2"
