"""Russian narration for the composition (HyperFrames' Kokoro TTS has no Russian voice).

Usage: python3 tools/tts.py <voices-dir> <voice> <speed> <out.wav>
  e.g. python3 tools/tts.py tools/voices dmitri-medium 1.0 assets/narration.wav
Voices: https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models (vits-piper-ru_RU-*).
Writes <out>.json next to the wav: word timings, sentence spans and a 30 fps loudness envelope.
"""
import json, re, sys, pathlib, numpy as np, soundfile as sf, sherpa_onnx
S=sys.argv[1]; voice=sys.argv[2]; speed=float(sys.argv[3]); out=sys.argv[4]
d=f"{S}/vits-piper-ru_RU-{voice}"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(
    model=f"{d}/ru_RU-{voice}.onnx", tokens=f"{d}/tokens.txt", data_dir=f"{d}/espeak-ng-data"), num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg)
script=json.load(open(pathlib.Path(__file__).with_name("script.json")))
VOW=set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")
def weight(w): return max(1,sum(c in VOW for c in w))+0.15*len(re.sub(r"\W","",w))/4
def frames_rms(x,sr,hop):
    n=len(x)//hop; return np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)) for i in range(n)])
audio=[]; words=[]; sents=[]; t=0.25; sr=None
audio.append(None)
for si,(disp,spoken,pause) in enumerate(script):
    g=tts.generate(spoken or disp, sid=0, speed=speed); x=np.array(g.samples,dtype=np.float32); sr=g.sample_rate
    hop=int(sr*0.01); r=frames_rms(x,sr,hop); thr=max(r.max()*0.04,1e-4)
    idx=np.where(r>thr)[0]; a=max(0,idx[0]-2)*hop; b=min(len(x),(idx[-1]+4)*hop); x=x[a:b]; r=r[max(0,idx[0]-2):idx[-1]+4]
    dur=len(x)/sr
    # internal pauses (>=0.09s below threshold)
    quiet=r<thr*1.5; pauses=[]; i=0
    while i<len(quiet):
        if quiet[i]:
            j=i
            while j<len(quiet) and quiet[j]: j+=1
            if (j-i)>=9 and i>3 and j<len(quiet)-3: pauses.append((i*0.01,j*0.01))
            i=j
        else: i+=1
    toks=disp.split()
    # split tokens into phrases at internal punctuation
    phrases=[[]]
    for k,tk in enumerate(toks):
        if tk in ("—","-"):
            if phrases[-1]: phrases.append([])
            continue
        phrases[-1].append(tk)
        if re.search(r"[,:;]$",tk) and k<len(toks)-1: phrases.append([])
    phrases=[p for p in phrases if p]
    bounds=[0.0]
    if len(pauses)==len(phrases)-1:
        for p0,p1 in pauses: bounds+= [p0,p1]
    else:
        # fallback: proportional by weight
        W=[sum(weight(w) for w in p) for p in phrases]; acc=0
        for wv in W[:-1]: acc+=wv; bounds+= [dur*acc/sum(W)]*2
    bounds.append(dur)
    for pi,p in enumerate(phrases):
        a0,b0=bounds[2*pi],bounds[2*pi+1]; W=[weight(w) for w in p]; acc=0
        for w,wv in zip(p,W):
            ws=a0+(b0-a0)*acc/sum(W); acc+=wv; we=a0+(b0-a0)*acc/sum(W)
            words.append([w, round(t+ws,3), round(t+we,3), si])
    sents.append([round(t,3), round(t+dur,3)])
    audio.append(x); t+=dur+pause
    print(f"{si}: {dur:.2f}s pauses={len(pauses)} phrases={len(phrases)}", file=sys.stderr)
audio[0]=np.zeros(int(sr*0.25),dtype=np.float32)
full=[]
for si,x in enumerate(audio[1:]):
    full.append(x if si==0 else x); full.append(np.zeros(int(sr*script[si][2]),dtype=np.float32))
y=np.concatenate([audio[0]]+full); y=y/max(1e-6,np.abs(y).max())*0.89
sf.write(out, y, sr)
hop=sr/30; env=[float(np.sqrt(np.mean(y[int(i*hop):int((i+1)*hop)]**2))) for i in range(int(len(y)/hop))]
env=np.array(env); env=np.clip(env/np.percentile(env[env>0.01],95),0,1)
env=np.convolve(env,[0.25,0.5,0.25],mode="same")
json.dump({"duration":round(len(y)/sr,3),"words":words,"sentences":sents,"env":[round(float(v),2) for v in env]},open(out.replace(".wav",".json"),"w"),ensure_ascii=False)
print("total", round(len(y)/sr,2), "words", len(words), file=sys.stderr)
