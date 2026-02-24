
import wave
import math
import struct
import os

def generate_tone(filename, frequency=440.0, duration=2.0, volume=0.5):
    sample_rate = 44100
    n_frames = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as obj:
        obj.setnchannels(1) # Mono
        obj.setsampwidth(2) # 2 bytes (16 bit) per sample
        obj.setframerate(sample_rate)
        
        data = []
        for i in range(n_frames):
            t = float(i) / sample_rate
            value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
            data.append(struct.pack('<h', value))
            
        obj.writeframes(b''.join(data))
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "assets", "music")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    generate_tone(os.path.join(out_dir, "test_tone_440.wav"), 440, 2.0)
    generate_tone(os.path.join(out_dir, "alert_tone.wav"), 880, 0.5)
    generate_tone(os.path.join(out_dir, "low_hum.wav"), 120, 5.0)
