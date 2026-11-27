import re, unittest
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class ProfileTests(unittest.TestCase):
    def test_readme_local_images(self):
        content=(ROOT/'README.md').read_text()
        for src in re.findall(r'<img\s+[^>]*src="([^"]+)"',content):
            if '://' in src: continue
            p=ROOT/src
            self.assertTrue(p.is_file(),src)
            if p.suffix=='.svg': ET.parse(p)
    def test_signallab_evidence(self):
        content=(ROOT/'README.md').read_text()
        for token in ['assets/projects/signallab.svg','https://github.com/DanoV1m/SignalLab','46009785710','not a released live demo']:
            self.assertIn(token,content)
