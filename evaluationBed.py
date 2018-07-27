from project519.docCls import doc_object
from project519.docClean import content_preprocessor
from project519.tfidfStrategy import tfidf_model
from project519.LDAStrategy import lda_model
from project519.word2vecStrategy import w2v_model

_LATEX_BLACK_LIST_FILE = "C:\\Users\\ibipul\\codes\\CSE519-2017-111578726\\project519\\latex_keywords.txt"
class evaluation_bed:
    def __init__(self, doc_obj_list):
        """
        Constructor of the Evaluation bed
        :param doc_obj_list list[doc_obj]: List of the doc_objects
        """
        self.doc_objs = doc_obj_list
        self.ltx_blacklist = self.read_latex_blacklist()
        self.preprocessed_doc_objects = self.preprocessing()
        self.corpus = self.get_corpus()
        self.model = None

    def read_latex_blacklist(self,file= _LATEX_BLACK_LIST_FILE):
        """
        Reads a static list of Blacklist of keywords from file on the disk
        :param file string: Path to the file
        :return:
        :rtype: list[string]
        """
        with open(file) as f:
            blist = f.read().splitlines()
        return blist

    def filter_latex_blacklist(self, words):
        """
        Runs through doc_string of each doc_obj object and removes
        the words in the black_listed latex keywords
        :param words list[string]:
        :return: Returns cleaned doc_string
        :rtype: list[string]
        """
        set_difference_doc_string = set(set(words)).difference(self.ltx_blacklist)
        return ' '.join(list(set_difference_doc_string))  # setdiff of words & blacklist

    def preprocessing(self):
        """
        This is the interface function to the pre-processing toolchain every doc_object goes
        :return: returns a list of processed and cleaned doc_objects
        :rtype: list[doc_obj]
        """
        preprocessed_obj_list = []
        for obj in self.doc_objs:
            if len(obj.index_keywords) == 0:
                print("Directory: ", obj.dirname, " has a deeper hierarchy. Skipping")
                continue
            doc_preprocessor = content_preprocessor(doc_object=obj)
            preprocessed_obj = doc_preprocessor.preprocess()
            preprocessed_obj.doc_string = \
                self.filter_latex_blacklist(words=preprocessed_obj.doc_string.split())
            print(preprocessed_obj.dirname)
            preprocessed_obj_list.append(preprocessed_obj)

        return preprocessed_obj_list

    def get_corpus(self):
        """
        Called by constructor, Fetches the flat list of doc-string representing each of the doc_obj encapsulating the docs
        :return:
        """
        docs = []
        for doc_obj in self.preprocessed_doc_objects:
            docs.append(doc_obj.doc_string)

        return docs

    # Define index computation algorithm
    def plugin_algorithm(self, algorithm_name='tfidf',lower = 0, upper = .99):
        """
        This is the global Algorithmic evaluation invocation point,
        depending on the passed argument for algorithm type, coresponding model object is spawned.
        Model is trained and then we get back list of index keywords for each doc, also evaluation metric for
        each of the computed index sets.
        :param algorithm_name string: Currently one of 'tfifd', 'lda','word2vec'
        :param lower float: lower quantile score threshold
        :param upper float: upper quantile score threshold
        :return:
        """
        if algorithm_name == 'tfidf':
            print(" Creating the TF.IDF model from sklearn")
            print(" Using ", len(self.preprocessed_doc_objects)," documents, these are fine")
            ## Creat the tfidf model object
            tfidf_obj = tfidf_model(corpus=self.corpus, lower_threshold=lower, upper_threshold=upper)
            print(" Fitting the Corpus to the model")
            tfidf_obj.fit()
            self.model = tfidf_obj
            print("Running update on each doc based on TFIDF we have defined")
            for doc in self.preprocessed_doc_objects:
                candidate_words_dict = tfidf_obj.get_dictionary_for_doc(doc.doc_string)
                candidate_words_list= candidate_words_dict.keys()
                doc.candidate_words_list = candidate_words_list
                ## Update eval metric per iteration
                doc.weighted_intersection = \
                    self.model.weighted_index_overlap(doc.index_keywords, candidate_words_list)
                doc.evaluation_index_to_candidates, \
                doc.evaluation_candidates_to_index = \
                    self.model.evaluation_overlap_ratios(doc.index_keywords, candidate_words_list)
                # Display evaluatation for each doc in corpus
                print('Dir:%s' % doc.dirname, 'count: %s' % len(candidate_words_list),
                      'wg_o: %.3f' % doc.weighted_intersection, 'ov_rec: %.3f' % doc.evaluation_index_to_candidates,
                      'ov_prec: %.3f' % doc.evaluation_candidates_to_index)

        elif algorithm_name=='lda':
            ## In this set up LDA runs per doc, so this is accordingly set up.
            print("Running Th LDA strategy now from gensim")
            for doc in self.preprocessed_doc_objects:
                lda_model_obj = lda_model(doc_string=doc.doc_string)
                self.model = lda_model_obj
                candidate_words_list = self.model.index_words
                doc.candidate_words_list = candidate_words_list
                ## Update eval metric per iteration
                doc.weighted_intersection = \
                    self.model.weighted_index_overlap(doc.index_keywords,candidate_words_list)
                doc.evaluation_index_to_candidates, \
                doc.evaluation_candidates_to_index = \
                    self.model.evaluation_overlap_ratios(doc.index_keywords, candidate_words_list)
                # Display evaluatation for each doc in corpus
                print('Dir:%s'% doc.dirname,'count: %s'% len(candidate_words_list),
                      'wg_o: %.3f' % doc.weighted_intersection, 'ov_rec: %.3f' % doc.evaluation_index_to_candidates,
                      'ov_prec: %.3f' % doc.evaluation_candidates_to_index)

        elif algorithm_name=='word2vec':
            print("Running Word Embedding algorithm now with gensim and sklearn.kmeans")
            web_model_obj = w2v_model(corpus=self.corpus)
            self.model = web_model_obj
            for doc in self.preprocessed_doc_objects:
                candidate_words_list = self.model.get_index_words(doc_string=doc.doc_string)
                doc.candidate_words_list = candidate_words_list
                ## Update eval metric per iteration
                doc.weighted_intersection = \
                    self.model.weighted_index_overlap(doc.index_keywords, candidate_words_list)
                doc.evaluation_index_to_candidates, \
                doc.evaluation_candidates_to_index = \
                    self.model.evaluation_overlap_ratios(doc.index_keywords, candidate_words_list)
                # Display evaluatation for each doc in corpus
                print('Dir:%s'% doc.dirname, 'count: %s' % len(candidate_words_list),
                      'wg_o: %.3f' % doc.weighted_intersection, 'ov_rec: %.3f' % doc.evaluation_index_to_candidates,
                      'ov_prec: %.3f' % doc.evaluation_candidates_to_index)
                print(candidate_words_list)
        else:
            raise ValueError('That Algorithm is Not implemented yet')
