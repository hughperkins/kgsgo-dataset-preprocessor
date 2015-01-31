#!/usr/bin/python
#
# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

# goal of this is to partition the data into two sets:
# - training data
# - testing data
#
# These sets will be assigned according to the following principles:
# - both sets should be relatively stable, not change as new archive data is available
# - test set should be not too big, but large enough that accuracy will be to around 0.1%
# - training set will contain the rest of the data
# - the same matches should not be present in both training and test set (not even different moves from
#   the same match)
# - should probably be documented which are in which perhaps?  eg stored as a python file in the 
#   repository (or as a yaml file?)

from __future__ import print_function, unicode_literals, division, absolute_import

import sys, os, time

def go():
    pass

# pre-requisites:
# - have already downloaded the zip files
if __name__ == '__main__':
    sTargetDirectory = 'data'
    if len(sys.argv) == 2:
        sTargetDirectory = sys.argv[1]
    else:
        print('Usage: ' + sys.argv[0] + ' [data directory]' )
        sys.exit(-1)
    go(sTargetDirectory)


