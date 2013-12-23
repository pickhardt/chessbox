import subprocess
import time
import os
import re

from move import *

class Engine:
  """Represents a chess engine."""

  def __init__(self, engine_path, options={}):
    self.engine = subprocess.Popen(
      engine_path,
      universal_newlines=True,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
    )
  
  def get_two_top_moves(self, moves, thinking=10):
    self._put("ucinewgame")
    self._get()
    self._put("position startpos moves %s" % " ".join(moves))
    self._get()
    self._put('go infinite')
    time.sleep(thinking)
    
    candidate_moves = [None, None]
    for line in self._get_lines():
      matching = re.match(r'.*? score .. (-?\d+) .*? multipv (\d) pv ([^ ]+) ', line)
      if matching:
        score = matching.groups()[0]
        candidate_number = int(matching.groups()[1])
        move = matching.groups()[2]
        candidate_moves[candidate_number - 1] = CandidateMove(move, score)
    
    self._put('stop')
    
    return candidate_moves[0], candidate_moves[1]
  
  def set_option(self, name, value):
    self._put("setoption name %s value %s" % (name, value))
  
  def _put(self, command):
    self.engine.stdin.write("%s\n" % command)
  
  def _get(self):
    response = ""
    for line in self._get_lines():
      response += "\n%s" % line
    return response
  
  def _get_lines(self):
    # Using the isready command to
    # know when we've reached the last line
    # of stdout (engine will answer 'readyok')
    self.engine.stdin.write('isready\n')
    while True:
      text = self.engine.stdout.readline().strip()
      if text == 'readyok':
        break
      if text != '':
        yield text
