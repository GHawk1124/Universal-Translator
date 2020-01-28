from google.cloud import speech_v1p1beta1
from googletrans import Translator
import wave
import pyaudio
import pyttsx3
import io
import os
import sys
import soundfile as sf
import sounddevice as sd
import noisereduce as nr
import webrtcvad
import resemblyzer
import threading
import time
import numpy as np
import librosa
import sys
from pathlib import Path
from utUtils import config, recognize, translate, say, authenticate, RecordOptions
from Real-Time-Voice-Cloning.encoder.params_model import model_embedding_size as speaker_embedding_size
from Real-Time-Voice-Cloning.utils.argutils import print_args
from Real-Time-Voice-Cloning.synthesizer.inference import Synthesizer
from Real-Time-Voice-Cloning.encoder import inference as encoder
from Real-Time-Voice-Cloning.vocoder import inference as vocoder
#from Oscil import Oscil, setupOscil

RATE = 16000

class audioManager:
    def __init__(self, recOps, people):
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
        self.lock = threading.Lock()
        self.people = people
        encoder.load_model("encoder/saved_models/pretrained.pt")
        synthesizer = Synthesizer("synthesizer/saved_models/logs-pretrained/".joinpath("taco_pretrained"), low_mem=args.low_mem)
        vocoder.load_model("vocoder/saved_models/pretrained/pretrained.pt")
    
    def start(self):
        self.running = True
        self.run()

    def stop(self):
        self.running = False

    def checkAudio(self):
        count = 0
        self.lock.acquire()
        try:
            for f in self.pastFrames:
           	    count += int(f)
        finally:
            self.lock.release()
        if count >= self.audioPercent:
            time.sleep(1)
            self.check = True

    def clone(self):
        embed = []
        for i in range(len(self.people))
            in_fpath = Path(self.people[i][0].replace("\"", "").replace("\'", ""))
            preprocessed_wav = encoder.preprocess_wav(in_fpath)
            print(self.people[i][0] + " embedding successfull")
            embed.append(encoder.embed_utterance(preprocessed_wav))
            print("Created the embedding")
        return embed


    def run(self):
        print("Audio Manager Running")
        embeds = self.clone()
        frames = []
        while self.running:
            threading.Thread(target=self.checkAudio).start()
            try:
                frame = self.stream.read(2) * int(RATE * 10 / 1000)
            except OSError as e:
                raise
                frame = b'\x00\x00'
            self.recording = self.vad.is_speech(frame, RATE)
            startRecord = self.recording
            self.lock.acquire()
            try:
                self.pastFrames.append(self.recording)
            finally:
                self.lock.release()
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
                    #say(translation)
                    self.check = False
            if len(self.pastFrames) == 100:
                self.pastFrames.pop(0)
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

if __name__ == '__main__':
    configuration = config()
    am = audioManager(RecordOptions, configuration)
    am.start()
