from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from string import punctuation
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk import PorterStemmer
from scipy import stats
from nltk import pos_tag
import collections
import re

class tfidf_model:

    def __init__(self, corpus, lower_threshold, upper_threshold):
        """
        Constructor for initializing the tfidf model
        :param corpus list[string]: flat list of doc_strings from all the component doc in corpus
        :param lower_threshold:
        :param upper_threshold:
        """
        self._LOWER_THRESHOLD = lower_threshold
        self._UPPER_THRESHOLD = upper_threshold
        self.corpus = corpus
        self.stop_words = stopwords.words('english') + list(punctuation)
        self.vocabulary = self.corpus_vocabulary()
        self.model = self.generate_model()
        #self.candidate_word_dict ={}

    def filter_black_list(self,tok_list):
        """
        Makes sure we filter out most forms of parts of speech, remove non-nouns from the index word output
        from our index words
        :param tok_list list[string]: list of word tokens
        :return:
        """
        white_list_words = []
        remove_pos = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
                      'WP', 'WDT', 'RB', 'MD', 'RBR', 'RBS', 'PRP', 'JJ', 'JJR', 'JJS', 'IN', 'DT', 'CD', 'CC']
        for tok in tok_list:
            if tok[1] not in remove_pos:
                white_list_words.append(tok[0])

        return white_list_words

    def tokenize(self, text):
        """
        Tokenize the strings to each words
        :param text string:
        :return:
        :rtype: list[tokens)
        """
        words = word_tokenize(text)
        words = [w.lower() for w in words]
        words = pos_tag(words)
        words = self.filter_black_list(words)
        return words

    def corpus_vocabulary(self):
        """
        Creates the complete vocabulary over all documents
        :return:
        """
        vocabulary = set()
        for str in self.corpus:
            words = self.tokenize(str)
            vocabulary.update(words)

        return vocabulary

    def generate_model(self):
        tfidf_obj = TfidfVectorizer(stop_words=self.stop_words,tokenizer=self.tokenize,vocabulary=self.vocabulary)
        return tfidf_obj

    def fit(self):
        """
        Fits the model using the corpus
        :return:
        """
        self.model.fit([doc_str for doc_str in self.corpus])

    def get_dictionary_for_doc(self, document_string):
        """"
        Get the final word=score dictionary for the candidate words for computed index.
        :param model tv_id model_obj
        """
        X = self.model.transform([document_string])
        doc_tokens = self.tokenize(document_string)

        candidate_word_dict = defaultdict(lambda:0)
        for word in doc_tokens:
            word_score = X[0, self.model.vocabulary_[word]]
            if word_score > 0 :
                candidate_word_dict[word] += word_score
        candidate_word_dict = dict(candidate_word_dict)

        # Get a select subset out of the whole bag based on a quantile score
        final_dict = self.filter_by_threshold(candidate_word_dict=candidate_word_dict,
                                              lower=self._LOWER_THRESHOLD,upper=self._UPPER_THRESHOLD)
        scored = collections.Counter(final_dict)
        final_dict = dict(scored.most_common(100))
        return final_dict

    def filter_by_threshold(self,candidate_word_dict, lower, upper):
        """
        Helps in choosing a subset of words for candidates using the quantile thresholds fed to the model
        :param candidate_word_dict:
        :param lower:
        :param upper:
        :return:
        """
        keys = list(candidate_word_dict.keys())
        values = list(candidate_word_dict.values())
        quantile_scores = stats.rankdata(values, 'average') / len(values)

        final_dictionary = defaultdict(lambda:0)
        for i in range(len(quantile_scores)):
            if quantile_scores[i] > lower and quantile_scores[i] < upper:
                key = keys[i]
                value = values[i]
                final_dictionary[key] = value

        return dict(final_dictionary)

    def weighted_index_overlap(self, index_truth, computed_index):
        """
        Returns an weigned overlap score for the index words and selected candictates,
        :param index_truth:
        :param computed_index:
        :return:
        """
        index_words = []
        for text in index_truth:
            index_words += self.tokenize(text)
        results = {}
        for i in computed_index:
            results[i] = index_words.count(i)
        w_sum = 0.0
        for key in results.keys():
            if results[key] > 0:
                w_sum += results[key] + 1

        score = float(w_sum / (len(index_words) + len(computed_index)))
        return score

    def evaluation_overlap_ratios(self, index_phrases, computed_index):
        """
        Computates the two overlap to index set, and computed words set.
        :param index_phrases list[string]: actual index words
        :param computed_index: computed index words
        :return:
        lrtype: float, float

        """
        index_words = []
        for text in index_phrases:
            index_words += self.tokenize(text)

        index_vocabulary = set(index_words)
        overlap = index_vocabulary.intersection(computed_index)

        index_to_candidates = len(overlap)/len(index_vocabulary)
        candidate_to_index = len(overlap)/len(computed_index)

        return index_to_candidates, candidate_to_index
