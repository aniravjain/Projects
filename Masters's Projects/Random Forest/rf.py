import numpy as np
from sklearn.utils import resample

from dtree import *

class RandomForest621:
    def __init__(self, n_estimators=10, oob_score=False):
        self.n_estimators = n_estimators
        self.oob_score = oob_score
        self.oob_score_ = np.nan

    def fit(self, X, y):
        """
        Given an (X, y) training set, fit all n_estimators trees to different,
        bootstrapped versions of the training data.  Keep track of the indexes of
        the OOB records for each tree.  After fitting all of the trees in the forest,
        compute the OOB validation score estimate and store as self.oob_score_, to
        mimic sklearn.
        """
        oob_tracker = []
        all_indices = [j for j in range(X.shape[0])]
        for i in range(self.n_estimators):
            dtree_indices = resample(range(X.shape[0]))
            oob_indices = list(set(all_indices) - set(dtree_indices))
            oob_tracker.append(oob_indices)
            X_fit = X[dtree_indices]
            y_fit = y[dtree_indices]
            self.trees[i].fit(X_fit,y_fit)
        if self.oob_score:
            self.oob_score_ = self.compute_oob_score(oob_tracker, X, y)
            
            
class RandomForestRegressor621(RandomForest621):
    def __init__(self, n_estimators=10, min_samples_leaf=3, 
    max_features=0.3, oob_score=False):
        super().__init__(n_estimators, oob_score=oob_score)
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.n_estimators = n_estimators
        self.trees = [RegressionTree621(max_features = self.max_features, min_samples_leaf = self.min_samples_leaf) for p in range(self.n_estimators)]

    def predict(self, X_test) -> np.ndarray:
        """
        Given a 2D nxp array with one or more records, compute the weighted average
        prediction from all trees in this forest. Weight each trees prediction by
        the number of observations in the leaf making that prediction.  Return a 1D vector
        with the predictions for each input record of X_test.
        """
        leaf_list = []
        for i in range(len(self.trees)):
            leaf_list.append(self.trees[i].predict_leaf(X_test))
            
        leaf_list = list(zip(*leaf_list))
        pred_list = []
        for j in leaf_list:
            num_obs = 0
            sum_num = 0
            for k in j:
                num_obs = num_obs + k.n
                sum_num = sum_num + k.n*k.prediction
            predicted_value = sum_num/num_obs
            pred_list.append(predicted_value)
        return np.array(pred_list)
                
                
        
        
    def score(self, X_test, y_test) -> float:
        """
        Given a 2D nxp X_test array and 1D nx1 y_test array with one or more records,
        collect the prediction for each record and then compute R^2 on that and y_test.
        """
        predictions = self.predict(X_test)
        return r2_score(y_test, predictions)
        
    def compute_oob_score(self, oob_tracker, X, y):
        pred_ls = []
        y_ls = []
        for q in range(len(oob_tracker)):
            oob_indices = oob_tracker[q]
            predictions = self.trees[q].predict(X[oob_indices])
            y_ls.append(y[oob_indices])
            pred_ls.append(predictions)
        y_list = [item for sublist in y_ls for item in sublist]
        pred_list = [item for sublist in pred_ls for item in sublist]
        return r2_score(y_list, pred_list)
        # pred_lst = []
        # for q in range(len(oob_tracker)):
        #     oob_indices = oob_tracker[q]
        #     predictions = self.trees[q].predict(X[oob_indices])
        #     r2_s = r2_score(y[oob_indices],predictions)
        #     pred_lst.append(r2_s)
        # return np.mean(pred_lst)

            
            
        
class RandomForestClassifier621(RandomForest621):
    def __init__(self, n_estimators=10, min_samples_leaf=3, 
    max_features=0.3, oob_score=False):
        super().__init__(n_estimators, oob_score=oob_score)
        n_estimators = n_estimators
        self.max_features = max_features
        self.min_samples_leaf = min_samples_leaf
        self.trees = [ClassifierTree621(min_samples_leaf = self.min_samples_leaf, max_features = self.max_features) for p in range(n_estimators)]

    def predict(self, X_test) -> np.ndarray:
        leaf_list = []
        for i in range(len(self.trees)):
            leaf_list.append(self.trees[i].predict_leaf(X_test)) #returns a list of leaf nodes for n observations per tree
        leaf_list = list(zip(*leaf_list)) #converting 10*n to n*10
        
        pred_list = []
        for j in leaf_list:
            combined_counts = []
            for k in j:
                combined_counts = combined_counts + list(k.y)
            combined_mode = stats.mode(combined_counts)[0][0]
            pred_list.append(combined_mode)
        return np.array(pred_list)
        
    def score(self, X_test, y_test) -> float:
        """
        Given a 2D nxp X_test array and 1D nx1 y_test array with one or more records,
        collect the predicted class for each record and then compute accuracy between
        that and y_test.
        """
        predictions = self.predict(X_test)
        return accuracy_score(y_test, predictions)
        
    def compute_oob_score(self, oob_tracker, X, y):
        pred_ls = []
        y_ls = []
        for q in range(len(oob_tracker)):
            oob_indices = oob_tracker[q]
            predictions = self.trees[q].predict(X[oob_indices])
            y_ls.append(y[oob_indices])
            pred_ls.append(predictions)
        y_list = [item for sublist in y_ls for item in sublist]
        pred_list = [item for sublist in pred_ls for item in sublist]
        return accuracy_score(y_list, pred_list)