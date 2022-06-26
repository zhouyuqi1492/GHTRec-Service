import os
import argparse
import pickle
import json
import sys
import time

from transformers import BertModel, BertTokenizer
import torch.nn as nn
import torch
from torch.optim import Adam


CONTEXT_PAD = 0
MODEL_SAVE_PATH = "./trained_models/model_30_0.8664965986394558.mdl"
LABEL_IDX_PATH = "./files/label2idx.json"
N_CLASSES = 134
MODEL_NAME = "bert-base-uncased"
IDX2LABEL = {}

with open(LABEL_IDX_PATH, "r", encoding="utf-8") as f:
    label2idx = json.load(f)
IDX2LABEL = {value: key for key, value in label2idx.items()}

class BertTopicModel(nn.Module):
    def __init__(self):
        super().__init__()

        # model components
        self.bert = BertModel.from_pretrained(MODEL_NAME)
        self.predict = nn.Sequential(
            # nn.Dropout(0.3),
            nn.Linear(in_features=768, out_features=N_CLASSES)
        )
        self.sigmod = nn.Sigmoid()
        self.loss = nn.BCELoss()
        pass

    def forward(self, tokens, labels=None, is_train=False):
        # tokens: bsz * length
        mask = tokens != CONTEXT_PAD
        bert_output = self.bert(input_ids=tokens, attention_mask=mask)[1]

        logits = self.predict(bert_output)
        prediction = self.sigmod(logits)
        if not is_train:
            return prediction

        loss = self.loss(prediction, labels)
        return loss

def test(text, topn=8):
    judge = 1
    while(judge):
        try:
            model = BertTopicModel()
            model.load_state_dict(torch.load(MODEL_SAVE_PATH,map_location='cpu'))
            tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
            judge = 0
        except:
            print('tokenization HTTPSConnectionPool')
            print('休息10s')
            time.sleep(10)
    tokens = tokenizer.tokenize(text)
    tokens = tokenizer.convert_tokens_to_ids(tokens)
    tokens = tokenizer.build_inputs_with_special_tokens(tokens)
    tokens = torch.LongTensor([tokens[:512]])

    with torch.no_grad():
        prediction = model(tokens=tokens, is_train=False)

    stat = {}
    for idx, prob in enumerate(prediction[0]):
        stat[IDX2LABEL[idx]] = float(prob)
    stat = sorted(stat.items(), key=lambda x : x[1], reverse=True)
    return stat[:topn]

if __name__ == "__main__":
    with open(LABEL_IDX_PATH, "r", encoding="utf-8") as f:
        label2idx = json.load(f)
    IDX2LABEL = {value: key for key, value in label2idx.items()}
    # print(test("hhhh"))
    pass
    

