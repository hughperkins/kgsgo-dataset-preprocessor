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
from os import path, sys
sys.path.append( path.dirname(path.abspath(__file__)) + '/thirdparty/future/src' )
from builtins import ( bytes, dict, int, list, object, range, str, ascii, chr,
   hex, input, next, oct, open, pow, round, super, filter, map, zip )

import sys, os, time, random

import index_processor

numTestGames = 100
testGames = []
trainGames = []

def draw_samples( dataDirectory, numSamples ):
    # draws filename, and game index number, from the available games
    # without replacement (so we should check for dupes :-( )

    # first we should create a single list, containing pairs of ( filename, gameindex )
    # then we will draw samples from this
    # we should restrict the available games to something static, eg everything up to dec 2014, inclusive
    availableGames = []
    fileinfos = index_processor.get_fileInfos( dataDirectory )
    for fileinfo in fileinfos:
        filename = fileinfo['filename']
        year = int( filename.split('-')[1].split('_')[0] )
        if year > 2014:
            continue  # ignore after 2014, to keep the set of games fixed
        numgames = fileinfo['numGames']
        for i in range( numgames + 1 ):
            availableGames.append( ( filename, i ) )
    print( 'total num games: ' + str( len( availableGames ) ) )

    # need to seed random first
    random.seed(0)
    
    samplesSet = set()
    while len( samplesSet ) < numSamples:
        sample = random.choice( availableGames )
        if sample not in samplesSet:
            samplesSet.add( sample )
    print( 'Drawn ' + str( numSamples ) + ' samples:' )
    # copy to list
    samples = list( samplesSet )
    return samples

def draw_training_games( dataDirectory ):
    # gets list of all non-test games, that are no later than dec 2014
    global testGames
    train_games = []
    fileinfos = index_processor.get_fileInfos( dataDirectory )
    for fileinfo in fileinfos:
        filename = fileinfo['filename']
        year = int( filename.split('-')[1].split('_')[0] )
        if year > 2014:
            continue  # ignore after 2014, to keep the set of games fixed
        numgames = fileinfo['numGames']
        for i in range( numgames + 1 ):
            sample = ( filename, i )
            if sample not in testGames:
                train_games.append( sample )
    print( 'total num training games: ' + str( len( train_games ) ) )

def draw_test_samples( dataDirectory ):
    global numTestGames, testGames
    if len( testGames ) > 0:
        return testGames
    try:
        testSampleFile = open( 'test_samples.py', 'r' )
        samplesContents = testSampleFile.read()
        testSampleFile.close()
        for line in samplesContents.split('\n'):
            #print( line )
            if line != "":
                ( filename, count ) = eval( line )
                testGames.append( ( filename, count ) )
    except Exception as e:
        print( e )
        testGames = draw_samples( dataDirectory, numTestGames )
        testSampleFile = open( '~test_samples.py', 'w' )
        for sample in testGames:
            testSampleFile.write( str( sample ) + "\n" )
        testSampleFile.close()
        os.rename( '~test_samples.py', 'test_samples.py' )
#    for sample in testGames:
#        print( 'testgame: ' + str( sample ) )
    return testGames

def go(dataDirectory):
    testsamples = draw_test_samples( dataDirectory )
    for sample in testsamples:
        print( 'testgame: ' + str( sample ) )
    # all other games are training games...
    draw_training_games( dataDirectory )
        
if __name__ == '__main__':
    sTargetDirectory = 'data'
    if len(sys.argv) == 2:
        sTargetDirectory = sys.argv[1]
    go(sTargetDirectory)


