from sklearn.tree import DecisionTreeClassifier, export_graphviz
import numpy as np
from sklearn.model_selection import KFold
import csv
import sys
from scipy import stats


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

    def twoInRowDiagonal(self, state):
        num_two_in_a_row_player1 = 0
        num_two_in_a_row_player2 = 0
        for c in range(state.columns):
            for r in range(state.rows):
                neighbors = state.generateNeighbors(c, r, True)
                for n in neighbors:
                    if state.board[c][r] == 1 and n == 1:
                        num_two_in_a_row_player1 += 1
                    elif state.board[c][r] == 2 and n == 2:
                        num_two_in_a_row_player2 += 1
        return num_two_in_a_row_player1 - num_two_in_a_row_player2

    def twoInRowFreeSpace(self, state):
        player1_count = 0
        player2_count = 0

        for c in range(state.columns):
            for r in range(state.rows):
                if state.board[c][r] == 1:
                    if state.pieceEqualTo(c, r-1, 1) and state.pieceEqualTo(c, r-2, 0):
                        player1_count += 1
                    if state.pieceEqualTo(c-1, r, 1) and state.pieceEqualTo(c-2, r, 0):
                        player1_count += 1
                    if state.pieceEqualTo(c, r+1, 1) and state.pieceEqualTo(c, r+2, 0):
                        player1_count += 1
                    if state.pieceEqualTo(c+1, r, 1) and state.pieceEqualTo(c+2,r , 0):
                        player1_count += 1
                    # if state.pieceEqualTo(c-1, r-1, 1) and state.pieceEqualTo(c-2, r-2, 0):
                    #     player1_count += 1
                    # if state.pieceEqualTo(c-1, r+1, 1) and state.pieceEqualTo(c-2, r+2, 0):
                    #     player1_count += 1
                    # if state.pieceEqualTo(c+1, r-1, 1) and state.pieceEqualTo(c+2, r-2, 0):
                    #     player1_count += 1
                    # if state.pieceEqualTo(c+1, r+1, 1) and state.pieceEqualTo(c+2, r+2, 0):
                    #     player1_count += 1
                if state.board[c][r] == 2:
                    if state.pieceEqualTo(c, r-1, 2) and state.pieceEqualTo(c, r-2, 0):
                        player2_count += 1
                    if state.pieceEqualTo(c-1, r, 2) and state.pieceEqualTo(c-2, r, 0):
                        player2_count += 1
                    if state.pieceEqualTo(c, r+1, 2) and state.pieceEqualTo(c, r+2, 0):
                        player2_count += 1
                    if state.pieceEqualTo(c+1, r, 2) and state.pieceEqualTo(c+2,r , 0):
                        player2_count += 1
                    # if state.pieceEqualTo(c-1, r-1, 2) and state.pieceEqualTo(c-2, r-2, 0):
                    #     player2_count += 1
                    # if state.pieceEqualTo(c-1, r+1, 2) and state.pieceEqualTo(c-2, r+2, 0):
                    #     player2_count += 1
                    # if state.pieceEqualTo(c+1, r-1, 2) and state.pieceEqualTo(c+2, r-2, 0):
                    #     player2_count += 1
                    # if state.pieceEqualTo(c+1, r+1, 2) and state.pieceEqualTo(c+2, r+2, 0):
                    #     player2_count += 1

        return player1_count - player2_count


class BoardState():

    def __init__(self, board1D):
        self.winner = board1D[len(board1D)-1]
        self.rows = 6
        self.columns = 7

        self.board1D = board1D

        self.board = []

        for c in range(self.columns):
            self.board.append([])
            for r in range(self.rows):
                index = c * self.rows + r
                self.board[c].append(int(board1D[index]))

    def display(self):
        print("")
        for r in range(self.rows):
            line = ""
            for c in range(self.columns):     
                line += str(self.board[c][self.rows - r - 1]) + " "
            print(line)
        print("\n\tWinner: {}".format(self.winner))

    def generateNeighbors(self, c, r, diagonal=False):
        neighbors = []

        if self.checkBounds(c + 1, r + 1): neighbors.append(self.board[c + 1][r + 1])
        if self.checkBounds(c - 1, r - 1): neighbors.append(self.board[c - 1][r - 1])
        if self.checkBounds(c + 1, r - 1): neighbors.append(self.board[c + 1][r - 1])
        if self.checkBounds(c - 1, r + 1): neighbors.append(self.board[c - 1][r + 1])

        if diagonal:
            return neighbors

        if self.checkBounds(c, r + 1): neighbors.append(self.board[c][r + 1])
        if self.checkBounds(c + 1, r): neighbors.append(self.board[c + 1][r])
        if self.checkBounds(c - 1, r): neighbors.append(self.board[c - 1][r])
        if self.checkBounds(c, r - 1): neighbors.append(self.board[c][r - 1])

        return neighbors

    def pieceEqualTo(self, c, r, piece):
        return self.checkBounds(c, r) and self.board[c][r] == piece

    def checkBounds(self, c, r):
        return (c >= 0 and c < self.columns) and (r >= 0 and r < self.rows)


def loadTrainData(filename):
    data = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        reader_iter = iter(reader)
        next(reader_iter)
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
        feature_4 = finder.twoInRowDiagonal(data)
        feature_5 = finder.twoInRowFreeSpace(data)
        decision_data[i].extend((feature_1, feature_2, feature_3, feature_4, feature_5))
        winner_data.append(data.winner)
    return (decision_data, winner_data)

def createDecisionDataHoldFeature(finder, dataSet, featureHold):
    decision_data = []
    winner_data = []

    for i in range(len(dataSet)):
        data = dataSet[i]
        decision_data.append([])

        if featureHold != 1:
            feature_1 = finder.bottomLeft(data)
            decision_data[i].append(feature_1)
        if featureHold != 2:
            feature_2 = finder.numCenterPieces(data)
            decision_data[i].append(feature_2)
        if featureHold != 3:
            feature_3 = finder.centerPiece(data)
            decision_data[i].append(feature_3)
        if featureHold !=4:
            feature_4 = finder.twoInRowDiagonal(data)
            decision_data[i].append(feature_4)
        if featureHold !=5:
            feature_5 = finder.twoInRowFreeSpace(data)
            decision_data[i].append(feature_5)
        winner_data.append(data.winner)
    return (decision_data, winner_data)

def saveOutputData(filename, data, decision_data):

    output_rows = []
    for i in range(len(data)):
        state = data[i]
        output_rows.append([])
        for piece in state.board1D:
            output_rows[i].append(piece)
        for feature in decision_data[i]:
            output_rows[i].append(feature)


    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')

        for row in output_rows:
            writer.writerow(row)




def kFoldCrossValidation(k, xData, yData):
    xData = np.asarray(xData)
    yData = np.asanyarray(yData)
    kf = KFold(n_splits=k, shuffle=True)
    X_train, Y_train, X_test, Y_test = [], [], [], []

    accuracy = []

    for train_index, test_index in kf.split(xData):
        X_train, X_test = xData[train_index], xData[test_index]
        Y_train, Y_test = yData[train_index], yData[test_index]

        clf = buildTree(X_train, Y_train)
        accuracy.append(clf.score(X_test, Y_test))
    print(np.mean(accuracy))


def buildTree(xData, yData):
    clf_entropy = DecisionTreeClassifier(criterion = "entropy", random_state = 100, min_samples_leaf=30)
    clf_entropy.fit(xData, yData)
    return clf_entropy

#     export_graphviz(tree, feature_names=["Bottom Left", "Center Columns", "Center Piece", "Two in Row Diagonal", "Two in a Row and Free Space"], out_file = 'connectFour' +  number + '.dot')
def visualizeTree(tree, number):
    if(number == 'full'):
        export_graphviz(tree, feature_names=["Bottom Left", "Center Columns", "Center Piece", "Two in Row Diagonal", "Two in a Row and Free Space"], out_file='connectFour' + number + '.dot')
    if(number == 'hold1'):
        export_graphviz(tree, feature_names=["Center Columns", "Center Piece", "Two in Row Diagonal", "Two in a Row and Free Space"], out_file = 'connectFour' +  number + '.dot')
    if(number == 'hold2'):
        export_graphviz(tree, feature_names=["Bottom Left", "Center Piece", "Two in Row Diagonal", "Two in a Row and Free Space"], out_file = 'connectFour' +  number + '.dot')
    if(number == 'hold3'):
        export_graphviz(tree, feature_names=["Bottom Left", "Center Columns", "Two in Row Diagonal", "Two in a Row and Free Space"], out_file = 'connectFour' +  number + '.dot')
    if(number == 'hold4'):
        export_graphviz(tree, feature_names=["Bottom Left", "Center Columns", "Center Piece", "Two in a Row and Free Space"], out_file = 'connectFour' +  number + '.dot')
    if(number == 'hold5'):
        export_graphviz(tree, feature_names=["Bottom Left", "Center Columns", "Center Piece", "Two in Row Diagonal"], out_file = 'connectFour' +  number + '.dot')

if __name__== "__main__":

    input_file = ""
    output_file = ""

    try:
        input_file, output_file = ("trainDataSet.csv", "output.csv")#sys.argv[1:3]
    except ValueError:
        print ('Please enter two arguments in the format \"input_file.csv output_file.csv\".')

    if not '.csv' in input_file or not '.csv' in output_file:
        print ('Error! Please Input and Output files must be .csv!')
        sys.exit(1)

    data = []
    try:
        data = loadTrainData("trainDataSet.csv")
    except IOError:
        print('Error: Could not find CSV File!')
        sys.exit(1)

    print('Successfully Loaded {} Data Entries'.format(len(data)))

    finder = FeatureFinder()

    decision_data, winner_data = createDecisionData(finder, data)
    decision_data_hold1, winner_data_hold1 = createDecisionDataHoldFeature(finder, data, 1)
    decision_data_hold2, winner_data_hold2 = createDecisionDataHoldFeature(finder, data, 2)
    decision_data_hold3, winner_data_hold3 = createDecisionDataHoldFeature(finder, data, 3)
    decision_data_hold4, winner_data_hold4 = createDecisionDataHoldFeature(finder, data, 4)
    decision_data_hold5, winner_data_hold5 = createDecisionDataHoldFeature(finder, data, 5)

    tree_full = buildTree(decision_data, winner_data)
    tree_hold1 = buildTree(decision_data_hold1, winner_data_hold1)
    tree_hold2 = buildTree(decision_data_hold2, winner_data_hold2)
    tree_hold3 = buildTree(decision_data_hold3, winner_data_hold3)
    tree_hold4 = buildTree(decision_data_hold4, winner_data_hold4)
    tree_hold5 = buildTree(decision_data_hold5, winner_data_hold5)

    prediction_full = tree_full.predict(decision_data).astype(np.int)
    prediction_hold1 = tree_hold1.predict(decision_data_hold1).astype(np.int)
    prediction_hold2 = tree_hold2.predict(decision_data_hold2).astype(np.int)
    prediction_hold3 = tree_hold3.predict(decision_data_hold3).astype(np.int)
    prediction_hold4 = tree_hold4.predict(decision_data_hold4).astype(np.int)
    prediction_hold5 = tree_hold5.predict(decision_data_hold5).astype(np.int)

    #print(type(prediction_full[0]))
    #print (stats.ttest_ind(prediction_full, prediction_hold1))
    #print (stats.ttest_ind(prediction_full, prediction_hold2))
    #print (stats.ttest_ind(prediction_full, prediction_hold3))
    #print (stats.ttest_ind(prediction_full, prediction_hold4))
    #print (stats.ttest_ind(prediction_full, prediction_hold5))


    saveOutputData(output_file, data, decision_data)

    #data[7].display()

    #print (finder.twoInRowFreeSpace(data[7]))
    #print (decision_data[7])
    kFoldCrossValidation(10, decision_data, winner_data)

    visualizeTree(tree_full, 'full')
    visualizeTree(tree_hold1, 'hold1')
    visualizeTree(tree_hold2, 'hold2')
    visualizeTree(tree_hold3, 'hold3')
    visualizeTree(tree_hold4, 'hold4')
    visualizeTree(tree_hold5, 'hold5')


