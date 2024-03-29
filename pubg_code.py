# -*- coding: utf-8 -*-
"""pubg-code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wvnLHmsw-grUqM_RSwl3zRfh2Z77whI3
"""

# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All"
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

train = pd.read_csv('/kaggle/input/pubg-finish-placement-prediction/train_V2.csv')
test = pd.read_csv('/kaggle/input/pubg-finish-placement-prediction/test_V2.csv')
submission = pd.read_csv('/kaggle/input/pubg-finish-placement-prediction/sample_submission_V2.csv')

train.info()

test.info()

# drop Nans
train.dropna(inplace=True)
test.dropna(inplace=True)

# drop categorical data
train.drop(columns=['Id', 'groupId', 'matchId', 'matchType'], inplace=True)
test.drop(columns=['Id', 'groupId', 'matchId', 'matchType'], inplace=True)

train_corr = train.corr()
train_corr['winPlacePerc'].sort_values(ascending=False)

# drop features that correlation coeffcient < 0.2
train.drop(columns=['swimDistance', 'vehicleDestroys', 'numGroups', 'maxPlace',
         'roadKills', 'rankPoints', 'teamKills', 'killPoints',
         'winPoints', 'matchDuration', 'killPlace'], inplace=True)
test.drop(columns=['swimDistance', 'vehicleDestroys', 'numGroups', 'maxPlace',
         'roadKills', 'rankPoints', 'teamKills', 'killPoints',
         'winPoints', 'matchDuration', 'killPlace'], inplace=True)

train.describe(exclude='O').T

import matplotlib.pyplot as plt
import seaborn as sns

#correlation matrix
train_response = train.drop('winPlacePerc', axis=1)
f,ax = plt.subplots(figsize=(10,10))
sns.heatmap(train_response.corr(), vmin=-1, vmax=1, center=0, annot=True, fmt='.2f', ax=ax)
plt.show()

# split x, y
y = train['winPlacePerc']
x = train.drop('winPlacePerc', axis= 1 )

y.head(20)

from sklearn.preprocessing import StandardScaler

scal = StandardScaler()
x = scal.fit_transform(x)
x_te = scal.transform(test)

# split train, valid
from sklearn.model_selection import train_test_split

x_tr, x_val, y_tr, y_val = train_test_split(x, y,test_size=0.2, random_state=42)

# model
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD

tf.keras.backend.clear_session()
np.random.seed(1)
tf.random.set_seed(1)

model = keras.models.Sequential([
    keras.layers.Dense(10, activation='relu', kernel_initializer='he_normal', input_shape=x_tr.shape[1:]),
    keras.layers.Dropout(rate=0.2),
    keras.layers.Dense(5, activation='relu', kernel_initializer='he_normal'),
    keras.layers.Dropout(rate=0.2),
    keras.layers.Dense(1, activation='sigmoid')
  ])

model.summary()

#compile
opt = keras.optimizers.SGD(learning_rate=0.001, momentum=0.9)
model.compile(loss='mse', optimizer=opt)

#train
train = model.fit(x_tr, y_tr, epochs=5, validation_data=(x_val, y_val))

pd.DataFrame(train.history).plot()
plt.grid(True)
plt.ylim(0,0.1)
plt.show()

y_te = model.predict(x_te, batch_size=16)

y_te

y_te = y_te.reshape(-1)

submission = submission['Id'].append(y_te)

submission.head()

submission.to_csv('submission.csv', index = False)