import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_comp and self.max_comp

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        BIC_model = None
        BIC_score = float('inf')

        for comp in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = self.base_model(comp)
                n_params = (comp ** 2) + 2 * len(self.X[0]) * comp
                logL = model.score(self.X, self.lengths)
                N = np.sum(self.lengths)
                current_score = -2 * logL + n_params * np.log(N)
                if current_score < BIC_score:
                    BIC_score = current_score
                    BIC_model = model
            except:
                pass

        return BIC_model


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        DIC_score = -float("inf")
        DIC_model = None
        
        for comp in range(self.min_n_components, self.max_n_components + 1):
            temp_score = 0
            try:
                model = self.base_model(comp)
                score = model.score(self.X, self.lengths) 
                words = self.words.copy()
                
                del words[self.this_word]
                
                for word in words:
                    otherX, otherlength = self.hwords[word]
                    try:
                        temp_score += model.score(otherX, otherlength)
                    except:
                        pass
                temp_score = temp_score / len(words)
                current_score = score - temp_score
                if current_score > DIC_score:
                    DIC_score = current_score
                    DIC_model = model
            except:
                pass
        return DIC_model


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_score = float('-inf')
        best_num_state = 1

        for state in range(self.min_n_components, self.max_n_components + 1):
            i = 0
            score = 0
            word_sequences = self.sequences
            try:
                CV_model = KFold(n_splits=min(3, len(word_sequences)))
            except:
                return None

            try:
                for train, test in CV_model.split(word_sequences):
                    train_x, train_len = combine_sequences(train, word_sequences)
                    test_x, test_len = combine_sequences(test, word_sequences)

                    model = GaussianHMM(n_components=state, covariance_type='diag', n_iter=n, random_state=self.random_state,
                                        verbose=False)
                    model.fit(train_x, train_len)
                    score += model.score(test_x, test_len)
                    i += 1

                if score/i > best_score:
                    best_score = score / i
                    best_num_state = state
            except:
                pass

        return self.base_model(best_num_state)