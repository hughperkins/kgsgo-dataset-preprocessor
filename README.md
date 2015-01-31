# kgsgo-dataset-preprocessor
Dataset preprocessor for the KGS go dataset, eg according to Clark and Storkey input planes

#goal

The goal of this project is to take the data from the [kgsgo website](http://u-go.net/gamerecords/), and make it available into a somewhat generic format, that can be fed into any go-agnostic learning algorithm.  The guidelines
used for the creation of this project is to be able to somewhat reproduce the experiments in the [Clark and Storkey
paper](http://arxiv.org/abs/1412.3409), and also somewhat targetting the [Maddison et al paper](http://arxiv.org/abs/1412.6564).

#Pre-requisites

* python (tested with 2.7, but including lots of python3 compatibility headers, but gomill would need a bit of tweaking, if we want to run with full, real python 3)
* internet connection
* about 4GB disk space

#Instructions

These are written for linux.  They may need some slight tweaking for Windows

Type:

    git clone --recursive https://github.com/hughperkins/kgsgo-dataset-preprocessor.git
    cd kgsgo-dataset-preprocessor
    python kgs_dataset_preprocessor.py

#Results

Planned design, not implemented yet:
- the datasets are downloaded from http://u-go.net/gamerecords/, into `data` subdirectory
- processed into .dat files, with the same name as the unzipped zip files, just with `.dat` instead of `.zip`, also in `data` directory
- finally, consolidated together, into ~~two~~ three .dat file, in the `data` subdirectory:
  - `kgsgo-test.dat`: data from 100 games, randomly selected, and itemized in [test_samples.py](test_samples.py)
  - `kgsgo-train10k.dat`: data from 10,000 games, randomly selected, and non-overlapping with the test games
  - (and we can easily create a larger training data set, with everything except the test games, by just adding 3 lines in [kgs_dataset_preprocessor.py](kgs_dataset_preprocessor.py), at around line 315, but I figure I'm going to try with train10k first, before filling up my hard drive :-D

#Data format of resulting file

* it's a binary file, consisting of 1 or more fixed size records, followed by bytes 'E' 'N' 'D'
* Each record represents one labelled training example.  Each training example has the following format:
  * 2 bytes 'G' 'O', just to help verify alignment during loading
  * 2 bytes containing the label:
    * First byte is the `moverow`, 0 to 18
    * Second byte is the `movecol` 0 to 18
    * To get the `label` for this example, 0 to 360, you can calculate:
      * `row * 19 + column`
  * 361 bytes (19 by 19) containing the training features, representing a 19x19x8 cube
     * Each byte represents a vertical cross-section through the cube, 8 layers, with each bit as the value, 0 or 1
     * The bytes are laid out in rows, with 19 bytes per row, for a total of 19 rows, each of 19 bytes

#Data processing applied

* The data cubes created are derived from Go games, downloaded from http://u-go.net/gamerecords/ 
* each training example comprises one position in the game, with the label being the subsequent next move in the game
* goal is to predict the next move in the game (which might not always be the game-theoretic optimal move)
* The planes of each training data cube are derived as follows, with plane order starting from the least significant byte in each byte of training data:
  * plane 0: location has our own piece, with 1 liberty
  * plane 1: location has our own piece, with 2 liberties
  * plane 2: location has our own piece, with 3 or more liberties
  * plane 3: location has opponent piece, with 1 liberty
  * plane 4: location has opponent piece, with 2 liberties
  * plane 5: location has opponent piece, with 3 or more liberties
  * plane 6: location would be an illegal simple-ko
  * plane 7: always 1 (represents the valid area of the board, since we might be zero-padding the images during CNN training)

#MD5sum

When I run it, I get md5sums:
```
850d2c91b684de45f39a205378fd7967  kgsgo-test.dat
80cfa39797fa1ea32af30191b2fb962c  kgsgo-train10k.dat
```
If it's different, it doesn't necessarily matter, but if it's the same, it's a good sign :-)

#Third-party libraries used

* [gomill](https://github.com/mattheww/gomill.git)

#Related projects

I'm building a convolutional network library in OpenCL, aiming to train this, at [ClConvolve](https://github.com/hughperkins/ClConvolve)

