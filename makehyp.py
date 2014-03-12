# coding: utf-8

import sys
import codecs
import math
from collections import defaultdict

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread

def load(fnames):
	print('--------')
	print('loading data ...')
	corpus_in = [x for x in dlmread(fnames['IN'], ' ')]
	
	tab_pid_pmt = {}
	with \
		codecs.open(fnames['PID'], 'r', 'utf-8') as fp_pid, \
		codecs.open(fnames['PMT'], 'r', 'utf-8') as fp_pmt:
		for lid, lmt in zip(fp_pid, fp_pmt):
			key = tuple(int(x) for x in lid.strip().split(' '))
			val = lmt.strip().split(' ')
			tab_pid_pmt[key] = val

	tab_sp = defaultdict(lambda: [])
	with codecs.open(fnames['SP'], 'r', 'utf-8') as fp:
		for l in fp:
			lineno, wordno = tuple(int(x) for x in l.strip().split(' '))
			tab_sp[lineno].append(wordno)
	
	print('  # of input sentence     : %d' % len(corpus_in))
	print('  # of part id-mt table   : %d' % len(tab_pid_pmt))
	print('  # of splitting table    : %d' % sum(len(x) for x in tab_sp.values()))
	return corpus_in, tab_pid_pmt, tab_sp


def makehyp(corpus_in, tab_pid_pmt, tab_sp):
	print('--------')
	print('making hypotheses ...')
	parts_inp = []
	parts_hyp = []
	num_part = 0
	moment1 = 0
	moment2 = 0
	for i, s_in in enumerate(corpus_in):
		inp = []
		hyp = []
		begin = 0
		len_in = len(s_in)
		if len_in > 0:
			for sp in sorted(tab_sp[i]):
				part = tab_pid_pmt[i, begin, sp]
				len_part = sp - begin + 1
				num_part += 1
				moment1 += len_part
				moment2 += len_part*len_part
				inp.append(s_in[begin:sp+1])
				hyp.append(part)
				begin = sp+1
			if begin < len_in:
				part = tab_pid_pmt[i, begin, len_in-1]
				len_part = len_in - begin
				num_part += 1
				moment1 += len_part
				moment2 += len_part*len_part
				inp.append(s_in[begin:len_in])
				hyp.append(part)
		parts_inp.append(inp)
		parts_hyp.append(hyp)

	moment1 /= num_part
	moment2 /= num_part
	sd = math.sqrt(moment2 - moment1*moment1)
	print('  number of parts : %d' % num_part)
	print('  mean of length  : %f' % moment1)
	print('  SD of length    : %f' % sd)

	return parts_inp, parts_hyp


def savehyp(parts_inp, parts_hyp, fname):
	with open(fname+'.input', 'w', encoding='utf-8') as fp:
		for inp in parts_inp:
			fp.write(' ||| '.join([' '.join(part) for part in inp]) + '\n')
	with \
		open(fname, 'w', encoding='utf-8') as f1, \
		open(fname+'.sep', 'w', encoding='utf-8') as f2:
		for hyp in parts_hyp:
			f1.write(' '.join([' '.join(part) for part in hyp]) + '\n')
			f2.write(' ||| '.join([' '.join(part) for part in hyp]) + '\n')


def main():
	if len(sys.argv) != 6:
		print('USAGE: python3 makehyp.py \\')
		print('              <in-file: input sentence> \\')
		print('              <in-file: part-ID table> \\')
		print('              <in-file: part-MT table> \\')
		print('              <in-file: splitter table> \\')
		print('              <out-file: hypothesis sentence>')
		return
	
	fnames = {}
	fnames['IN'] = sys.argv[1]
	fnames['PID'] = sys.argv[2]
	fnames['PMT'] = sys.argv[3]
	fnames['SP'] = sys.argv[4]
	fnames['HYP'] = sys.argv[5]

	print('========')
	print('input corpus     : %s' % fnames['IN'])
	print('part ID table    : %s' % fnames['PID'])
	print('part MT table    : %s' % fnames['PMT'])
	print('splitting table  : %s' % fnames['SP'])

	corpus_in, tab_pid_pmt, tab_sp = load(fnames)
	parts_inp, parts_hyp = makehyp(corpus_in, tab_pid_pmt, tab_sp)
	savehyp(parts_inp, parts_hyp, fnames['HYP'])


if __name__ == '__main__':
	main()

