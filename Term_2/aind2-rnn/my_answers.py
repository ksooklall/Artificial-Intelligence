import numpy as np

from keras.layers import LSTM
from keras.models import Sequential
from keras.layers import Dense, Activation


# TODO: fill out the function below that transforms the input series 
# and window-size into a set of input/output pairs for use with our RNN model
def window_transform_series(series, window_size):
    # containers for input/output pairs
    X = []
    y = []

    for i in range(len(series) - window_size):
        X.append(series[i:i+window_size])
        y.append(series[i + window_size])

    # reshape each
    X = np.asarray(X)
    X.shape = (np.shape(X)[0:2])
    y = np.asarray(y)
    y.shape = (len(y),1)
    return X,y

# TODO: build an RNN to perform regression on our time series input/output data
def build_part1_RNN(window_size):
    model = Sequential()
    model.add(LSTM(5, input_shape=(window_size, 1)))
    model.add(Dense(1))
    return model

### TODO: return the text input with only ascii lowercase and the punctuation given below included.
def cleaned_text(text):
    """
    Cleans text by removing all non ascii_lowecase elements.

    ascii_lowercase elements: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    :param text: Input string to be cleaned
    :return: (str) text only containing ascii elements
    """
    punctuation = {'!', ',', '.', ':', ';', '?'}
    ascii_lower = {chr(i): i  for i in range(97, 123)}
    for i in punctuation:
        ascii_lower[i] = None

    return ''.join([i if i in ascii_lower else ' ' for i in text.lower().strip()])

### TODO: fill out the function below that transforms the input text and window-size into a set of input/output pairs for use with our RNN model
def window_transform_text(text, window_size, step_size):
    # containers for input/output pairs
    inputs = []
    outputs = []
    for i in range(len(text)//step_size - window_size):
        start = i * step_size
        end = start + window_size

        inputs.append(text[start:end])
        outputs.append(text[end])
    return inputs,outputs

# TODO build the required RNN model: 
# a single LSTM hidden layer with softmax activation, categorical_crossentropy loss 
def build_part2_RNN(window_size, num_chars):
    model = Sequential()
    model.add(LSTM(200, input_shape=(window_size, num_chars)))
    model.add(Dense(num_chars, activation='linear'))
    model.add(Activation('softmax'))
    return model
