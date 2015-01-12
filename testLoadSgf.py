import sys, os

import kgs_dataset_preprocessor

filepath = sys.argv[1]
print 'processing ' + filepath
kgs_dataset_preprocessor.loadSgf( None, filepath )

# /data/norep/git/kgsgo-dataset-preprocessor/data/kgs-19-2011-09-new/2011-09-04-27.sgf move 207, move 118
# /data/norep/git/kgsgo-dataset-preprocessor/data/kgs-19-2013-04-new/2013-04-17-9.sgf
# /data/norep/git/kgsgo-dataset-preprocessor/data/kgs-19-2011-09-new/2011-09-02-34.sgf

