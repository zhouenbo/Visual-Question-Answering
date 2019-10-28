"""
Given the VQA annotations & questions file, generates a dataset file (.txt) in the following format:

`image_name` \t `question` \t `answer`

The resulting file vqa_dataset.txt is stored in the --output_dir
"""

import argparse
import os
from datahelper import VQA as DataHelper
from transformers import BertTokenizer

def pad_with_zero(num):
    total_digits = 6 if args.balanced_real_images else 5
    num_zeros = total_digits - len(str(num))
    return num_zeros * "0" + str(num)


parser = argparse.ArgumentParser(description='Prepare data for balanced real images QA aka COCO')

parser.add_argument('-a', '--annot_file',   type=str, help='path to annotations file (.json)', required=True)
parser.add_argument('-q', '--ques_file',    type=str, help='path to questions file (.json)', required=True)
parser.add_argument('-o', '--output_dir',   type=str, help='stores vqa_dataset.txt (img, ques, ans)', required=True)

group = parser.add_mutually_exclusive_group()
group.add_argument("--balanced_real_images", action="store_true",
                   help="image format is COCO_train2014_000000xxxxxx.jpg")

group.add_argument("--abstract_scene_images", action="store_true",
                   help="image format is abstract_v002_train2015_0000000xxxxx.png")

args = parser.parse_args()

# image_prefix = args.input_dir + "images/"
image_prefix = ""
image_postfix = ""
assert (args.balanced_real_images != args.abstract_scene_images)
if args.balanced_real_images:
    image_prefix += "COCO_train2014_000000"
    image_postfix = ".jpg"
elif args.abstract_scene_images:
    image_prefix += "abstract_v002_train2015_0000000"
    image_postfix = ".png"

helper = DataHelper(args.annot_file, args.ques_file) # from VQA
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

output_file_path = os.path.join(args.output_dir, "vqa_dataset.txt")
input_img_path = os.path.join(args.annot_file, "images/")
# each line contains: image_filename[tab]question[tab]answer
with open(output_file_path, "w") as output_file:
    for i in range(len(helper.dataset['annotations'])):

        imd_id = helper.dataset['annotations'][i]['image_id']
        img_name = image_prefix + pad_with_zero(imd_id) + image_postfix

        ques_id = helper.dataset['annotations'][i]['question_id']
        question = helper.qqa[ques_id]['question']

        # Convert to comma-separated token string (not with BERT)
        # question = ','.join(question.strip().split())

        answer = helper.dataset['annotations'][i]['multiple_choice_answer']

        text_2_bert = "[CLS] " + question + "[SEP] " + answer + " [SEP]"
        tokenized_text = tokenizer.tokenize(text_2_bert)
        tokenized_text = ",".join(tokenized_text)
        if i % 3000 == 0:
            print(tokenized_text)
            print(os.path.join(input_img_path, img_name))
            print("exists?", os.path.exists(os.path.join(input_img_path, img_name)))
        output_file.write(img_name + "\t" + tokenized_text + "\n")
