## Takes in training data and trains an XGBoost model on it. 
# It is used by the other files in the project to train the 
# model for later predictions.
# It is also used to save and load the model from the 
# versioning database.

from data.database.sqlite import db as db
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

X = db.get_whole_table('gaia_dr3_data')
X = pd.DataFrame(X, columns=['source_id', 'ra', 'dec', 'parallax', 'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag'])
y = db.get_whole_table('nasaea_data')
y = pd.DataFrame(y, columns=['id', 'name', 'ra', 'dec', 'magnitude'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

## intake cleaned DR3 data and train an XGBoost model on it
dtrain = xgb.DMatrix(data=X_train.drop(columns=['source_id']), label=y_train['magnitude'])
dtest = xgb.DMatrix(data=X_test.drop(columns=['source_id']), label=y_test['magnitude'])

## Specify the parameters for the XGBoost model
params = {
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'max_depth': 5,
    'eta': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'seed': 42
}
num_boost_round = 100

## Train the XGBoost model
bst = xgb.train(params=params, dtrain=dtrain, num_boost_round=100, evals=[(dtest, 'test')])

## Make a sample prediction on the test data
y_pred = bst.predict(dtest)