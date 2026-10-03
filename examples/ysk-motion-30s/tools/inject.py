"""Write WORDS / SENT / ENV from tools/timing.json into index.html (between @generated markers)."""
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((root / "tools" / "timing.json").read_text())
words = ",\n        ".join(json.dumps([w[0], w[1], w[2], w[3]], ensure_ascii=False) for w in d["words"])
env = ", ".join(str(v) for v in d["env"])
block = (
    "/* @generated:begin — tools/inject.py writes WORDS / SENT / ENV from tools/timing.json */\n"
    "      // [display word, start s, end s, sentence index] — timing guide (no audio in the video)\n"
    f"      const WORDS = [\n        {words},\n      ];\n"
    f"      const SENT = {json.dumps(d['sentences'])};\n"
    "      // guide loudness at 30 fps (0..1), drives the mouth rig\n"
    f"      const ENV = [{env}];\n"
    "      /* @generated:end */"
)
html = (root / "index.html").read_text()
html = re.sub(r"/\* @generated:begin.*?@generated:end \*/", lambda m: block, html, flags=re.S)
(root / "index.html").write_text(html)
print("injected", len(d["words"]), "words,", len(d["env"]), "env frames")
