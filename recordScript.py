#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  recordScript.py
#  
#  Copyright 2023 vidali <>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import wave
import sys
import pyaudio
import subprocess

'''
This script records a .wav file of a provided length using the currently registered audio input.
Afterwards it applies a decimation process to chop the sample rate and bit depth. 
'''

CHUNK = int(1024/16)
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == 'darwin' else 2
RATE = int(44100)
RECORD_SECONDS = 5
FILENAME='output.wav'

##Records a .wav file using registered input at 44.1k
def record(length):
	if length.isnumeric():
		length = int(length)
	else:
		length=RECORD_SECONDS
	with wave.open(FILENAME, 'wb') as wf:
		p = pyaudio.PyAudio()
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(p.get_sample_size(FORMAT))
		wf.setframerate(RATE)

		stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

		print('Recording...')
		for _ in range(0, RATE // CHUNK * length):
			wf.writeframes(stream.read(CHUNK))
		print('Done')
    

		stream.close()
		p.terminate()

#Creates new file that with sample rate reduced by given factor (df) and with selected bit-depth (bd)   
def decimate(filename, bd, df):	
	##Get up filepath where sox.exe is
	FilePath=r"C:\Users\vidali\Desktop\AudioTools\sox-14-4-2"
	
	##Run sox.exe at verbose level 1 (-V1) only errors will be outputted to std-out	
	subprocess.call(['sox.exe', '-V1', FILENAME, '-b', bd, filename, 'downsample', df], stdout=subprocess.PIPE)
	return 0

##Basic case to test functions without arguments
def test_case():
	record('5')
	decimate('newfile.wav', '8', '12')

def main(args):
	
	if len(args)!=5:
		print("USAGE: py recordScript.py filename time bit-depth decimation-factor")
	else:
		record(args[2])
		decimate(args[1], args[3], args[4])
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
