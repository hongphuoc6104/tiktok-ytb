import React, {useLayoutEffect} from 'react';
import {AbsoluteFill, Audio, Composition, Img, registerRoot, staticFile, useCurrentFrame, interpolate} from 'remotion';


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

      {/* Phụ đề: chỉ hiển thị nếu không bật hideSubtitles */}
      {!p.hideSubtitles && sub && (
        <div data-check="subtitle" style={{
          position: 'absolute',
          bottom: isVertical ? 150 : 70,
          left: '50%',
          transform: 'translateX(-50%)',
          width: isVertical ? width - 88 : Math.min(width - 160, 1400),
          fontSize: isVertical ? 34 : 32,
          fontWeight: 600,
          lineHeight: '46px',
          textAlign: 'center',
          padding: '14px 24px',
          boxSizing: 'border-box',
          borderRadius: 18,
          background: 'rgba(15, 23, 42, 0.88)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
        }}>
          {sub.text}
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
