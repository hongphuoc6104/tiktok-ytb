import os
import json
import wave
import numpy as np
import soundfile as sf
from kokoro import KPipeline

os.makedirs("scratch/en_audio_segments", exist_ok=True)
os.makedirs("scratch/render_output", exist_ok=True)

# 24 scenes authentic English narration with natural pacing and micro-pauses for listing items
scenes_en = [
    {
        "id": "SC01",
        "text": "Do you often translate words from your native language before speaking? This habit makes you hesitate and lose confidence. Stop translating in your head. Today, let's train your brain to think directly in English."
    },
    {
        "id": "SC02",
        "text": "Here is the good news. Thinking in English is a muscle, and anyone can build it with five simple daily exercises. No textbooks, and no complicated grammar rules required."
    },
    {
        "id": "SC03",
        "text": "Make sure you stay until the end of this video. The final exercise is the most powerful mindset shift that will completely unlock your fluency."
    },
    {
        "id": "SC04",
        "text": "Exercise number one: Name everything around you. Right now, look around your room. Don't translate. Just label what you see in English.",
        "list_items": ["Window.", "Fan.", "Chair.", "Backpack.", "Bottle.", "Phone."]
    },
    {
        "id": "SC05",
        "text": "Whenever you spot an everyday object, name it immediately. A table, a mug, a doorway. One simple word at a time trains your brain to connect sight directly to English."
    },
    {
        "id": "SC06",
        "text": "Next, turn single words into simple sentences. For example: The window is open. The chair is comfortable. This fan is cool. Keep it completely natural."
    },
    {
        "id": "SC07",
        "text": "Take this habit outside when you walk. Notice a red car, a tall tree, a flying bird, or warm sunshine. Describe your world without translating."
    },
    {
        "id": "SC08",
        "text": "Exercise number two: Talk to yourself in English. When you are alone, you have zero pressure and zero fear of making mistakes."
    },
    {
        "id": "SC09",
        "text": "No one is judging you. You don't need a conversation partner. You are free to speak, make errors, and correct yourself naturally."
    },
    {
        "id": "SC10",
        "text": "Narrate your morning routine step by step. What are you doing right now? Say it out loud or think it softly in your mind."
    },
    {
        "id": "SC11",
        "text": "For instance: I am pouring hot water into my cup. The aroma of fresh coffee smells wonderful. I am ready for a productive day."
    },
    {
        "id": "SC12",
        "text": "Exercise number three: Use pictures instead of translations. When learning a new word, never attach it to your native language definition."
    },
    {
        "id": "SC13",
        "text": "Take the word hungry. Don't translate it. Instead, visualize your stomach rumbling and a plate of delicious hot food. Connect the sound to the feeling."
    },
    {
        "id": "SC14",
        "text": "When you hear the word run, picture a stickman sprinting down the street with fresh wind on his face. Create mental images, not dictionary entries."
    },
    {
        "id": "SC15",
        "text": "Stand in front of your mirror every morning and speak positive affirmations.",
        "list_items": ["Yes, I can!", "I've got this!", "I am confident!", "Practice makes progress!"]
    },
    {
        "id": "SC16",
        "text": "Exercise number four: Listen and repeat immediately. This technique is called shadowing. It trains your mouth and ears at the exact same time."
    },
    {
        "id": "SC17",
        "text": "Don't just repeat the words. Mimic the pitch, the rhythm, and the emotional expression of the native speaker. Feel the musical cadence of English."
    },
    {
        "id": "SC18",
        "text": "A vital tip: Always choose content that is easy and enjoyable. If material is too difficult, your brain will slip back into translation mode."
    },
    {
        "id": "SC19",
        "text": "Exercise number five: Live small moments in English. Dedicate five peaceful minutes every day entirely to English thinking."
    },
    {
        "id": "SC20",
        "text": "When you brush your teeth, wash dishes, or enjoy your lunch, switch your inner monologue completely into English."
    },
    {
        "id": "SC21",
        "text": "Look at the gentle clouds in the sky. Feel the evening breeze. Experience these genuine human moments directly through the English language."
    },
    {
        "id": "SC22",
        "text": "Remember: your brain functions exactly like a muscle. At first, thinking in English feels challenging, but with daily practice, it becomes effortless."
    },
    {
        "id": "SC23",
        "text": "One day soon, you will speak English without even realizing it. The words will simply flow from your heart, naturally and authentically."
    },
    {
        "id": "SC24",
        "text": "Start today with just five minutes. Stop translating in your head, and discover the true freedom of thinking in English. You can do this!"
    }
]

print("Initializing British English pipeline ('b') for bm_george...")
pipe = KPipeline(lang_code='b')

# 300ms silence at 24000Hz (sample rate of Kokoro)
pause_300ms = np.zeros(int(24000 * 0.32), dtype=np.float32)
pause_200ms = np.zeros(int(24000 * 0.22), dtype=np.float32)

all_scene_audio = []
cursor = 0.0
segments_en = []

for idx, sc in enumerate(scenes_en):
    sc_id = sc["id"]
    print(f"Synthesizing {sc_id}...")
    
    # Generate main text
    audio_parts = []
    generator = pipe(sc["text"], voice="bm_george", speed=0.90, split_pattern=r'\n+')
    for gs, ps, audio in generator:
        audio_parts.append(audio)
        audio_parts.append(pause_200ms)
    
    # If there are list items (e.g. SC04, SC15), synthesize each with distinct 300ms pause
    if "list_items" in sc:
        audio_parts.append(pause_300ms)
        for item in sc["list_items"]:
            gen_item = pipe(item, voice="bm_george", speed=0.88)
            for gs, ps, audio in gen_item:
                audio_parts.append(audio)
            audio_parts.append(pause_300ms)
            
    sc_audio = np.concatenate(audio_parts)
    dur = len(sc_audio) / 24000.0
    
    # Save individual scene audio
    sc_file = f"scratch/en_audio_segments/{sc_id}.wav"
    sf.write(sc_file, sc_audio, 24000)
    
    segments_en.append({
        "scene_id": sc_id,
        "text": sc["text"],
        "start": cursor,
        "end": cursor + dur,
        "path": sc_file
    })
    
    all_scene_audio.append(sc_audio)
    # 250ms pause between scenes
    all_scene_audio.append(pause_200ms)
    cursor += dur + 0.22

# Concatenate full English narration
full_en_audio = np.concatenate(all_scene_audio)
full_wav_path = "scratch/narration_en.wav"
sf.write(full_wav_path, full_en_audio, 24000)
print(f"Full English audio generated: {len(full_en_audio) / 24000.0:.2f}s (~{len(full_en_audio) / 24000.0 / 60:.1f} minutes)")

# Apply gentle studio mastering EQ
mastered_wav = "scratch/narration_en_mastered.wav"
os.system(f"ffmpeg -y -i {full_wav_path} -af 'equalizer=f=180:t=q:w=1.2:g=2.5,equalizer=f=3800:t=q:w=1.5:g=-2.0,loudnorm=I=-16:TP=-1.5:LRA=11' {mastered_wav} >/dev/null 2>&1")
if os.path.exists(mastered_wav) and os.path.getsize(mastered_wav) > 10000:
    os.replace(mastered_wav, full_wav_path)
    print("Mastering applied to scratch/narration_en.wav")

# Save segment metadata
with open("scratch/en_segments.json", "w") as f:
    json.dump(segments_en, f, indent=2)

print("English narration complete!")
