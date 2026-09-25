import React, {useEffect, useLayoutEffect, useState} from 'react';
import {captionStyle, captionMaxHeight} from './captions.mjs';
import {
  AbsoluteFill, Audio, Composition, Img, Loop, OffthreadVideo, Sequence, continueRender, delayRender,
  registerRoot, spring, staticFile, useCurrentFrame, useVideoConfig
} from 'remotion';

// Overlay text is Vietnamese with diacritics: the bundled Noto Sans is
// inlined into the bundle (render.mjs turns .ttf imports into data URLs), so
// no tab waits on a font request while many render tabs share the server.
// The system font stack below is only a fallback.
// @ts-ignore -- asset import resolved by webpack
import notoSansBold from './fonts/NotoSans-Bold.ttf';
export const FONT = "'Noto Sans', 'DejaVu Sans', Arial, sans-serif";
// The delayRender handle lives in the component: the renderer resets the
// handle list after page setup, so a module-level handle was never cleared.
const fontReady: Promise<void> = typeof window !== 'undefined' && 'FontFace' in window
  ? new FontFace('Noto Sans', `url(${notoSansBold}) format('truetype')`, {weight: '100 900'})
    .load().then((face) => {document.fonts.add(face);})
    .catch((e) => console.warn('Overlay font not loaded; using system fallback', e))
  : Promise.resolve();

const INK = '#1b1b1b';
const PAPER = '#fffdf5';
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const isClip = (b: any) => b?.kind === 'clip' || /\.mp4$/i.test(b?.src || '');
const TRANSITIONS = ['fade', 'slide_left', 'pop'];

/** Transform/opacity for one beat. progress: 0..1 over the beat; transition:
 *  0..1 over its first ≤0.3 s; pop: spring 0..1 from the beat start. */
function beatStyle(effect: string, progress: number, transition: number, pop: number) {
  let scale = 1, x = 0, opacity = 1;
  if (effect === 'zoom_in') scale = 1 + .08 * progress;
  else if (effect === 'zoom_out') scale = 1.08 - .08 * progress;
  else if (effect === 'fade') opacity = transition;
  else if (effect === 'slide_left') x = (1 - transition) * 100;
  // Pans stay inside the 10% zoom margin so no frame edge is revealed.
  else if (effect === 'pan_left') {scale = 1.1; x = 4 - 8 * progress;}
  else if (effect === 'pan_right') {scale = 1.1; x = -4 + 8 * progress;}
  else if (effect === 'pop') {scale = .82 + .18 * pop; opacity = Math.min(1, transition * 1.5);}
  return {transform: `translateX(${x}%) scale(${scale})`, opacity};
}

const Visual: React.FC<{beat: any; from: number; frames: number; style: React.CSSProperties}> = ({beat, from, frames, style}) => {
  const {fps} = useVideoConfig();
  const media: React.CSSProperties = {position: 'absolute', width: '100%', height: '100%', objectFit: 'contain', ...style};
  if (!isClip(beat)) return <Img src={staticFile(beat.src)} style={media} />;
  // Clip beats: muted MP4, looped when shorter than the beat, cut at its end.
  const clipFrames = Math.max(1, Math.round((beat.clip_seconds || 8) * fps));
  return (
    <Sequence from={from} durationInFrames={Math.max(1, frames)} name={beat.id}>
      <Loop durationInFrames={clipFrames}>
        <OffthreadVideo src={staticFile(beat.src)} muted style={media} />
      </Loop>
    </Sequence>
  );
};

const sticker = (s: number): React.CSSProperties => ({
  fontFamily: FONT, fontWeight: 800, color: INK, background: PAPER,
  border: `${Math.max(2, Math.round(4 * s))}px solid ${INK}`, borderRadius: Math.round(14 * s),
  boxShadow: `${Math.round(6 * s)}px ${Math.round(6 * s)}px 0 rgba(0,0,0,.85)`,
  padding: `${Math.round(8 * s)}px ${Math.round(20 * s)}px`, lineHeight: 1.2, textAlign: 'center',
  // max-content + maxWidth: wraps only at maxWidth, never because the anchor
  // sits near a frame edge (an absolute box shrinks to the space left of it).
  width: 'max-content', whiteSpace: 'normal', overflowWrap: 'normal', boxSizing: 'border-box'
});

/** Keeps a box inside the frame: anchor shifts with x/y (0 → left edge, 1 → right edge). */
const anchored = (x: number, y: number, extra = ''): React.CSSProperties => ({
  position: 'absolute', left: `${x * 100}%`, top: `${y * 100}%`,
  transform: `translate(-${x * 100}%, -${y * 100}%) ${extra}`
});

const Overlay: React.FC<{ov: any; local: number; remaining: number; fps: number; width: number; height: number}> = ({ov, local, remaining, fps, width, height}) => {
  const s = Math.min(width, height) / 1080;
  const appear = spring({frame: local * fps, fps, config: {damping: 13, stiffness: 170, mass: .7}});
  const fadeIn = clamp01(local / .25);
  const fontSize = Math.round(44 * s);
  // Max box height for n text lines (padding + border + rounding slack).
  const lines = (n: number, size: number) => Math.ceil(size * 1.2 * n + 2 * (8 + 4) * s + 2);
  const text = ov.text || '';
  if (ov.type === 'label') {
    return (
      <div data-check="overlay" data-max-height={lines(2, fontSize)}
        style={{...sticker(s), ...anchored(ov.x, ov.y, `scale(${.6 + .4 * appear})`), fontSize, maxWidth: width * .42, opacity: fadeIn}}>
        {text}
      </div>
    );
  }
  if (ov.type === 'chapter_title') {
    // Slides in, holds, then leaves after 3.5 s so it does not cover the whole beat.
    const out = clamp01((local - 3.5) / .4);
    const size = Math.round(70 * s);
    return (
      <div data-check="overlay" data-max-height={lines(2, size)}
        style={{...sticker(s), ...anchored(ov.x, ov.y, `translateX(${(1 - appear) * -120 + out * 120}%)`),
          fontSize: size, maxWidth: width * .8, padding: `${Math.round(18 * s)}px ${Math.round(40 * s)}px`,
          background: '#ffd84d', opacity: Math.min(fadeIn, 1 - out)}}>
        {text}
      </div>
    );
  }
  if (ov.type === 'counter') {
    const to = Number(ov.to) || 0;
    const decimals = Math.min(2, (String(ov.to).split('.')[1] || '').length);
    const t = clamp01(local / Math.min(1.6, Math.max(.4, remaining * .6)));
    const value = to * (1 - Math.pow(1 - t, 3));
    const shown = value.toLocaleString('vi-VN', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
    const size = Math.round(96 * s);
    return (
      <div data-check="overlay" data-max-height={lines(1, size) + lines(2, Math.round(36 * s))}
        style={{...sticker(s), ...anchored(ov.x, ov.y, `scale(${.6 + .4 * appear})`), maxWidth: width * .5, opacity: fadeIn}}>
        <div style={{fontSize: size, lineHeight: 1.15}}>{shown}</div>
        {text && <div style={{fontSize: Math.round(36 * s)}}>{text}</div>}
      </div>
    );
  }
  if (ov.type === 'map_pin') {
    const pin = Math.round(64 * s);
    const left = ov.x > .6;
    const drop = (1 - appear) * -60 * s;
    return (
      <div style={{position: 'absolute', left: ov.x * width, top: ov.y * height, width: 0, height: 0}}>
        <svg width={pin} height={pin * 1.35} viewBox="0 0 40 54"
          style={{position: 'absolute', left: -pin / 2, top: -pin * 1.35 + drop, opacity: fadeIn}}>
          <path d="M20 52 C20 52 3 30 3 19 A17 17 0 1 1 37 19 C37 30 20 52 20 52 Z" fill="#e2413b" stroke={INK} strokeWidth="3" />
          <circle cx="20" cy="19" r="6.5" fill={PAPER} stroke={INK} strokeWidth="2.5" />
        </svg>
        {text && (
          <div data-check="overlay" data-max-height={lines(2, Math.round(38 * s))}
            style={{...sticker(s), position: 'absolute', top: -pin * .95, fontSize: Math.round(38 * s),
              maxWidth: width * .3, width: 'max-content', opacity: clamp01((local - .15) / .25),
              ...(left ? {right: pin * .6} : {left: pin * .6})}}>
            {text}
          </div>
        )}
      </div>
    );
  }
  if (ov.type === 'arrow') {
    const length = Math.round(220 * s), thick = Math.max(4, Math.round(10 * s));
    const draw = clamp01(local / .45);
    const angle = Number(ov.angle) || 0;
    const rad = angle * Math.PI / 180;
    const tail = {x: ov.x * width - Math.cos(rad) * (length + 30 * s), y: ov.y * height - Math.sin(rad) * (length + 30 * s)};
    return (
      <>
        <div style={{position: 'absolute', left: ov.x * width, top: ov.y * height, width: 0, height: 0,
          transform: `rotate(${angle}deg)`, transformOrigin: '0 0'}}>
          <svg width={length} height={thick * 5} viewBox={`0 0 ${length} ${thick * 5}`}
            style={{position: 'absolute', left: -length, top: -thick * 2.5, overflow: 'visible'}}>
            <line x1={0} y1={thick * 2.5} x2={length - thick * 2} y2={thick * 2.5} stroke={INK} strokeWidth={thick}
              strokeLinecap="round" strokeDasharray={length} strokeDashoffset={length * (1 - draw)} />
            <path d={`M${length - thick * 4} ${thick * .6} L${length} ${thick * 2.5} L${length - thick * 4} ${thick * 4.4} Z`}
              fill={INK} opacity={draw >= .85 ? 1 : 0} />
          </svg>
        </div>
        {text && (
          <div data-check="overlay" data-max-height={lines(2, Math.round(36 * s))}
            style={{...sticker(s), position: 'absolute', left: tail.x, top: tail.y, transform: 'translate(-50%, -50%)',
              fontSize: Math.round(36 * s), maxWidth: width * .3, width: 'max-content', opacity: fadeIn}}>
            {text}
          </div>
        )}
      </>
    );
  }
  return null;
};

const Video: React.FC<any> = (p) => {
  const frame = useCurrentFrame();
  const fps = p.fps || 30;
  const t = frame / fps;
  const width = p.width || 1080;
  const height = p.height || 1920;
  const [fontHandle] = useState(() => delayRender('Loading overlay font'));
  useEffect(() => {fontReady.then(() => continueRender(fontHandle));}, [fontHandle]);

  useLayoutEffect(() => {
    for (const element of document.querySelectorAll<HTMLElement>('[data-check]')) {
      const maxHeight = element.dataset.check === 'subtitle' ? captionMaxHeight(width, height) : Number(element.dataset.maxHeight || Infinity);
      // Overlay boxes are shrink-to-fit, so allow the 1 px scrollWidth rounding.
      const slack = element.dataset.check === 'subtitle' ? 0 : 1;
      if (element.scrollWidth > element.clientWidth + slack || element.offsetHeight > maxHeight) {
        throw new Error('Actual render text overflow: ' + element.textContent);
      }
    }
  }, [frame, width, height]);

  const scene = p.scenes.find((s: any) => t >= s.start && t < s.end) || p.scenes[p.scenes.length - 1] || {start: 0, end: 1, image: '', title: ''};
  // Cues are pre-cut once in Python (adapters.subtitle_cues); the renderer
  // only has to find which one is active, never split text itself.
  const cue = (p.cues || []).find((c: any) => t >= c.start && t < c.end);
  const imageList = scene.images || [{src: scene.image, at: 0, effect: 'hold'}];
  const relative = t - scene.start;
  let active = 0;
  for (let i = 0; i < imageList.length; i++) if (relative >= imageList[i].at) active = i;
  const beat = imageList[active];
  const nextAt = imageList[active + 1]?.at ?? (scene.end - scene.start);
  const beatLength = Math.max(.001, nextAt - beat.at);
  const local = relative - beat.at;
  const progress = clamp01(local / beatLength);
  const transition = clamp01(local / Math.min(.3, Math.max(.001, beatLength / 2)));
  const beatFrom = Math.round((scene.start + beat.at) * fps);
  const beatTo = Math.round((scene.start + nextAt) * fps);
  const pop = spring({frame: frame - beatFrom, fps, config: {damping: 12, mass: .6}});
  const prev = active > 0 ? imageList[active - 1] : null;

  return (
    <AbsoluteFill style={{background: '#ffffff', fontFamily: FONT, color: 'white', width, height, overflow: 'hidden'}}>
      {prev && TRANSITIONS.includes(beat.effect) && transition < 1 && (
        <Visual beat={prev} from={Math.round((scene.start + prev.at) * fps)}
          frames={beatFrom - Math.round((scene.start + prev.at) * fps) + Math.round(.4 * fps)} style={{}} />
      )}
      {beat?.src && (
        <Visual beat={beat} from={beatFrom} frames={beatTo - beatFrom}
          style={{...beatStyle(beat.effect, progress, transition, pop),
            transformOrigin: `${(beat.focus?.x ?? .5) * 100}% ${(beat.focus?.y ?? .5) * 100}%`}} />
      )}

      {(beat?.overlays || []).filter((ov: any) => local >= (ov.at || 0)).map((ov: any, i: number) => (
        <Overlay key={beat.id + '-' + i} ov={ov} local={local - (ov.at || 0)} remaining={nextAt - beat.at - (ov.at || 0)}
          fps={fps} width={width} height={height} />
      ))}

      {/* Phụ đề dùng cùng bố cục với preflight, tối đa hai dòng có chủ đích */}
      {!p.hideSubtitles && cue && (
        <div data-check="subtitle" style={captionStyle(width, height) as React.CSSProperties}>
          {cue.text}
        </div>
      )}

      <Audio src={staticFile(p.audioSrc || 'narration.wav')} />
    </AbsoluteFill>
  );
};

registerRoot(() => (
  <Composition
    id="Pilot"
    component={Video}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={1800}
    defaultProps={{scenes: [], cues: []}}
    calculateMetadata={({props}: any) => {
      const isHorizontal = props.aspect_ratio === '16:9' || props.width === 1920;
      return {
        width: props.width || (isHorizontal ? 1920 : 1080),
        height: props.height || (isHorizontal ? 1080 : 1920),
        fps: props.fps || 30,
        durationInFrames: Math.ceil((props.duration || 60) * (props.fps || 30))
      };
    }}
  />
));
