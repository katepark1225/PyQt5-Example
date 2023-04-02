from PyPDF2 import PdfReader
import pandas as pd
import re
import numpy as np
import random

def pluralize_short_terms(terminology):
    pluralized=[]
    term_kor=[]
    kor_pronunciation=[]
    for i, x in terminology.iterrows():
        char = x['term'][len(x['term'])-2:]
        if char == "s":
            pluralized.append(x['term'] + "es")
            term_kor.append(x['term_kor'])
            kor_pronunciation.append(x['kor_pronunciation'])
        elif char == "y":
            pluralized.append(x['term'][:len(x['term']-2)] + "ies")
            term_kor.append(x['term_kor'])
            kor_pronunciation.append(x['kor_pronunciation'])
        else:
            pluralized.append(x['term'] + "s")
            term_kor.append(x['term_kor'])
            kor_pronunciation.append(x['kor_pronunciation'])
            pluralized.append(x['term'] + "'s")
            term_kor.append(x['term_kor'])
            kor_pronunciation.append(x['kor_pronunciation'])
    i=0
    while i < len(pluralized):
        terminology.loc[len(terminology)] = [pluralized[i], term_kor[i], kor_pronunciation[i]]
        i+=1
    return terminology

def pluralize_long_terms(terminology):
    conjugative = ['of', 'for']
    plural_forms, pluralize, pluralized = [], [], []
    for i, x in terminology.iterrows():
        isFound=False
        for conj in conjugative:
            if conj in x['term']:
                str = (" ".join(x['term'].split(" "))).split(conj)[0].strip()
                pluralize.append(str)
                isFound=True
        if isFound == False:
            pluralize.append(x['term'].split(" ")[-1])
    for word in pluralize:
        if [','.join(word)][-1] == 's':
            pluralized.append(word + 'es')
        elif [','.join(word)][-1] == 'y':
            pluralized.append(word[:len(word)-2] + 'ies')
        else:
            pluralized.append(word + 's')
    for i, x in terminology.iterrows():
        plural_forms.append(x['term'].replace(pluralize[i], pluralized[i]))
    return plural_forms

def detect_link(word):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, word)
    if len(url) > 0:
        return True
    else:
        return False
    
def detect_next_line(ln, special_symbols, long_term):
    capital_words = ["IT"]
    symbols = [",", ".", "(", ")", "{", "}", "[", "]", "-", "?", "<", ">", "®", "_"]
    for word in ln.split(" "):
        res = re.findall('[A-Z][^A-Z]*', word)
        if len(res) > 1:
            _res=[]
            for char in res:
                isFound=False
                for symbol in symbols:
                    if symbol in char:
                        _res.append(char.replace(symbol, ""))
                        isFound=True
                if isFound==False:
                    _res.append(char)
            joined_word = "".join(_res)
            isFound=False
            if (special_symbols[special_symbols['term'] == joined_word.lower()].count() > 0).any():
                isFound=True
            else:
                for w in capital_words:
                    if w == joined_word:
                        isFound=True
            if isFound == False:
                splitted_by_space = " ".join(_res)
                if (long_term[long_term['term'] == splitted_by_space.lower()].count() > 0).any():
                    ln = ln.replace(joined_word, splitted_by_space)
                else:
                    ln = ln.replace(joined_word, "\n".join(_res))
    return ln

def join_lines(lines):
    matching_symbols = [["(", ")"], ["{", "}"], ["[", "]"]]
    quotation_marks = ['"', "'"]
    final = ""
    for line in lines.split("\n"):
        isLine = True
        chars = [char[0] for char in line.split()]
        for char in chars:
            if char.islower():
                final += " " + line
                isLine = False
            break
        for symbol in matching_symbols:
            if symbol[1] in line and symbol[0] not in line:
                final += " " + line
                isLine = False
        for mark in quotation_marks:
            if mark in line and line.count(mark) == 1:
                final += " " + line
                isLine = False
        if isLine == True:
            final += "\n" + line
    final = final.replace("  ", " ")
    return final

def remove_repeated_lines(output):
    input=""
    for phrase in output.split("."):
        if output.count(phrase) > 1:
            continue
        else:
            input += " " + phrase
    return input

def random_number():
    i=0
    rand=""
    while i < 10:
        rand += str(random.randrange(1,10))
        i+=1
    return rand

def terminology():
  # DB 구축 전에 담은 데이터 리스트
  # DB를 구축해야 용어 번역을 수정할 수 있음
    terms = [["functional escalation", "펑셔널 에스컬레이션"], ["hierarchical escalation", "하이얼키칼 에스컬레이션"], ["single point of contact", "싱글 포인트 오브 컨택"],
             ["support hour", "서포트아워"], ["service desk", "서비스데스크"], ["support level", "서포트레벨"], ["incident management", "인시던트 메니지먼트"],
             ["major incident", "메이져 인시던트"], ["request fulfillment", "리케스트 풀필먼트"], ["request model", "리케스트 모델"], ["service request", "서비스 레벨"],
             ["problem management", "프로블럼 메니지먼트"], ["proactive problem management", "프로엑티브 프로블럼 메니지먼트"], ["change advistory board", "체인지 어드바이서리 보드"], 
             ["standard change", "스텐더드 체인지"], ["request for change", "리케스트 포 체인지"], ["configuration item", "컨피겨레이션 아이템"], 
             ["ci type", "CI 타입"], ["change management", "체인지 메니지먼트"], ["change model", "체인지 모델"], ["change schedule", "체인지 스케쥴"], 
             ["emergency change", "이머젠시 체인지"],
             ["emergency change advisory board", "이머젠시 체인지 어드바이서리 보드"], ["normal change", "노멀 체인지"], 
             ["configuration management data base", "컨피겨레이션 메니지먼트 데이터베이스"], ["asset management", "에셋 메니지먼트"]
             , ["configuration record", "컨피겨레이션 레코드"], ["service asset", "서비스 에셋"], ["configuration management", "컨피겨레이션 메니지먼트"], 
             ["service level agreement", "서비스 레벨 어그리먼트"], ["information technology infrastructure library", "Information Technology Infrastructure Library"],
             ["service level management", "서비스 레벨 메니지먼트"], ["event management", "이벤트 메니지먼트"], ["proactive monitoring", "프로액티브 모니터링"], 
             ["reactive monitoring", "리액티브 모니터링"], ["back out", "벡아웃"], ["known error", "노운에러"], ["service provider", "서비스 프로바이더"]]
    terminology = pd.DataFrame(terms, columns=['term', 'term_kor'])
    terminology['code'] = np.nan
    plural_form = pluralize_long_terms(terminology)
    for idx, ele in enumerate(plural_form):
        terminology.loc[len(terminology), 'term'] = ele
        terminology.loc[len(terminology)-1, 'term_kor'] = terms[idx][1]
    for i, x in terminology.iterrows():
        terminology.loc[i, 'code'] = random_number()
    # DB 구축 전에 담은 데이터 리스트
    terms = [["activity", "액티비티"], ["client", "클라이언트"], ["function", "펑션"], ["impact", "임팩트"], ["priority", "프라이오리티"], ["process", "프로세스"], 
             ["resolution", "레솔루션"], ["role", "롤"], ["service", "서비스"], ["urgency", "어젠시"], ["user", "유저"], ["escalation", "에스컬레이션"], ["incident", "인시던트"],
             ["problem", "프러블럼"], ["workaround", "워크어라운드"], ["back-out", "백아웃"], ["backout", "백아웃"], ["change", "체인지"], ["attribute", "어트리뷰트"], ["alert", "알러트"], 
             ["event", "이벤트"], ["monitoring", "모니터링"], ["lifecycle", "라이프사이클"], ["resource", "리소스"]]
    short_terms = pd.DataFrame(terms, columns=['term', 'term_kor'])
    short_terms['code'] = np.nan
    for i, x in short_terms.iterrows():
        short_terms.loc[i, 'code'] = random_number()
    # DB 구축 전에 담은 데이터 리스트
    specialSymbols = [["IT", "IT", "아이티"], ["itil", "ITIL", "아이틸"], ["sr", "SR", "에스알"], ["sla", "SLA", "에스엘레이"], ["cab", "CAB", "씨에이비"], 
                      ["ecab", "ECAB", "이씨에이비"], ["rfc", "RFC", "알에프씨"], ["ci", "CI", "씨아이"], ["cmdb", "CMDB", "씨엠디비"]]
    special_symbols = pd.DataFrame(specialSymbols, columns=['term', 'term_kor', 'kor_pronunciation'])
    special_symbols = pluralize_short_terms(special_symbols)
    special_symbols['code'] = np.nan
    for i, x in special_symbols.iterrows():
        special_symbols.loc[i, 'code'] = random_number()
    return [terminology, short_terms, special_symbols]

def check_dissected_terms(input, long_term, short_term, special_symbols):
    last_word=""
    output=""
    for line in input.split("\n"):
        if last_word != "":
            joined_word = last_word + line.split(" ")[0]
            joined_word_long = last_word + " " + line.split(" ")[0]
            if (long_term[long_term['term'] == joined_word_long.lower()].count() > 0).any():
                if " " in joined_word_long:
                    output += " " + line
                else:
                    output += line
            elif (short_term[short_term['term'] == joined_word.lower()].count() > 0).any():
                output += line
            elif (special_symbols[special_symbols['term'] == joined_word.lower()].count() > 0).any():
                output += line
            else:
                output += "\n" + line
        else:
            output += "\n" + line
        last_word = line.split(" ")[-1]
    return output

def add_space(ln):
    closing_symbols = [')', '}', ']', ",", '"', "'"]
    for symb in closing_symbols:
        ln = ln.replace(symb, symb+" ")
    return ln.replace("  ", " ")

def standalone_parentheses(ln):
    isTrue=0
    for id, word in enumerate(ln.split()):
        if id == 0:
            for idx, char in enumerate(word.split()):
                if idx == 0:
                    if char == "(":
                        isTrue=1
                    else:
                        continue
        elif id == len((ln.split()))-1:
            for idx, char in enumerate(word.split()):
                if idx == len((word.split()))-1:
                    if char == ")":
                        isTrue=2
    if isTrue == 2:
        return True
    else:
        return False

def join_splitted_word(ln):
    extracted_letters = []
    for word in ln.split(" "):
        if len(word) == 1:
            extracted_letters.append(word)
    extracted_words = []
    extracted_word = ""
    for idx, char in enumerate(extracted_letters):
        if char.isupper():
            if extracted_word != "":
                extracted_words.append(extracted_word)
            extracted_word = char
        else:
            extracted_word += char
            if idx == len(extracted_letters)-1:
                extracted_words.append(extracted_word)
    for word in extracted_words:
        current = " ".join(word)
        ln = ln.replace(current, word)
    return ln

def load_file(path):
    pdf = PdfReader(path)
    pages = pdf.pages
    terms = terminology()
    long_term = terms[0]
    short_term = terms[1]
    special_symbols = terms[2]
    page_number=0
    for page in pages:
        page_number+=1
        if page_number != 1: # remove
            continue
        text = page.extract_text()
        output=""
        for ln in text.split("\n"):
            output += "\n" + join_splitted_word(ln)
        lines=""
        for ln in output.split('\n'):
            lines += "\n" + detect_next_line(ln, special_symbols, long_term)
        output = join_lines(lines)
        output = remove_repeated_lines(output)
        output = check_dissected_terms(output, long_term, short_term, special_symbols)
        lines=""
        for ln in output.split("\n"):
            lines += "\n" + add_space(ln)
        output=""
        for ln in lines.split("\n"):
            if standalone_parentheses(ln) == True:
                output += " " + ln
            else:
                output += "\n" + ln
    return output
