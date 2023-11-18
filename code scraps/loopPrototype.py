#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  loopPrototype.py
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

##actual looping prototype

import pyaudio
import wave
import sys
import threading
def play_audio():
	CHUNK = 1024
	
	with wave.open("Parmesan.wav", 'rb') as wf:
		# Instantiate PyAudio and initialize PortAudio system resources (1)
		p = pyaudio.PyAudio()
	
		# Open stream (2)
		stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
						channels=wf.getnchannels(),
						rate=wf.getframerate(),
						output=True)

		# Play samples from the wave file (3)
		while len(data := wf.readframes(CHUNK)):  # Requires Python 	3.8+ for :=
			stream.write(data)

	
		# Close stream (4)
		stream.close()

		# Release PortAudio system resources (5)
		p.terminate()
    
def loop_audio():
	while is_playing:
		play_audio()

global is_playing
global my_thread
is_playing=False
if not is_playing:
        is_playing = True
        my_thread = threading.Thread(target=loop_audio)
        my_thread.start()


