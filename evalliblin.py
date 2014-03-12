# coding: utf-8

import sys

sys.path.append('/project/nakamura-lab01/Work/yusuke-o/python')
from data.reader import dlmread


def main():
	if len(sys.argv) != 3:
		print('USAGE: python3 evalliblin.py \\')
		print('               <in-file: LIBLINEAR input file>')
		print('               <in-file: LIBLINEAR prediction result>')
		return

	fname_ref = sys.argv[1]
	fname_hyp = sys.argv[2]

	sp_ref = 0
	sp_hyp = 0
	sp_match = 0
	nosp_ref = 0
	nosp_hyp = 0
	nosp_match = 0

	for ls_ref, ls_hyp in zip(dlmread(fname_ref), dlmread(fname_hyp)):
		ref = int(ls_ref[0])
		hyp = int(ls_hyp[0])

		if ref == 1:
			sp_ref += 1
		else:
			nosp_ref += 1

		if hyp == 1:
			sp_hyp += 1
		else:
			nosp_hyp += 1

		if ref == hyp:
			if ref == 1:
				sp_match += 1
			else:
				nosp_match += 1

	print('LIBLIN-R: %f [%d/%d]' % (0 if sp_ref==0 else sp_match/sp_ref, sp_match, sp_ref))
	print('LIBLIN-P: %f [%d/%d]' % (0 if sp_hyp==0 else sp_match/sp_hyp, sp_match, sp_hyp))
	print('LIBLIN-F: %f [2*%d/(%d+%d)]' % (0 if sp_ref+sp_hyp==0 else 2*sp_match/(sp_ref+sp_hyp), sp_match, sp_ref, sp_hyp))

if __name__ == '__main__':
	main()

