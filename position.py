# Credit to Renato de Pontes Pereira, renato.ppontes at gmail dot com
# for py pgn parser

#import pdb
import re
from common import *
from draw import *

class Position:
  """Represents a position."""

  def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
    self._generate_from_fen(fen)
  
  def can_castle(self, player, side):
    side = side[0].lower() # e.g. "king" becomes "k"x
    player = player[0].lower() # e.g. "king" becomes "k"
    
    if player == "w":
      side_letter = side_letter.upper()
    else:
      side_letter = side_letter.lower()
    
    return side_letter in self.castle_info
  
  def can_current_player_castle(self, side):
    return self.can_castle(self.current_player, side)
    
  def get_piece(self, symbol=None, end_square=None, player=None, extra={}):
    if not player:
      player = self.current_player
  
    if not symbol and not end_square:
      raise BaseException("Must pass either symbol or end_square.")
  
    for piece in self.pieces:
      if player != piece.player:
        continue
  
      if symbol.lower() != piece.lower_symbol:
        continue
  
      if piece.can_move_to(end_square):
        if "move_from" not in extra:
          return piece
        elif extra["move_from"] in piece.position:
            return piece
  
  def get_square(self, position):
    for piece in self.pieces:
      if piece.position == position:
        return piece
    return None
  
  def generate_fen(self, flip=False):
    return "%s %s %s %s %s %s" % (self.generate_piece_placement_fen(flip), self.current_player, self.castle_info, self.enpassant, self.halfmove_clock, self.move_number)
  
  def generate_piece_placement_fen(self, flip=False):
    column_letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    
    line_info = ""
    
    for row_negative_number in range(8):
      if not flip:
        row_number = 8 - row_negative_number
      else:
        row_number = 1 + row_negative_number
      
      empty_squares = 0

      for column_number in range(8):
        column_index = column_number
        if flip:
          column_index = 7 - column_number
        
        position = "%s%i" % (column_letters[column_index], row_number)
        piece = self.get_square(position)
        
        if piece:
          if empty_squares > 0:
            line_info += str(empty_squares)
            empty_squares = 0
          line_info += piece.symbol
        else:
          empty_squares += 1
      
      if empty_squares > 0:
        line_info += str(empty_squares)
      
      if (not flip and row_number != 1) or (flip and row_number != 8):
        line_info += "/"
      
    return line_info
  
  def castle(self, which_side):
    player = self.current_player
    if player == "w":
      row = 1
      self.castle_info = self.castle_info.replace("k", "")
      self.castle_info = self.castle_info.replace("q", "")
    else:
      row = 8
      self.castle_info = self.castle_info.replace("K", "")
      self.castle_info = self.castle_info.replace("Q", "")
    
    if self.castle_info == "":
      self.castle_info = "-"
    
    king_start_col = "e"
    if which_side == "k":
      rook_start_col = "h"
      rook_end_col = "f"
      king_end_col = "g"
    elif which_side =="q":
      rook_start_col = "a"
      rook_end_col = "d"
      king_end_col = "c"
    else:
      raise BaseException("Cannot castle to unknown side '%s'" % which_side)

    king = self.get_square("%s%s" % (king_start_col, row))
    assert king.lower_symbol == "k"
    king.position = "%s%s" % (king_end_col, row)
    
    rook = self.get_square("%s%s" % (rook_start_col, row))
    assert rook.lower_symbol == "r"
    rook.position = "%s%s" % (rook_end_col, row)
    
    return "%s%s" % (king_start_col, row), "%s%s" % (king_end_col, row), ""
        
  def move(self, command):
    """
    command can be along the lines of:
        a2-a4, a2a4, Nf3, Nge6, cxd5, a8=Q, 
        Ba6+, Re8#, 0-0, O-O, 0-0-0, O-O-O, Qxd7+
    
     What is not currently supported?
        descriptive notation
    """
    command = command.strip()
    before_square, after_square, extra = self.move_process_main(command)
    self.move_postprocess()
    return before_square, after_square, extra
  
  def move_process_main(self, command):
    if command in ["O-O", "o-o", "0-0"]:
      return self.castle("k")
    
    if command in ["O-O-O", "o-o-o", "0-0-0"]:
      return self.castle("q")
    
    matching = re.match(r'^([BNRQK])([a-h])?x?([a-h][0-8])', command)
    if matching:
      move_piece_command = command
      move_from_info = matching.groups()[1]
      extra = {}
      if move_from_info:
        extra = {"move_from": move_from_info}
        move_piece_command = "%s%s" % (matching.groups()[0], matching.groups()[2])
      return self.move_piece(move_piece_command, extra)
    
    matching = re.match(r'^([a-h][0-8])-?([a-h][0-8])', command)
    if matching:
      move_from = matching.groups()[0]
      move_to = matching.groups()[1]
      return self.move_from_to(move_from, move_to, command)
    
    matching = re.match(r'^([a-h][0-8]-)?([a-h][0-8])', command)
    if matching:
      return self.move_pawn(matching.groups()[1])
    
    matching = re.match(r'[a-h]x[a-h][0-8]', command)
    if matching:
      return self.take_with_pawn(command)
    
    matching = re.match(r'([a-h])[0-8]x([a-h][0-8])', command)
    if matching:
      return self.take_with_pawn("%sx%s%s" % (matching.groups()[0], matching.groups()[1], matching.groups()[2]))
    
    return "", "", ""
  
  def generate_image(self, flip=False):
    board = chess_position_using_font(self.generate_piece_placement_fen(flip), os.getcwd() + '/chess_merida_unicode.ttf', 64)
    return board
  
  def save_image(self, filename, flip=False):
    board = self.generate_image(flip)
    board.convert('RGB').save("%s" % filename)
    
  def take_with_pawn(self, command):
    after_position = command[2:4]
    
    before_col = command[0]
    before_row = int(command[3])
    
    if self.current_player == "w":
      before_row -= 1
    else:
      before_row += 1
    
    before_position = "%s%i" % (before_col, before_row)    
    piece = self.get_square(before_position)
    if not piece:
      raise BaseException("Unable to interpret move %s" % command)
    
    taken_piece = self.get_square(after_position)
    if not taken_piece:
      raise BaseException("Move %s could not find the captured piece on square %s" % (command, after_position))
    
    self.remove_piece(taken_piece)
    piece.position = after_position
    
    return before_position, after_position, ""
  
  def move_from_to(self, move_from, move_to, original_command=""):
    piece = self.get_square(move_from)
    if not piece:
      raise BaseException("Unable to interpret move %s, from %s to %s." % (original_command, move_from, move_to))
    
    if piece.lower_symbol == "k":
      # special check for castling
      if (move_from == "e1" and move_to == "g1"):
        return self.castle("k")
      if (move_from == "e1" and move_to == "c1"):
        return self.castle("q")
      if (move_from == "e8" and move_to == "g8"):
        return self.castle("k")
      if (move_from == "e8" and move_to == "c8"):
        return self.castle("q")
    
    taken_piece = self.get_square(move_to)
    if taken_piece:
      self.remove_piece(taken_piece)
    
    piece.position = move_to
    
    return move_from, move_from, ""
    
  def move_pawn(self, command, before_position=None):
    # e.g. "d4"
    after_position = command
    col = after_position[0]
    row = after_position[1]
    before_row = int(row)
    
    if not before_position:
      if self.current_player == "w":
        before_row -= 1
      else:
        before_row += 1
      before_position = "%s%i" % (col, before_row)
      piece = self.get_square(before_position)
      if not piece:
        # double move from 2nd or 7th row
        if self.current_player == "w":
          before_row -= 1
        else:
          before_row += 1
        before_position = "%s%i" % (col, before_row)
    
    piece = self.get_square(before_position)
    if not piece:
      raise BaseException("Unable to interpret move %s" % command)
    piece.position = after_position
    
    return before_position, after_position, ""
  
  def move_piece(self, command, extra={}):
    command = command.replace("x", "")
    command = command.replace("X", "")
    command = command.replace("-", "")
    piece_symbol = command[0]
    after_position = command[1:3]

    piece = self.get_piece(piece_symbol, after_position, self.current_player, extra)
    if not piece:
      raise BaseException("Unable to interpret move %s. (Could not find piece %s that can move to %s)" % (command, piece_symbol, after_position))
    
    taken_piece = self.get_square(after_position)
    if taken_piece:
      self.remove_piece(taken_piece)
    
    before_position = piece.position
    piece.position = after_position
    
    return before_position, after_position, ""
  
  def move_postprocess(self):
    self.halfmove_clock += 1
    if self.current_player == "w":
      self.current_player = "b"
    else:
      self.current_player = "w"
      self.move_number += 1
  
  def remove_piece(self, piece):
    index = self.pieces.index(piece)
    if index:
      self.pieces.pop(index)
      del piece
    
  def _generate_from_fen(self, fen):
    fen_split = fen.split(" ")

    self.current_player = fen_split[1]
    self.castle_info = fen_split[2]
    self.enpassant = fen_split[3]
    
    try:
      self.halfmove_clock = int(fen_split[4])
    except:
      self.halfmove_clock = 0
      
    try:
      self.move_number = int(fen_split[5])
    except:
      self.move_number = 0
    
    self.pieces = []
    
    row = 9
    column_letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    for line in fen_split[0].split("/"):
      row -= 1
      col = -1
      for char in line:
        col += 1
        try:
          # is number
          col += int(char)
          col -= 1
        except:
          # is letter
          piece = Piece(char, "%s%i" % (column_letters[col], row))
          self.pieces.append(piece)

class Piece:
  def __init__(self, symbol="", position=""):
    self.is_white = symbol.upper() == symbol
    self.is_black = not self.is_white
    if self.is_white:
      self.player = "w"
    else:
      self.player = "b"
    self.symbol = symbol
    self.lower_symbol = symbol.lower()
    self.position = position
  
  def can_move_to(self, square):
    if self.lower_symbol == "k":
      return self.can_king_move_to(square)
    elif self.lower_symbol == "q":
      return self.can_queen_move_to(square)
    elif self.lower_symbol == "n":
      return self.can_knight_move_to(square)
    elif self.lower_symbol == "b":
      return self.can_bishop_move_to(square)
    elif self.lower_symbol == "r":
      return self.can_rook_move_to(square)
    else:
      raise BaseException("Unkown piece symbol '%s'." % self.lower_symbol)
  
  def can_king_move_to(self, square):
    col = Piece.col_to_number(self.col())
    to_col = Piece.col_to_number(square[0])
    
    row = int(self.row())
    to_row = int(square[1])
    
    return abs(row - to_row) <= 1 and abs(col - to_col) <= 1
  
  def can_queen_move_to(self, square):
    return self.can_bishop_move_to(square) or self.can_rook_move_to(square)
    
  def can_knight_move_to(self, square):
    col = Piece.col_to_number(self.col())
    to_col = Piece.col_to_number(square[0])
    
    row = int(self.row())
    to_row = int(square[1])
    
    row_diff = abs(row - to_row)
    col_diff = abs(col - to_col)
    
    return (row_diff == 1 and col_diff == 2) or (row_diff == 2 and col_diff == 1)
    
  def can_bishop_move_to(self, square):
    col = Piece.col_to_number(self.col())
    to_col = Piece.col_to_number(square[0])
    
    row = int(self.row())
    to_row = int(square[1])
    
    return abs(row - to_row) == abs(col - to_col)
    
  def can_rook_move_to(self, square):
    col = Piece.col_to_number(self.col())
    to_col = Piece.col_to_number(square[0])
    
    row = int(self.row())
    to_row = int(square[1])
    
    return col == to_col or row == to_row
  
  def col(self):
    return self.position[0]
  
  def row(self):
    return self.position[1]
  
  @staticmethod
  def col_to_number(col):
    return ["a", "b", "c", "d", "e", "f", "g", "h"].index(col)
    
  @staticmethod
  def generate_all_move_squares(type):
    pass
