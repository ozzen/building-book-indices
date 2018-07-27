from glob import glob
from project519.docCls import doc_object
from project519.evaluationBed import evaluation_bed
_TEST_ROOT = 'C:\\Users\\ibipul\\codes\\datasets\\arxiv\\'
_LATEX_DIRS = glob(_TEST_ROOT+"/*/")
_FILE_LOCATION = 'C:\\Users\\ibipul\\codes\\datasets\\'

_LOWER = 0.1
_UPPER = 0.95
def main():

    dlist = [doc_object(dir_path) for dir_path in _LATEX_DIRS]
    eval_environment = evaluation_bed(doc_obj_list=dlist)
    for lval in [0.1,0.2,0.3,0.4,0.5,0.6]:
        for wsize in [0.2,0.3,0.4]:
            _LOWER = lval
            _UPPER = round(lval + wsize,1)
            print(" Generating data set for {0} to {1}".format(_LOWER,_UPPER))
            file_name = "trial_{0}_{1}.csv".format(_LOWER, _UPPER)
            eval_environment.plugin_algorithm(algorithm_name='tfidf', lower=_LOWER, upper=_UPPER)
            #eval_environment.plugin_algorithm(algorithm_name='lda', lower=_LOWER, upper=_UPPER)
            #eval_environment.plugin_algorithm(algorithm_name='word2vec', lower=_LOWER, upper=_UPPER)
            line = 'dir_name,lower,upper,index_capture_ratio,overlap_to_true_index,overlap_to_subset'
            thefile = open(_FILE_LOCATION+file_name, 'w')
            thefile.write("%s\n" % line)
            for obj in eval_environment.preprocessed_doc_objects:
                print(
                    "Dirname: '{0}', index_capture: '{1}', Overlap/True Index words:'{2}',Overlap/Candidate words: '{3}'".format(
                    obj.dirname, round(obj.evaluation_performance_per_index, 3), round(obj.evaluation_index_to_candidates, 3),
                    round(obj.evaluation_candidates_to_index, 3)))
                temp_line = \
                    [obj.dirname,_LOWER,_UPPER, round(obj.weighted_intersection, 3),
                     round(obj.evaluation_index_to_candidates, 3),round(obj.evaluation_candidates_to_index, 3)]
                thefile.write("%s\n" % ','.join(str(v) for v in temp_line))

            thefile.close()

if __name__ == "__main__":
    main()
