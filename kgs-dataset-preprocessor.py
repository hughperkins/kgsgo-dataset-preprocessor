#!/usr/bin/python

# assumptions:
# - at least python 2.7
# - not python 3.x
# - internet is available

import sys,os,time, os.path
import urllib
import zipfile
import shutil

sKgsUrl = 'http://u-go.net/gamerecords/'

def downloadPage( url ):
    fp = urllib.urlopen(url)
    data = fp.read()
    fp.close()
    return data

def downloadFiles( sTargetDirectory, iMaxFiles ):
    global sKgsUrl
    page = downloadPage( sKgsUrl )
#    print page
    splitpage = page.split('<a href="')
    iCount = 0
    for downloadUrlBit in splitpage:
        if downloadUrlBit.startswith( "http://" ):
            downloadUrl = downloadUrlBit.split('">Download')[0]
            if downloadUrl.endswith('.zip'):
                print downloadUrl
                sFilename = os.path.basename( downloadUrl )
                if not os.path.isfile( sTargetDirectory + '/' + downloadUrl ):
                    print 'downloading ' + downloadUrl + ' ... '
                    urllib.urlretrieve ( downloadUrl, sTargetDirectory + '/~' + sFilename )
                    os.rename( sTargetDirectory + '/~' + sFilename, sTargetDirectory + '/' + sFilename )
        iCount = iCount + 1
        if iMaxFiles != -1 and iCount > iMaxFiles:
            print 'reached limit of files you requested, skipping other downlaods'
            return

def unzipFiles( sTargetDirectory, iMaxFiles ):
    iCount = 0
    for sFilename in os.listdir( sTargetDirectory ):
        sFilepath = sTargetDirectory + '/' + sFilename
        if os.path.isfile( sFilepath ) and not sFilename.startswith('~'):
            #print sFilepath
            thiszip = zipfile.ZipFile( sFilepath )
            zipdirname = thiszip.namelist()[0]
            if not os.path.isdir( sTargetDirectory + '/' + zipdirname ):
                print 'unzipping ' + sFilepath + '...'
                thiszip.extractall( sTargetDirectory + '/~' + zipdirname )
                shutil.move( sTargetDirectory + '/~' + zipdirname + '/' + zipdirname, sTargetDirectory )
                os.rmdir( sTargetDirectory + '/~' + zipdirname )
            iCount = iCount + 1
            if iMaxFiles != -1 and iCount > iMaxFiles:
                print 'reached limit of files you requested, skipping other unzips'
                return

def go(sTargetDirectory, iMaxFiles):
    print 'go'
    if not os.path.isdir( sTargetDirectory ):
        os.makedirs( sTargetDirectory )
    downloadFiles( sTargetDirectory, iMaxFiles )
    unzipFiles( sTargetDirectory, iMaxFiles )

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: ' + sys.argv[0] + ' [targetdirectory] [[maxfiles]]'
        print '[maxfiles] is optional argument, to limit how many files to download/process'
        sys.exit(-1)
    sTargetDirectory = sys.argv[1]
    iMaxFiles = -1
    if len(sys.argv) >= 3:
        iMaxFiles = int( sys.argv[2] )
    go(sTargetDirectory, iMaxFiles)

