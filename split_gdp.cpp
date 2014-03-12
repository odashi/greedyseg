// split_gdp.cpp

#include <stdexcept>
#include <iostream>
#include <fstream>
#include <string>
#include <tuple>
#include <vector>
#include <map>
#include <set>
#include <utility>
#include <algorithm>
#include <limits>
#include <ctime>
#include <cmath>
#include <cstdlib>
#include <boost/format.hpp>
#include <boost/function.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>

using namespace std;
//using namespace boost;

namespace
{
typedef uint16_t WordID;
typedef uint16_t SentenceID;
typedef uint16_t Position;
typedef vector<WordID> Sentence; // [word]
typedef vector<Sentence> Corpus; // [[word]]
typedef tuple<WordID, WordID> Feature; // feature of segment (POS, POS)
typedef tuple<SentenceID, Position> SegmentID; // segment ID (Sentence, position)
typedef tuple<SentenceID, Position, Position> PartID; // part ID (Sentence, begin, end)
typedef boost::function<double(const Sentence&, const Sentence&)> Evaluator; // type of EV
}

// word-to-ID table
class WordIDTable {
	typedef map<string, WordID> Table;
	Table table_;
public:
	WordIDTable() {}
	~WordIDTable() {}

	inline Table::size_type size() const { return table_.size(); }
	inline Table::iterator begin() { return table_.begin(); }
	inline Table::const_iterator begin() const { return table_.begin(); }
	inline Table::iterator end() { return table_.end(); }
	inline Table::const_iterator end() const { return table_.end(); }

	WordID operator[](const string& word)
	{
		auto it = table_.find(word);
		if (it != table_.end()) return it->second;
		WordID newid = table_.size();
		table_.insert(Table::value_type(word, newid));
		return newid;
	}
};


// BLEU+1 scorer
class BLEUp1
{
	// make N-gram
	Sentence makeNGram(const Sentence& sent, Position begin, unsigned int n)
	{
		Sentence ret;
		auto it1 = sent.begin() + begin;
		auto it2 = it1 + n;
		ret.insert(ret.end(), it1, it2);
		return move(ret);
	}

public:
	BLEUp1() {}
	~BLEUp1() {}

	double operator()(const Sentence& ref, const Sentence& hyp)
	{
		const unsigned int MAX_N = 4;
		int numer[MAX_N] = {0, 1, 1, 1};
		int denom[MAX_N] = {0, 1, 1, 1};
		size_t len_ref = ref.size();
		size_t len_hyp = hyp.size();
		map<Sentence, int> possible;
	
		// gather statistics
		for (unsigned int n = 0; n < MAX_N && len_hyp > n; ++n) {
			denom[n] += len_hyp - n;
	
			for (Position k = 0; k + n < len_ref; ++k) {
				++possible[makeNGram(ref, k, n+1)];
			}
	
			for (Position k = 0; k + n < len_hyp; ++k) {
				auto it = possible.find(makeNGram(hyp, k, n+1));
				if (it != possible.end() && it->second > 0) {
					--it->second;
					++numer[n];
				}
			}
		}
	
		if (numer[0] == 0) return 0.0;
	
		// calculate averatge precision
		double np = 0.0;
		for (unsigned int n = 0; n < MAX_N; ++n) {
			np += log((double)numer[n]) - log((double)denom[n]);
		}
	
		// calculate brevity penalty
		double bp = 1.0 - len_ref / (double)len_hyp;
		if (bp > 0.0) bp = 0.0;
	
		return exp(np/MAX_N + bp);
	}
};


// utility functions
class Utils
{
public:
	// print usage
	static void usage()
	{
		cout << "USAGE: split_gdp" << endl;
		cout << "         <[1] in-file: input sentence by POS>" << endl;
		cout << "         <[2] in-file: reference sentence>" << endl;
		cout << "         <[3] in-file: part-ID table>" << endl;
		cout << "         <[4] in-file: part-MT table>" << endl;
		cout << "         <[5] out-file: splitter model>" << endl;
		cout << "         <[6] str: evaluator name (\"BLEU\" or \"RIBES\")>" << endl;
		cout << "         <[7] flaot: minimum mean of #words>" << endl;
		cout << "         <[8] float: regularization strength>" << endl;
	}

	// get timestamp string as format "YYYY-MM-DD hh-mm-ss"
	static string getTimeStamp()
	{
		time_t t;
		time(&t);
			tm* s = localtime(&t);
		return move(boost::str(boost::format("%04d-%02d-%02d %02d:%02d:%02d")
			% (s->tm_year+1900) % (s->tm_mon+1) % s->tm_mday
			% s->tm_hour % s->tm_min % s->tm_sec));
	}

	// check the file is open
	template<class FileStreamT>
	static void checkFileOpen(const FileStreamT& fs, const string& fname)
	{
		if (!fs.is_open()) {
			throw runtime_error("could not open file: " + fname);
		}
	}

	// choose evaluator function
	static Evaluator getEvaluator(const string& name)
	{
		if (name == "BLEU") {
			return BLEUp1();
		} else if (name == "RIBES") {
			throw runtime_error("RIBES is still not implemented");
		} else {
			throw runtime_error("unknown evaluator name: " + name);
		}
	}
};


namespace
{


// load input sentence and POS
Corpus loadcorpus_input(const string& fname, WordIDTable& wid)
{
	Corpus corpus_pos;

	ifstream ifs(fname);
	Utils::checkFileOpen(ifs, fname);

	string s;
	while (getline(ifs, s)) {
		vector<string> sent;
		boost::trim(s);
		if (s.size() > 1) {
			boost::split(sent, s, boost::is_any_of(" "));
		}

		Sentence poss;
		for (auto& w : sent) {
			vector<string> word_pos;
			boost::split(word_pos, w, boost::is_any_of("_"));
			poss.push_back(wid[word_pos[1]]);
		}

		corpus_pos.push_back(move(poss));
	}

	return move(corpus_pos);
}


// load reference sentence
Corpus loadcorpus_reference(const string& fname, WordIDTable& wid)
{
	Corpus corpus_word;

	ifstream ifs(fname);
	Utils::checkFileOpen(ifs, fname);

	string s;
	while (getline(ifs, s)) {
		vector<string> sent;
		boost::trim(s);
		if (s.size() > 1) {
			boost::split(sent, s, boost::is_any_of(" "));
		}

		Sentence words;
		for (auto& w : sent) {
			words.push_back(wid[w]);
		}

		corpus_word.push_back(move(words));
	}

	return move(corpus_word);
}


// load parts table : {PartID: sentence}
map<PartID, Sentence> loadparts(const string& fname_id, const string& fname_mt, WordIDTable& wid_ref)
{
	map<PartID, Sentence> table;

	ifstream ifs_id(fname_id);
	ifstream ifs_mt(fname_mt);
	Utils::checkFileOpen(ifs_id, fname_id);
	Utils::checkFileOpen(ifs_mt, fname_mt);

	string s_id, s_mt;
	while (getline(ifs_id, s_id) && getline(ifs_mt, s_mt)) {
		vector<string> words_id, words_mt;
		boost::trim(s_id);
		boost::trim(s_mt);
		boost::split(words_id, s_id, boost::is_any_of(" "));
		if (s_mt.size() > 1) {
			boost::split(words_mt, s_mt, boost::is_any_of(" "));
		}
		PartID key(stoi(words_id[0]), stoi(words_id[1]), stoi(words_id[2]));

		Sentence val;
		for (auto& w : words_mt) {
			val.push_back(wid_ref[w]);
		}
		table[key] = move(val);
	}
	
	return move(table);
}


// make inverted index {Feature: [segment]}
map<Feature, vector<SegmentID> > makeinv_feature_segment(const Corpus& corpus_inp_pos)
{
	map<Feature, vector<SegmentID> > table;

	for (SentenceID i = 0; i < corpus_inp_pos.size(); ++i) {
		auto& sent = corpus_inp_pos[i];
		if (sent.size() == 0) continue;
		for (Position j = 0; j < sent.size()-1; ++j) {
			auto key = Feature(sent[j], sent[j+1]);
			table[key].push_back(SegmentID(i, j));
		}
	}
	
	return move(table);
}


// make hypothesis MT(f|S)
Sentence make_hyp(SentenceID sent, int len_sent, const vector<Position>& segs, const map<PartID, Sentence>& table_partid_mt)
{
	Sentence hyp;
	
	if (len_sent > 0) {
		Position begin = 0;
		for (Position seg : segs) {
			auto& part = table_partid_mt.at(PartID(sent, begin, seg));
			hyp.insert(hyp.end(), part.begin(), part.end());
			begin = seg+1;
		}
		auto& part = table_partid_mt.at(PartID(sent, begin, len_sent-1));
		hyp.insert(hyp.end(), part.begin(), part.end());
	}

	return move(hyp);
}


// Greedy+DP segmentation search
void gdp_search(
	const Corpus& corpus_inp_pos,
	const Corpus& corpus_ref,
	const map<PartID, Sentence>& table_partid_mt,
	const map<Feature, vector<SegmentID> >& table_feat_segid,
	Evaluator ev,
	double mu,
	double alpha,
	ofstream& fo)
{
	// check parameters
	if (mu < 1.0) throw runtime_error("\"mu\" must be larger than 1.0");
	
	// number of sentence in the training set
	unsigned int num_sents = corpus_inp_pos.size();
	if (num_sents != corpus_ref.size()) {
		throw runtime_error("corpus sizes are different");
	}

	// number of words in input sentence
	unsigned int num_words = 0;
	for (auto& sent : corpus_inp_pos) {
		num_words += sent.size();
	}

	// number of segments to be chosen
	int num_segs = static_cast<int>(num_words/mu - num_sents);
	if (num_segs < 0) num_segs = 0;

	// DP tables
	map<int, vector<double> > dp_scores;
	map<int, vector<vector<Position> > > dp_segs;
	map<int, set<Feature> > dp_feats;

	// set dp[0]
	vector<double> scores;
	vector<vector<Position> > segs;
	for (unsigned int i = 0; i < num_sents; ++i) {
		size_t len_inp = corpus_inp_pos[i].size();
		auto& ref = corpus_ref[i];
		if (len_inp > 0) {

			auto& hyp = table_partid_mt.at(PartID(i, 0, len_inp-1));
			scores.push_back(ev(ref, hyp));
		} else {
			scores.push_back(0.0);
		}

		segs.push_back(vector<Position>());
	}

	dp_scores[0] = move(scores);
	dp_segs[0] = move(segs);
	dp_feats[0] = set<Feature>();

	// score memo
	vector<map<Sentence, double> > memo(num_sents);

	// DP bounding width (maximum occuring in all feature)
	int bounding = 0;
	for (auto& keyval : table_feat_segid) {
		int x = keyval.second.size();
		if (x > bounding) bounding = x;
	}

#ifdef _OPENMP
	// feature list (for OpenMP)
	vector<Feature> featurelist;
	for (auto& keyval : table_feat_segid) featurelist.push_back(keyval.first);
	int num_features = featurelist.size();
#endif

	// run DP
	for (int n = 1; n <= num_segs; ++n) {
		// release old table (to suppress memory)
		if (n - bounding > 0) {
			int m = n - bounding - 1;
			dp_scores.erase(m);
			dp_segs.erase(m);
			dp_feats.erase(m);
		}

		// initialize current results
		vector<double> best_scores = dp_scores[n-1];
		vector<vector<Position> > best_segs = dp_segs[n-1];
		set<Feature> best_feats = dp_feats[n-1];
		double best_sum_score = 0.0;

		// search next feature to be added
#ifdef _OPENMP
		#pragma omp parallel for schedule(dynamic, 4)
		for (int i = 0; i < num_features; ++i) {
			auto& new_feat = featurelist[i];
			auto& new_segs = table_feat_segid.at(new_feat);
#else
		for (auto& keyval : table_feat_segid) {
			auto& new_feat = keyval.first;
			auto& new_segs = keyval.second;
#endif

			int k = new_segs.size();

			if (k > n) continue;
			if (dp_feats[n-k].find(new_feat) != dp_feats[n-k].end()) continue;

			vector<double> scores = dp_scores[n-k];
			vector<vector<Position> > segs = dp_segs[n-k];
			set<Feature> feats = dp_feats[n-k];
			feats.insert(new_feat);

			set<SentenceID> sents_to_update;
			for (auto& seg : new_segs) {
				SentenceID sent = get<0>(seg);
				Position position = get<1>(seg);
				segs[sent].push_back(position);
				sents_to_update.insert(sent);
			}

			for (SentenceID sent : sents_to_update) {
				sort(segs[sent].begin(), segs[sent].end());
				auto hyp = ::make_hyp(sent, corpus_inp_pos[sent].size(), segs[sent], table_partid_mt);
				auto it = memo[sent].find(hyp);

				if (it != memo[sent].end()) {
					scores[sent] = it->second;
				} else {
					double s = ev(corpus_ref[sent], hyp);
					scores[sent] = s;
					#pragma omp critical
					memo[sent][hyp] = s;
				}
			}

			double sum_score = 0;
			for (auto s : scores) {
				sum_score += s;
			}
			sum_score -= alpha * feats.size(); 

			# pragma omp critical
			if (sum_score > best_sum_score) {
				best_scores = move(scores);
				best_segs = move(segs);
				best_feats = move(feats);
				best_sum_score = sum_score;
			}
		}

		// add results into DP table
		dp_scores[n] = move(best_scores);
		dp_segs[n] = move(best_segs);
		dp_feats[n] = move(best_feats);

		// print progress
		cerr << boost::format("%s ... %d/%d, score=%.6f, #feat=%u") %
			Utils::getTimeStamp() % n % num_segs % best_sum_score % dp_feats[n].size() << endl;
		
		fo << n;
		for (auto feat : dp_feats[n]) {
			fo << " " << get<0>(feat) << "_" << get<1>(feat);
		}
		fo << endl;

		// cleanup memo (to suppress memory)
//		if (n % bounding == 0) {
//			memo.clear();
//		}
	}
}


} // namespace


// main routine
int main(int argc, char *argv[])
{
	if (argc != 9) {
		Utils::usage();
		return 0;
	}

	// store filenames
	map<string, string> fnames;
	fnames["corpus-inp-pos"] = argv[1];
	fnames["corpus-ref"] = argv[2];
	fnames["part-id"] = argv[3];
	fnames["part-mt"] = argv[4];
	fnames["model"] = argv[5];

	// Word-ID tables
	WordIDTable wid_inp_pos;
	WordIDTable wid_ref;
	
	try {
		// get evaluator
		auto ev = Utils::getEvaluator(argv[6]);

		// load/check numbers
		double mu = stof(argv[7]);
		double alpha = stof(argv[8]);

		// load data
		auto corpus_inp_pos = ::loadcorpus_input(fnames["corpus-inp-pos"], wid_inp_pos);
		auto corpus_ref = ::loadcorpus_reference(fnames["corpus-ref"], wid_ref);
		auto table_partid_mt = ::loadparts(fnames["part-id"], fnames["part-mt"], wid_ref);

		// make inverted indices
		auto table_feat_segid = ::makeinv_feature_segment(corpus_inp_pos);

		// output model file
		ofstream fo(fnames["model"]);
		Utils::checkFileOpen(fo, fnames["model"]);

		int num_words = 0;
		for (auto& sent : corpus_inp_pos) {
			num_words += sent.size();
		}

		// print information
		fo << "#sent: " << corpus_inp_pos.size() << endl;
		fo << "#word: " << num_words << endl;
		fo << "#fid: " << wid_inp_pos.size() << endl;

		// print POS-ID table
		for (auto elm : wid_inp_pos) {
			fo << elm.first << " " << elm.second << endl;
		}

		// Greedy+DP search
		::gdp_search(corpus_inp_pos, corpus_ref, table_partid_mt, table_feat_segid, ev, mu, alpha, fo);

	} catch (const exception& ex) {
		cerr << "ERROR: " << ex.what() << endl;
		return 1;
	}

	return 0;
}

