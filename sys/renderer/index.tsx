import React, {useLayoutEffect} from 'react';
import {captionStyle, captionMaxHeight} from './captions.mjs';
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  Video as RemotionVideo,
  registerRoot,
  staticFile,
  useCurrentFrame
} from 'remotion';

function renderHighlightedText(text: string, targetWord?: string, modern = false) {
  if (!text) return null;
  const cleanTarget = targetWord ? targetWord.toLowerCase().trim() : '';

  // Tách từ theo khoảng trắng và các dấu ngắt câu
  const parts = text.split(/(\s+|[.,!?:;"“”]+)/);
  return parts.map((part, i) => {
    const cleanPart = part.toLowerCase().replace(/[^a-z0-9-]/g, '');
    const isTarget = cleanTarget && cleanPart === cleanTarget;
    const isEnglishKeyword = !modern && /^[A-Z][a-zA-Z0-9-]*$/.test(part) && part.length > 1;

    if (isTarget || isEnglishKeyword) {
      return (
        <span
          key={i}
          style={{
            color: '#FACC15', // Vibrant Yellow highlight
            fontWeight: 900,
            textShadow: '0 0 16px rgba(250, 204, 21, 0.7), 0 2px 4px rgba(0, 0, 0, 0.95)',
            display: 'inline-block',
            letterSpacing: '0.02em',
          }}
        >
          {part}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

const Video: React.FC<any> = (p) => {
  const frame = useCurrentFrame();
  const fps = p.fps || 30;
  const t = frame / fps;
  const width = p.width || 1080;
  const height = p.height || 1920;
  const duration = p.duration || 30;

  useLayoutEffect(() => {
    for (const element of document.querySelectorAll<HTMLElement>('[data-check]')) {
      if (
        element.scrollWidth > element.clientWidth ||
        (element.dataset.check === 'subtitle' &&
          element.offsetHeight > captionMaxHeight(width, height))
      ) {
        throw new Error('Actual render text overflow: ' + element.textContent);
      }
    }
  }, [frame, width, height]);

  const scene =
    p.scenes.find((s: any) => t >= s.start && t < s.end) ||
    p.scenes[p.scenes.length - 1] ||
    {start: 0, end: 1, image: '', title: ''};

  const cue = (p.cues || []).find((c: any) => t >= c.start && t < c.end);
  const imageList = scene.images || [{src: scene.image, at: 0, effect: 'auto'}];
  const relative = t - scene.start;

  let active = 0;
  for (let i = 0; i < imageList.length; i++) {
    if (relative >= imageList[i].at) active = i;
  }
  const beat = imageList[active] || {src: scene.image, at: 0, effect: 'auto'};
  const currentImageSrc = beat?.src || scene.image;
  const nextAt = imageList[active + 1]?.at ?? (scene.end - scene.start);
  const beatDuration = Math.max(0.001, nextAt - beat.at);
  const progress = Math.max(0, Math.min(1, (relative - beat.at) / beatDuration));
  const transition = Math.max(0, Math.min(1, (relative - beat.at) / Math.min(0.3, beatDuration / 2)));

  // Ken Burns Motion Engine: Không để bất kỳ khung hình nào đứng yên (Never static)
  let scale = 1;
  let translateX = 0;
  let translateY = 0;
  const effect = beat.effect || 'auto';

  if (effect === 'punch_in') {
    const punchT = Math.min(1, (relative - beat.at) / 0.35);
    scale = 1.25 - 0.17 * punchT; // Snap punch-in 1.25x rồi dịu về 1.08x
  } else if (effect === 'zoom_in') {
    scale = 1 + 0.08 * progress;
  } else if (effect === 'zoom_out') {
    scale = 1.08 - 0.08 * progress;
  } else if (effect === 'pan_left') {
    scale = 1.06;
    translateX = (0.5 - progress) * 3;
  } else if (effect === 'pan_right') {
    scale = 1.06;
    translateX = (progress - 0.5) * 3;
  } else if (effect === 'slide_left') {
    translateX = (1 - transition) * 100;
  } else if (!p.modern_style && effect !== 'hold') {
    // AUTO KEN BURNS (Chu kỳ chuyển động camera êm ái chống nhàm chán)
    const cycle = active % 4;
    if (cycle === 0) {
      scale = 1.0 + 0.06 * progress; // Zoom in
    } else if (cycle === 1) {
      scale = 1.05;
      translateX = (progress - 0.5) * 2.5; // Pan right
    } else if (cycle === 2) {
      scale = 1.06 - 0.06 * progress; // Zoom out
    } else {
      scale = 1.05;
      translateX = (0.5 - progress) * 2.5; // Pan left
    }
  }

  // Screen Shake (Rung chấn màn hình comic khi va đập / giật mình)
  let shakeX = 0;
  let shakeY = 0;
  if (effect === 'shake' || (effect === 'punch_in' && (relative - beat.at) < 0.28)) {
    const shakeTime = relative - beat.at;
    const decay = Math.max(0, 1 - shakeTime / 0.28);
    shakeX = Math.sin(shakeTime * 55) * 14 * decay;
    shakeY = Math.cos(shakeTime * 55) * 12 * decay;
  }

  const opacity = beat.effect === 'fade' ? transition : 1;
  const focusX = (beat.focus?.x ?? 0.5) * 100;
  const focusY = (beat.focus?.y ?? 0.42) * 100;
  const isVideoAsset = currentImageSrc && (currentImageSrc.endsWith('.mp4') || currentImageSrc.endsWith('.webm'));

  return (
    <AbsoluteFill style={{background: p.modern_style ? '#F8FAFC' : '#090D16', fontFamily: 'Arial, sans-serif', color: 'white', width, height, overflow: 'hidden'}}>
      {/* Background layer transition */}
      {active > 0 && ['fade', 'slide_left'].includes(beat.effect) && transition < 1 && (
        <Img
          src={staticFile(imageList[active - 1].src)}
          style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'contain'}}
        />
      )}

      {/* Main Visual Layer: Image with Ken Burns or Video Clip */}
      {currentImageSrc && (
        isVideoAsset ? (
          <RemotionVideo
            src={staticFile(currentImageSrc)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              opacity
            }}
          />
        ) : (
          <Img
            src={staticFile(currentImageSrc)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              transform: `translate(calc(${translateX}% + ${shakeX}px), calc(${translateY}% + ${shakeY}px)) scale(${scale})`,
              transformOrigin: `${focusX}% ${focusY}%`,
              opacity
            }}
          />
        )
      )}

      {/* 2D Comic Doodle Visual Accents */}
      {/* 1. Dấu chấm than giật mình (tùy chọn khi tranh chưa có sẵn biểu cảm) */}
      {!p.modern_style && p.show_exclamation && scene.id === 'SC01' && relative >= 0.5 && relative <= 2.2 && (
        <div
          style={{
            position: 'absolute',
            top: '22%',
            left: '20%',
            transform: `scale(${Math.min(1.15, 0.4 + (relative - 0.5) * 5)}) rotate(${Math.sin((relative - 0.5) * 16) * 10}deg)`,
            zIndex: 15,
            filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.4))'
          }}
        >
          <svg width="65" height="85" viewBox="0 0 65 85">
            <path
              d="M 22 8 L 43 8 L 36 48 L 29 48 Z"
              fill="#EF4444"
              stroke="#0F172A"
              strokeWidth="5"
              strokeLinejoin="round"
            />
            <circle cx="32.5" cy="70" r="8" fill="#EF4444" stroke="#0F172A" strokeWidth="5" />
          </svg>
        </div>
      )}

      {/* 2. Interactive Practice Indicator: Đếm nhịp luyện nói tự động đồng bộ theo Cue */}
      {!p.modern_style && cue && (cue.practice || cue.text?.includes('Cùng nhắc lại nhé')) && (() => {
        const pDur = cue.end - cue.start;
        const pRel = t - cue.start;
        const pProgress = Math.max(0, Math.min(1, pRel / pDur));
        if (pProgress < 0.4) return null;
        const countProgress = (pProgress - 0.4) / 0.6;
        const countText = countProgress < 0.33 ? '3...' : countProgress < 0.66 ? '2...' : '1... 🎙️';
        return (
          <div
            style={{
              position: 'absolute',
              bottom: height >= width ? 510 : 180,
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'rgba(15, 23, 42, 0.94)',
              border: '2px dashed #FACC15',
              borderRadius: 30,
              padding: '10px 24px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              zIndex: 25,
              boxShadow: '0 8px 24px rgba(250, 204, 21, 0.35)'
            }}
          >
            <span style={{fontSize: 32}}>🗣️</span>
            <span style={{fontSize: 26, fontWeight: 800, color: '#FACC15'}}>
              Luyện nói: {countText}
            </span>
          </div>
        );
      })()}

      {/* Subtitles (Phụ đề động bắt mắt) */}
      {!p.hideSubtitles && cue && (() => {
        const lineText = cue.text;
        const targetWord = p.target_word;
        return (
          <div data-check="subtitle" style={captionStyle(width, height) as React.CSSProperties}>
            {renderHighlightedText(lineText, targetWord, p.modern_style)}
          </div>
        );
      })()}

      {/* Subtle Progress Bar (Thanh thời gian mỏng phát sáng ở đáy) */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          height: 6,
          width: `${Math.min(100, Math.max(0, (t / duration) * 100))}%`,
          background: 'linear-gradient(90deg, #38BDF8, #FACC15)',
          boxShadow: '0 0 10px rgba(56, 189, 248, 0.8)',
          zIndex: 20
        }}
      />

      {/* Audio Mixer: Voice narration */}
      <Audio src={staticFile(p.audioSrc || 'narration.wav')} volume={1} />

      {/* Audio Mixer: Background Music (BGM) */}
      {p.bgmSrc && (
        <Audio
          src={staticFile(p.bgmSrc)}
          volume={p.bgmVolume ?? 0.12}
          loop
        />
      )}
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
        durationInFrames: Math.ceil((props.duration || 30) * (props.fps || 30))
      };
    }}
  />
));
