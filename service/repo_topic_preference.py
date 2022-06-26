import os
import argparse
import pickle
import json

from bert_test_for_asentence import test
from data_prepare import preocess_text


class Repo_Topic_Preferences():
    def __init__(self, readmetext, destext):
        self.readmetext = readmetext
        self.destext = destext
        
        self.input_preprocess()

    def input_preprocess(self):
        self.readmetext =preocess_text(self.readmetext)
        self.destext = preocess_text(self.destext)

    def cal_topic_preferences(self):
        text = self.destext + self.readmetext
        prediction = test(text)
        print(prediction)
        return prediction