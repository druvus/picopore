"""
    This file is part of Picopore.

    Picopore is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Picopore is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Picopore.  If not, see <http://www.gnu.org/licenses/>.
"""

from multiprocessing import Pool
import os

from parse_args import parseArgs, checkSure
from util import recursiveFindFast5, log, getPrefixedFilename
from compress import compressWrapper, chooseCompressFunc
from test import checkEquivalent

def run(revert, mode, input, y, threads, group, prefix):
	func = chooseCompressFunc(revert, mode)
	fileList = recursiveFindFast5(input)
	preSize = sum([os.stat(f).st_size for f in fileList])
	log("on {} files... ".format(len(fileList)))
	if y or checkSure():
		if threads <= 1:
			for f in fileList:
				compressWrapper([func,f, group, prefix])
		else:
			argList = [[func, f, group, prefix] for f in fileList]
			pool = Pool(threads)
			pool.map(compressWrapper, argList)
		postSize = sum([os.stat(getPrefixedFilename(f, prefix)).st_size for f in fileList])
		if revert:
			preStr, postStr = "Compressed", "Raw"
		else:
			preStr, postStr = "Raw", "Compressed"
		log("Complete.")
		log("{} size: {}".format(preStr, preSize))
		log("{} size: {}".format(postStr, postSize))
		return 0
	else:
		log("User cancelled. Exiting.")
		exit(1)
		
def runTest(args):
	fileList = recursiveFindFast5(args.input)
	run(False, args.mode, args.input, True, args.threads, args.group, args.prefix)
	run(True, args.mode, [getPrefixedFilename(i, args.prefix) for i in args.input], True, args.threads, args.group, None)
	for f in fileList:
		compressedFile = getPrefixedFilename(f, args.prefix)
		checkEquivalent(f, compressedFile)
		os.remove(compressedFile)
	return 0
	
def main():
	args = parseArgs()
	if args.test:
		runTest(args)
	else:
		run(args.revert, args.mode, args.input, args.y, args.threads, args.group, args.prefix)
	return 0

if __name__ == "__main__":
	exit(main())
