class CandidateMove:
  """Represents a candidate move."""

  def __init__(self, move, score):
    self.move = move
    self.score = float(score) # relative