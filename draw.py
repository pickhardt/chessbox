#! /usr/bin/env python

# Code sourced from:
# http://mip.noekeon.org/HTMLTTChess/chess_merida_unicode.html
# http://wordaligned.org/articles/drawing-chess-positions

'''Code to draw chess board and pieces.

FEN notation to describe the arrangement of peices on a chess board.

White pieces are coded: K, Q, B, N, R, P, for king, queen, bishop,
rook knight, pawn. Black pieces use lowercase k, q, b, n, r, p. Blank
squares are noted with digits, and the "/" separates ranks.

As an example, the game starts at:

rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR

See: http://en.wikipedia.org/wiki/Forsyth-Edwards_Notation
'''
import re
import os
import Image
import ImageDraw
import ImageFont

class BadChessboard(ValueError):
  def __init__(self, *args):
    # *args is used to get a list of the parameters passed in
    self.args = [a for a in args]
    
def expand_blanks(fen):
  '''Expand the digits in an FEN string into spaces
  
  >>> expand_blanks("rk4q3")
  'rk    q   '
  '''
  def expand(match):
    return ' ' * int(match.group(0))
  return re.compile(r'\d').sub(expand, fen)

def check_valid(expanded_fen):
  '''Asserts an expanded FEN string is valid'''
  match = re.compile(r'([KQBNRPkqbnrp ]{8}/){8}$').match
  if not match(expanded_fen + '/'):
    raise BadChessboard(expanded_fen)

def expand_fen(fen):
  '''Preprocesses a fen string into an internal format.
  
  Each square on the chessboard is represented by a single 
  character in the output string. The rank separator characters
  are removed. Invalid inputs raise a BadChessboard error.
  '''
  expanded = expand_blanks(fen)
  check_valid(expanded)
  return expanded.replace('/', '')
    
def draw_board(n=8, sq_size=(20, 20)):
  '''Return an image of a chessboard.
  
  The board has n x n squares each of the supplied size.'''
  from itertools import cycle
  def square(i, j):
    return i * sq_size[0], j * sq_size[1]
  opaque_grey_background = 192, 255
  board = Image.new('LA', square(n, n), opaque_grey_background) 
  draw_square = ImageDraw.Draw(board).rectangle
  whites = ((square(i, j), square(i + 1, j + 1))
    for i_start, j in zip(cycle((0, 1)), range(n))
    for i in range(i_start, n, 2))
  for white_square in whites:
    draw_square(white_square, fill='white')
  return board

    
def chess_position_using_font(fen, font_file, sq_size):
  '''Return a chess position image.
  
  font_file - the name of a font file
  sq_size - the size of each square on the chess board
  '''
  font = ImageFont.truetype(font_file, sq_size)
  pieces = expand_fen(fen)
  board = draw_board(sq_size=(sq_size, sq_size))
  put_piece = ImageDraw.Draw(board).text
  unichr_pieces=dict(
    zip("KQRBNPkqrbnp", (unichr(uc) for uc in range(0x2654, 0x2660))))
  
  def point(i, j):
    return i * sq_size, j * sq_size
  
  def not_blank(pt_pce):
    return pt_pce[1] != ' '
  
  def is_white_piece(piece):
    return piece.upper() == piece
  
  squares = (point(i, j) for j in range(8) for i in range(8))
  for square, piece in filter(not_blank, zip(squares, pieces)):
    if is_white_piece(piece):
      # Use the equivalent black piece, drawn white,
      # for the 'body' of the piece, so the background
      # square doesn't show through.
      filler = unichr_pieces[piece.lower()]
      put_piece(square, filler, fill='white', font=font)
    else:
      filler = unichr_pieces[piece.upper()]
      put_piece(square, filler, fill='white', font=font)
    put_piece(square, unichr_pieces[piece], fill='black', font=font)
  return board
