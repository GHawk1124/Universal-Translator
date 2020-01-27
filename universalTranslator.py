"""Universal Translator.

Usage:
  universalTranslator.py (-h | --help)
  universalTranslator.py --version
  universalTranslator.py [-rc | --record] [-u | --upload] [-rg | --recognize] [-t | --translate] [-s | --say] [--config] [--noise-reduce] 
  universalTranslator.py (-a | -all) [-u | --upload]
  universalTranslator.py (--no-rec)
  
Options:
  -h --help              Show this screen.
  --version              Show version.
  -rc --record           Record the audio again.
  -u --upload            Upload File to Google Storage.
  -rg --recognize        Recognize Audio Speech.
  -t --translate         Translate the Transcript.
  -s --say               Say the Transcript.
  -a --all               Record, Recognize, Translate, and Say.
  --no-rec               Recognize, Translate, and Say.
  --config               Record a Sample for Noise Reduction.
  --noise-reduce         Reduce Noise in the Audio.
  
"""
from docopt import docopt
from utUtils import *

if __name__ == '__main__':
    arguments = docopt(__doc__, version='universalTranslator v0.0.1')
    rec = False
    upl = False
    if arguments['--all']:
        rec = True
        if arguments['--upload']:
            upl = True
        Main(rec, upl)
        sys.exit()
    if arguments['--config']: config()
    if arguments['--no-rec']:
        rec = False
        Main(rec, upl)
        sys.exit()
    if arguments['--record']: record(RecordOptions)
    if arguments['--upload']: upload(RecordOptions['Filename'])
    if arguments['--noise-reduce']: noiseCancel(NO_NOISE)
    if arguments['--recognize']:
        text = recognize(RecordOptions['Filename'])
        if arguments['--translate']:
            translation = translate(text, NATIVE_LANGUAGE)
            if arguments['--say']: say(translation)
