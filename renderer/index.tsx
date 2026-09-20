import React, {useLayoutEffect} from 'react';
import {AbsoluteFill, Audio, Composition, Img, registerRoot, staticFile, useCurrentFrame, interpolate} from 'remotion';


function splitIntoPhrases(text: string, maxLen = 32): string[] {
  if (!text || text.length <= maxLen) return [text || ''];
  const rawParts = text.split(/([,?!;:\.—])/).filter(Boolean);
  const clauses: string[] = [];
  let curr = '';
  for (const p of rawParts) {
    if (['.', ',', '?', '!', ';', ':', '—'].includes(p)) {
      curr += p;
    } else {
      if (curr.trim()) clauses.push(curr.trim());
      curr = p;
    }
  }
  if (curr.trim()) clauses.push(curr.trim());

  const result: string[] = [];
  for (const clause of clauses) {
    if (clause.length <= maxLen) {
      result.push(clause);
    } else {
      const words = clause.split(/\s+/);
      let buf = '';
      for (const w of words) {
        if ((buf ? buf + ' ' + w : w).length <= maxLen) {
          buf = buf ? buf + ' ' + w : w;
        } else {
          if (buf) result.push(buf);
          buf = w;
        }
      }
      if (buf) result.push(buf);
    }
  }
  return result.length > 0 ? result : [text];
}

function getActiveSubtitle(sub: {text: string, start: number, end: number}, t: number): string {
  if (!sub || !sub.text) return '';
  if (sub.text.length <= 32) return sub.text;
  const chunks = splitIntoPhrases(sub.text, 32);
  if (chunks.length <= 1) return chunks[0] || sub.text;

  const duration = Math.max(0.1, sub.end - sub.start);
  const relTime = Math.max(0, Math.min(duration, t - sub.start));
  const progress = relTime / duration;

  const totalChars = chunks.reduce((sum, c) => sum + Math.max(c.length, 6), 0);
  let accumulated = 0;
  const targetChar = progress * totalChars;
  for (const c of chunks) {
    accumulated += Math.max(c.length, 6);
    if (targetChar <= accumulated) {
      return c;
    }
  }
  return chunks[chunks.length - 1];
}

const Video: React.FC<any> = (p) => {
  const frame = useCurrentFrame();
  const fps = p.fps || 30;
  const t = frame / fps;
  const width = p.width || 1080;
  const height = p.height || 1920;
  const isVertical = height >= width;

  useLayoutEffect(() => {
    for (const element of document.querySelectorAll<HTMLElement>('[data-check]')) {
      const rect = element.getBoundingClientRect();
      if (element.scrollWidth > element.clientWidth || (element.dataset.check === 'subtitle' && element.offsetHeight > 180)) {
        throw new Error('Actual render text overflow: ' + element.textContent);
      }
    }
  }, [frame]);

  const scene = p.scenes.find((s: any) => t >= s.start && t < s.end) || p.scenes[p.scenes.length - 1] || {start: 0, end: 1, image: '', title: ''};
  const sub = p.segments.find((s: any) => t >= s.start && t < s.end);
  const scale = interpolate(t, [scene.start, scene.end], [1, 1.04], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  // Progressive reveal image selection based on relative time in scene
  let currentImageSrc = scene.image;
  if (scene.images && Array.isArray(scene.images) && scene.images.length > 0) {
    const relTime = t - scene.start;
    for (const item of scene.images) {
      if (relTime >= (item.at || 0)) {
        currentImageSrc = item.src;
      }
    }
  }

  return (
    <AbsoluteFill style={{background: '#ffffff', fontFamily: 'Arial, sans-serif', color: 'white', width, height}}>
      {currentImageSrc && (
        <Img
          src={staticFile(currentImageSrc)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            transform: `scale(${scale})`,
            opacity: interpolate(t, [scene.start, scene.start + 0.2, scene.end - 0.2, scene.end], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
          }}
        />
      )}

      {/* Phụ đề: chỉ hiển thị nếu không bật hideSubtitles - luôn nằm gọn trên 1 dòng duy nhất */}
      {!p.hideSubtitles && sub && (() => {
        const lineText = getActiveSubtitle(sub, t);
        return (
          <div data-check="subtitle" style={{
            position: 'absolute',
            bottom: isVertical ? 180 : 70,
            left: '50%',
            transform: 'translateX(-50%)',
            maxWidth: isVertical ? width - 80 : Math.min(width - 160, 1400),
            width: 'auto',
            whiteSpace: 'nowrap',
            fontSize: isVertical ? 32 : 28,
            fontWeight: 800,
            lineHeight: '44px',
            textAlign: 'center',
            padding: '10px 24px',
            boxSizing: 'border-box',
            borderRadius: 18,
            background: 'rgba(15, 23, 42, 0.88)',
            border: '1.5px solid rgba(255, 255, 255, 0.25)',
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
            letterSpacing: '0.2px'
          }}>
            {lineText}
          </div>
        );
      })()}

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
    defaultProps={{scenes: [], segments: []}}
    calculateMetadata={({props}: any) => {
      const isHorizontal = props.aspect_ratio === '16:9' || props.width === 1920;
      return {
        width: props.width || (isHorizontal ? 1920 : 1080),
        height: props.height || (isHorizontal ? 1080 : 1920),
        durationInFrames: Math.ceil((props.duration || 60) * (props.fps || 30))
      };
    }}
  />
));
