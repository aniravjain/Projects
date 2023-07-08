import numpy as np
from sklearn.tree import DecisionTreeClassifier
from pathlib import Path

def accuracy(y, pred):
    return np.sum(y == pred) / float(len(y))

def parse_spambase_data(filename):
    """ Given a filename return X and Y numpy arrays

    X is of size number of rows x num_features
    Y is an array of size the number of rows
    Y is the last element of each row. (Convert 0 to -1)
    """
    ### BEGIN SOLUTION
    with open(filename) as f:
        lines = f.readlines()
    X=[]
    Y=[]
    for i in lines:
        row = [float(x) for x in i.split(',')]
        X.append(row[:-1])
        Y.append(row[-1])
        
    X = np.array(X)
    Y = np.array(Y)
    Y[Y == 0] = -1
    
    ### END SOLUTION
    return X, Y


def adaboost(X, y, num_iter, max_depth=1):
    """Given an numpy matrix X, a array y and num_iter return trees and weights 
   
    Input: X, y, num_iter
    Outputs: array of trees from DecisionTreeClassifier
             trees_weights array of floats
    Assumes y is {-1, 1}
    """
    trees = []
    trees_weights = [] 
    N, _ = X.shape
    d = np.ones(N) / N # initial weights
    epsilon = 10**-9
    ### BEGIN SOLUTION
    for i in range(num_iter):
        err = np.sum(0)
        h = DecisionTreeClassifier(max_depth = max_depth, random_state=0)
        h.fit(X, y, sample_weight=d)
        pred = h.predict(X)
        indices = np.where(pred!=y)[0]
        for p in indices:
            err = err + d[p]/np.sum(d)
        alpha_m = np.log((1-err+epsilon)/(err+epsilon))
        for q in indices:
            d[q] = d[q]*np.exp(alpha_m)
        trees.append(h)
        trees_weights.append(alpha_m)
        

    ### END SOLUTION
    return trees, trees_weights


def adaboost_predict(X, trees, trees_weights):
    """Given X, trees and weights predict Y
    """
    # X input, y output
    N, _ =  X.shape
    y = np.zeros(N)
    ### BEGIN SOLUTION
    for i in range(len(trees)):
        y = y+trees_weights[i]*trees[i].predict(X)
    y = np.where(y >= 0, 1, -1)
    
    ### END SOLUTION
    return y
