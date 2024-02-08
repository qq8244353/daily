import os, random, subprocess, re
from openai import OpenAI
from dotenv import load_dotenv
from mdutils.mdutils import MdUtils

load_dotenv(override=True)
client = OpenAI(
    api_key = os.environ['APIKEY']
)
english_list_str="theme,sentence,cycle,concept,rhythm,tradition,theory,correct,blank,quiet,smooth,wet,chief,raw,personal,double,dirty,normal,full,simple,equal,quick,rapid,ideal,rough,silent,violent,rich,perfect,weak,upper,inner,awful,false,vivid,pure,minor,mild,admire,drop,reflect,dig,beg,freeze,adopt,measure,flow,fulfill"
japanese_list_str="テーマ、文、周期、概念、リズム、伝統、理論、正しい、白紙の、静かな、滑らかな、濡れた、最高の、生の、個人の、２倍の、汚れた、普通の、いっぱいの、簡単な、等しい、短時間の、急速な、理想的な、大まかな、無言の、暴力的な、豊富な、完全な、弱い、上の方の、内部の、ひどい、間違った、鮮やかな、純粋な、重要ではない、穏やかな、称賛する、落とす、映し出す、掘る、懇願する、凍る、採用する、測る、流れる、実現させる"
english_list = english_list_str.split(',')
japanese_list = japanese_list_str.split('、')
print(len(english_list), len(japanese_list))
if len(english_list) != len(japanese_list):
    exit(0)
n = len(english_list)
count=5
filename="{:0>3d}.md".format(count)
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

choice_str_list = []
answer_str = ""
# クイズの順番をランダムにする
ind = [ i for i in range(n) ]
random.shuffle(ind)
for j in range(n):
    i = ind[j]
    cnt=-1
    while True:
        cnt+=1
        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "あなたは高校の英語教師です。\nあなたは専門的な知識を利用して難しい英単語のクイズを作ろうとしています。英単語と答えを教えるので英単語の意味として正しくないダミー選択肢を5つ教えてください。答えは日本語で表記してください。また、単語のみカンマ区切りで出力してください。また、品詞を一致させてください\n出力形式の例を以下に示します。\n例）truth,真実 \n 信念,発見,成果 \n 例）excellent,素晴らしい \n 悪い,劣った,平均的な" },
            {"role": "user", "content": "{},{}".format(english_list[i], japanese_list[i]) }
          ]
        )
        dummys = response.choices[0].message.content.strip().split(',')
        if cnt > 0:
              print("retry: {}".format(cnt))
        alpha_included = False
        index_memo = -1
        valid_dummys = []
        for k in range(len(dummys)):
            if re.search(r'[a-zA-Z]|選択肢|\n', dummys[k]) is None and dummys[k] != japanese_list[i]:
                valid_dummys.append(dummys[k])
        valid_dummys = list(set(valid_dummys))
        print(english_list[i], japanese_list[i], valid_dummys)
        if len(valid_dummys) < 3:
            print("too short valid dummys len: {}".format(len(valid_dummys)))
            continue
        choice = [japanese_list[i]] + valid_dummys[:3]
        random.shuffle(choice)
        print(choice)
        choice_str_list.append("{}, 2. {}, 3. {}, 4. {}".format(choice[0], choice[1], choice[2], choice[3]))
        for k in range(4):
            if choice[k] == japanese_list[i]:
                answer_str += "[{}]:{}, ".format(j + 1, k + 1)
                break
        break

item_list = []
for i in range(n):
    j = ind[i]
    item_list.append(english_list[j])
    item_list.append([choice_str_list[i]])

mdFile.new_list(item_list, marked_with='1')
mdFile.new_line("<div style=\"page-break-before:always\"></div>")
mdFile.new_line(answer_str)
mdFile.create_md_file()

# 先頭を消す
subprocess.run("sed -ie '1,4d' {}".format(filename), shell=True)
# pdfに変換
subprocess.run("md-to-pdf {}".format(filename), shell=True)
