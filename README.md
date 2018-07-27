# building-book-indices
### Building Document Index

This project is aimed towards building an automated index creating mechanism.
Component files are:
#### docCls.py
- Contains the *doc_object* class definition that encapsulates each complex/simple tex document structure behind a pdf file. *doc_class* takes the top level directory containing the tex file(s). The structure is as follows:
    - tex file names are read into tex_filenames
    - tex_file_contents contain raw tex file contents read in a string
    - Extract all index phrases encoded in latex fomats form the text
    - Preprocess the above to get the english like phrases each line is capturing
    - memeber variable to contain cleaned file strings (after preprocessing)
    - memeber variable to contain a set of computer index words on return from evaluation
    - an evaluation metric per object that quantifies the quality of index 

#### docClean.py
- Contains the *content_preprocessor*  class definition that recieves a *doc_object*.
- It contains a set of tools that run a set of filters on the file string
	- Removes comments
	- Strips varied type of white spaces
	- Remove all inline Math expressions
	- Remove all math equation objects (not implemented yet)

#### evaluationBed.py
- This is the main evaluation class, it recieves a list of document objects.
- An algotithm creates the relevant corpus from all documents.
- *content_preprocessor* is run on each doc_object to get a sanitized file string containing filtered content strings from them
- Run some algorithm to compute index words
- Get evaluation for each participating *doc_object* and update it in them

#### strip_comments.py
- This python file is taken from https://gist.github.com/amerberg/a273ca1e579ab573b499
- It is a work of https://gist.github.com/amerberg
- Here is it used with default encoding set to 'latin-1'

#### test_driver.py
This file is the main invokating point for any demo run.

#### Algorithm objects
Evalusation bed acceps algorithm objects that work on the loaded copous in the environment.
All the algorithm objects have identical invocation and evaluation interfaces that are invocable.
Following are the Algorithm objects
###### tfidfStrategy.py
    This contains the implementation of a band threshold based idea that Luhn talked about in his 1958 paper.
###### LDAStrategy.py
    This contains a topic modelling approach, that works per document.
###### word2vecStrategy
    This contains the word embedding based clustering approach. 
    Here first we generate the word embedding for all words in a document--
    current implementation uses gensim word2vec for this purpose.
    Then use this in each doc to cluster the words to find a list of topics, 
    currently sklearn K-means, with n_cluster set at 20.
    Other clustering and distance metric could be tested out in future if needed.
