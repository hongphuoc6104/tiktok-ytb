import React, {useLayoutEffect} from 'react';
import {captionStyle, captionMaxHeight} from './captions.mjs';
import {AbsoluteFill, Audio, Composition, Img, registerRoot, staticFile, useCurrentFrame} from 'remotion';


const Video: React.FC<any> = (p) => {
  const frame = useCurrentFrame();
  const fps = p.fps || 30;
  const t = frame / fps;
  const width = p.width || 1080;
  const height = p.height || 1920;

  useLayoutEffect(() => {
    for (const element of document.querySelectorAll<HTMLElement>('[data-check]')) {
      if (element.scrollWidth > element.clientWidth || (element.dataset.check === 'subtitle' && element.offsetHeight > captionMaxHeight(width, height))) {
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
  const currentImageSrc = beat?.src || scene.image;
  const nextAt = imageList[active + 1]?.at ?? (scene.end - scene.start);
  const progress = Math.max(0, Math.min(1, (relative - beat.at) / Math.max(.001, nextAt - beat.at)));
  const transition = Math.max(0, Math.min(1, (relative - beat.at) / Math.min(.3, Math.max(.001, (nextAt - beat.at) / 2))));
  const scale = beat.effect === 'zoom_in' ? 1 + .08 * progress : beat.effect === 'zoom_out' ? 1.08 - .08 * progress : 1;
  const opacity = beat.effect === 'fade' ? transition : 1;
  const translate = beat.effect === 'slide_left' ? (1 - transition) * 100 : 0;

  return (
    <AbsoluteFill style={{background: '#ffffff', fontFamily: 'Arial, sans-serif', color: 'white', width, height}}>
      {active > 0 && ['fade', 'slide_left'].includes(beat.effect) && transition < 1 && (
        <Img src={staticFile(imageList[active - 1].src)} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'contain'}} />
      )}
      {currentImageSrc && (
        <Img
          src={staticFile(currentImageSrc)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            transform: `translateX(${translate}%) scale(${scale})`,
            transformOrigin: `${(beat.focus?.x ?? .5)*100}% ${(beat.focus?.y ?? .5)*100}%`,
            opacity
          }}
        />
      )}

      {/* Phụ đề dùng cùng bố cục với preflight, tối đa hai dòng có chủ đích */}
      {!p.hideSubtitles && cue && (() => {
        const lineText = cue.text;
        return (
          <div data-check="subtitle" style={captionStyle(width, height) as React.CSSProperties}>
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
    defaultProps={{scenes: [], cues: []}}
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
