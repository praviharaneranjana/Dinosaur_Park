# Audio Architecture and Optimization Guidelines

This rule establishes technical standards for Audio Mixers (`audio-setup-mixers`), sound routing, DSP effects, and memory optimization (`optimize-audio`).

## 1. AudioMixer Hierarchy & Routing
- **Bus Hierarchy**: Route all game `AudioSource` components through a structured `Master` AudioMixer:
  ```text
  Master
  ├── Music (BGM, stingers, ambient loops)
  ├── SFX
  │   ├── Weapons / Combat
  │   ├── Environment / Footsteps
  │   └── UI / Feedback
  └── Voice / Dialogue
  ```
- **Sidechain Ducking**: Use AudioMixer Ducking sends (e.g. from Voice or Combat SFX to Music) to preserve speech clarity without manual script volume manipulation.
- **Mixer Snapshots**: Use snapshots (`Normal`, `Paused`, `Underwater`, `LowHealth`) with `snapshot.TransitionTo(duration)` for scene transitions.

## 2. AudioClip Memory & Load Type Optimization
Choose `AudioClipLoadType` strictly based on clip duration and playback frequency:

| Clip Duration / Type | Recommended Load Type | Compression Format | Rationale |
| :--- | :--- | :--- | :--- |
| **Short SFX (< 2 seconds)** (gunshots, UI clicks, footsteps) | **Decompress On Load** | PCM or ADPCM | Zero CPU decompression overhead on repeated triggers; minimal RAM footprint. |
| **Medium SFX (2 - 15 seconds)** (explosions, ambient gusts, creature cries) | **Compressed In Memory** | Vorbis (Quality: 70) | Reduces memory usage by ~80% while incurring minor CPU decoding on playback. |
| **Long Music & Ambience (> 15 seconds)** | **Streaming** | Vorbis (Quality: 60-70) | Minimal memory footprint (streams in small chunks from disk/SSD buffer). |

## 3. General Directives
- **Force to Mono**: Check `Force To Mono` for all 3D spatialized sound effects (footsteps, gunshots, impacts) to cut audio memory in half. Leave stereo only for 2D UI and non-spatialized background music.
- **Preload Audio Data**: Leave `Preload Audio Data` enabled for gameplay-critical sound effects to avoid stutter on first trigger.
