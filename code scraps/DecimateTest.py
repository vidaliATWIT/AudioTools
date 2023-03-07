#!/usr/bin/env python
import librosa
import soundfile as sf
from scipy.io.wavfile import read, write
import sox

##have to install samplerate and soxr

def main(args):
	
	file1='loop2.wav'
	filename = 'decimateloop.wav'
	'''
	sr = 2000 #samplerate
	y, s = librosa.load(file1, 44100)
	librosa.resample=resampo
	
	y_8k = librosa.resample(y, orig_sr=44100, target_sr=sr, res_type='zero_order_hold')
	print("DECIMATED")'''
	
	#open audio
	
	tfm = sox.Transformer()
	tfm.downsample(5)
	tfm.build_file(file1, filename)
	

	#rate, data = read('loop2.wav')
	#write('decimateloop2.wav', int(rate/12), data[::n])
	
	##sf.write(filename, y_8k, sr)
	return 0
	


if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
