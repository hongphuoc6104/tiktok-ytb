/** One source of truth for language, timeline and output dimensions.
 *
 * props.voice_language is the language of the 16:9 track (default English,
 * as before); 9:16 is always Vietnamese. props.subtitles=false turns the
 * burned-in Vietnamese subtitles off; English tracks never carry subtitles. */
export function outputPlans(props, hasEnglish) {
  const ratio = props.aspect_ratio || '9:16';
  if (!['9:16', '16:9', 'dual'].includes(ratio)) throw Error('Unsupported output aspect ratio');
  const wide = ratio === '9:16' ? 'vi' : (props.voice_language || 'en');
  if (ratio !== '9:16' && wide === 'en' && (!hasEnglish || !props.en_scenes || !props.en_duration)) throw Error('English track and timeline required');
  const hideVi = props.subtitles === false;
  const vertical = {...props, width: 1080, height: 1920, hideSubtitles: hideVi, audioSrc: 'narration.wav'};
  const horizontal = wide === 'vi'
    ? {...props, scenes: ratio === 'dual' ? props.horizontal_scenes : props.scenes,
      width: 1920, height: 1080, hideSubtitles: hideVi, audioSrc: 'narration.wav'}
    : {...props, scenes: props.en_scenes, duration: props.en_duration,
      width: 1920, height: 1080, hideSubtitles: true, audioSrc: 'narration_en.wav'};
  if (!horizontal.scenes && ratio !== '9:16') throw Error('16:9 timeline required');
  return ratio === 'dual' ? [{file: 'video_9x16.mp4', props: vertical}, {file: 'video_16x9.mp4', props: horizontal}]
    : [{file: 'video.mp4', props: ratio === '16:9' ? horizontal : vertical}];
}
