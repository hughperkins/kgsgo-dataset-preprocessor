# Copyright Hugh Perkins 2015 hughperkins at gmail
#
# This Source Code Form is subject to the terms of the Mozilla Public License, 
# v. 2.0. If a copy of the MPL was not distributed with this file, You can 
# obtain one at http://mozilla.org/MPL/2.0/.

import numpy as np

# doubly-indexed collection of locations on a board
# - given a location, can determine if it exists in the 'bag' of lcoations, in O(1)
# - can iterate over the locations, in time O(1) per locations
# - can remove a location, in O(1)
class Bag2d(object):
    def __init__(self, boardSize):
        self.boardSize = boardSize
        self.pieces = []
        self.board = np.zeros((boardSize,boardSize), dtype=np.int8)
        self.numPieces = 0

    def swapToEnd( self, index ):
       indexCombo = self.pieces[index];
       endCombo = self.pieces[numPieces - 1];
       self.pieces[index] = endCombo;
       self.pieces[numPieces - 1] = indexCombo;
       ( indexRow, indexCol ) = indexCombo
       ( endRow, endCol ) = endCombo
       self.board[ indexRow, indexCol] = self.numPieces - 1
       self.board[endRow, endCol] = index

    def insert( self, combo ):
        ( row, col ) = combo
        i1d = self.board[row,col]
        if( i1d >= 0 and i1d < self.numPieces and self.pieces[i1d] == combo ):
            return
        self.pieces.append( combo )
        self.board[row,col] = self.numPieces
        self.numPieces = self.numPieces + 1

    def erase( self, combo ):
        ( row, col ) = combo
        i1d = self.board[row, col]
        if( i1d >= 0 and i1d < self.numPieces and self.pieces[i1d] == combo ):
            self.pieces[i1d] = self.pieces[sel.fnumPieces - 1]
            movedcombo = self.pieces[i1d]
            ( movedrow, movedcol ) = movedcombo
            self.board[movedrow, movedcol] = i1d
            self.numPieces = self.numPieces - 1

    def erase( self, combo ):
        ( row, col ) = combo
        i1d = self.board[row, col]
        if( i1d >= 0 and i1d < self.numPieces and self.pieces[i1d] == combo ):
            self.pieces[i1d] = self.pieces[self.numPieces - 1];
            movedcombo = self.pieces[i1d];
            ( movedrow, movedcol ) = movedcombo
            self.board[movedrow, movedcol] = i1d
            self.numPieces = self.numPieces - 1

    def exists( self, combo ):
        ( row, col ) = combo
        i1d = self.board[row, col]
        if( i1d >= 0 and i1d < self.numPieces and self.pieces[i1d] == combo ):
            return True
        return False

    def size(self):
        return self.numPieces

    def __getitem__( self, i1d ):
        return self.pieces[i1d]

    def __str__(self):
        result = 'Bag2d\n'
        for row in range(0,self.boardSize ):
            thisline = ""
            for col in range(0, self.boardSize):
                if self.exists( (row, col) ):
                    thisline = thisline + "*"
                else:
                    thisline = thisline + "."
            result = result + thisline + "\n"
        return result

