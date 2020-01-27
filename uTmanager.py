from google.cloud import speech_v1p1beta1
from googletrans import Translator
import wave
import pyaudio
import pyttsx3
import io
import os
import sys
import soundfile as sf
import noisereduce as nr
import webrtcvad
import threading
import time
from utUtils import config, recognize, translate, say, RecordOptions

RATE = 16000

class audioManager:
    def __init__(self, recOps):
        self.running = False
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=recOps['Format'], 
                            channels=recOps['Channels'], 
                            rate=recOps['Rate'], 
                            input=True, 
                            frames_per_buffer=recOps['Chunk'])
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(1)
        self.recording = False
        self.audioPercent = 100
        self.recOps = recOps
        self.check = False
        self.pastFrames = []

    def start(self):
        self.running = True
        self.run()

    def stop(self):
        self.running = False

    def checkAudio(self):
        count = 0
        for f in self.pastFrames:
            count += int(f)
        if count >= self.audioPercent:
            time.sleep(1)
            self.check = True

    def run(self):
        print("Audio Manager Running")
        frames = []
        while self.running:
            threading.Thread(target=self.checkAudio).start()
            frame = self.stream.read(2) * int(RATE * 10 / 1000)
            self.recording = self.vad.is_speech(frame, RATE)
            startRecord = self.recording
            self.pastFrames.append(self.recording)
            count = 0
            for f in self.pastFrames:
                count += int(f)
            if len(self.pastFrames) == 100:
                if count >= self.audioPercent:
                    data = self.stream.read(CHUNK)
                    frames.append(data)
                elif count == 0 and self.check:
                    waveFile = wave.open(self.recOps['Filename'], 'wb')
                    waveFile.setnchannels(self.recOps['Channels'])
                    waveFile.setsampwidth(self.audio.get_sample_size(self.recOps['Format']))
                    waveFile.setframerate(self.recOps['Rate'])
                    waveFile.writeframes(b''.join(frames))
                    waveFile.close()
                    frames = []
                    r_text = recognize(self.recOps['Filename'])
                    translation = translate(r_text, NATIVE_LANGUAGE)
                    say(translation)
                    self.check = False
            if len(self.pastFrames) == 100:
                self.pastFrames.pop(0)
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

if __name__ == '__main__':
    config()
    am = audioManager(RecordOptions)
    am.start()
