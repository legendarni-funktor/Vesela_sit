from Tkinter import Tk
from tkFileDialog import askopenfilename
from random import shuffle

def select_path():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    return askopenfilename() # show an "Open" dialog box and return the path to the selected file

def prepare_sets(positive, negative, ratio, train_set, valid_set, test_set):
    index_pos_train = int(len(positive)*ratio[0])
    index_neg_train = int(len(negative)*ratio[0])
    
    index_pos_valid = int(len(positive)*ratio[1])
    index_neg_valid = int(len(negative)*ratio[1])
    
    shuffle(positive)
    shuffle(negative)
    
    train_set.extend(positive[0:index_pos_train])
    train_set.extend(negative[0:index_neg_train])
    
    valid_set.extend(positive[index_pos_train: index_pos_train + index_pos_valid])
    valid_set.extend(negative[index_neg_train: index_neg_train + index_neg_valid])
    
    test_set.extend(positive[index_pos_train + index_pos_valid:])
    test_set.extend(negative[index_neg_train + index_neg_valid:])
    
    print "    Total count of training patterns: {0}".format(len(train_set))    
    print "    Every day I'm shuffling!!!! (data sets)"
    shuffle(train_set)
    shuffle(valid_set)
    shuffle(test_set)