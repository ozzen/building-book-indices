import re
from project519.docCls import doc_object
from project519.strip_comments import strip_comments


class content_preprocessor:
    def __init__(self, doc_object):
        """
         content_preprocessor constructor
        :param doc_object doc_object:
        """
        self.doc_object = doc_object
        # self._latex_blist = self.read_latex_blacklist()

    def remove_math_exp(self):
        """
        This function is used to remove all inline mathematical expressions from the file
        """
        p = re.compile(r'\$([^\$]+)\$+', re.I)
        content_string_list = self.doc_object.sanitized_file_strings
        math_exp_sanitized_string_list = []
        for cont_str in content_string_list:
            math_exp_sanitized_string = re.sub(p, '', cont_str)
            math_exp_sanitized_string_list.append(math_exp_sanitized_string)

        self.doc_object.sanitized_file_strings = math_exp_sanitized_string_list

    def remove_math_formula(self):
        """
        This function clears out text segments enclosed in $$
        and those enclosed in \begin{equation}\end{equation}
        :return:
        """
        pass

    def clear_math(self):
        """
        Wrapper that initiates math clearing operation on content strings
        :return:
        """
        self.remove_math_exp()
        self.remove_math_formula()

    def clear_comments(self):
        """
        Calls dzhuang/strip_comments.py for comment removal
        Default encoding is now set to latin-1 other option is utf-8
        """
        content_string_list = self.doc_object.tex_file_contents
        comment_removed_content_list = []
        for cont_str in content_string_list:
            comment_removed_content = strip_comments(cont_str)
            comment_removed_content_list.append(comment_removed_content)

        self.doc_object.sanitized_file_strings = comment_removed_content_list

    def sanitize_whitespace(self):
        """
        Clears substansive extra formatting white spaces in the text
        """
        content_string_list = self.doc_object.sanitized_file_strings
        space_sanitized_string_list = []
        for cont_str in content_string_list:
            space_sanitized_string = re.sub('\s+',' ', cont_str)
            space_sanitized_string_list.append(space_sanitized_string)

        self.doc_object.sanitized_file_strings = space_sanitized_string_list


    def clear_latex_formatting(self):
        ## Remove bibliography
        p_bibliography = re.compile(r'(\\begin\{thebibliography\}[\s|\W|\w]+\\end\{thebibliography\})')
        self.doc_object.doc_string = re.sub(p_bibliography, '', self.doc_object.doc_string)
        ## All begin{xyz} items
        p_begin= re.compile(r'(\\begin\{[a-z|*]+\})',re.I)
        self.doc_object.doc_string = re.sub(p_begin, '', self.doc_object.doc_string)
        ## All end{xyz} items
        p_end = re.compile(r'(\\end\{[a-z|*]+\})', re.I)
        self.doc_object.doc_string = re.sub(p_end, '', self.doc_object.doc_string)
        ## All label{xyz} items
        p_label = re.compile(r'(\\label\{[a-z|*|\W|\[|\]]+\})',re.I)
        self.doc_object.doc_string = re.sub(p_label, '', self.doc_object.doc_string)
        ## All citations and references
        p_citeref = re.compile(r'(\\[cite|ref]+\{[\w|\-|\:|\||0-9|]+\})')
        self.doc_object.doc_string = re.sub(p_citeref, '', self.doc_object.doc_string)


    def remove_words_aretifacts_le_2(self):
        self.doc_object.doc_string = ' '.join(word for word in self.doc_object.doc_string.split() if len(word) > 3)

    def clear_punct_specialchar(self):
        self.doc_object.doc_string = re.sub(r'[^a-zA-Z ]', r' ', self.doc_object.doc_string)

    def preprocess(self):
        """
        Invocation creates sanitized file strings of latex files for index computation
        component functions are sequentially called
        :return: doc_object with sanitized filestrings updated
        :rtype doc_object:
        """
        # TODO: ibipul@cs.stonybrook.edu

        self.clear_comments()
        self.sanitize_whitespace()
        self.clear_math()
        self.doc_object.doc_string = ''.join(self.doc_object.sanitized_file_strings).lower()
        self.clear_latex_formatting()
        self.clear_punct_specialchar()
        self.sanitize_whitespace()
        self.remove_words_aretifacts_le_2()

        return self.doc_object