#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ProcessAudio.py
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
from pydub import AudioSegment
import pyaudio

def main(args):
	output = ''
	if len(args)>8 or len(args)<3:
		print("USAGE: py processAudio.py filename [r]everse [s#]peed [t##]rim ")
	else:
		filename = args[1]
		audio = AudioSegment.from_wav(args[1])
		if args[2]=='r':
			output = reverse(audio)
			filename = "RV" + filename
		elif args[2]=='s':
			output = repitch(audio, args[3])
			filename = "RP" + filename
		elif args[2]=='t':
			output = trim(audio, args[3], args[4])
			filename = "TR" + filename
		elif args[2]=='a':
			output = amplify(audio, args[3])
			filename = "AM" + filename
		else:
			print("No processing specified")
			return 0
		output.export(filename, format="wav")
	return 0
	
	
    
   
def repitch(audio, mult):
	octaves = 0.5
	#This variable changes the speed-> 1 is normal, 2 is twice as fast, .5 is half speed
	speed_control = float(mult)
	
	new_sample_rate = int(audio.frame_rate * (speed_control ** octaves))
	
	pitched_sound=audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
	
	pitched_sound = pitched_sound.set_frame_rate(48000)
	return pitched_sound

def reverse(audio):
	audio = audio.reverse()
	return audio
	
def trim(audio, start, end):
	# pydub does things in miliseconds
	start=int(float(start) * 1000)
	end=int(float(end) * 1000)

	audio = audio [start:end]
	return audio

def amplify(audio, amp):
	amp=int(amp)
	audio+=amp
	return audio



if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
