# coding: utf-8

import sys
import os

def main():
	if len(sys.argv) != 8:
		print('USAGE: python maketraindata.py \\')
		print('              <str: name of input dataset> \\')
		print('              <str: name of output dataset> \\')
		print('              <str: foreign language> \\')
		print('              <str: target language> \\')
		print('              <path: directory of input data> \\')
		print('              <path: directory of output data> \\')
		print('              <int: number of sentence to use>')
		return
	
	dataname_in = sys.argv[1]
	dataname_out = sys.argv[2]
	lang_f = sys.argv[3]
	lang_e = sys.argv[4]
	dirname_in = sys.argv[5]
	dirname_out = sys.argv[6]
	num_sents = int(sys.argv[7])

	# make directories
	if not os.path.isdir(dirname_out):
		os.mkdir(dirname_out)
	if not os.path.isdir(dirname_out+'/ref'):
		os.mkdir(dirname_out+'/ref')
	if not os.path.isdir(dirname_out+'/out'):
		os.mkdir(dirname_out+'/out')
	if not os.path.isdir(dirname_out+'/tok'):
		os.mkdir(dirname_out+'/tok')
	
	# make corpus_f
	fname_in = dirname_in+'/ref/'+dataname_in+'.'+lang_f
	fname_out = dirname_out+'/ref/'+dataname_out+'.'+lang_f
	sys.stderr.write('%s -> %s ...\n' % (fname_in, fname_out))
	with \
		open(fname_in, 'r', encoding='utf-8') as fi, \
		open(fname_out, 'w', encoding='utf-8') as fo:
		n = 0
		for l in fi:
			fo.write(l)
			n += 1
			if n >= num_sents:
				break
	
	# n: number of actually copied sentences
	
	# make corpus_e
	fname_in = dirname_in+'/ref/'+dataname_in+'.'+lang_e
	fname_out = dirname_out+'/ref/'+dataname_out+'.'+lang_e
	sys.stderr.write('%s -> %s ...\n' % (fname_in, fname_out))
	with \
		open(fname_in, 'r', encoding='utf-8') as fi, \
		open(fname_out, 'w', encoding='utf-8') as fo:
		for i in range(n):
			fo.write(next(fi))
	
	# make corpus_f (capitalized)
	fname_in = dirname_in+'/tok/'+dataname_in+'.'+lang_e
	fname_out = dirname_out+'/tok/'+dataname_out+'.'+lang_e
	if os.path.exists(fname_in):
		sys.stderr.write('%s -> %s ...\n' % (fname_in, fname_out))
		with \
			open(fname_in, 'r', encoding='utf-8') as fi, \
			open(fname_out, 'w', encoding='utf-8') as fo:
			for i in range(n):
				fo.write(next(fi))

	# make part-id table
	fname_in = dirname_in+'/ref/'+dataname_in+'split'+lang_f+lang_e+'.'+lang_f+'.ids'
	fname_out = dirname_out+'/ref/'+dataname_out+'split'+lang_f+lang_e+'.'+lang_f+'.ids'
	sys.stderr.write('%s -> %s ...\n' % (fname_in, fname_out))
	with \
		open(fname_in, 'r', encoding='utf-8') as fi, \
		open(fname_out, 'w', encoding='utf-8') as fo:
		nn =  0
		for l in fi:
			data = [int(x) for x in l.strip().split(' ')]
			if data[0] >= n:
				break
			fo.write(l)
			nn += 1
	
	# nn: number of actually copied parts

	# make part-mt table
	fname_in = dirname_in+'/out/'+dataname_in+'split'+lang_f+lang_e+'.'+lang_e
	fname_out = dirname_out+'/out/'+dataname_out+'split'+lang_f+lang_e+'.'+lang_e
	sys.stderr.write('%s -> %s ...\n' % (fname_in, fname_out))
	with \
		open(fname_in, 'r', encoding='utf-8') as fi, \
		open(fname_out, 'w', encoding='utf-8') as fo:
		for i in range(nn):
			fo.write(next(fi))


if __name__ == '__main__':
	main()

