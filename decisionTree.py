from sklearn.tree import DecisionTreeClassifier
import csv
import sys

class FeatureFinder():

    # Which Player Has a Piece in the Bottom Left Position
    def bottomLeft(self, state):
        return state.board[0][0]

    # score of center pieces
    def numCenterPieces(self, state):
        player1count = 0
        player2count = 0
        for c in range(2,5):
            for r in range(state.rows):
                if state.board[c][r] == 1:
                    player1count += 1
                if state.board[c][r] == 2:
                    player2count += 1
        return player1count - player2count

    def centerPiece(self, state):
        return state.board[3][0]

class BoardState():

    def __init__(self, board1D):
        self.winner = board1D[len(board1D)-1]
        self.rows = 6
        self.columns = 7

        self.board = []

        for c in range(self.columns):
            self.board.append([])
            for r in range(self.rows):
                index = c * self.rows + r
                self.board[c].append(int(board1D[index]))

    def display(self):
        print ""
        for r in range(self.rows):
            line = ""
            for c in range(self.columns):     
                line += str(self.board[c][self.rows - r - 1]) + " "
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

def createDecisionData(finder, dataSet):
    decision_data = []
    winner_data = []

    for i in range(len(dataSet)):
        data = dataSet[i]
        decision_data.append([])
        feature_1 = finder.bottomLeft(data)
        feature_2 = finder.numCenterPieces(data)
        feature_3 = finder.centerPiece(data)
        decision_data[i].extend((feature_1, feature_2, feature_3))
        winner_data.append(data.winner)
    return (decision_data, winner_data)

if __name__== "__main__":
    data = []
    try:
        data = loadTrainData("trainDataSet.csv")
    except IOError:
        print 'Error: Could not find CSV File!'
        sys.exit(1)

    print 'Successfully Loaded {} Data Entries'.format(len(data))

    finder = FeatureFinder()

    decision_data, winner_data = createDecisionData(finder, data)

    data[0].display()

    print decision_data[0]
    print winner_data[0]
