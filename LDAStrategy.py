from collections import defaultdict
from string import punctuation
from nltk import word_tokenize
from nltk import PorterStemmer
from scipy import stats
import re
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import pos_tag
from gensim import corpora
import gensim

class lda_model:

    #Class Tokenizer & Stop words
    _TOKENIZER = RegexpTokenizer(r'\w+')
    _EN_STOP_WORDS = set(stopwords.words('english'))
    _FILTER_POS_LIST = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
                      'WP', 'WDT', 'RB', 'MD', 'RBR', 'RBS', 'PRP', 'JJ', 'JJR', 'JJS', 'IN', 'DT', 'CD', 'CC']

    def __init__(self, doc_string, num_topics=50, num_words=5):
        self._NTOPICS = num_topics
        self._NWORDS = num_words
        self.doc_string = doc_string
        self.model = self.generate_model()
        self.index_words = self.get_index_words()
        #self.candidate_word_dict ={}

    def filter_black_list(self, tok_list):
        """
        Makes sure we filter out most forms of parts of speech
        from our index words
        :param tok_list:
        :return:
        """
        white_list_words = []
        remove_pos = self._FILTER_POS_LIST
        for tok in tok_list:
            if tok[1] not in remove_pos:
                white_list_words.append(tok[0])
        return white_list_words

    def process_doc(self):
        texts = []
        raw = self.doc_string.lower()
        tokens = self._TOKENIZER.tokenize(raw)
        stopped_tokens = [i for i in tokens if not i in self._EN_STOP_WORDS]
        texts.append(stopped_tokens)
        dictionary = corpora.Dictionary(texts)
        corp = [dictionary.doc2bow(text) for text in texts]
        ## Return the doc term matrix
        return corp, dictionary

    def generate_model(self):
        doc_term_mat, dictionary = self.process_doc()
        lda_obj = gensim.models.ldamodel.LdaModel(doc_term_mat, num_topics=self._NTOPICS, id2word=dictionary, passes=5)
        return lda_obj

    def get_index_words(self):
        nwords = self._NTOPICS//self._NWORDS
        results = self.model.print_topics(num_topics=self._NTOPICS//5, num_words=nwords)
        ilist = []
        for i in results:
            l = [x.split('*')[1] for x in i[1].replace('"', '').split('+')]
            ilist += l
        return ilist

    def tokenize(self, text):
        # stemmer = PorterStemmer()
        words = word_tokenize(text)
        words = [w.lower() for w in words]
        # words = [w for w in words if not bool(re.search(r'\d', w))]
        words = pos_tag(words)
        # words = [w for w in words if not bool(re.search(r'[%s]'% punctuation, w))]
        words = self.filter_black_list(words)

        # stemmed_words =  [stemmer.stem(w) for w in words if w not in self.stop_words and not w.isdigit()]
        return words

    def weighted_index_overlap(self, index_truth, computed_index):
        ##
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
        index_words = []
        for text in index_phrases:
            index_words += self.tokenize(text)

        index_vocabulary = set(index_words)
        overlap = index_vocabulary.intersection(computed_index)

        index_to_candidates = len(overlap) / len(index_vocabulary)
        candidate_to_index = len(overlap) / len(computed_index)

        return index_to_candidates, candidate_to_index

