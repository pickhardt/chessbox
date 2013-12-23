# Credit to Renato de Pontes Pereira, renato.ppontes at gmail dot com
# for py pgn parser

import re
import pdb
from position import Position

class Game:
  """Represents a game."""

  def __init__(self):
    self.attributes = {}
    self.moves = []
    pass
  
  def set_attribute(self, name, value):
    self.attributes[name] = value
  
  def get_attribute(self, name):
    return self.attributes[name]
  
  def generate_long_algebraic_moves(self):
    position = Position()
    for move in self.moves:
      try:
        long_move = "%s%s%s" % position.move(move)
        if len(long_move) > 0:
          yield long_move
      except Exception, err:
        raise BaseException("Could not process move %s (%s)" % (move, err))
    
  def ply_count(self):
    count = len(self.moves)
    if count > 0 and self.moves[-1] in ["1-0", "0-1", "1/2-1/2", "0.5-0.5"]:
      count -= 1
    return count
  
  def to_pgn(self):
    response = ""
    
    TAG_ORDER = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result',
                 'Annotator', 'PlyCount', 'TimeControl', 'Time', 'Termination',
                 'Mode', 'FEN', 'ECO']
    
    for i, tag in enumerate(TAG_ORDER):
      if self.attributes.has_key(tag.lower()):
        response += '[%s "%s"]\n' % (tag, self.attributes[tag.lower()])
      elif i <= 6:
        response += '[%s "?"]\n' % tag
    
    for name, val in self.attributes.iteritems():
      if name.capitalize() in TAG_ORDER or name.upper() in TAG_ORDER:
        continue
      response += "[%s %s]\n" % (name.capitalize(), val)
    
    response += "\n"
    
    is_white_to_move = False
    move_count = 0
    for move in self.moves:
      if not is_white_to_move:
        is_white_to_move = True
        move_count += 1
        response += " %i." % move_count
      else:
        is_white_to_move = False
      response += " "
      response += move
    return response
  
  @staticmethod
  def parse_tag(token):
    """Parse a tag token and returns a tuple with (name, value)."""
    tag, value = re.match(r'\[(\w*)\s*(.+)', token).groups()
    return tag.lower(), value.strip('"[] ')
  
  @staticmethod
  def parse_moves(token):
    """Parse a moves token and returns a list with movements."""
    moves = []
    while token:
      token = re.sub(r'^\s*(\d+\.+\s*)?', '', token)
      
      if token.startswith('{'):
        pos = token.find('}')+1
      else:
        pos1 = token.find(' ')
        pos2 = token.find('{')
        if pos1 <= 0:
          pos = pos2
        elif pos2 <= 0:
          pos = pos1
        else:
          pos = min([pos1, pos2])
      
      if pos > 0:
        moves.append(token[:pos])
        token = token[pos:]
      else:
        moves.append(token)
        token = ''
    
    return moves

  @staticmethod
  def games_to_pgn(games=[]):
    '''
    Serialize a list os PGNGames (or a single game) into text format.
    '''
    all_dumps = []
    
    if not isinstance(games, (list, tuple)):
      games = [games]
    
    for game in games:
      dump = ''
      for i, tag in enumerate(PGNGame.TAG_ORDER):
        if getattr(game, tag.lower()):
          dump += '[%s "%s"]\n' % (tag, getattr(game, tag.lower()))
        elif i <= 6:
          dump += '[%s "?"]\n' % tag
      
      
      dump += '\n'
      i = 0
      for move in game.moves:
        if not move.startswith('{'):
          if i%2 == 0:
            dump += str(i/2+1)+'. '
          
          i += 1
        
        dump += move + ' '
      
      all_dumps.append(dump.strip())
    
    return '\n\n\n'.join(all_dumps)

  @staticmethod
  def next_token(lines):
    '''
    Get the next token from lines (list of text pgn file lines).
    
    There is 2 kind of tokens: tags and moves. Tags tokens starts with ``[``
    char, e.g. ``[TagName "Tag Value"]``. Moves tags follows the example: 
    ``1. e4 e5 2. d4``.
    '''
    if not lines:
      return None
    
    token = lines.pop(0).strip() 
    if token.startswith('['):
      return token
    
    while lines and not lines[0].startswith('['):
      token += ' '+lines.pop(0).strip()
    
    return token.strip()

  @staticmethod
  def games_from_pgn(pgn_file):
    """Returns an array of Games from a PGN file."""
    games = []
    game = None
    
    # Preprocess, remove comments
    lines = []
    for line in pgn_file.readlines():
      line = re.sub(r'\s*(\\r)?\\n\s*', '\n', line.strip())
      if line:
        lines.append(line)

    while True:
      token = Game.next_token(lines)
      
      if not token:
        break
      
      if token.startswith('['):
        tag_name, value = Game.parse_tag(token)
        
        if not game or (game and game.moves):
          game = Game()
          games.append(game)
        
        game.set_attribute(tag_name, value)
      else:
        game.moves = Game.parse_moves(token)
    
    return games
