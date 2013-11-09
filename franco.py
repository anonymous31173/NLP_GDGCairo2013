import sys
import nltk

from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize

from nltk.classify import SklearnClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB


text = {}


def load(filename='corpus/franco.txt'):
    ''' Load data from arabizi.txt
        Then put data as key & value in text
    '''
    fd = open(filename)
    for line in fd.readlines():
        try:
            key, val = line.split(':', 1)
            text[key] = val.lower().strip()
        except:
            pass



def show():
    ''' Displays data loaded from arabizi.txt
        Data is put as key & value pairs in text
    '''
    for key in text:
        print key + ':' + text[key][0:100] + '... (Length: ' + str(len(text[key])) + ' characters)'
        words = wordpunct_tokenize(text[key])
        print key + ':' + ','.join(words[0:100]) + '... (Length: ' + str(len(words)) + ' words)'
    print '\n'



def get_freq(mode='char', alpha_sorted=False):
    ''' Get tokenz freuquencies
        mood: char, 2-gram, word
    '''
    fdist = {}
    for label in text:
        fdist[label] = []
        if mode == 'char':
            tokenz = [char for char in text[label]]
        if mode.endswith('gram'):
            n = int(mode.split('-')[0])
            tokenz = [text[label][i:i+n] for i in range(len(text[label]))]
        else:
            tokenz = word_tokenize(text[label])   
        nltk_txt = nltk.Text(tokenz)
        #nltk_txt.plot()
        for char in nltk_txt.vocab().keys():
            fdist[label].append((char, nltk_txt.vocab()[char]))
        if alpha_sorted:
            fdist[label].sort()
    return fdist 
        
def print_debug(message, debug=False):
    if debug:
        print message
            

def classifier(n=1):
    ''' Classify English vs Arabizi
        Usage:
            c = classifier(n=2)
            predict(input_text, c)
        Update: We now use predict_nltk(), ignore this method.
    '''
    v = DictVectorizer(sparse=False)
    featureset = []
    labels = []
    for label in text:
        tokenz = [text[label][i:i+n] for i in range(len(text[label]))]
        fdist = nltk.FreqDist(tokenz)
        features = {}
        for tok in fdist.keys():
            features[tok] = fdist[tok]
        #print label, features
        featureset.append(features)
        labels.append(label)
    featureset_scikit = v.fit_transform(featureset)
    nb = MultinomialNB(alpha=0.1, fit_prior=False)
    nb.fit(featureset_scikit, labels)
    return {'learner': nb, 'vectorizer': v, 'n': n}


def predict(text='', classifier=None):
    ''' Convert string to featureset
        Then use scikit-learn and classifier to classify it.
        Usage:
            c = classifier(n=2)
            predict(input_text, c)
        Update: We now use predict_nltk(), ignore this method.
    '''
    n = classifier['n']
    v = classifier['vectorizer']
    nb = classifier['learner']
    tokenz = [text[i:i+n] for i in range(len(text))]
    fdist = nltk.FreqDist(tokenz)
    features = {}
    for tok in fdist.keys():
        features[tok] = fdist[tok]
    featureset_scikit = v.transform(features)
    y = nb.predict(featureset_scikit)
    print 'Class:', y[0]
    


def text_features(in_text='', n=2):
    ''' Convert string to featureset
        To be used by predict_nltk
    '''
    tokenz = [in_text[i:i+n] for i in range(len(in_text))]
    fdist = nltk.FreqDist(tokenz)
    features = {}
    for tok in fdist.keys():
        features[tok] = fdist[tok]
    return features

        
def predict_nltk(in_text='', n=2): 
    ''' Text language classification
        Then use scikit-learn classifiers from within NLTK 
        to classify new taxt based on training set.
    '''
    trainingset = []  
    for label in text:
        featurs = text_features(text[label])
        trainingset.append((featurs, label))
    classifier = SklearnClassifier(MultinomialNB()).train(trainingset)
    in_features = text_features(in_text, n=n)
    lang = classifier.classify(in_features)
    print 'Language:', lang
    
                
   


if __name__ == '__main__':

    load()
    #show()
    
    DEBUG = False
    
    # This is for debugging purpose only
    for key in text:
        msg =  key + ' => Length: ' + str(len(text[key]))
        print_debug(msg, debug=DEBUG)
    print ''
    
    # This is for debugging purpose only
    for key in text:
        lex_richness = float( len(text[key])) / len(set(text[key]) )
        msg = key + ' => Lexical richness: ' + str(lex_richness)
        print_debug(msg, debug=DEBUG)
    print_debug('', debug=DEBUG)
    
    # This is for debugging purpose only
    if DEBUG:
        txt_freqs = get_freq(mode='word')
        for label in txt_freqs:
            msg = label + str(txt_freqs[label])
            print_debug(msg, debug=DEBUG)
    
    try:
        input_text = ' '.join(sys.argv[1:])
        print 'Text:', input_text
        predict_nltk(input_text, n=2)
    except:
        print 'Please type some text'
        pass
        
    
        