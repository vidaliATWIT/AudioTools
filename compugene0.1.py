#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compugene0.1.py
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
from pydub import AudioSegment

def divisible(val):
	
	if (44100%val==0):
		return 44100
	elif (48000%val==0):
		return 48000
	else:
		return 0
		
def getDivisor(master, samplerate):
	return master/samplerate

def main(args):
	
	record=False
	running=True
	length=0
	master_sample_rate=0
	sample_rate=0
	bit_depth=0
	sample_rate_flag=False
	bit_depth_flag=False
	
	while(running):
		#Step #1 Record:
		while(not record):
			while(length<=0):
				length=input("Specify the length of recording in seconds\n")
				if (length.isnumeric()):
					length=int(length)
				else:
					length=0
			while(master_sample_rate!=48000 and master_sample_rate!=44100):
				sample_rate=input("Specify the sample rate for the recording\nMust be divisible by 44100 or 48000\n")
				if (sample_rate.isnumeric()):
					sample_rate=int(sample_rate)
					master_sample_rate = divisible(sample_rate)
				else:
					master_sample_rate=0
					
			while(bit_depth!=8 and bit_depth!=16):
				bit_depth=input("Specify the bit-depth for the recording (8 or 16)\n")
				if (bit_depth.isnumeric()):
					bit_depth=int(bit_depth)
				else:
					bit_depth=0
			##Record Audio
			comp = recorder(master_sample_rate)
			print("Recording for " + str(length) + " seconds at SR of " + str(sample_rate) + " and bit-depth of " + str(bit_depth))
			comp.record(str(length), str(bit_depth), str(getDivisor(master_sample_rate, sample_rate)))
			record=True
			
		##Step #2 Processing and Playback
		audio_seg_name = 'modified.wav'
		proc = processor(master_sample_rate, 'decimated.wav')
		audio_seg = proc.get_audiosegment()
		loop = looper()
			
		while (running):
			#setup audiosegment and recompile into wav
			exporter.export(audio_seg, audio_seg_name)
			command=input("Enter your command: [r]everse [s]peedup [a]mplify [c]ut [p]layback [q]uit [e]xport\n")
			
			if (command=='r'):
				audio_seg=proc.reverse(audio_seg)
			elif (command=='s'):
				multiplier=input("SPEEDUP-> enter rate of speed change from 0->5\n")
				try:
					multiplier = float(multiplier)
					audio_seg = proc.alter_speed(audio_seg, multiplier)
				except:
					print("rate must be a float between 0-5")
			elif (command=='a'):
				db=input("AMPLIFY-> enter value of amplification -inf->inf)\n")
				if (db.isnumeric()):
					audio_seg = proc.amplify(audio_seg, int(db))
			elif (command=='c'):
				command = input("set [s]tart or [e]nd?")
				if (command=='s'):
					start=input("set start time in miliseconds")
					audio_seg = proc.trim(audio_seg, start, proc.get_length())
				elif (command=='e'):
					end=input("set end time in miliseconds")
					audio_seg = proc.trim(audio_seg, 0, end)
			elif (command=='p'):
				print("PLAYBACK\n")
				loop.loop_audio(audio_seg_name, 2)
			elif (command=='e'):
				name=input("EXPORT-> enter name for output file\n")
				name+=".wav"
				exporter.export(audio_seg, name)
			elif (command=='q'):
				print("QUITTING...\n")
				exit(0)
    
class recorder:
	master_rec = None
	processed_rec = None
	recorded = False
	
	CHUNK = int(1024/16)
	FORMAT = pyaudio.paInt16
	CHANNELS = 1 if sys.platform == 'darwin' else 2
	RATE = int(44100) ##Master sample rate
	FILENAME="output.wav"
	master_framerate = 44100
	
	def __init__(self, master_framerate):
		if (master_framerate!=44100):
			self.master_framerate=master_framerate
	
	def record(self, length, bitdepth, decimation):
		self.o_record(length)
		self.recorded=True
		self.master_rec=self.FILENAME
		self.processed_rec="decimated.wav"
		self.decimate(self.processed_rec, bitdepth, decimation)

	##Records a .wav file using registered input at 44.1k
	def o_record(self, length):
		if length.isnumeric():
			length = int(length)
		else:
			length=5
		with wave.open(self.FILENAME, 'wb') as wf:
			p = pyaudio.PyAudio()
			wf.setnchannels(self.CHANNELS)
			wf.setsampwidth(p.get_sample_size(self.FORMAT))
			wf.setframerate(self.RATE)

			stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True)

			print('Recording...')
			for _ in range(0, self.RATE // self.CHUNK * length):
				wf.writeframes(stream.read(self.CHUNK))
			print('Done')
		

			stream.close()
			p.terminate()

	#Creates new file that with sample rate reduced by given factor (df) and with selected bit-depth (bd)   
	def decimate(self, filename, bd, df):	
		##Get up filepath where sox.exe is
		FilePath=r"C:\Users\vidali\Desktop\AudioTools\sox-14-4-2"
		
		print(filename)
		print(bd)
		print(df)
		
		##Run sox.exe at verbose level 1 (-V1) only errors will be outputted to std-out	
		subprocess.call(['sox.exe', '-V1', self.FILENAME, '-b', bd, filename, 'downsample', df], stdout=subprocess.PIPE)
		return 0
	
	def has_recorded(self):
		return self.recorded
	
class processor:
	fwd = True
	speed = 1.0
	master_framerate = 44100
	audio = "None"
	
	def __init__(self, master_framerate, filename):
		if (master_framerate!=44100):
			self.master_framerate=master_framerate	
		audio = AudioSegment.from_wav(filename)
		self.audio=audio
	
	def alter_speed(self, audio, mult):
		octaves = 0.5
		#This variable changes the speed-> 1 is normal, 2 is twice as fast, .5 is half speed
		speed_control = float(mult)
		
		new_sample_rate = int(audio.frame_rate * (speed_control ** octaves))
		
		pitched_sound=audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
		
		pitched_sound = pitched_sound.set_frame_rate(self.master_framerate)
		self.audio=pitched_sound
		return pitched_sound

	def reverse(self, audio):
		audio = audio.reverse()
		self.fwd = not self.fwd
		return audio
		
	def trim(self, audio, startT, endT):
		# pydub does things in miliseconds
		startT=int(startT)
		endT=int(endT)
		
		start=max(0, startT)
		end=min(len(self.audio), endT)
		
		start=min(start, end-1)
		end=max(start+1, end)
		
		audio = audio [start:end]
		self.audio=audio
		return audio
	
	##gets length of audiosegment in milliseconds
	def get_length(self):
		return len(self.audio)
	

	def amplify(self, audio, amp):
		amp=int(amp)
		audio+=amp
		self.audio=audio
		return audio
	
	def get_audiosegment(self):
		return self.audio
	
	def is_fwd(self):
		return self.fwd

class exporter:
	def export(audio_seg, filename):
		audio_seg.export(filename, format="wav")

class looper:
	
	def __init__(self):
		return
		
	def play_audio(self, wf, p, stream):
		CHUNK = 1024
		while len(data := wf.readframes(CHUNK)):  # Requires Python 	3.8+ for :=
			stream.write(data)

	def loop_audio(self, filename, repeats):
		with wave.open(filename, 'rb') as wf:
			p = pyaudio.PyAudio()
			stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
							channels=wf.getnchannels(),
							rate=wf.getframerate(),
							output=True)
					
			repeats = int(repeats)
			
			while repeats>0:
				self.play_audio(wf, p, stream)
				wf = wave.open(filename, 'rb')
				repeats-=1
				
			stream.close()
			p.terminate()
	
	def loop_until_flag(self, filename, flag):
		with wave.open(filename, 'rb') as wf:
			p = pyaudio.PyAudio()
			stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
							channels=wf.getnchannels(),
							rate=wf.getframerate(),
							output=True)
					
			repeats = int(repeats)
			
			while repeats>flag:
				self.play_audio(wf, p, stream)
				wf = wave.open(filename, 'rb')
				repeats-=1
				
			stream.close()
			p.terminate()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
