#!/usr/bin/python
#
# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, division, print_function

import sys,os,time, os.path
import zipfile

mydir = os.path.dirname(os.path.abspath(__file__))
print( mydir )
sys.path.append(mydir + '/gomill' )
import gomill
import gomill.sgf
#import gomill.handicap_layout

import kgs_dataset_preprocessor

def scanZip( zipfilepath ):
    thiszip = zipfile.ZipFile( zipfilepath )
    for name in thiszip.namelist():
        #print( name )
        if name.endswith('.sgf'):
            sgfContents = thiszip.read( name )
            #sgf = gomill.sgf.Sgf_game.from_string( sgfContents )
            #print( sgfContents )
            try:
                whiterank = sgfContents.split("\nWR[")[1].split("]")[0]
                blackrank = sgfContents.split("\nBR[")[1].split("]")[0]
                print( whiterank + " " + blackrank )
            except:
                print( "[not known]" )
            #sys.exit(-1)

def go( sTargetDirectory ):
    for sZipfilename in os.listdir( sTargetDirectory ):
        if sZipfilename.endswith('.zip'):
            scanZip( sTargetDirectory + '/' + sZipfilename )
        
if __name__ == '__main__':
    sTargetDirectory = 'data'
    go( sTargetDirectory )

