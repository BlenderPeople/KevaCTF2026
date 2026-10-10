/**
 * Synthesizes vintage mechanical typewriter sound effects using Web Audio API.
 * No external mp3/wav files required! Works offline and directly in any browser.
 */
class TypewriterSoundEngine {
    constructor() {
        this.audioCtx = null;
    }

    init() {
        if (!this.audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContext();
        }
        if (this.audioCtx.state === 'suspended') {
            this.audioCtx.resume();
        }
    }

    // Sound of a mechanical metal key hit and ribbon strike
    playKeyStrike() {
        try {
            this.init();
            const now = this.audioCtx.currentTime;

            // 1. Noise burst (mechanical click/impact)
            const bufferSize = this.audioCtx.sampleRate * 0.04;
            const noiseBuffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
            const output = noiseBuffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.2));
            }

            const whiteNoise = this.audioCtx.createBufferSource();
            whiteNoise.buffer = noiseBuffer;

            const noiseFilter = this.audioCtx.createBiquadFilter();
            noiseFilter.type = 'bandpass';
            noiseFilter.frequency.value = 1800 + (Math.random() * 600 - 300);
            noiseFilter.Q.value = 3.0;

            const noiseGain = this.audioCtx.createGain();
            noiseGain.gain.setValueAtTime(0.8, now);
            noiseGain.gain.exponentialRampToValueAtTime(0.01, now + 0.04);

            whiteNoise.connect(noiseFilter);
            noiseFilter.connect(noiseGain);
            noiseGain.connect(this.audioCtx.destination);
            whiteNoise.start(now);

            // 2. Metallic clack body tone (low resonant ping)
            const osc = this.audioCtx.createOscillator();
            const oscGain = this.audioCtx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(320 + Math.random() * 80, now);
            osc.frequency.exponentialRampToValueAtTime(110, now + 0.05);

            oscGain.gain.setValueAtTime(0.5, now);
            oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

            osc.connect(oscGain);
            oscGain.connect(this.audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.06);

        } catch (e) {
            // Audio context might fail before user gesture
        }
    }

    // Vintage typewriter margin bell ("Ding!")
    playBell() {
        try {
            this.init();
            const now = this.audioCtx.currentTime;

            const osc = this.audioCtx.createOscillator();
            const gain = this.audioCtx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(2200, now);

            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);

            osc.connect(gain);
            gain.connect(this.audioCtx.destination);

            osc.start(now);
            osc.stop(now + 0.8);
        } catch (e) {}
    }

    // Carriage return ratchet sound
    playCarriageReturn() {
        try {
            this.init();
            const now = this.audioCtx.currentTime;
            
            // series of quick ratchet clicks
            for (let i = 0; i < 6; i++) {
                const clickTime = now + (i * 0.04);
                const osc = this.audioCtx.createOscillator();
                const gain = this.audioCtx.createGain();
                
                osc.type = 'square';
                osc.frequency.setValueAtTime(600 + i * 40, clickTime);
                gain.gain.setValueAtTime(0.15, clickTime);
                gain.gain.exponentialRampToValueAtTime(0.001, clickTime + 0.02);
                
                osc.connect(gain);
                gain.connect(this.audioCtx.destination);
                osc.start(clickTime);
                osc.stop(clickTime + 0.03);
            }
        } catch (e) {}
    }
}

window.soundEngine = new TypewriterSoundEngine();
