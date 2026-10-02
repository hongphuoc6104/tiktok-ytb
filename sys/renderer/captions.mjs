export function captionStyle(width = 1080, height = 1920) {
  const portrait = height >= width;
  const scale = width / (portrait ? 1080 : 1920);
  return {
    position: 'absolute',
    bottom: Math.round((portrait ? 280 : 85) * scale),
    left: '50%',
    transform: 'translateX(-50%)',
    width: Math.round((portrait ? 940 : 1400) * scale),
    maxWidth: '92%',
    whiteSpace: 'pre-line',
    overflowWrap: 'normal',
    fontFamily: 'Arial, sans-serif',
    fontSize: Math.round((portrait ? 48 : 38) * scale),
    fontWeight: 800,
    lineHeight: 1.28,
    textAlign: 'center',
    padding: `${Math.round(14 * scale)}px ${Math.round(24 * scale)}px`,
    boxSizing: 'border-box',
    borderRadius: Math.round(20 * scale),
    color: '#ffffff',
    background: 'rgba(15, 23, 42, 0.88)',
    border: '2px solid rgba(56, 189, 248, 0.45)',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4), 0 2px 6px rgba(0,0,0,0.3)',
    textShadow: '0 2px 8px rgba(0, 0, 0, 0.8)'
  };
}

export function captionMaxHeight(width = 1080, height = 1920) {
  const s = captionStyle(width, height);
  const verticalPadding = Number.parseFloat(s.padding) * 2;
  return Math.ceil(s.fontSize * s.lineHeight * 2 + verticalPadding + 12);
}

