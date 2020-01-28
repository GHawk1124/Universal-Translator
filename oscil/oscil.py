import numpy as np
import cv2
import soundcard as sc
import time

class Oscil():
    def __init__(self, imWidth, imHeight, microphone, screen, xs):
        self.width = imWidth
        self.height = imHeight
        self.mic = microphone
        self.screen = screen
        self.xs = xs
        self.stop = False
        self.noiseConf = 3
        self.noise = None

    def draw_wave(self, screen, mono_audio, xs, title="oscilloscope", gain=5):
        screen *= 0
        ys = self.height / 2 * (1 - np.clip(gain * mono_audio[0:len(xs)], -1, 1))
        pts = np.array(list(zip(xs, ys))).astype(np.int)
        cv2.polylines(screen, [pts], False, (0, 255, 0))
        cv2.imshow(title, screen)

    def run(self):
        while not self.stop:
            with self.mic.recorder(samplerate=44100) as mic:
                audio_data = mic.record(numframes=1024)
            self.draw_wave(self.screen, audio_data[:,0], xs)
            key = cv2.waitKey(1) & 0xFF
            if ord('q') == key:
                stop = True
    
    def stop(self):
        self.stop = True

def setupOscil():
    global imWidth = 1024
    global imHeight = 512
    global default_mic = sc.default_microphone()
    global screen = np.zeros((imHeight,imWidth,3), dtype=np.uint8)
    global xs = np.arange(imWidth).astype(np.int)

if __name__ == '__main__':
    oscil = Oscil(imWidth, imHeight, default_mic, screen, xs)
    oscil.run()
