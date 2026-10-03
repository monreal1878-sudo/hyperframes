"""Stretch a tts.py timing guide to the target pace and save tools/timing.json.

Usage: python3 tools/timing.py <guide.json> <stretch>
The video ships without audio: the guide only sets the subtitle rhythm and the mouth
envelope. Re-time later from a real voiceover (e.g. `hyperframes transcribe voice.mp3`).
"""
import json, sys, pathlib
import numpy as np

src, k = sys.argv[1], float(sys.argv[2])
d = json.load(open(src))
words = [[w[0], round(w[1] * k, 3), round(w[2] * k, 3), w[3]] for w in d["words"]]
sents = [[round(a * k, 3), round(b * k, 3)] for a, b in d["sentences"]]
env = np.array(d["env"], dtype=float)
n = int(len(env) * k)
env = np.interp(np.arange(n) / k, np.arange(len(env)), env)
out = {"words": words, "sentences": sents, "env": [round(float(v), 2) for v in env]}
p = pathlib.Path(__file__).with_name("timing.json")
p.write_text(json.dumps(out, ensure_ascii=False))
print("speech ends", words[-1][2], "frames", n)
