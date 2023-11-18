#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compugene.py
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


def main(args):
	
	#NOTE: The constructors for recorder and processor both require we establish a MASTER sample rate. Either 44100 or 48000. Both classes refer to this master sample rate when performing certain calculations, hence we need to keep them consistent
	
	##Record Audio
	#1) Instantiate a recorder object with the master sample rate
	#comp = recorder(44100)
	
	#2) Record-> args are: length, bit-depth and decimation factor
	#comp.record('5', '16', '4')
	
	#3) Getter for whether you have a recording or not
	#comp.has_recorded()
	
	##Process audio:
	 
	##1) convert recorded wav into an audiosegment
	audio_seg_name = 'modified.wav'
	
	##2) Instantiate a processor object with master sample rate, and filename of your recording (decimated.wav is post decimation recording)
	proc = processor(44100, 'decimated.wav')
	##3) Retrieve the audiosegment version of your recording
	audio_seg = proc.get_audiosegment()
	##4) Use that audiosegment as the argument for calls to processor's processing functions
	audio_seg = proc.reverse(audio_seg)
	audio_seg = proc.amplify(audio_seg, 6)
	audio_seg = proc.repitch(audio_seg, .5)
	
	##5) Getter for wheter recording is forward or backwards
	proc.is_fwd()
	
	#Export audio segment
	#1) Exporter can only export audiosegments, hence you call it with the audio_segment, and the name of the output file
	exporter.export(audio_seg, audio_seg_name)
	
	#Loop Audio Segment
	#1) Instantiate a looper object
	loop = looper()
	#2) Call the loop_audio function passing the name of the file you want to loop, and the number of loops
	loop.loop_audio(audio_seg_name, 2)
	
	#3) Loop_until_flag will probably be the one we used in the final version, having flag be something you set with start and stop
	#loop.loop_until_flag(audio_seg_name, flag)
	return 0


	
    
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
		print("processor initialized")
		print(master_framerate)
		print(filename)
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
		
		pitched_sound = pitched_sound.set_frame_rate(master_framerate)
		self.audio=pitched_sound
		return pitched_sound

	def reverse(self, audio):
		audio = audio.reverse()
		self.fwd = not self.fwd
		return audio
		
	def trim(self, audio, start, end):
		# pydub does things in miliseconds
		start=int(float(start) * 1000)
		end=int(float(end) * 1000)

		audio = audio [start:end]
		self.audio=audio
		return audio

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
