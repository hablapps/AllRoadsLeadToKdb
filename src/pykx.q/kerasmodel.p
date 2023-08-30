from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM, Dropout, Conv1D

model = Sequential()
model.add(LSTM(units = 500, return_sequences=True, input_shape=[None,5]))
model.add(LSTM(units = 250,return_sequences=True))
model.add(LSTM(units = 50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units = 1))
model.compile(loss='mae', optimizer='adam')
model.summary()

def fit(train_X, train_y, test_X, test_y):
    model.fit(train_X, train_y, epochs=3, batch_size=64, validation_data=(test_X, test_y), verbose=1, shuffle=False)
    return True


def predict(data):
    return model.predict(data)
