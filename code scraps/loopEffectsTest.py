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
from pydub import AudioSegment, playback
from pydub.playback import play
import pyaudio

def main(args):
	##Load audio file
	song = AudioSegment.from_wav("Pad 1.wav")

	##Set start point
	'''
	# pydub does things in miliseconds
	ten_seconds = 10 * 1000

	first_10_seconds = song[:10000]

	last_5_seconds = song[-5000:
	'''
	
	##Splice Audio
	#song = song[2100:2150]
	
	##Add 6 dbs of volume
	'''
	song+=6
	'''
	
	##Reverse audio
	
	song = song.reverse()
	
	##Change pitch
	sound=song
	octaves = 0.5
	
	#This variable changes the speed-> 1 is normal, 2 is twice as fast, .5 is half speed
	speed_control = 5
	
	new_sample_rate = int(sound.frame_rate * (speed_control ** octaves))
	
	hipitch_sound=sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
	
	hipitch_sound = hipitch_sound.set_frame_rate(48000)
	hipitch_sound += 20
	

	
	i = 3
	while(i>0):
		playback._play_with_pyaudio(hipitch_sound)
		i-=1
		

	
	
	
if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
