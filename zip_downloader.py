#!/usr/bin/python
#
# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

# this module will download the modules from the kgsgo archive site

from __future__ import print_function, unicode_literals, division, absolute_import

import sys, os, time
import urllib
import multiprocessing

import index_processor

def downloadUrl( downloadUrl, targetPath ):
    urllib.urlretrieve ( downloadUrl, targetPath + '~' )
    os.rename( targetPath + '~', targetPath )

def worker( urlAndTargetPath ):
    #    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        ( url, targetPath ) = urlAndTargetPath
        print('downloading ' + targetPath + ' ...' )
        downloadUrl( url, targetPath )
        print( '... ' + targetPath + ' done' )
    except (KeyboardInterrupt, SystemExit):
        print( "Exiting child..." )

def downloadFiles( sTargetDirectory ):
    fileInfos = index_processor.get_fileInfos( sTargetDirectory )
    urlsToDo = []
    for fileinfo in fileInfos:
        url = fileinfo['url']
        print( url )
        sFilename = fileinfo['filename']
        if not os.path.isfile( sTargetDirectory + '/' + sFilename ):
            urlsToDo.append( ( url, sTargetDirectory + '/' + sFilename ) )
            print( 'to do: ' + url + ' ... ' )
    pool = multiprocessing.Pool( processes = 16 )
    try:
        it = pool.imap( worker, urlsToDo,  )
        for i in it:
            # print( i )
            pass
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print( "Caught KeyboardInterrupt, terminating workers" )
        pool.terminate()
        pool.join()
        sys.exit(-1)

def go( dataDirectory ):
    if not os.path.isdir( sTargetDirectory ):
        os.makedirs( sTargetDirectory )
    downloadFiles( dataDirectory )
    
if __name__ == '__main__':
    sTargetDirectory = 'data'
    if len(sys.argv) == 2:
        sTargetDirectory = sys.argv[1]
#    else:
#        print('Usage: ' + sys.argv[0] + ' [data directory]' )
#        sys.exit(-1)
    go(sTargetDirectory)


