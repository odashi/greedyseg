# coding utf-8

import sys
import codecs
import copy
from collections import defaultdict

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread
from smt import bleu
sys.path.append('/project/nakamura-lab01/Work/yusuke-o/lib2/RIBES')
from RIBES import RIBESevaluator


ribeseval = RIBESevaluator()

def evalBLEU(hyp, ref):
	return bleu.BLEUp1(hyp, ref)

def evalRIBES(hyp, ref):
	global ribeseval
	return ribeseval.eval([hyp], [[ref]])[0]

def getevaluator(evalname):
	if evalname == 'BLEU':
		return evalBLEU
	elif evalname == 'RIBES':
		return evalRIBES
	else:
		raise RuntimeError('invalid type of evaluator')


def load(fnames):
	print('--------')
	print('loading data ...')
	corpus_in = [x for x in dlmread(fnames['IN'], ' ')]
	corpus_ref = [x for x in dlmread(fnames['REF'], ' ')]
	
	tab_pid_pmt = {}
	with \
		codecs.open(fnames['PID'], 'r', 'utf-8') as fp_pid, \
		codecs.open(fnames['PMT'], 'r', 'utf-8') as fp_pmt:
		for lid, lmt in zip(fp_pid, fp_pmt):
			key = tuple(int(x) for x in lid.strip().split(' '))
			val = lmt.strip().split(' ')
			tab_pid_pmt[key] = val

	print('  # of input sentence     : %d' % len(corpus_in))
	print('  # of reterence sentence : %d' % len(corpus_ref))
	print('  # of part id-mt table   : %d' % len(tab_pid_pmt))
	return corpus_in, corpus_ref, tab_pid_pmt


def makehyp(i, len_in, splitter, tab_pid_pmt):
	hyp = []
	begin = 0
	for sp in sorted(splitter):
		hyp += tab_pid_pmt[i, begin, sp]
		begin = sp+1
	return hyp + tab_pid_pmt[i, begin, len_in-1]


def makelookup(corpus_in, corpus_ref, tab_pid_pmt, ev):
	print('--------')
	print('generating lookup table ...')

	# generate lookup table
	tab_lookup = []
	for i, (inp, ref) in enumerate(zip(corpus_in, corpus_ref)):
		len_in = len(inp)
		order = [] # [(pos, delta-bleu)]
		if len_in > 0:
			whole = set(range(len(inp)-1)) # {pos}
			added = set() # {pos}
			bleu_past = ev(tab_pid_pmt[i, 0, len_in-1], ref)
			for j in range(len(inp)-1):
				candidate = whole - added
				best_bleu = -1
				best_pos = -1
				for pos in candidate:
					added.add(pos)
					hyp = makehyp(i, len_in, added, tab_pid_pmt)
					bleu_new = ev(hyp, ref)
					if bleu_new > best_bleu:
						best_bleu = bleu_new
						best_pos = pos
					added.remove(pos)
				added.add(best_pos)
				order.append((best_pos, best_bleu - bleu_past))
				bleu_past = best_bleu
		tab_lookup.append(order)
	
	return tab_lookup


def makesp(corpus_in, meanlen, tab_lookup):
	tab_sp = defaultdict(lambda: [])
	len_corpus = len(corpus_in)
	num_words = sum(len(x) for x in corpus_in)
	num_iteration = max(0, num_words//meanlen - len_corpus)

	# greedy search
	print('--------')
	print('#words     : %d' % num_words)
	print('#splitters : %d' % num_iteration)
	for n in range(num_iteration):
		best_delta = -100
		best_pos = -1
		best_k = -1
		for k in range(len_corpus):
			if not tab_lookup[k]:
				continue
			pos, delta = tab_lookup[k][0]
			if delta > best_delta:
				best_delta = delta
				best_pos = pos
				best_k = k
		tab_lookup[best_k] = tab_lookup[best_k][1:]
		tab_sp[best_k].append(best_pos)

	return tab_sp


def save(tab_sp, fname):
	print('--------')
	print('save as %s ...' % fname)
	with codecs.open(fname, 'w', 'utf-8') as fp:
		for k, sps in sorted(tab_sp.items(), key=lambda x: x[0]):
			for sp in sps:
				fp.write('%d %d\n' % (k, sp))


def main():
	if len(sys.argv) < 7:
		print('USAGE: python split_greedy.py \\')
		print('              <in-file: input sentence> \\')
		print('              <in-file: reference sentence> \\')
		print('              <in-file: part-ID table> \\')
		print('              <in-file: part-MT table> \\')
		print('              <str: prefix of splitter file>')
		print('              <str: evaluator name ("BLEU" or "RIBES")>')
		print('              [list: <int: mean of #words>] \\')
		return
	
	fnames = {}
	fnames['IN'] = sys.argv[1]
	fnames['REF'] = sys.argv[2]
	fnames['PID'] = sys.argv[3]
	fnames['PMT'] = sys.argv[4]
	fnames['SP'] = sys.argv[5]

	evname = sys.argv[6]
	ev = getevaluator(evname)

	meanlens = [int(x) for x in sys.argv[7:]]

	print('========')
	print('input corpus           : %s' % fnames['IN'])
	print('reference corpus       : %s' % fnames['REF'])
	print('part ID table          : %s' % fnames['PID'])
	print('part MT table          : %s' % fnames['PMT'])
	print('splitting table prefix : %s' % fnames['SP'])
	print('evaluator              : %s' % evname)

	corpus_in, corpus_ref, tab_pid_pmt = load(fnames)
	tab_lookup = makelookup(corpus_in, corpus_ref, tab_pid_pmt, ev)

	for meanlen in meanlens:
		print('========')
		print('mean of #words : %s' % meanlen)
		tab_lookup_temp = copy.deepcopy(tab_lookup)
		tab_sp = makesp(corpus_in, meanlen, tab_lookup_temp)
		save(tab_sp, fnames['SP']+'.greedy_%s_%02d.split' % (evname, meanlen))
	

if __name__ == '__main__':
	main()

