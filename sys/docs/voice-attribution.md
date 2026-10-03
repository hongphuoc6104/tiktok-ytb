# English voice attribution

New English briefs default to **reference-narrator at 0.92**, using the exact saved sample selected by the user. Its [profile](../assets/voices/reference-narrator/profile.json) records the reference text, hash and historical source; [asset notes](../assets/voices/reference-narrator/README.md) distinguish the 3.24-second cloned WAV from the longer source-video interval. Do not assign Alba's identity or license to this different reference.

Historical jobs selecting **Alba MacKenna — casual** use Kyutai's official voice collection:
https://huggingface.co/kyutai/tts-voices/tree/main/alba-mackenna

The voice reference is licensed under **Creative Commons Attribution 4.0 International**:
https://creativecommons.org/licenses/by/4.0/

The original reference was generated with Pocket TTS's precomputed Alba voice state.
The saved profile in `assets/voices/alba/profile.json` derives from two English
fragments of the earlier `vocab-weather-001` job. It is not a sample extracted
from the user's YouTube channel or the Ink Explainer reference video.

For jobs selecting Alba, engine 4 uses OmniVoice on Colab to clone the saved Alba reference, with voice
and requested speed frozen in the job brief/request. Assembly, resampling,
scene-end pauses and mastering run on Colab. No endorsement by the voice
performer is implied; technical validation does not prove voice similarity.

When publishing videos that use Alba, include this credit in the description or accompanying credits:

> English synthetic voice reference: Alba MacKenna (casual), via Kyutai Pocket TTS; adapted with OmniVoice.
> Reference voice: https://huggingface.co/kyutai/tts-voices/tree/main/alba-mackenna
> Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
> Adapted through speech synthesis, resampling and audio mastering.

Historical reference-source runtime: pocket-tts 3.1.0, packaged English configuration and its pinned upstream model/voice
revisions, dynamic INT8 attention and feed-forward layers, FP32 audio decoder, CPU only.
The historical Pocket dependency lock contains no Chatterbox or CUDA runtime dependencies.
Current runtime details are in `colab-tts.md` and each immutable Colab request/result manifest.
