import csv
import sys

class BoardState():

    def __init__(self, board1D):
        self.winner = board1D[len(board1D)-1]
        self.rows = 6
        self.columns = 7

        self.board = []

        for c in range(self.columns):
            self.board.append([])
            for r in range(self.rows):
                index = c * self.rows + (self.rows - r - 1)
                self.board[c].append(board1D[index])

    def display(self):
        print ""
        for r in range(self.rows):
            line = ""
            for c in range(self.columns):     
                line += self.board[c][r] + " "
            print line
        print "\n\tWinner: {}".format(self.winner)
    


def loadTrainData(filename):
    data = []
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        reader_iter = iter(reader)
        reader_iter.next()
        for entry in reader_iter:
            data.append(BoardState(entry))
    return data

if __name__== "__main__":
    data = []
    try:
        data = loadTrainData("trainDataSet.csv")
    except IOError:
        print 'Error: Could not find CSV File!'
        sys.exit(1)

    print 'Successfully Loaded {} Data Entries'.format(len(data))
 
