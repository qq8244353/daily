import os, random, subprocess, re
from openai import OpenAI
from dotenv import load_dotenv
from mdutils.mdutils import MdUtils

load_dotenv(override=True)
client = OpenAI(
    api_key = os.environ['APIKEY']
)
english_list_str="parent,husband,wife,kid,twin,relative,cousin,ancestor,job,work,occupation,career,business,interview,hire,retire,clerk,officer,engineer,artist,director,actor,nurse,secretary,agent,civil,mayor,chairperson,professor,principal,expert,leader,queen,prince,royal,slave,hall,office,bank,apartment,library,gym,museum,theater,studio,stadium,temple,shrine,castle,tower,entrance,exit,architecture,avenue,block,corner,intersection,zone,square,market,path"
japanese_list_str="親、夫、妻、子供、双子、親戚、いとこ、先祖、仕事、仕事、職業、職業、仕事、面接、雇う、退職する、店員、警官、技師、芸術家、監督、俳優、看護師、秘書、代行業者、民間の、市長、議長、教授、校長、専門家、指導者、女王、王子、国王の、奴隷、会館、事務所、銀行、アパート、図書館、体育館、博物館、劇場、スタジオ、競技場、寺院、聖堂、城、塔、入口、出口、建築、大通り、１区画、曲がり角、交差点、地帯、広場、市場、小道"
english_list = english_list_str.split(',')
japanese_list = japanese_list_str.split('、')
print(len(english_list), len(japanese_list))
if len(english_list) != len(japanese_list):
    exit(0)
n = len(english_list)
count=9
filename="{:0>3d}.md".format(count)
if os.path.isfile(filename):
    print("{}が存在するようです。続けますか？(y/n)".format(filename))
    s = input()
    if s == "n":
        exit(0)
mdFile = MdUtils(file_name=filename)
mdFile.new_line("""---
css: 'body{{ column-count: 2}}'
pdf_options:
  format: A4
  margin: 10mm
  printBackground: true
---

第{}回クイズ
""".format(count))

item_list = []
answer_str = ""
# クイズの順番をランダムにする
ind = [ i for i in range(n) ]
random.shuffle(ind)

for j in range(n):
    i = ind[j]
    cnt = -1
    # ４択クイズにしない
    if japanese_list[i][0] == "！":
        cnt = 5
    # ４択クイズの処理
    while cnt < 5:
        cnt+=1
        if cnt > 0:
              print("retry: {}".format(cnt))
        japanese_word = japanese_list[i]
        # 助詞のマーカーを解釈
        particle = ""
        if not re.search(r'（.*）', japanese_word) is None:
            particle = re.match(r'（.*）', japanese_word).group()[1:-1]
            japanese_word = re.sub(r'（.*）', "", japanese_word)

        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "あなたは高校の英語教師です。\nあなたは専門的な知識を利用して難しい英単語のクイズを作ろうとしています。英単語と答えを教えるので英単語の意味として正しくないダミー選択肢を5つ教えてください。答えは日本語で表記してください。また、単語のみカンマ区切りで出力してください。また、品詞を一致させてください\n出力形式の例を以下に示します。\n例）truth,真実 \n 信念,発見,成果 \n 例）excellent,素晴らしい \n 悪い,劣った,平均的な" },
            {"role": "user", "content": "{},{}".format(english_list[i], particle + japanese_word) }
          ]
        )
        dummys = response.choices[0].message.content.strip().split(',')
        # 助詞を加えたものとする
        japanese_word = particle + japanese_word
        dummys = list(map(lambda s: s if re.match(r'{}'.format(particle), s) else particle + s, dummys))

        alpha_included = False
        index_memo = -1
        valid_dummys = []
        for k in range(len(dummys)):
            if re.search(r'[a-zA-Z]|選択肢|\n', dummys[k]) is None and dummys[k] != japanese_word:
                valid_dummys.append(dummys[k])
        valid_dummys = list(set(valid_dummys))
        print(english_list[i], japanese_word, valid_dummys)
        if len(valid_dummys) < 3:
            print("too short valid dummys len: {}".format(len(valid_dummys)))
            continue
        choice = [japanese_word] + valid_dummys[:3]
        random.shuffle(choice)
        print(choice)
        choice_str = "{}, 2. {}, 3. {}, 4. {}".format(choice[0], choice[1], choice[2], choice[3])
        item_list.append(english_list[i])
        item_list.append([choice_str])
        # 解のリストを更新
        for k in range(4):
            if choice[k] == japanese_word:
                answer_str += "[{}]:{}, ".format(j + 1, k + 1)
                break
        # 完答クイズに追加しない
        cnt = 0
        break
    # 完答クイズの追加
    if cnt == 5:
        not_choice_str = "{} の意味を書け".format(english_list[i])
        item_list.append(not_choice_str)
        answer_str += "[{}]:{}, ".format(j + 1, japanese_list[i][1:])
        print("! ", english_list[i], japanese_list[i], not_choice_str)

mdFile.new_list(item_list, marked_with='1')
mdFile.new_line("<div style=\"page-break-before:always\"></div>")
mdFile.new_line(answer_str)
mdFile.create_md_file()

# 先頭を消す
subprocess.run("sed -ie '1,4d' {}".format(filename), shell=True)
# pdfに変換
subprocess.run("md-to-pdf {}".format(filename), shell=True)
