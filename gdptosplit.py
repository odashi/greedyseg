# coding: utf-8

import sys

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread

def loadmodel(fname, mu):
	fid = {}

	with open(fname, encoding='utf-8') as fp:
		# information
		num_sents = int(next(fp).split()[1])
		num_words = int(next(fp).split()[1])
		num_fids = int(next(fp).split()[1])

		# feature-ID table
		for i in range(num_fids):
			ls = next(fp).split()
			fid[ls[1]] = ls[0]

		# model
		num_segs = max(0, int(num_words/mu) - num_sents)
		for i in range(num_segs-1):
			next(fp)
		features = [x.split('_') for x in next(fp).split()[1:]]
		features = [(fid[x[0]], fid[x[1]]) for x in features]

	return features

def main():
	if len(sys.argv) != 5:
		print('USAGE: python3 gdptosplit.py')
		print('                 <[1] in-file: GreedyDP model>')
		print('                 <[2] in-file: input corpus with POS>')
		print('                 <[3] out-file: splitter table>')
		print('                 <[4] float: mean of #words>')
		return
	
	fname_model = sys.argv[1]
	fname_in = sys.argv[2]
	fname_sp = sys.argv[3]
	mu = float(sys.argv[4])
	
	try:
		model = loadmodel(fname_model, mu)
	except Exception as ex:
		sys.stderr.write('ERROR: mu is too small %s' % ex)
		return 1
	
	print(model)

	corpus_in = [[tuple(x.split('_')) for x in inp] for inp in dlmread(fname_in, ' ')]
	
	with open(fname_sp, 'w', encoding='utf-8') as fp:
		for i, inp in enumerate(corpus_in):
			for j in range(len(inp)-1):
				if (inp[j][1], inp[j+1][1]) in model:
					fp.write('%d %d\n' % (i, j))


if __name__ == '__main__':
	main()

