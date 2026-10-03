/** One source of truth for language, timeline and output dimensions. */
export function outputPlans(props, hasEnglish) {
  const ratio = props.aspect_ratio || '9:16';
  if (!['9:16', '16:9', 'dual'].includes(ratio)) throw Error('Unsupported output aspect ratio');
  if (props.outputs) {
    const expected = ratio === 'dual' ? ['9:16', '16:9'] : [ratio];
    if (!Array.isArray(props.outputs) || props.outputs.length !== expected.length) throw Error('Explicit output contract required');
    return props.outputs.map((plan, i) => {
      if (plan.aspect_ratio !== expected[i] || !['vi', 'en'].includes(plan.language) || typeof plan.subtitles !== 'boolean') throw Error('Invalid output contract');
      let track = props.tracks?.[plan.language];
      if (!track && props.primary_language === plan.language) {
        track = {audioSrc: 'narration.wav', duration: props.duration,
          scenesByAspect: props.scenes_by_aspect || {[expected[0]]: props.scenes}, cues: props.cues};
      }
      const scenes = track?.scenesByAspect?.[plan.aspect_ratio];
      if (!track?.audioSrc || !Number.isFinite(track.duration) || track.duration <= 0 || !Array.isArray(scenes) || !scenes.length) throw Error('Missing language track/timeline for requested aspect');
      if (plan.subtitles && !Array.isArray(track.cues)) throw Error('Missing captions for requested language');
      const vertical = plan.aspect_ratio === '9:16';
      return {file: ratio === 'dual' ? `video_${vertical ? '9x16' : '16x9'}.mp4` : 'video.mp4',
        props: {...props, scenes, duration: track.duration, cues: track.cues || [],
          width: vertical ? 1080 : 1920, height: vertical ? 1920 : 1080,
          hideSubtitles: !plan.subtitles, audioSrc: track.audioSrc, language: plan.language}};
    });
  }
  if (ratio !== '9:16' && (!hasEnglish || !props.en_scenes || !props.en_duration)) throw Error('English track and timeline required');
  const vertical = {...props, width: 1080, height: 1920, hideSubtitles: false, audioSrc: 'narration.wav'};
  const horizontal = {...props, scenes: props.en_scenes, duration: props.en_duration,
    width: 1920, height: 1080, hideSubtitles: true, audioSrc: 'narration_en.wav'};
  return ratio === 'dual' ? [{file: 'video_9x16.mp4', props: vertical}, {file: 'video_16x9.mp4', props: horizontal}]
    : [{file: 'video.mp4', props: ratio === '16:9' ? horizontal : vertical}];
}
