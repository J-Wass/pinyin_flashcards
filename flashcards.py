from collections import defaultdict
import time
import requests
import vlc
import os
import random
import msvcrt
from typing import Set
import json
import signal
import sys

from pinyin_paths import pinyin_paths # implement yourself. 


score_tracker = defaultdict(int)
"""mapping of pinyin -> score"""

# update from save file, if it exists
try:
    with open("score_tracker.json", "r") as f:
        score_tracker.update(json.load(f))
except FileNotFoundError:
    pass

frequency_weights = {
    # Top 10-20 high-frequency syllables
    'shi4': 100,
    'de5': 95,
    'bu4': 90,
    'le5': 88,
    'ren2': 85,
    'zai4': 83,
    'you3': 80,
    'wo3': 78,
    'ta1': 75,
    'zhe4': 73,
    'yi1': 70,
    'ge4': 68,
    'he2': 65,
    'ye3': 62,
    'zhong1': 60,
    'guo2': 58,
    'shang4': 55,
    'xue2': 53,
    'xiao3': 50,

    # Medium-frequency
    'hao3': 45,
    'ma1': 42,
    'ni3': 40,
    'men5': 38,
    'lai2': 36,
    'kan4': 34,
    'shuo1': 32,
    'xin1': 30,
    'dui4': 28,
    'na3': 26,
    'qu4': 24,
    'hui4': 22,
    'chi1': 20,
}
# Default catch-all (used in calculate_weight)
# any others not in this list will get 10
for key in pinyin_paths:
    base = key.split(".")[0]
    if base not in frequency_weights:
        frequency_weights[base] = 10

def pinyin_numbered_to_accented(pinyin: str) -> str:
    tone_marks = {
        'a': ['ā', 'á', 'ǎ', 'à'],
        'o': ['ō', 'ó', 'ǒ', 'ò'],
        'e': ['ē', 'é', 'ě', 'è'],
        'i': ['ī', 'í', 'ǐ', 'ì'],
        'u': ['ū', 'ú', 'ǔ', 'ù'],
        'ü': ['ǖ', 'ǘ', 'ǚ', 'ǜ'],
    }

    tone_number = None
    for i in range(len(pinyin)):
        if pinyin[i].isdigit():
            tone_number = int(pinyin[i]) - 1
            pinyin_base = pinyin[:i]
            break

    # if there's no tone
    if tone_number is None or tone_number not in range(4):
        return pinyin

    for vowel in ['a', 'o', 'e', 'i', 'u', 'ü']:
        if vowel in pinyin_base:
            return pinyin_base.replace(vowel, tone_marks[vowel][tone_number], 1)

    return pinyin_base

def wait_for_key(valid_keys: Set[str]) -> str:
    """Waits for a key in valid_keys to be pressed and returns its name."""
    while True:
        valid_keys = {k.lower() for k in valid_keys}
        key = msvcrt.getch()
        
        # Handle special keys
        if key == b'\r':  # Enter key
            if 'enter' in valid_keys:
                return 'enter'
        elif key == b'\x1b':  # Escape key
            if 'esc' in valid_keys:
                return 'esc'
        else:
            # Handle regular keys
            try:
                key_char = key.decode('utf-8').lower()
                if key_char in valid_keys:
                    return key_char
            except UnicodeDecodeError:
                continue

            
def calculate_weight(base: str) -> float:
    base_score = score_tracker[base]
    base_freq = frequency_weights.get(base, 10)
    score_factor = max(1, 5 - base_score)  # More wrong = higher priority
    return base_freq * score_factor

def cleanup_and_exit(signum=None, frame=None):
    """Clean up and exit gracefully."""
    sys.exit(0)

if __name__ == "__main__":  
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)
    
    try:
        vlc_instance = vlc.Instance("--quiet --no-plugins-cache")
        if vlc_instance is None:
            print("Failed to create VLC instance. Please ensure VLC is installed.")
            cleanup_and_exit()
    except Exception as e:
        print(f"Error creating VLC instance: {e}")
        print("Please ensure VLC is installed and accessible.")
        cleanup_and_exit()
        
    try:
        while True:
            pinyin_list = []
            selected_paths = []

            # calculate new weights of each sound
            choices = list(pinyin_paths.keys())
            weights = []
            for sound in choices:
                base = sound.split(".")[0]
                weight = calculate_weight(base)
                weights.append(weight)

            # select 1 or 2 random sounds, weighted
            for i in range(random.randint(1,2)):
                sound = random.choices(choices, weights=weights, k=1)[0]

                # If the sound doesn't exist, download it.
                expected_path = os.path.join(os.getcwd(), "sounds", sound)
                selected_paths.append(expected_path)
                if not os.path.exists(expected_path):
                    os.makedirs(os.path.dirname(expected_path), exist_ok=True)
                    mp3_lookup = requests.get(pinyin_paths[sound])
                    with open(expected_path, "wb") as new_mp3:
                        new_mp3.write(mp3_lookup.content)

                pinyin = sound.split(".")[0]
                accented_pinyin = pinyin_numbered_to_accented(pinyin)
                pinyin_list.append(accented_pinyin)

            pinyin = " ".join(pinyin_list)
            print(f"Pronounce: {pinyin}\nHit Enter to continue or Esc to end")
            key = wait_for_key({'enter', 'esc'})
            if key == 'enter':
                # play the sound (it may be multiple sounds to form a "phrase")
                for path in selected_paths:
                    try:
                        p = vlc_instance.media_player_new()
                        media = vlc_instance.media_new(path)
                        p.set_media(media)
                        p.play()
                        # Wait for playback to end
                        while True:
                            state = p.get_state()
                            if state == 6:  # vlc.State.Ended = 6
                                break
                            time.sleep(0.1)
                    except Exception as e:
                        print(f"Error playing audio file {path}: {e}")
                        continue

                # sound is done playing, prompt for correctness
                print("Did you get it right? (y/n)")
                user_input = wait_for_key({'y', 'n'})
                for path in selected_paths:
                    base = os.path.basename(path).split(".")[0]
                    if user_input == 'y':
                        score_tracker[base] += min(score_tracker[base] + 1, 10)
                    elif user_input == 'n':
                        score_tracker[base] -= 2
                    print(f"  New score for {base}: {score_tracker[base]}")
                print()

            elif key == 'esc':
                with open("score_tracker.json", "w") as f:
                    json.dump(score_tracker, f)
                cleanup_and_exit()
    finally:
        # Clean up keyboard listener to prevent keystrokes from going to shell
        cleanup_and_exit()
