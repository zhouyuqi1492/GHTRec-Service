import os
from typing import Pattern

import torch.nn as nn
import torch
import re
from transformers import BertTokenizer, BertModel


text = 'https://web.archive.org/web/20211123000036/https://github.com/trending'
pattern = '/(\d+)/'
print(re.search(pattern, text).group(1)[:8])