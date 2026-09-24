/** Shared by the actual composition and the geometry preflight. */
export function captionStyle(width = 1080, height = 1920) {
  const portrait = height >= width;
  const scale = width / (portrait ? 1080 : 1920);
  return {
    position: 'absolute',
    bottom: Math.round((portrait ? 290 : 85) * scale),
    left: '50%',
    transform: 'translateX(-50%)',
    width: Math.round((portrait ? 880 : 1380) * scale),
    maxWidth: '90%',
    whiteSpace: 'pre-line',
    overflowWrap: 'normal',
    fontFamily: 'Arial, sans-serif',
    fontSize: Math.round((portrait ? 50 : 40) * scale),
    fontWeight: 700,
    lineHeight: 1.24,
    textAlign: 'center',
    padding: `${Math.round(12 * scale)}px ${Math.round(22 * scale)}px`,
    boxSizing: 'border-box',
    borderRadius: Math.round(16 * scale),
    color: '#ffffff',
    background: 'rgba(15, 23, 42, 0.92)',
    border: '1px solid rgba(255, 255, 255, 0.25)',
    boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
  };
}

export function captionMaxHeight(width = 1080, height = 1920) {
  const s = captionStyle(width, height);
  const verticalPadding = Number.parseFloat(s.padding) * 2;
  return s.fontSize * s.lineHeight * 2 + verticalPadding + 3;
}
