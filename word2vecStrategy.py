import gensim
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk import word_tokenize

class w2v_model:
    _EN_STOP_WORDS = set(stopwords.words('english'))
    _FILTER_POS_LIST = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',
                      'WP', 'WDT', 'RB', 'MD', 'RBR', 'RBS', 'PRP', 'JJ', 'JJR', 'JJS', 'IN', 'DT', 'CD', 'CC']

    def __init__(self,corpus, topic_count=20):
        """
        Constructor for extracting the word-embedding strategy
        :param corpus list[strings]: list of doc-strings from docs in corpus
        :param topic_count int: Number of topics we want to create for our docs
        """
        self.corpus = corpus
        self.topic_count = topic_count
        self.num_features = 150 #feature vector size for words
        self.sentences = self.breakdown_to_sentences()
        self.model = self.get_model()

    def breakdown_to_sentences(self, sentance_size=80):
        """
        Transform the corpus into sets of sentances
        Default is set at 80 character sentances.
        We create the sentance list of list representation here
        :return:
        """
        sentence_representation = []
        for element in self.corpus:
            z = map(''.join, zip(*[iter(element)] * sentance_size))
            w_split = [i.split() for i in z]
            sentence_representation += w_split
        return sentence_representation

    def get_model(self):
        """
        We generate the feature vectors for each of the words in the corpus vocabulary
        using the gensim word2vec NN model available in gensim package
        :return:
        """
        model = gensim.models.word2vec.Word2Vec(sentences=self.sentences, size=self.num_features, min_count=1)
        model.init_sims(replace=True)
        return model

    def filter_black_list(self, tok_list):
        """
        Makes sure we filter out most forms of parts of speech, remove non-nouns from the index word output
        from our index words
        :param tok_list list[string]: list of word tokens
        :return:
        """
        white_list_words = []
        remove_pos = self._FILTER_POS_LIST
        for tok in tok_list:
            if tok[1] not in remove_pos:
                white_list_words.append(tok[0])
        return white_list_words

    def get_index_words(self,doc_string):
        """
        Here we exctact word feature vector for words in a doc.
        Then we apply k-means to get about 20 topics in clusters.
        We output ~5 words from each cluster
        :param doc_string:
        :return:
        """
        component_words = doc_string.split()
        feature_vectors=[]
        for word in component_words:
            try:
                fv = self.model[word]
            except KeyError:
                fv = np.array([0]*self.num_features)
            feature_vectors.append(fv)
        # Word feature vectors
        v = np.stack(feature_vectors)
        kmeans = KMeans(n_clusters=self.topic_count, random_state=0).fit(v)
        word_clusters = pd.DataFrame({'word':component_words, 'cluster':kmeans.labels_})

        # Prune Cluster by word length
        word_clusters['w_len'] = word_clusters['word'].apply(lambda x: len(x))

        out_words = []
        for i in range(self.topic_count):
            z = word_clusters[word_clusters['cluster']==i]
            z = z[z['w_len'] > 5]
            picked_word = [i for i in z['word'].values[:10]]
            out_words += picked_word

        # Remove stop words
        stopped_tokens = [i for i in out_words if not i in self._EN_STOP_WORDS]
        # Filter by POS tag
        tok_pos_tagged = pos_tag(stopped_tokens)
        out_words = self.filter_black_list(tok_pos_tagged)
        return out_words

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
         :rtype: float, float

         """
        index_words = []
        for text in index_phrases:
            index_words += self.tokenize(text)

        index_vocabulary = set(index_words)
        overlap = index_vocabulary.intersection(computed_index)

        index_to_candidates = len(overlap)/len(index_vocabulary)
        candidate_to_index = len(overlap)/len(computed_index)

        return index_to_candidates, candidate_to_index