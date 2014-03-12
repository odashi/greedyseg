# coding: utf-8

import sys
import codecs

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread

def main():

	if len(sys.argv) != 4:
		print('USAGE: python3 predicttosplit.py \\')
		print('               <in-file: LIBLINEAR prediction> \\')
		print('               <in-file: input corpus> \\')
		print('               <out-file: splitter table>')
		return

	fname_predict = sys.argv[1]
	fname_in = sys.argv[2]
	fname_splitter = sys.argv[3]

	corpus_in = [x for x in dlmread(fname_in, ' ')]

	with \
		codecs.open(fname_predict, 'r', 'utf-8') as fp_pred, \
		codecs.open(fname_splitter, 'w', 'utf-8') as fp_sp:
		line = 0
		pos = 0
		for i, l in enumerate(fp_pred):
			while not corpus_in[line] or pos == len(corpus_in[line])-1:
				line += 1
				pos = 0
			status = int(l.strip())
			if status == 1:
				fp_sp.write('%d %d\n' % (line, pos))
			pos += 1

if __name__ == '__main__':
	main()

