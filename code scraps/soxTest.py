#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  soxCallbackTest.py
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
import subprocess

def main(args):
	
	##Obligatory check for correct number of arguments
	if len(args)!=7: 
		print("USAGE: py ./soxTest.py bit-depth decimation")
		return
	
	
	##Get up filepath where sox.exe is
	FilePath=r"C:\Users\vidali\Desktop\AudioTools\sox-14-4-2"
	
	##Run sox.exe at verbose level 1 (-V1) only errors will be outputted to std-out	
	subprocess.call(['sox.exe', '-V1', args[1], args[2], args[3], args[4], args[5], args[6]], stdout=subprocess.PIPE)
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
