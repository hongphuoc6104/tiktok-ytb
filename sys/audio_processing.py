"""Sample-preserving audio preparation; shipped to Colab for new jobs."""
import json,shutil,subprocess,wave
from pathlib import Path

class AudioProcessingError(RuntimeError):
 pass

Blocked = AudioProcessingError

def frames_of(path):
 with wave.open(str(path)) as wav:return wav.getnframes()

def run_ffmpeg(cmd,log):
 """Run one ffmpeg step, appending its command and output to `log`.

 Distinguishes "ffmpeg is not installed" (FileNotFoundError from the OS,
 nothing to log) from "ffmpeg ran and exited non-zero" (logged for postmortem)
 so master()'s caller gets an accurate Blocked message either way.
 """
 try:r=subprocess.run(cmd,capture_output=True,text=True)
 except FileNotFoundError:raise Blocked('ffmpeg not found on PATH; install ffmpeg to master narration audio')
 with open(log,'a') as f:f.write('$ '+' '.join(cmd)+'\n'+r.stdout+r.stderr+'\n')
 return r

def master(src,dst,cfg):
 """EQ, then a static gain to target loudness with a true-peak limiter.

 loudnorm is used for ANALYSIS only: its dynamic mode pads and resamples to
 192 kHz, which would break the +/-30 ms duration gates in pilot.checks.
 No compressor: a limiter only touches the few samples above the ceiling, so
 it reaches the loudness target without flattening the prosody we just gained.
 alimiter needs level=disabled or it auto-normalises straight back to 0 dBFS.
 Every filter here is sample-preserving; the frame count is asserted anyway.

 Every ffmpeg invocation is logged to <dst>.log next to tts.log/tts-en.log.
 Any ffmpeg failure or invalid intermediate file raises Blocked instead of
 silently leaving the un-mastered `src` in place -- a swallowed failure here
 would let an unmastered or clipped track pass every downstream gate, since
 pilot.checks only looks at duration and RMS, not loudness/EQ correctness.
 """
 log=dst.parent/(dst.stem+'.log')
 eq='equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=7000:t=q:w=2:g=-2.5'
 r=run_ffmpeg(['ffmpeg','-y','-i',str(src),'-af',eq,'-ar','48000','-c:a','pcm_s16le',str(dst)],log)
 if r.returncode or not (dst.exists() and dst.stat().st_size>1000):
  raise Blocked(f'Audio mastering (EQ) failed; see {log.name}')
 r=run_ffmpeg(['ffmpeg','-v','info','-i',str(dst),'-af','loudnorm=print_format=json','-f','null','-'],log)
 try:m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
 except ValueError:
  dst.unlink(missing_ok=True)
  raise Blocked(f'Audio mastering (loudness analysis) failed; see {log.name}')
 peak=float(cfg.get('audio_peak_db',-1.5));gain=float(cfg.get('audio_lufs',-14.))-float(m['input_i'])
 final=dst.with_name('narration_lv.wav')
 r=run_ffmpeg(['ffmpeg','-y','-i',str(dst),'-af',f'volume={gain:.2f}dB,alimiter=limit={10**(peak/20):.4f}:level=disabled','-ar','48000','-c:a','pcm_s16le',str(final)],log)
 dst.unlink(missing_ok=True)
 if r.returncode:
  final.unlink(missing_ok=True)
  raise Blocked(f'Audio mastering (gain/limiter) failed; see {log.name}')
 if not (final.exists() and final.stat().st_size>1000):
  raise Blocked(f'Audio mastering produced an invalid file; see {log.name}')
 if frames_of(final)!=frames_of(src):
  final.unlink(missing_ok=True)
  raise Blocked(f'Audio mastering changed frame count; refusing to replace source; see {log.name}')
 shutil.move(str(final),str(src))
