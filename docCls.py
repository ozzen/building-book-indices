import glob
import re
import io
from collections import defaultdict

class doc_object:
    """
    doc_object is the class that encapsulates each complex/simple tex document structure
    behind a pdf file.
    1. tex file names are read into tex_filenames
    2. tex_file_contents contain raw tex file contents read in a string
    """
    def __init__(self, dir_path):
        """
        Constructor for doc_object class
        :param dir_path string: base folder of each directory containing the tex files
        """
        self.dir_path = dir_path
        self.dirname = self.dir_path.split('\\')[-2]
        self.tex_filenames = self.read_filenames(doc_directory=self.dir_path)

        ## File content related variables
        self.tex_file_raw_contents = self.read_files_as_string(filenames_list=self.tex_filenames)
        self.index_ground_truth, self.tex_file_contents = \
            self.extract_index_words_and_content_strings(raw_content_strings=self.tex_file_raw_contents)

        # Index related Variables
        self.index_keywords = self.raw_keywords(ground_truth=self.index_ground_truth)
        self.index_keywords_toplevel = self.raw_main_keywords(ground_truth=self.index_ground_truth)


        ## Evaluation Metrics
        self.sanitized_file_strings = []  # Updated by preprocessor.preprocess()
        self.doc_string = '' #Updated by preprocessor.preprocess()
        self.latex_black_list = []
        self.computed_index_words = []  # Updated by evaluation bed TODO ibipul
        self.candidate_words_dict=None
        self.candidate_words_list=[]
        self.evaluation_performance_per_index = 0.0
        self.weighted_intersection= 0.0
        self.evaluation_index_to_candidates = 0.0
        self.evaluation_candidates_to_index = 0.0

    def read_filenames(self, doc_directory):
        """
        Function to read all tex file names in the base directory
        :param doc_directory string:
        :return filenames list:
        """
        tex_files = glob.glob(doc_directory + '*.tex')
        return tex_files

    def read_files_as_string(self, filenames_list):
        """
        Reads Contents of tex files
        :param filenames_list list[char]: list of component filenames
        :return: list of contents of files as strings
        :rtype list[char]:
        """
        content_strings = []
        for file_name in filenames_list:
            with io.open(file_name, encoding='latin-1') as content_file:
                content = content_file.read()
                content_strings.append(content)
        return content_strings

    def sanitize_and_extract_index(self, content_strings):
        """
        Given a docstring eliminates the index_terms from it,
        and returns a list of index words
        :param content_strings string:
        :return:
        :rtype:
        string, list[str]
        """
        index_list = [m.start() for m in re.finditer('index', content_strings)]
        index_terms = []
        for word_start in index_list:
            start_index = word_start - 1
            if content_strings[start_index] == '\\' and content_strings[start_index + 6] == '{':
                index = start_index + 7
                bracket_count = 1
                while bracket_count != 0:
                    next_char = content_strings[index]
                    if next_char == '{':
                        bracket_count += 1
                    elif next_char == '}':
                        bracket_count -= 1

                    index += 1
                end_index = index
                index_terms.append(content_strings[start_index:end_index])
            else:
                continue

        for term in index_terms:
            content_strings = content_strings.replace(term, '')

        index_word_list = [t[7:-1] for t in index_terms]
        return content_strings, index_word_list

    def extract_index_words_and_content_strings(self, raw_content_strings):
        """
        Extracts and returns a list of index words encoded in the tex files
        :return: a list of index words extracted
        :rtype list[string], lis[string]
        """
        all_index_words = []
        all_content_strings = []
        for cont_str in raw_content_strings:
            clean_str, indices = self.sanitize_and_extract_index(content_strings=cont_str)
            all_content_strings.append(clean_str)
            all_index_words += indices
        return all_index_words, all_content_strings

    def raw_keywords(self,ground_truth):
        """
        Implements a variation of keywords, this method tries
        to reconstruct full pharases of sub-index entries
        :param ground_truth string: phrases in the index
        :return:
        :rtype: list[string]
        """
        keyword_list = []
        for word in ground_truth:
            if '|' in word:
                w_split = word.split('|')
                if '!' in w_split[0]:
                    tword = w_split[0].replace('!',' ')
                    keyword_list.append(tword)
                else:
                    keyword_list.append(w_split[0])
            elif '!' in word:
                tword = word.replace('!', ' ')
                keyword_list.append(tword)
            else:
                keyword_list.append(word)
        return keyword_list

    def raw_main_keywords(self,ground_truth):
        """
        This extracts the top level index words with multiplicity.
        :param ground_truth string:
        :return:
        :rtype: list[string]
        """
        keyword_list = []
        for word in ground_truth:
            if '|' in word:
                w_split = word.split('|')
                if '!' in w_split[0]:
                    tword = w_split[0].split('!')
                    keyword_list.append(tword[0])
                else:
                    keyword_list.append(w_split[0])
            elif '!' in word:
                tword = word.split('!')
                keyword_list.append(tword[0])
            else:
                keyword_list.append(word)
        return keyword_list