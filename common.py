def is_int(string):
  try:
    int(s)
    return True
  except ValueError:
    return False
