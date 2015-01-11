#!/usr/bin/python

# assumptions:
# - at least python 2.7
# - not python 3.x
# - internet is available

import sys,os,time, os.path
import urllib

sKgsUrl = 'http://u-go.net/gamerecords/'

def downloadPage( url ):
    fp = urllib.urlopen(url)
    data = fp.read()
    fp.close()
    return data

def go(sTargetDirectory):
    global sKgsUrl
    print 'go'
    if not os.path.isdir( sTargetDirectory ):
        os.makedirs( sTargetDirectory )
    page = downloadPage( sKgsUrl )
#    print page
    splitpage = page.split('<a href="')
    for downloadUrlBit in splitpage:
        if not downloadUrlBit.startswith( "http://" ):
            continue
        downloadUrl = downloadUrlBit.split('">Download')[0]
        if not downloadUrl.endswith('.zip'):
            continue
        print downloadUrl
        sFilename = os.path.basename( downloadUrl )
        if os.path.isfile( sTargetDirectory + '/' + downloadUrl ):
            continue
        print 'downloading ' + downloadUrl + ' ... '
        urllib.urlretrieve ( downloadUrl, sTargetDirectory + '/~' + sFilename )
        os.rename( sTargetDirectory + '/~' + sFilename, sTargetDirectory + '/' + sFilename )

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: ' + sys.argv[0] + ' [targetdirectory]'
        sys.exit(-1)
    sTargetDirectory = sys.argv[1]
    go(sTargetDirectory)

