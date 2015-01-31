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

# should unzip sZipfilename inside a directory with same name, but '.zip' removed
# will unzip to create a new subdirectory inside this directory, so the sgfs will be two levels
# down
# this way the top level subdirectory name matches the zipfile name, so easy to reconcile/match
def unzipFile( sTargetDirectory, sZipfilename ):
    zipfilepath = sTargetDirectory + '/' + sZipfilename
    thiszip = zipfile.ZipFile( zipfilepath )
    zipdirname = thiszip.namelist()[0]
    print( 'unzipping ' + zipfilepath + '...' )
    thiszip.extractall( sTargetDirectory + '/~' + sZipfilename.replace(".zip","~" ) )
    sBasename = replace( sZipfilename, ".zip","" )
    os.rename( sTargetDirectory + '/~' + sBasename, sTargetDirectory + '/' + sBasename )
    #shutil.move( sTargetDirectory + '/~' + zipdirname + '/' + zipdirname, sTargetDirectory )
    #os.rmdir( sTargetDirectory + '/~' + zipdirname )
    return sTargetDirectory + '/' + sBasename + '/' + zipdirname

def unzipFiles( sTargetDirectory, iMaxFiles ):
    iCount = 0
    for sFilename in os.listdir( sTargetDirectory ):
        sFilepath = sTargetDirectory + '/' + sFilename
        if os.path.isfile( sFilepath ) and not sFilename.startswith('~') and sFilename.endswith('.zip'):
            #print sFilepath
            thiszip = zipfile.ZipFile( sFilepath )
            zipdirname = thiszip.namelist()[0]
            if not os.path.isdir( sTargetDirectory + '/' + zipdirname ):
                print( 'unzipping ' + sFilepath + '...' )
                thiszip.extractall( sTargetDirectory + '/~' + zipdirname )
                shutil.move( sTargetDirectory + '/~' + zipdirname + '/' + zipdirname, sTargetDirectory )
                os.rmdir( sTargetDirectory + '/~' + zipdirname )
            iCount = iCount + 1
            if iMaxFiles != -1 and iCount > iMaxFiles:
                print( 'reached limit of files you requested, skipping other unzips' )
                return

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
    datafile.write(chr(row)) # write the move
    datafile.write(chr(col))
#    print( 'writing move: ' + str(row) + "," + str(col))
    for row in range( 0, goBoard.boardSize ):
        for col in range( 0, goBoard.boardSize ):
            thisbyte = 0
            pos = (row,col)
            if goBoard.board.get(pos) == color:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    thisbyte = thisbyte | 1
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    thisbyte = thisbyte | 2
                else:
                    thisbyte = thisbyte | 4
            if goBoard.board.get(pos) == enemyColor:
                if goBoard.goStrings[pos].liberties.size() == 1:
                    thisbyte = thisbyte | 8
                elif goBoard.goStrings[pos].liberties.size() == 2:
                    thisbyte = thisbyte | 16
                else:
                    thisbyte = thisbyte | 32
            if goBoard.isSimpleKo( color, pos ):
                thisbyte = thisbyte | 64
            thisbyte = thisbyte | 128
            datafile.write( chr(thisbyte) )
            #print ( str( thisbyte - 128 ) + ' ', end= '')
        #print ( '')
    #print ( '')

def walkthroughSgf( datafile, sgfContents ):
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
    moveIdx = 0
    for it in sgf.main_sequence_iter():
        (color,move) = it.get_move()
#        print( 'color ' + str(color) )
#        print( move )
        if color != None and move != None:
            (row,col) = move
            if doneFirstMove and datafile != None:
                addToDataFile( datafile, color, move, goBoard )
            #print 'applying move ' + str( moveIdx )
            goBoard.applyMove( color, (row,col) )
            #print goBoard
            moveIdx = moveIdx + 1
            doneFirstMove = True
            #if moveIdx >= 120:
            #    sys.exit(-1)
    #print( goBoard )
    #print 'winner: ' + sgf.get_winner()

def loadSgf( datafile, sgfFilepath ):
    sgfile = open( sgfFilepath, 'r' )
    contents = sgfile.read()
    sgfile.close()
#        print contents
    if contents.find( 'SZ[19]' ) < 0:
        print( 'not 19x19, skipping' )
        return
    try:
        walkthroughSgf( datafile, contents )
    except:
        print( "exception caught for file " + path.abspath( sgfFilepath ) )
        raise 
    #print( sgfFilepath )

def loadAllSgfs( sDirPath ):
    iCount = 0
    datafile = open( sDirPath + '.~dat', 'wb' )
    for sSgfFilename in os.listdir( sDirPath ):
#        print sSgfFilename
        #print( '.', end='')
        if iCount > 0 and iCount % 80 == 0:
            print( "processed " + str(iCount) + " sgf files" )
        loadSgf( datafile, sDirPath + '/' + sSgfFilename )
        iCount = iCount + 1
    datafile.write('END')
    datafile.close()
    os.rename( sDirPath + '.~dat', sDirPath + '.dat' )

# unzip the zip, process the sgfs to .dat, and remove the unzipped directory
def processZip( sDirectoryName, sZipfilename  ):
    sBasename = sZipfilename.replace('.zip', '')
    thiszip = zipfile.ZipFile( sDirectoryName + '/' + sZipfilename )
    datafile = open( sDirectoryName + '/' + sBasename + '.~dat', 'wb' )
    for name in thiszip.namelist():
        print( name )
        if name.endswith('.sgf'):
            contents = thiszip.read( name )
            #print( contents )
            walkthroughSgf( datafile, contents )
#            sys.exit(-1)
            #break
    datafile.write('END')
    datafile.close()
    os.rename( sDirectoryName + '/' + sBasename + '.~dat', sDirectoryName + '/' + sBasename + '.dat' )
    
    #unzippedDirectory = unzipFile( sDirectoryName, sZipfilename )
    #sBasename = sZipfilename.replace( ".zip", "" )
    #datafile = open( sDirectoryName + '/' + sBasename + '.~dat', 'wb' )
    #for sSgfFilename in os.listdir( unzippedDirectory ):
#        loadSgf( datafile, sDirPath + '/' + sSgfFilename )
#        iCount = iCount + 1
#    datafile.write('END')
#    datafile.close()
#    os.rename( sDirectoryName + '/' + sBasename + '.~dat', sDirectoryName + '/' + sBasename + '.dat' )
#    shutil.rmtree( sDirectoryName + '/' + sBasename
    
def worker( directoryandzipfilepath ):
#    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        (sDirectoryName, sZipfilename ) = directoryandzipfilepath
        processZip( sDirectoryName, sZipfilename )
    except (KeyboardInterrupt, SystemExit):
       print( "Exiting child..." )

#def init_worker():
#    signal.signal(signal.SIGINT, signal.SIG_IGN)

def createSingleDat( targetDirectory ):
    print( 'creating consolidated .dat...' )
    consolidatedfile = open( targetDirectory + '/kgsgo.~dat', 'wb' )
    for filename in os.listdir( sTargetDirectory ):
        filepath = sTargetDirectory + '/' + filename
        if os.path.isfile( filepath ) and filename.endswith('.dat'):
            singledat = open( filepath, 'rb' )
            data = singledat.read()
            if data[-3:] != 'END':
                print( 'Invalid file, doesnt end with END' )
            consolidatedfile.write( data[:-3] )
            singledat.close()
    consolidatedfile.write( 'END' )
    consolidatedfile.close()
    os.rename( targetDirectory + '/kgsgo.~dat', targetDirectory + '/kgsgo.dat' )

# for each .zip file, if no .dat file, then unzip, process the sgfs, and create the .dat
# then remove the unzipped directory
def zipsToDats( sTargetDirectory, iMaxFiles ):
    iCount = 0
    zipsToDo = []
    for sZipfilename in os.listdir( sTargetDirectory ):
        #sFilepath = sTargetDirectory + '/' + 
        if sZipfilename.endswith('.zip'):
            sBasename = sZipfilename.replace('.zip','')
            if not os.path.isfile( sTargetDirectory + '/' + sBasename + '.dat' ):
                zipsToDo.append( ( sTargetDirectory, sZipfilename ) )
            iCount = iCount + 1
            if iMaxFiles > 0 and iCount >= iMaxFiles:
                break
    #for dirpath in dirsToDo:
    #    loadAllSgfs( dirpath )
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

def go(sTargetDirectory, iMaxFiles):
    print( 'go' )
    if not os.path.isdir( sTargetDirectory ):
        os.makedirs( sTargetDirectory )
    downloadFiles( sTargetDirectory, iMaxFiles )
    # unzipFiles( sTargetDirectory, iMaxFiles )
    zipsToDats( sTargetDirectory, iMaxFiles )
    # make one single .dat file
    createSingleDat(sTargetDirectory)

if __name__ == '__main__':
    sTargetDirectory = 'data'
    if len(sys.argv) >= 2:
        sTargetDirectory = sys.argv[1]
    iMaxFiles = -1
    if len(sys.argv) >= 3:
        iMaxFiles = int( sys.argv[2] )
    go(sTargetDirectory, iMaxFiles)

