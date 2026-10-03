"""Write WORDS / SENT / ENV from tools/narration.json into index.html (between @generated markers)."""
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((root / "tools" / "narration.json").read_text())
words = ",\n        ".join(json.dumps([w[0], w[1], w[2], w[3]], ensure_ascii=False) for w in d["words"])
env = ", ".join(str(v) for v in d["env"])
block = (
    "/* @generated:begin — tools/inject.py writes WORDS / SENT / ENV from tools/narration.json */\n"
    "      // [display word, start s, end s, sentence index] — Piper ru_RU-dmitri timings\n"
    f"      const WORDS = [\n        {words},\n      ];\n"
    f"      const SENT = {json.dumps(d['sentences'])};\n"
    "      // narration loudness at 30 fps (0..1), drives the mouth rig\n"
    f"      const ENV = [{env}];\n"
    "      /* @generated:end */"
)
html = (root / "index.html").read_text()
html = re.sub(r"/\* @generated:begin.*?@generated:end \*/", lambda m: block, html, flags=re.S)
(root / "index.html").write_text(html)
print("injected", len(d["words"]), "words,", len(d["env"]), "env frames, duration", d["duration"])
