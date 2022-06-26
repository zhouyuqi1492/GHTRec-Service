from genericpath import exists
import os
import sys
import json
import re

def build_filename2label(data_train_dir, data_test_dir, dst_file):
    filename2label = {}
    for sub_dir in os.listdir(data_train_dir):
        if not os.path.isdir(os.path.join(data_train_dir, sub_dir)):
            continue
        if sub_dir == ".DS_store":
            continue

        curr_dir = os.path.join(data_train_dir, sub_dir)
        for filename in os.listdir(curr_dir):
            if not os.path.isfile(os.path.join(curr_dir, filename)):
                continue
            if filename == ".DS_store":
                continue

            if filename not in filename2label:
                filename2label[filename] = []
            filename2label[filename].append(sub_dir)
    for sub_dir in os.listdir(data_test_dir):
        if not os.path.isdir(os.path.join(data_test_dir, sub_dir)):
            continue
        if sub_dir == ".DS_store":
            continue

        curr_dir = os.path.join(data_test_dir, sub_dir)
        for filename in os.listdir(curr_dir):
            if not os.path.isfile(os.path.join(curr_dir, filename)):
                continue
            if filename == ".DS_store":
                continue

            if filename not in filename2label:
                filename2label[filename] = []
            filename2label[filename].append(sub_dir)
    with open(dst_file, "w", encoding="utf-8") as f:
        json.dump(filename2label, f, ensure_ascii=False)

def build_label2idx(data_train_dir, data_test_dir, dst_file):
    label2idx = {}
    for sub_dir in os.listdir(data_train_dir):
        if not os.path.isdir(os.path.join(data_train_dir, sub_dir)):
            continue
        if sub_dir == ".DS_store":
            continue

        if sub_dir not in label2idx:
            label2idx[sub_dir] = len(label2idx)
    for sub_dir in os.listdir(data_test_dir):
        if not os.path.isdir(os.path.join(data_test_dir, sub_dir)):
            continue
        if sub_dir == ".DS_store":
            continue

        if sub_dir not in label2idx:
            label2idx[sub_dir] = len(label2idx)
    with open(dst_file, "w", encoding="utf-8") as f:
        json.dump(label2idx, f, ensure_ascii=False)

def preocess_text(text):
    try:
        text = eval(text).decode()
    except Exception as e:
        print(e)
        pass
    pattern = re.compile(r"\[(.*?)\]\(.*?\)", re.I|re.M)
    while True:
        match = pattern.search(text)
        if not match:
            break
        text = text.replace(match.group(0), match.group(1))
    while "  " in text:
        text = text.replace("  ", " ") 
    text = text.replace("-", "")
    text = text.replace("\n", " ")
    text = re.sub(r"#+", "", text)
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"<img.+?>", "", text)
    text = re.sub(r"<a.+?>", "", text)
    text = re.sub(r"<p.+?>", "", text)
    text = re.sub(r"</?[ap]>", "", text)
    text = re.sub(r"</?img>", "", text)
    return text

def clear_md(data_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    for sub_dir in os.listdir(data_dir):
        curr_dir = os.path.join(data_dir, sub_dir)
        new_curr_dir = os.path.join(dst_dir, sub_dir)
        if not os.path.isdir(curr_dir):
            continue
        if sub_dir == ".DS_store":
            continue
        
        if not os.path.exists(new_curr_dir):
            os.mkdir(new_curr_dir)
        
        for filename in os.listdir(curr_dir):
            curr_file = os.path.join(curr_dir, filename)
            if not os.path.isfile(curr_file):
                continue
            if filename == ".DS_store":
                continue
            new_curr_file = os.path.join(new_curr_dir, filename)
            with open(curr_file, "r", encoding="utf-8") as inf, open(new_curr_file, "w", encoding="utf-8") as outf:
                print("processing file {}".format(curr_file))
                outf.write(preocess_text(inf.read()))

def has_chinese(text):
    for ch in text:
        if u"\u4e00" <= ch <=  u"\u9fff":
            return True
    return False

def remove_md_with_chinese(data_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    for sub_dir in os.listdir(data_dir):
        curr_dir = os.path.join(data_dir, sub_dir)
        new_curr_dir = os.path.join(dst_dir, sub_dir)
        if not os.path.isdir(curr_dir):
            continue
        if sub_dir == ".DS_store":
            continue
        if not os.path.exists(new_curr_dir):
            os.mkdir(new_curr_dir)
        
        for filename in os.listdir(curr_dir):
            curr_file = os.path.join(curr_dir, filename)
            if not os.path.isfile(curr_file):
                continue
            if filename == ".DS_store":
                continue
            new_curr_file = os.path.join(new_curr_dir, filename)
            with open(curr_file, "r", encoding="utf-8") as inf:
                text = inf.read()
            if has_chinese(text):
                with open(new_curr_file, "w", encoding="utf-8") as outf:
                    outf.write(text)
                os.remove(curr_file)

def remove_md_with_chinese_for_test(data_dir):
    for sub_dir_1 in os.listdir(data_dir):
        curr_dir_1 = os.path.join(data_dir, sub_dir_1)
        for sub_dir_2 in os.listdir(curr_dir_1):
            curr_dir_2 = os.path.join(curr_dir_1, sub_dir_2)
            for sub_dir_3 in os.listdir(curr_dir_2):
                curr_dir = os.path.join(curr_dir_2, sub_dir_3)
                curr_file = os.path.join(curr_dir, "readme.txt")
                if not os.path.exists(curr_file):
                    continue
                new_curr_file = os.path.join(curr_dir, "readme_has_chinese.txt")
                with open(curr_file, "r", encoding="utf-8") as f:
                    text = f.read()
                if has_chinese(text):
                    os.rename(curr_file, new_curr_file)

def remove_md_with_chinese_for_test2(data_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    for sub_dir_1 in os.listdir(data_dir):
        curr_dir_1 = os.path.join(data_dir, sub_dir_1)
        for sub_dir_2 in os.listdir(curr_dir_1):
            curr_dir_2 = os.path.join(curr_dir_1, sub_dir_2)
            for sub_dir_3 in os.listdir(curr_dir_2):
                curr_dir_3 = os.path.join(curr_dir_2, sub_dir_3)
                if not os.path.isdir(curr_dir_3):
                    continue
                for sub_dir_4 in os.listdir(curr_dir_3):
                    curr_dir_4 = os.path.join(curr_dir_3, sub_dir_4)
                    if not os.path.isdir(curr_dir_4):
                        continue
                    for filename in os.listdir(curr_dir_4):
                        curr_file = os.path.join(curr_dir_4, filename)
                        with open(curr_file, "r", encoding="utf-8") as f:
                            text = f.read()
                        if has_chinese(text):
                            with open(os.path.join(dst_dir, filename), "w", encoding="utf-8") as outf:
                                outf.write(text)
                            os.remove(curr_file)

def has_chinese_data(data_dir):
    cnt = 0
    for sub_dir in os.listdir(data_dir):
        curr_dir = os.path.join(data_dir, sub_dir)
        if not os.path.isdir(curr_dir):
            continue
        if sub_dir == ".DS_store":
            continue
        
        cnt += len(os.listdir(curr_dir))
    print(cnt)

if __name__ == "__main__":
    # data_train_dir = "./data/train/"
    # data_test_dir = "./data/test"
    # dst_dir = "./files/filename2label.json"
    # build_filename2label(data_train_dir, data_test_dir, dst_dir)

    # data_train_dir = "./data/train/"
    # data_test_dir = "./data/test/"
    # dst_file = "./files/label2idx.json"
    # build_label2idx(data_train_dir, data_test_dir, dst_file)
    # text = "[Spaceship screenshots](https://raw.githubusercontent.com/a1studmuffin/SpaceshipGenerator/master/screenshots/spaceships_grid.jpg)\n\nUsage"
    # print(preocess_text(text))
    # clear_md("./raw_data/train/", "./data/train/")
    # clear_md("./raw_data/test/", "./data/test/")

    # print(has_chinese("wocongshiyigeren "))
    # remove_md_with_chinese("./data/train", "./data_has_chinese/train")
    # remove_md_with_chinese("./data/test", "./data_has_chinese/test")
    # has_chinese_data("./data_has_chinese/train")
    # has_chinese_data("./data_has_chinese/test")
    remove_md_with_chinese_for_test2("./history", "./history_has_chinese")
