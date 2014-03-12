# coding: utf-8

import sys
from collections import defaultdict

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread

def addfeature(fs, fid, name, mode):
	if mode == 'dev' or name in fid:
		fs.append(fid[name])

def main():
	if len(sys.argv) != 6:
		print('USAGE: python3 makeliblin_greedy.py \\')
		print('               <str: mode ("dev" or "test")>')
		print('               <in-file: input sentence with POS> \\')
		print('               <in-file: splitter table> \\')
		print('               <(dev)out-file, (test)in-file: feature ID table> \\')
		print('               <out-file: LIBLINEAR input data>')
		return

	mode = sys.argv[1]
	fname_pos = sys.argv[2]
	fname_splitter = sys.argv[3]
	fname_fid = sys.argv[4]
	fname_liblin = sys.argv[5]

	if mode not in ['dev', 'test']:
		sys.stderr.write('ERROR: unknown mode.\n')
		return

	# load word and pos
	corpus_in_pos = [x for x in dlmread(fname_pos, ' ')]
	for i in range(len(corpus_in_pos)):
		corpus_in_pos[i] = [w.split('_') for w in corpus_in_pos[i]]

	# load splitter
	tab_sp = defaultdict(lambda: [])
	with open(fname_splitter, 'r', encoding='utf-8') as fp:
		for l in fp:
			lineno, wordno = tuple(int(x) for x in l.strip().split(' '))
			tab_sp[lineno].append(wordno)

	# load or new feature id table
	fid = defaultdict(lambda: len(fid)+1)
	if mode == 'test':
		with open(fname_fid, 'r', encoding='utf-8') as fp:
			for l in fp:
				ls = l.split()
				k = ls[0]
				v = int(ls[1])
				fid[k] = v

	# make/save training data
	n = 0
	with open(fname_liblin, 'w', encoding='utf-8') as fp:
		for i in range(len(corpus_in_pos)):
			data = [['<s>', '<s>']] * 2 + corpus_in_pos[i] + [['</s>', '</s>']] * 2
			for j in range(len(data)-5): # ignore end of sentence
				jj = j+2
				features = []

				# unigram words
#				addfeature(features, fid, 'WORD[-2]=%s' % data[jj-2][0], mode)
				addfeature(features, fid, 'WORD[-1]=%s' % data[jj-1][0], mode)
				addfeature(features, fid, 'WORD[0]=%s' % data[jj+0][0], mode)
				addfeature(features, fid, 'WORD[+1]=%s' % data[jj+1][0], mode)
				addfeature(features, fid, 'WORD[+2]=%s' % data[jj+2][0], mode)
				# unigram POSes
#				addfeature(features, fid, 'POS[-2]=%s' % data[jj-2][1], mode)
				addfeature(features, fid, 'POS[-1]=%s' % data[jj-1][1], mode)
				addfeature(features, fid, 'POS[0]=%s' % data[jj+0][1], mode)
				addfeature(features, fid, 'POS[+1]=%s' % data[jj+1][1], mode)
				addfeature(features, fid, 'POS[+2]=%s' % data[jj+2][1], mode)
				# bigram words
#				addfeature(features, fid, 'WORD[-2:-1]=%s_%s' % (data[jj-2][0], data[jj-1][0]), mode)
				addfeature(features, fid, 'WORD[-1:0]=%s_%s' % (data[jj-1][0], data[jj+0][0]), mode)
				addfeature(features, fid, 'WORD[0:+1]=%s_%s' % (data[jj+0][0], data[jj+1][0]), mode)
				addfeature(features, fid, 'WORD[+1:+2]=%s_%s' % (data[jj+1][0], data[jj+2][0]), mode)
				# bigram POSes
#				addfeature(features, fid, 'POS[-2:-1]=%s_%s' % (data[jj-2][1], data[jj-1][1]), mode)
				addfeature(features, fid, 'POS[-1:0]=%s_%s' % (data[jj-1][1], data[jj+0][1]), mode)
				addfeature(features, fid, 'POS[0:+1]=%s_%s' % (data[jj+0][1], data[jj+1][1]), mode)
				addfeature(features, fid, 'POS[+1:+2]=%s_%s' % (data[jj+1][1], data[jj+2][1]), mode)
				# trigram words
#				addfeature(features, fid, 'WORD[-2:0]=%s_%s_%s' % (data[jj-2][0], data[jj-1][0], data[jj+0][0]), mode)
				addfeature(features, fid, 'WORD[-1:+1]=%s_%s_%s' % (data[jj-1][0], data[jj+0][0], data[jj+1][0]), mode)
				addfeature(features, fid, 'WORD[0:+2]=%s_%s_%s' % (data[jj+0][0], data[jj+1][0], data[jj+2][0]), mode)
				# trigram POSes
#				addfeature(features, fid, 'POS[-2:0]=%s_%s_%s' % (data[jj-2][1], data[jj-1][1], data[jj+0][1]), mode)
				addfeature(features, fid, 'POS[-1:+1]=%s_%s_%s' % (data[jj-1][1], data[jj+0][1], data[jj+1][1]), mode)
				addfeature(features, fid, 'POS[0:+2]=%s_%s_%s' % (data[jj+0][1], data[jj+1][1], data[jj+2][1]), mode)
				
				line = '1 ' if j in tab_sp[i] else '2 '
				
				line += ' '.join('%d:1'%f for f in sorted(features))
				fp.write(line+'\n')
				n += 1
	
	# save feature id table
	if mode == 'dev':
		with open(fname_fid, 'w', encoding='utf-8') as fp:
			for k, v in fid.items():
				fp.write('%s\t%d\n' % (k, v))


if __name__ == '__main__':
	main()

