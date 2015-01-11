# kgsgo-dataset-preprocessor
Dataset preprocessor for the KGS go dataset, eg according to Clark and Storkey input planes

#goal

The goal of this project is to take the data from the [kgsgo website](http://u-go.net/gamerecords/), and make it available into a somewhat generic format, that can be fed into any go-agnostic learning algorithm.  The guidelines
used for the creation of this project is to be able to somewhat reproduce the experiments in the [Clark and Storkey
paper](http://arxiv.org/abs/1412.3409), and also somewhat targetting the [Maddison et al paper](http://arxiv.org/abs/1412.6564).

#Technical goal

Should be able to type:

    python kgs-dataset-preprocessor.py [targetdirectory]

Results:
- the datasets are downloaded from http://u-go.net/gamerecords/
- decompressed
- loaded once at a time, and processed into a 2.5GB datafile, in sequence (clients can handle shuffling themselves I suppose?)

