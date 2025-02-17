
class ChessFuncs:
  def __init__(self):
    self.numbers = "12345678"
    self.letters = "abcdefgh"

  
  # turn a -> 0, h -> 7
  def fileToNumber(self, file: str):
    return self.letters.index(file)
  

  def squareToNumber(self, square: str):
    # ex: h8 -> 63
    file = self.fileToNumber(square[0])
    rank = int(square[1])
    
    return (rank * rank) - (rank - file)


chessFuncs = ChessFuncs()

print(chessFuncs.squareToNumber("a1"))
print(chessFuncs.squareToNumber("g8"))
print(chessFuncs.squareToNumber("h8"))