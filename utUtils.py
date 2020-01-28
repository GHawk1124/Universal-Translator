#import speech_recognition as sr
#from google.cloud import speech
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

version = "0.0.1"

NATIVE_LANGUAGE = "en"

# Constants
AUTHPATH = "/Users/garrett/universalTranslator/credentials.json"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
REC_SECONDS = 5
FILENAME = "voice.wav"
NOISE = "noise.wav"
NO_NOISE = "voiceNN.wav"
RecordOptions = {'Format': FORMAT, 'Channels': CHANNELS,
                 'Rate': RATE, 'Chunk': CHUNK,
                 'RecSeconds': REC_SECONDS,
                 'Filename': FILENAME}

def record(recOps, verbose=True):
    if verbose: print("Recording...")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=recOps['Format'],
                    channels=recOps['Channels'], 
                    rate=recOps['Rate'], input=True, 
                    frames_per_buffer=recOps['Chunk'])
    frames = []
    for i in range(0, int(recOps['Rate'] / recOps['Chunk'] * recOps['RecSeconds'])):
        data = stream.read(CHUNK)
        frames.append(data)
    if verbose: print("Finished Recording")
    if verbose: print("Writing to file...")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    waveFile = wave.open(recOps['Filename'], 'wb')
    waveFile.setnchannels(recOps['Channels'])
    waveFile.setsampwidth(audio.get_sample_size(recOps['Format']))
    waveFile.setframerate(recOps['Rate'])
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    if verbose: print("Finished Writing")

def config():
    conf = RecordOptions.copy()
    conf['RecSeconds'] = 1
    conf['Filename'] = NOISE
    print("Configuring Noise Cancellation (Don't Speak)")
    record(conf, False)
    print("Configured Noise Cancellation")
    peopleSpeaking = int(input("Type the number of people that will be speaking in this session: "))
    people = []
    conf['RecSeconds'] = 5
    for i in range(peopleSpeaking):
        people.append([input("Type your name: ")])
        people[i].append(input("Type your native language"))
        conf['Filename'] = people[i][0] + ".wav"
        print("Configuring your voice, after the sign, speak slow and clearly the following phrase: ")
        print("This is a test. The quick brown fox jumped over the lazy dog.")
        time.sleep(1)
        print("Speak")
        record(conf, False)
        print(people[i][0] + " Configured")
    return people

def noiseCancel(wfile, recOps):
    audio = pyaudio.PyAudio()
    vdata, vrate = sf.read(open(FILENAME, 'rb'))
    ndata, nrate = sf.read(open(NOISE, 'rb'))
    reduced_noise = nr.reduce_noise(audio_clip=vdata, noise_clip=ndata)
    audio.terminate()
    waveFile = wave.open(wfile, 'wb')
    waveFile.setnchannels(recOps['Channels'])
    waveFile.setsampwidth(audio.get_sample_size(recOps['Format']))
    waveFile.setframerate(recOps['Rate'])
    waveFile.writeframes(b''.join(reduced_noise))
    waveFile.close()

def upload(wfile):
    from googleapiclient import discovery
    from oauth2client.client import GoogleCredentials
    print("Uploading File to Google Storage...")
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('storage', 'v1', credentials=credentials)
    filename = './' + wfile
    bucket = 'uv-trans'
    gsPath = 'audio/' + wfile
    body = {'name': gsPath}
    req = service.objects().insert(bucket=bucket, body=body, media_body=filename)
    resp = req.execute()
    print("Finished Uploading")

def recognize(wfile):
    print("Recognizing Speech...")
    audioFile = './' + wfile
    client = speech_v1p1beta1.SpeechClient()
    primary_lang = "es"
    alternate_langs = ["zh", "fr", "en"]
    config = {
        "language_code": primary_lang,
        "alternative_language_codes": alternate_langs,
    }
    with io.open(audioFile, "rb") as f:
        content = f.read()
    audio = {"content": content}
    response = client.recognize(config, audio)
    if 'result' in str(response):
        print("Speech Recognized")
        print(f"Detected language: {response.results[0].language_code}")
        print(f"Transcript: {response.results[0].alternatives[0].transcript}")
        return response.results[0].alternatives[0].transcript
    else:
        print("Failed to Recognize Audio")
        sys.exit()

def translate(text, lang):
    print("Translating...")
    translator = Translator()
    translation = translator.translate(text, dest=lang)
    print("Finished Translating")
    print(f'Result: \"{translation.text}\"')
    return translation.text

def say(text):
    print("Saying Text...")
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()
    print("Finished Saying")

def authenticate():
    print("Authenticating Credentials...")
    try:
        os.system("export GOOGLE_APPLICATION_CREDENTIALS=\"{AUTHPATH}\"")
        print("Authentication Successful")
    except:
        print("Failed to Authenticate")
        sys.exit()

def Main(p_rec, p_upl):
    authenticate()
    config()
    print("Starting Translation")
    if p_rec == True: record(RecordOptions)
    if p_upl == True: upload(RecordOptions['Filename'])
    noiseCancel(NO_NOISE, RecordOptions)
    r_text = recognize(NO_NOISE)
    translation = translate(r_text, NATIVE_LANGUAGE)
    say(translation)
    print("Translation Complete")

if __name__ == '__main__':
    print(f'Universal Translator v{version}')
