<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [kgsgo-dataset-preprocessor](#kgsgo-dataset-preprocessor)
- [goal](#goal)
- [Pre-requisites](#pre-requisites)
- [Instructions](#instructions)
- [Results](#results)
- [Data format of resulting file](#data-format-of-resulting-file)
- [Data processing applied](#data-processing-applied)
- [MD5sum](#md5sum)
- [v2-format](#v2-format)
  - [md5 sums](#md5-sums)
  - [Example loader](#example-loader)
- [Third-party libraries used](#third-party-libraries-used)
- [Related projects](#related-projects)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# kgsgo-dataset-preprocessor
Dataset preprocessor for the KGS go dataset, eg according to Clark and Storkey input planes

#goal

The goal of this project is to take the data from the [kgsgo website](http://u-go.net/gamerecords/), and make it available into a somewhat generic format, that can be fed into any go-agnostic learning algorithm.  The guidelines
used for the creation of this project is to be able to somewhat reproduce the experiments in the [Clark and Storkey
paper](http://arxiv.org/abs/1412.3409), and also somewhat targetting the [Maddison et al paper](http://arxiv.org/abs/1412.6564).

#Pre-requisites

* python (tested with 2.7, but including lots of python3 compatibility headers, but gomill would need a bit of tweaking, if we want to run with full, real python 3)
* internet connection
* about 20GB disk space

# v1 vs v2 format

* both formats contain the same data
* v2 format is arguably a more generic format, eg it contains metadata inside describing the arrangement and type of the data

# v1 format

##Instructions

These are written for linux.  They may need some slight tweaking for Windows

Type:

    git clone --recursive https://github.com/hughperkins/kgsgo-dataset-preprocessor.git
    cd kgsgo-dataset-preprocessor
    python kgs_dataset_preprocessor.py

##Results

- the datasets are downloaded from http://u-go.net/gamerecords/, into `data` subdirectory
- processed into .dat files, with the same name as the unzipped zip files, just with `.dat` instead of `.zip`, also in `data` directory
- finally, consolidated together, into ~~two~~ three .dat file, in the `data` subdirectory:
  - `kgsgo-test.dat`: data from 100 games, randomly selected, and itemized in [test_samples.py](test_samples.py)
  - `kgsgo-train10k.dat`: data from 10,000 games, randomly selected, and non-overlapping with the test games
  - (and we can easily create a larger training data set, with everything except the test games, by just adding 3 lines in [kgs_dataset_preprocessor.py](kgs_dataset_preprocessor.py), at around line 315, but I figure I'm going to try with train10k first, before filling up my hard drive :-D

##Data format of resulting file

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

##MD5sum

When I run it, I get md5sums:
```
850d2c91b684de45f39a205378fd7967  kgsgo-test.dat
80cfa39797fa1ea32af30191b2fb962c  kgsgo-train10k.dat
```
If it's different, it doesn't necessarily matter, but if it's the same, it's a good sign :-)

# v2 format

## v2 format vs v1 format

After writing v1 format as detailed above, I noticed some things I'd prefer to do differently.  Therefore, v2
format modifies these things, but without changing anything detailed above.  If you continue to use `kg_dataset_preprocessor.py`, then the data produced will be unchanged.  In addition the filenames produced by v2
do not overwrite those produced by the earlier version.

v2 changes the following:
* run by doing `python kgs_dataset_preprocessor_v2.py`
* data files have a header, 1024 bytes, with the following format, eg:
```
mlv2-n=347-numplanes=7-imagewidth=19-imageheight=19-datatype=int-bpp=1
```
* where:
  * `n=` gives number of examples
  * `int` means the data is in ints, cf `float`, if in floats
  * `bpp=` gives the number of bits per pixel/point
* each data example is prefixed with 'GO' as before
* label is provided as a 4-byte integer, comprising `nextmoverow * 19 + nextmovecol`, in intel-endian
* data is arranged as in a sql 'group by' clause of: example, plane, row, column
* data is provided as a bitmap, eg where the 8 bits of the first byte represent the first 8 columns of the first row of the first plane
* bits are arranged so that if you wrote out the bytes in binary, the 1s and 0s would be arranged in order, ie in sql group by order of: plane, row, column
* bit continue to write into bytes, with no padding added, until the end of each example, eg if there are 4 plane, with imagewidth 1, imagewidth 1, and the first plane is 1, and the other are 0, then we'd have bits `1000`
* the final byte of each example is 0 padded, on the right hand side, so, in the example in the previous sentence, the byte would become `10000000`
* finally, compared to the previous version, only 7 planes are stored, the plane that is all 1s is omitted

## Running v2 format processor

```bash
python kgs_dataset_preprocessor_v2.py
```
Available options:
* `dir` specify the target directory, where the data will be downloaded to, and the datasets generated
* `sets` specify which sets to generate.  There are three sets available:
  * `test`: the test set, generated from 100 randomly selected, but fixed, games
  * `train10k`: training set, generated from 10,000 randomly selected, but fixed, games, non-overlapping with the test games
  * `trainall`: training set, generated from all games, excluding, and non-overlapping with, the test games
* eg you can do:
```bash
python kgs_dataset_preprocessor_v2.py dir=data sets=test,train10k,trainall
```
(this is the default in fact, if you run with no arguments)

## md5 sums

When I run this, I get the following md5 sums.  If these are different for you, it's not necessarily an issue.  If they are the same, this is a good sign :-)

```
57382be81ef419a5f1b1cf2632a8debf  kgsgo-test-v2.dat
6172e980f348103be3ad06ae7f946b47  kgsgo-train10k-v2.dat
20440801e72452b6714d5dd061673973  kgsgo-trainall-v2.dat
```

File sizes:
```
$ ls -lh kgsgo-*v2.dat
-rw-rw-r-- 1 ubuntu ubuntu 5.8M Feb  8 05:58 kgsgo-test-v2.dat
-rw-rw-r-- 1 ubuntu ubuntu 601M Feb  8 06:13 kgsgo-train10k-v2.dat
-rw-rw-r-- 1 ubuntu ubuntu  11G Mar  7 15:58 kgsgo-trainall-v2.dat
```

## Example loader

* Example of a loader for v2 format, in C++: [Kgsv2Loader.cpp](https://github.com/hughperkins/ClConvolve/blob/64783ebd2b0912f1f8d616cb497156199642b7c0/src/Kgsv2Loader.cpp)
* Note that this uses a couple of utility classes:
  * [FileHelper.h](https://github.com/hughperkins/ClConvolve/blob/64783ebd2b0912f1f8d616cb497156199642b7c0/src/FileHelper.h)
  * [stringhelper.cpp](https://github.com/hughperkins/ClConvolve/blob/64783ebd2b0912f1f8d616cb497156199642b7c0/src/stringhelper.cpp)

#Third-party libraries used

* [gomill](https://github.com/mattheww/gomill.git)

#Related projects

I'm building a convolutional network library in OpenCL, aiming to train this, at [ClConvolve](https://github.com/hughperkins/ClConvolve)

