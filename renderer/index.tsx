import React, {useLayoutEffect} from 'react';
import {AbsoluteFill, Audio, Composition, Img, registerRoot, staticFile, useCurrentFrame, interpolate} from 'remotion';

const VocabularyCard: React.FC<{vocab: any[]; isVertical: boolean}> = ({vocab, isVertical}) => {
  if (!vocab || !vocab.length) return null;
  return (
    <div style={{
      position: 'absolute',
      top: isVertical ? 180 : 70,
      right: isVertical ? 48 : 80,
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      zIndex: 10,
      maxWidth: isVertical ? 420 : 460
    }}>
      {vocab.map((item, idx) => (
        <div key={idx} style={{
          background: 'rgba(15, 23, 42, 0.88)',
          backdropFilter: 'blur(8px)',
          border: '2px solid rgba(56, 189, 248, 0.4)',
          borderRadius: 16,
          padding: '12px 18px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          color: '#ffffff',
          fontFamily: 'Arial, sans-serif'
        }}>
          <span style={{fontSize: 26}}>🏷️</span>
          <div>
            <div style={{fontSize: 24, fontWeight: 800, color: '#38bdf8', letterSpacing: '0.5px'}}>
              {item.word} {item.phonetic ? <span style={{fontSize: 18, fontWeight: 400, color: '#94a3b8'}}>{item.phonetic}</span> : null}
            </div>
            <div style={{fontSize: 18, fontWeight: 600, color: '#e2e8f0', marginTop: 2}}>
              {item.meaning}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

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
  const scale = interpolate(t, [scene.start, scene.end], [1, 1.055], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{background: '#0f172a', fontFamily: 'Arial, sans-serif', color: 'white', width, height}}>
      {scene.image && (
        <Img
          src={staticFile(scene.image)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${scale})`,
            opacity: interpolate(t, [scene.start, scene.start + 0.3, scene.end - 0.3, scene.end], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
          }}
        />
      )}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, transparent 35%, transparent 65%, rgba(0,0,0,0.88) 100%)'}} />

      {/* Tiêu đề cảnh */}
      <div data-check="title" style={{
        position: 'absolute',
        top: isVertical ? 92 : 48,
        left: isVertical ? 48 : 64,
        width: isVertical ? width - 96 : width * 0.55,
        fontSize: isVertical ? 40 : 36,
        fontWeight: 800,
        lineHeight: 1.25,
        color: '#f8fafc',
        textShadow: '0 2px 10px rgba(0,0,0,0.7)'
      }}>
        {scene.title}
      </div>

      {/* Thẻ từ vựng đồ vật xuất hiện trong cảnh */}
      {scene.vocabulary && <VocabularyCard vocab={scene.vocabulary} isVertical={isVertical} />}

      {/* Phụ đề */}
      {sub && (
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

      <Audio src={staticFile('narration.wav')} />
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
