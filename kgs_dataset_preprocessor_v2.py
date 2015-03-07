#!/usr/bin/python
#
# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

# assumptions:
# - at least python 2.7
# - not python 3.x
# - internet is available
# - on linux (since we're using signals)

from __future__ import absolute_import, division, print_function

import sys,os,time, os.path
import urllib
import zipfile
import shutil
#import numpy
import GoBoard
import multiprocessing
import signal
from os import sys, path
mydir = path.dirname(path.abspath(__file__))
print( mydir )
sys.path.append(mydir + '/gomill' )
import gomill
import gomill.sgf
#import gomill.handicap_layout

import index_processor
import zip_downloader
import dataset_partitioner

def addToDataFile( datafile, color, move, goBoard ):
    # color is the color of the next person to move
    # move is the move they decided to make
    # goBoard represents the state of the board before they moved
    # - we should flip the board and color so we are basically always black
    # - we should calculate liberties at each position
    # - we should get ko
    # - and we should write to the file :-)
    #
    # planes we should write:
    # 0: our stones with 1 liberty
    # 1: our stones with 2 liberty
    # 2: our stones with 3 or more liberties
    # 3: their stones with 1 liberty
    # 4: their stones with 2 liberty
    # 5: their stones with 3 or more liberty
    # 6: simple ko
    # 7: board... 
    (row,col) = move
    enemyColor = goBoard.otherColor( color )
    datafile.write('GO') # write something first, so we can sync/validate on reading
    label = row * 19 + col
    labelHighByte = label // 256
    labelLowbyte = label % 256
    datafile.write(chr(labelLowbyte))
    datafile.write(chr(labelHighByte))
    datafile.write(chr(0))
    datafile.write(chr(0))
    #datafile.write(chr(row)) # write the move
    #datafile.write(chr(col))
#    print( 'writing move: ' + str(row) + "," + str(col))
    thisbyte = 0
    thisbitpos = 0
    for plane in range(0, 7 ):
        for row in range( 0, goBoard.boardSize ):
            for col in range( 0, goBoard.boardSize ):
                thisbit = 0
                pos = (row,col)
                if goBoard.board.get(pos) == color:
                    if plane == 0 and goBoard.goStrings[pos].liberties.size() == 1:
                        thisbit = 1
                    elif plane == 1 and goBoard.goStrings[pos].liberties.size() == 2:
                        thisbit = 1
                    elif plane == 2:
                        thisbit = 1
                if goBoard.board.get(pos) == enemyColor:
                    if plane == 3 and goBoard.goStrings[pos].liberties.size() == 1:
                        thisbit = 1
                    elif plane == 4 and goBoard.goStrings[pos].liberties.size() == 2:
                        thisbit = 1
                    elif plane == 5:
                        thisbit = 1
                if plane == 6 and goBoard.isSimpleKo( color, pos ):
                        thisbit = 1
#                thisbyte = ( thisbyte << 1 ) + thisbit
                thisbyte = thisbyte + ( thisbit << ( 7 - thisbitpos ) )
                thisbitpos = thisbitpos + 1
                if thisbitpos == 8:
                    # thisbyte = thisbyte | 128
                    datafile.write( chr(thisbyte) )
                    thisbitpos = 0
                    thisbyte = 0
                    #print ( str( thisbyte - 128 ) + ' ', end= '')
            #print ( '')
        #print ( '')
    if thisbitpos != 0:
       datafile.write( chr(thisbyte) )

def writeFileHeader( datafile, N, numPlanes, boardSize, datatype, bitsPerPixel ):
    headerLine = 'mlv2'  # create a headerline, 1024 bytes
    headerLine = headerLine + '-n=' + str( N )
    headerLine = headerLine + '-numplanes=' + str(numPlanes)
    headerLine = headerLine + '-imagewidth=' + str(boardSize)
    headerLine = headerLine + '-imageheight=' + str(boardSize)
    headerLine = headerLine + '-datatype=' + datatype
    headerLine = headerLine + '-bpp=' + str( bitsPerPixel )
    print( headerLine )
    headerLine = headerLine + "\0\n" # \0 to end the string, and \n so we can use `strings` etc
    headerLine = headerLine + chr(0) * (1024-len(headerLine) )
    datafile.write( headerLine )
    
def walkthroughSgf( countOnly, datafile, sgfContents ):
    sgf = gomill.sgf.Sgf_game.from_string( sgfContents )
    # print sgf
    if sgf.get_size() != 19:
        print( 'boardsize not 19, ignoring' )
        return
    goBoard = GoBoard.GoBoard(19)
    doneFirstMove = False
    if sgf.get_handicap() != None and sgf.get_handicap() != 0:
        #print 'handicap not zero, ignoring (' + str( sgf.get_handicap() ) + ')'
        #handicappoints = gomill.handicap_layout.handicap_points( sgf.get_handicap(), 19 )
        numhandicap = sgf.get_handicap()
        #print sgf.get_root().get_setup_stones()
        #sys.exit(-1)
        #for move in getHandicapPoints( numhandicap ):
        for set in sgf.get_root().get_setup_stones():
            #print set
            for move in set:
                #print move
                goBoard.applyMove( 'b', move )
        #sys.exit(-1)
#        print( 'handicap: ' + str(numhandicap) )
        doneFirstMove = True
        #sys.exit(-1)
    # first, count number of moves...
    if countOnly:
        numMoves = 0
        countDoneFirstMove = doneFirstMove
        for it in sgf.main_sequence_iter():
            (color,move) = it.get_move()
            if color != None and move != None:
                #(row,col) = move
                if countDoneFirstMove:
                    numMoves = numMoves + 1
                    #addToDataFile( datafile, color, move, goBoard )
                countDoneFirstMove = True
        return numMoves
    #writeFileHeader( datafile, numMoves, 7, 19, 'int', 1 )
    moveIdx = 0
    for it in sgf.main_sequence_iter():
        (color,move) = it.get_move()
        if color != None and move != None:
            (row,col) = move
            if doneFirstMove:
                addToDataFile( datafile, color, move, goBoard )
            goBoard.applyMove( color, (row,col) )
            moveIdx = moveIdx + 1
            doneFirstMove = True

# unzip the zip, process the sgfs to .dat, and remove the unzipped directory
def processZip( sDirectoryName, sZipfilename, datfilename, indexlist ):
    sBasename = sZipfilename.replace('.zip', '')
    thiszip = zipfile.ZipFile( sDirectoryName + '/' + sZipfilename )
    namelist = thiszip.namelist()
    # first, count the total examples
    totalExamples = 0
    datafile = None
    for index in indexlist:
        print( 'index: ' + str(index) )
        name = namelist[index + 1] # skip name of directory
        print( name )
        if name.endswith('.sgf'):
            contents = thiszip.read( name )
            totalExamples = totalExamples + walkthroughSgf( True, datafile, contents )
        else:
            print('not sgf: [' + name + ']' )
            sys.exit(-1)
    # now write the examples, including the header
    datafile = open( sDirectoryName + '/' + datfilename + '~', 'wb' )
    writeFileHeader( datafile, totalExamples, 7, 19, 'int', 1 )
    for index in indexlist:
        print( 'index: ' + str(index) )
        name = namelist[index + 1] # skip name of directory
        print( name )
        if name.endswith('.sgf'):
            contents = thiszip.read( name )
            walkthroughSgf( False, datafile, contents )
        else:
            print('not sgf: [' + name + ']' )
            sys.exit(-1)
    datafile.write('END')
    datafile.close()
    os.rename( sDirectoryName + '/' + datfilename + '~', sDirectoryName + '/' + datfilename )
        
def worker( jobinfo ):
    try:
        (sDirectoryName, sZipfilename, sDatfilename, indexList ) = jobinfo
        processZip( sDirectoryName, sZipfilename, sDatfilename, indexList )
    except (KeyboardInterrupt, SystemExit):
       print( "Exiting child..." )
    except Exception as e:
       print( e )

# for each .zip file, if no .dat file, then unzip, process the sgfs, and create the .dat
# then remove the unzipped directory
# will use name parameter in name of dat file, and will only include games in the list
def zipsToDats( sTargetDirectory, samplesList, name ):
    iCount = 0
    zipNames = set()
    indexesByZipName = {}
    for sample in samplesList:
        (filename,index) = sample
        zipNames.add( filename )
        if not indexesByZipName.has_key( filename ):
           indexesByZipName[filename] = []
        indexesByZipName[filename].append( index )
    print( 'num zips: ' + str( len( zipNames ) ) )

    zipsToDo = []
    for zipName in zipNames:
        sBasename = zipName.replace('.zip','')
        sDatFilename = sBasename + name + '-v2.dat'
        if not os.path.isfile( sTargetDirectory + '/' + sDatFilename ):
            zipsToDo.append( ( sTargetDirectory, zipName, sDatFilename, indexesByZipName[zipName] ) )        

    cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool( processes = cores )
#    pool.map( loadAllSgfs, dirsToDo )
    p = pool.map_async( worker, zipsToDo )
    try:
        results = p.get(0xFFFF)
#        pool.close()
#        pool.join()
    except KeyboardInterrupt:
        print( "Caught KeyboardInterrupt, terminating workers" )
        pool.terminate()
        pool.join()
        sys.exit(-1)

def createSingleDat( targetDirectory, name, samples ):
    print( 'creating consolidated .dat...' )

    filePath = targetDirectory + '/kgsgo-' + name + '-v2.dat'    
    if os.path.isfile( filePath ):
        print( 'consolidated file ' + filePath + ' already exists :-)' )
        return

    # first check if we have all files
    # first need to get the names of all files
    # also, need to count total number of records
    numRecords = 0
    datfilesNeeded = set()
    for sample in samples:
        (filename, index ) = sample
        datfilesNeeded.add( filename )
    print( 'total dat files to be consolidated: ' + str( len( datfilesNeeded ) ) )
    datfilenames = []
    for zipfilename in datfilesNeeded:
        datfilename = zipfilename.replace('.zip','') + name + '-v2.dat'
        datfilenames.append(datfilename)
    allfilespresent = True
    for datfilename in datfilenames:
        if not os.path.isfile( targetDirectory + '/' + datfilename ):
            allfilespresent = False
            print( 'Missing dat file: ' + datfilename )
            sys.exit(-1)
        childdatfile = open( targetDirectory + '/' + datfilename, 'rb' )
        header = childdatfile.read(1024)
        thisN = int( header.split('-n=')[1].split('-')[0] )
        childdatfile.close()
        numRecords = numRecords + thisN
        print( 'child ' + datfilename + ' N=' + str(thisN) )

    consolidatedfile = open( filePath + '~', 'wb' )
    writeFileHeader( consolidatedfile, numRecords, 7, 19, 'int', 1 )
    for filename in datfilenames:
        print( 'reading from ' + filename + ' ...' )
        filepath = targetDirectory + '/' + filename
        singledat = open( filepath, 'rb' )
        # first, skip header
        singledat.read(1024)
        data = singledat.read()
        if data[-3:] != 'END':
            print( 'Invalid file, doesnt end with END: ' + filepath )
            sys.exit(-1)
        consolidatedfile.write( data[:-3] )
        singledat.close()
    consolidatedfile.write( 'END' )
    consolidatedfile.close()
    os.rename( filePath + '~', filePath )

def go(sTargetDirectory, sets):
    print( 'go' )
    if not os.path.isdir( sTargetDirectory ):
        os.makedirs( sTargetDirectory )
    index_processor.get_fileInfos( sTargetDirectory )
    zip_downloader.downloadFiles( sTargetDirectory )

    if 'test' in sets:
        test_samples = dataset_partitioner.draw_test_samples( sTargetDirectory )
        zipsToDats( sTargetDirectory, test_samples, 'test' )
        createSingleDat(sTargetDirectory, 'test', test_samples )

    if 'train10k' in sets:
        train10k_samples = dataset_partitioner.draw_training_10k( sTargetDirectory )
        zipsToDats( sTargetDirectory, train10k_samples, 'train10k' )
        createSingleDat(sTargetDirectory, 'train10k', train10k_samples )

    if 'trainall' in sets:
        trainall_samples = dataset_partitioner.draw_all_training( sTargetDirectory )
        zipsToDats( sTargetDirectory, trainall_samples, 'trainall' )
        createSingleDat(sTargetDirectory, 'trainall', trainall_samples )

def printUsage():
    print( 'Usage: python ' + sys.argv[0] + ' [options]' )
    print( 'Options:' )
    print( '  dir=[target directory]')
    print( '  sets=[list of sets, eg: test,train10k,trainall.  Available sets: test,train10k,trainall]')

def processArgs():
    sTargetDirectory = 'data'
    sets = [ 'test', 'train10k', 'trainall' ]
    for arg in sys.argv[1:]:
        splitarg = arg.split('=')
        print( 'arg: [' + arg + ']' )
        if( len(splitarg) != 2 ):
            print('options should be provided in form [key]=[value], eg dir=data')
            printUsage()
            return
        key = splitarg[0]
        value = splitarg[1]
        print('key: ' + key )
        if key == 'dir':
            sTargetDirectory = value
        elif key == 'sets':
            sets = value.split(',')
            for thisset in sets:
                if not thisset in ['test', 'train10k', 'trainall']:
                    print('unrecognized set: ' + thisset )
                    printUsage()
                    return
        else:
            print('unrecognized option ' + key )
            printUsage()
            return
    print( 'target directory: ' + sTargetDirectory )
    print( 'generate sets: ' + str( sets ) )
    go(sTargetDirectory, sets)

if __name__ == '__main__':
    processArgs()

