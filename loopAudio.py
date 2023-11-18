#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  loopAudio.py
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

import pyaudio
import wave
import sys

def main(args):
	if len(args)!=3:
		print("USAGE: py loopAudio.py filename repeats")
	else:
		loop_audio(args[1], args[2])
	return 0
    

def play_audio(wf, p, stream):
	CHUNK = 1024
	while len(data := wf.readframes(CHUNK)):  # Requires Python 	3.8+ for :=
		stream.write(data)

def loop_audio(filename, repeats):

	with wave.open(filename, 'rb') as wf:
		p = pyaudio.PyAudio()
		stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
						channels=wf.getnchannels(),
						rate=wf.getframerate(),
						output=True)
				
		repeats = int(repeats)
		
		while repeats>0:
			play_audio(wf, p, stream)
			wf = wave.open(filename, 'rb')
			repeats-=1
			
		stream.close()
		p.terminate()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
