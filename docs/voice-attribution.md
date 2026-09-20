# English voice attribution

English narration uses **Alba MacKenna — casual** from Kyutai's official voice collection:
https://huggingface.co/kyutai/tts-voices/tree/main/alba-mackenna

The voice reference is licensed under **Creative Commons Attribution 4.0 International**:
https://creativecommons.org/licenses/by/4.0/

The generated narration is synthetic, using Pocket TTS's precomputed Alba voice state.
The pipeline resamples output to 48 kHz, adds scene-end pauses and masters loudness.
It does not change speaking speed or pitch. No endorsement by the voice performer is implied.

When publishing videos, include this credit in the description or accompanying credits:

> English synthetic voice: Alba MacKenna (casual), via Kyutai Pocket TTS.
> Reference voice: https://huggingface.co/kyutai/tts-voices/tree/main/alba-mackenna
> Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
> Adapted through speech synthesis, resampling and audio mastering.

Runtime: pocket-tts 3.1.0, packaged English configuration and its pinned upstream model/voice
revisions, dynamic INT8 attention and feed-forward layers, FP32 audio decoder, CPU only.
The dependency lock contains no Chatterbox or CUDA runtime dependencies.
