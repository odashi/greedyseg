# coding: utf-8

import sys

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread


def main():
	if len(sys.argv) != 3:
		print('USAGE: python3 evalsplit.py \\')
		print('               <in-file: reference splitter>')
		print('               <in-file: hypothesis splitter>')
		return

	fname_ref = sys.argv[1]
	fname_hyp = sys.argv[2]

	sp_ref = 0
	sp_hyp = 0
	sp_match = 0
	nosp_ref = 0
	nosp_hyp = 0
	nosp_match = 0

	sps_ref = {(int(x[0]), int(x[1])) for x in dlmread(fname_ref)}
	sps_hyp = {(int(x[0]), int(x[1])) for x in dlmread(fname_hyp)}
	match = 0
	for sp in sps_hyp:
		if sp in sps_ref:
			match += 1
	
	len_r = len(sps_ref)
	len_h = len(sps_hyp)
	
	print('SPLIT-R: %f [%d/%d]' % (match/len_r, match, len_r))
	print('SPLIT-P: %f [%d/%d]' % (match/len_h, match, len_h))
	print('SPLIT-F: %f [2*%d/(%d+%d)]' % (2*match/(len_r+len_h), match, len_r, len_h))


if __name__ == '__main__':
	main()

