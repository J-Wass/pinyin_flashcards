# Pinyin Flashcards

An interactive command-line application for learning Chinese pinyin pronunciation through audio flashcards. The app uses spaced repetition and adaptive scoring to help you learn efficiently.

## Features

- **Audio Pronunciation**: Hear the correct pronunciation of pinyin syllables
- **Spaced Repetition**: The app tracks your performance and prioritizes difficult sounds
- **Adaptive Learning**: Scores adjust based on your accuracy
- **Multiple Syllables**: Practice with 1-2 syllable combinations
- **Progress Tracking**: Your learning progress is saved automatically

## Prerequisites

- **Python 3.7+**
- **VLC Media Player** (must be installed on your system)
- **Windows** (currently optimized for Windows due to msvcrt usage)

## Installation

1. **Clone or download this repository**

   ```bash
   git clone <repository-url>
   cd pinyin
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r reqs.txt
   ```

3. **Install VLC Media Player**

   - Download from [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)
   - Install with default settings

4. **Set up your pinyin paths**
   - Copy `pinyin_paths_sample.py` to `pinyin_paths.py`
   - Edit `pinyin_paths.py` to include your actual audio file URLs
   - The format should be: `"pinyin.mp3": "https://your-server.com/pinyin.mp3"`

## How to Play

1. **Start the application**

   ```bash
   python flashcards.py
   ```

2. **Game Flow**:

   - The app will show you a pinyin syllable (e.g., "yǒu")
   - Outloud, say the syllable with the best pronounciation you can.
   - Press **Enter** to hear the pronunciation
   - After hearing the audio, press **y** if you got it right, **n** if you got it wrong - use your best judgement.
   - Your score for that syllable will be updated
   - Press **Esc** at any time to quit and save your progress

3. **Controls**:
   - **Enter**: Play the next syllable
   - **Esc**: Quit the game and save progress
   - **y**: You pronounced it correctly
   - **n**: You pronounced it incorrectly

## Scoring System

- **Correct answers**: Score increases (up to a maximum of 10)
- **Incorrect answers**: Score decreases by 2
- **Adaptive weighting**: Sounds you struggle with appear more frequently
- **Frequency weighting**: Common syllables appear more often

## File Structure

```
pinyin/
├── flashcards.py          # Main application
├── pinyin_paths.py        # Your audio file URLs (create from sample)
├── pinyin_paths _sample.py # Sample file showing the required format
├── reqs.txt              # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── sounds/               # Downloaded audio files (auto-created)
└── score_tracker.json    # Your learning progress (auto-created)
```

## Setting Up Audio Files

You need to provide your own audio files for the pinyin syllables. The `pinyin_paths.py` file should contain a dictionary mapping pinyin filenames to their URLs:

```python
pinyin_paths = {
    "zi1.mp3": "https://your-server.com/zi1.mp3",
    "zi2.mp3": "https://your-server.com/zi2.mp3",
    # ... more entries
}
```

### Audio File Requirements:

- **Format**: MP3 files
- **Naming**: Use the format `pinyin+tone.mp3` (e.g., `ma1.mp3`, `shi4.mp3`)
- **Content**: Single syllable pronunciation
- **Quality**: Clear, native speaker pronunciation

### VLC Errors

- **"stale plugins cache"**: These are warnings from some VLC installation versions. They are harmless and don't interfere with the game.
- **"Failed to create VLC instance"**: Make sure VLC is installed and accessible
