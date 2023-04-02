import googletrans
from hangul_utils import split_syllables, join_jamos
import pandas as pd
import re
import numpy as np
import random

translator = googletrans.Translator()

def translate_text(input):
    return translator.translate(input, dest='ko', src='en').text

def append_string(output, word):
    if output == "":
        output = word
    else:
        output += " " + word
    return output

def check_noun(word, string):
    articles = ["the", "a", "an"]
    conjugative = ["of"]
    pronouns = ["he", "she", "it", "they", "we"]
    auxilliary = ["to"]
    input = []
    for str in string.split(" "):
        input.append(str)
    input.append(word)
    input.reverse()
    for idx, ele in enumerate(input):
        if idx == 0 and ele in pronouns:
            return False
        if idx == 0 and ele in auxilliary:
            return False
        if idx == 0 and ele in articles:
            return True
        if idx == 0 and ele in conjugative:
            return True
    return True # default

def conjugate_korean_simple(word, jamos):
    conjugative_001 = ['이', '가']
    conjugative_002 = ['는', '은']
    conjugative_003 = ['를', '을']
    conjugative_004 = ['으로']
    conjugative_005 = ['이가']
    conjugative_006 = ['이라고']
    korean_vowels = ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ', 'ㅐ', 'ㅔ', 'ㅒ', 'ㅖ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅞ', 'ㅝ', 'ㅟ', 'ㅢ']
    conjugation=""
    for ele in conjugative_001:
        if word == ele:
            if jamos[len(jamos)-1] in korean_vowels:
                conjugation = '가'
            else:
                conjugation = '이'
    for ele in conjugative_002:
        if word == ele:
            if jamos[len(jamos)-1] in korean_vowels:
                conjugation = '는'
            else:
                conjugation = '은'
    for ele in conjugative_003:
        if word == ele:
            if jamos[len(jamos)-1] in korean_vowels:
                conjugation = '를'
            else:
                conjugation = '을'
    for ele in conjugative_004:
        if word == ele:
            if jamos[len(jamos)-1] in korean_vowels:
                conjugation = "로"
    for ele in conjugative_005:
        if word == ele:
            if jamos[len(jamos)-1] in korean_vowels:
                conjugation = "가"
    for ele in conjugative_006:
        if word == ele:
            if jamos[len(jamos)-1] in korean_vowels:
                conjugation = "라고"
    return conjugation

def check_number(str):
    try:
        f=float(str)
    except ValueError:
        return False
    return True

def filter_text(text, long_term, short_term, special_symbols):
    long_terms_kor, terms, codes, long_terms_code, acronyms, acronyms_code = [], [], [], [], [], []
    conjugative = ['이', '가', '는', '은', '를', '을', '으로', '이가', '이라고']
    for i, x in special_symbols.iterrows():
        acronyms.append(x['term_kor'])
        acronyms_code.append(x['code'])
    for i, x in long_term.iterrows():
        long_terms_kor.append(x['term_kor'])
        long_terms_code.append(x['code'])
    for i, x in short_term.iterrows():
        terms.append(x['term_kor'])
        codes.append(x['code'])
    output=""
    for word in text.split(" "):
        isAppend=True
        code_number=""
        preceding_text=""
        succeeding_text=""
        for char in word:
            if check_number(char) == True:
                code_number+=str(char)
        if code_number.strip() != "" and code_number in word:
            if code_number != word:
                preceding_text = word.split(code_number)[0]
                succeeding_text = word.split(code_number)[1]
        for code in codes:
            if code in word:
                translated = terms[codes.index(code)]
                if len(word) > 10:
                    for conj in conjugative:
                        if word[10:] == conj:
                            jamos = split_syllables(translated)
                            conjugation = conjugate_korean_simple(word[10:], jamos)
                            succeeding_text = succeeding_text.replace(conj, conjugation)
                output += " " + preceding_text + translated + succeeding_text
                isAppend=False
        for code in long_terms_code:
            if code in word:
                translated = long_terms_kor[long_terms_code.index(code)]
                if len(word) > 10:
                    for conj in conjugative:
                        if word[10:] == conj:
                            jamos = split_syllables(translated)
                            conjugation = conjugate_korean_simple(word[10:], jamos)
                            succeeding_text = succeeding_text.replace(conj, conjugation)
                output += " " + preceding_text + translated + succeeding_text
                isAppend=False
        for code in acronyms_code:
            if code in word:
                translated = acronyms[acronyms_code.index(code)]
                if len(word) > 10:
                    for conj in conjugative:
                        if word[10:] == conj:
                            jamos = split_syllables(translated)
                            conjugation = conjugate_korean_simple(word[10:], jamos)
                            succeeding_text = succeeding_text.replace(conj, conjugation)
                output += " " + preceding_text + translated + succeeding_text
                isAppend=False
        if isAppend == True:
            output += " " + word
    return output

def base_word(word, df):
    for i, x in df.iterrows():
        if x['Word'] == word:
            return word
    if word[len(word)-2:] == "ss":
        return word
    if word[len(word)-1:] == "s":
        _word = word[:len(word)-1]
    if len(word) > 3 and word[len(word)-3:] == 'ies':
        _word = word[:len(word)-3] + "y"
    if len(word) > 4 and word[len(word)-4:] == "sses":
        _word = word[:len(word)-2]
    try:
        _word
        return _word
    except:
        return word

def detect_long_words(text, terms):
    for i, x in terms.iloc[::-1].iterrows():
        if x['term'] in text:
            text = text.replace(x['term'], x['code'])
    return text

def detect_acronyms(ln, special_symbols):
    special_acronyms = ['IT']
    symbols = [",", ".", "(", ")", "-", "_", "&", "?"]
    for word in ln.split(" "):
        for symbol in symbols:
            if symbol in word:
                word = word.replace(symbol, "")
        if (special_symbols[special_symbols['term'] == word.lower()].count() == 1).any():
            ln = ln.replace(word, special_symbols[special_symbols['term'] == word.lower()]['code'].to_string(index=False))
        elif word in special_acronyms:
            if (special_symbols[special_symbols['term'] == word].count() == 1).any():
                ln = ln.replace(word, special_symbols[special_symbols['term'] == word.lower()]['code'].to_string(index=False))
    return ln

def pluralize_long_terms(terminology):
    conjugative = ['of', 'for']
    plural_forms, pluralize, pluralized = [], [], []
    for i, x in terminology.iterrows():
        isFound=False
        for conj in conjugative:
            if conj in x['term']:
                if "and" not in x['term']:
                    before_conj = x['term'].split(conj)[0].strip().split(" ")[-1]
                    pluralize.append(before_conj)
                    isFound=True
                elif "and" in x['term'] and "," not in x['term']: # no commas
                    before_and = x['term'].split("and")[0].split(" ")[-1]
                    after_and = x['term'].split("and")[1].split(" ")[0]
                    pluralize.append(before_and + " " + after_and)
                    isFound=True
        if isFound == False:
            pluralize.append(x['term'].split(" ")[-1])
    for word in pluralize:
        if len(word.strip().split(" ")) == 1:
            if [','.join(word)][-1] == 's':
                pluralized.append(word + 'es')
            elif [','.join(word)][-1] == 'y':
                pluralized.append(word[:len(word)-2] + 'ies')
            else:
                pluralized.append(word + 's')
        else:
            _pluralized=[]
            for w in word.strip().split(" "):
                if [','.join(w)][-1] == 's':
                    _pluralized.append(w + 'es')
                elif [','.join(w)][-1] == 'y':
                    _pluralized.append(w[:len(w)-2] + 'ies')
                else:
                    _pluralized.append(w + 's')
            pluralized.append(" ".join(_pluralized))
    for i, x in terminology.iterrows():
        if len(pluralize[i].split(" ")) == 1 and len(pluralized[i].split(" ")) == 1:
            plural_forms.append(x['term'].replace(pluralize[i], pluralized[i]))
        else:
            for idx, word_to_change in enumerate(pluralize[i].split(" ")):
                word_changed = x['term'].replace(word_to_change, pluralized[i].split(" ")[idx])
            plural_forms.append(word_changed)
    return plural_forms

def detect_word(text, terms):
    _terms = []
    codes = []
    for i, x in terms.iterrows():
        _terms.append(x['term'])
        codes.append(x['code'])
    punctuation_marks = [',', '.', ';', "'", '"', '-', '_', '®']
    df = pd.read_csv("singular_nouns.csv")
    output = ""
    root = ""
    for word in text.split(" "):
        root = word
        if len(word) > 2:
            if word[len(word)-1:] == "s":
                word = base_word(word, df)
        punctuation_mark = ""
        for mark in punctuation_marks:
            if mark in word:
                punctuation_mark = mark
                word = word.replace(mark, "")
        if word in _terms:
            if check_noun(word, output) == True:
                temp_text = codes[_terms.index(word)] + punctuation_mark
                output = append_string(output, temp_text)
            else:
                word = word + punctuation_mark
                output = append_string(output, word)
        else:
            if root != word:
                word = root + punctuation_mark
            else:
                word = word + punctuation_mark
            output = append_string(output, word)
    return output

def detect_link(word):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, word)
    if len(url) > 0:
        return True
    else:
        return False
    
def remove_duplicate_symbols(output):
    punctuation_marks = [',', '.', ';', "'", '"', '-', '_', '®']
    for mark in punctuation_marks:
        duplicated = mark + mark
        output = output.replace(duplicated, mark)
    return output

def random_number():
    i=0
    rand=""
    while i < 10:
        rand += str(random.randrange(1,10))
        i+=1
    return rand

def extract_parentheses(line):
    if ")" in line:
        pos = line.find(")")
        if pos == len(line.strip())-1:
            lines = line.split("(")
            return translate_text(lines[0]) + " (" + translate_text(lines[1])
        else:
            words = line.split("(")[0]
            _words = words.split(" ")
            if "" in _words:
                _words.remove("")
            if len(_words) != 0:
                word = _words[-1]
                translated_word = translate_text(word)
                translated_text = translate_text(line)
                if translated_text.count(translated_word) > 0:
                    parentheses = line.split("(")[1].split(")")[0]
                    translated_parent = translate_text(parentheses)
                    wordlist=[]
                    for w in translated_text.split(" "):
                        if w == translated_word:
                            wordlist.append(w)
                            # wordlist.append(translated_parent)
                        else:
                            wordlist.append(w)
                    return " ".join(wordlist)
                else:
                    return translate_text(line)
            else:
                return translate_text(line)
    else:
        return translate_text(line)

def terminology():
  # DB 구축 이전에 리스트에 담은 데이터
    terms = [["functional escalation", "펑셔널 에스컬레이션"], ["hierarchical escalation", "하이얼키칼 에스컬레이션"], ["single point of contact", "싱글 포인트 오브 컨택"],
             ["support hour", "서포트아워"], ["service desk", "서비스데스크"], ["support level", "서포트레벨"], ["incident management", "인시던트 메니지먼트"],
             ["major incident", "메이져 인시던트"], ["request fulfillment", "리케스트 풀필먼트"], ["request model", "리케스트 모델"], ["service request", "서비스 레벨"],
             ["problem management", "프로블럼 메니지먼트"], ["proactive problem management", "프로엑티브 프로블럼 메니지먼트"], ["change advistory board", "체인지 어드바이서리 보드"], 
             ["standard change", "스텐더드 체인지"], ["request for change", "리케스트 포 체인지"], ["configuration item", "컨피겨레이션 아이템"], 
             ["ci type", "CI 타입"], ["change management", "체인지 메니지먼트"], ["change model", "체인지 모델"], ["change schedule", "체인지 스케쥴"], 
             ["emergency change", "이머젠시 체인지"], ["emergency change advisory board", "이머젠시 체인지 어드바이서리 보드"], ["normal change", "노멀 체인지"], 
             ["configuration management data base", "컨피겨레이션 메니지먼트 데이터베이스"], ["asset management", "에셋 메니지먼트"], ["configuration record", "컨피겨레이션 레코드"], 
             ["service asset", "서비스 에셋"], ["configuration management", "컨피겨레이션 메니지먼트"], ["service level agreement", "서비스 레벨 어그리먼트"], 
             ["information technology infrastructure library", "Information Technology Infrastructure Library"], ["service level management", "서비스 레벨 메니지먼트"], 
             ["event management", "이벤트 메니지먼트"], ["proactive monitoring", "프로액티브 모니터링"], ["reactive monitoring", "리액티브 모니터링"], ["back out", "벡아웃"], 
             ["known error", "노운에러"], ["service provider", "서비스 프로바이더"], ['it service management', 'IT 서비스 메니지먼트'], ['cloud computing', '클라우드 컴퓨팅'],
             ['infrastructure as a service', 'infrastructure as a service'],
             ["acceptance criteria", "억셉탄스 크라이테리아"], ["architecture management practice", "아키텍쳐 메니지먼트 프락티스"], ["asset register", "에셋 레지스터"], ["availability management practice", "어베일라빌리티 메니지먼트 프락티스"], ["best practice", "베스트 프락티스"], 
             ["big data", "빅데이터"], 
             ["business analysis practice", "비즈니스 에널리시스 프락티스"], ["business case", "비즈니스 케이스"], ["business impact analysis", "비즈니스 임펙트 에널리시스"], ["contact center", "컨텍센터"], ["contact centre", "컨텍센터"], 
             ["capacity and performance management practice", "카파시티 엔 퍼포먼스 메니지먼트 프락티스"], 
             ["capacity planning", "카파시티 플레닝"], ["change authority", "체인지 오토리티"], ["change control practice", "체인지 컨트롤 프락티스"], 
             ["configuration management database", "컨피겨레이션 메니지먼트 데이터베이스"], ["configuration management system", "컨피겨레이션 메니지먼트 시스템"], 
             ["continual improvement practice", "컨티뉴얼 임프루먼트 프락티스"], 
             ["continuous deployment", "컨티뉴어스 디플로이먼트"], ["continuous integration", "컨티뉴어스 인티그레이션"], ["continuous delivery", "컨티뉴어스 딜리버리"], ["cost centre", "코스트 센터"], ["critical success factor", "크리티컬 석세스 팩터"], ["customer experience", "고객경험"],
             ["deliver and support", "딜리버 엔 서포트"], ["deployment management practice", "디플로이먼트 메니지먼트 프락티스"], ["design and transition", "디자인과 트렌시션"], ["design thinking", "디자인 싱킹"], ["development environment", "개발환경"], 
             ["digital transformation", "디지털 트렌스포메이션"], ["disaster recovery plan", "디사스터 리커버리 플렌"], ["error control", "에러 컨트롤"], ["information and technology", "인포메이션 테크놀로지"], ["information security management practice", "이포메이션 시큐리티 메니지먼트 프락티스"], 
             ["information security policy", "인포메이션 시큐리티 폴리시"], ["infrastructure and platform management practice", "인프라 및 플렛폼 메니지먼트 프락티스"], ["feedback loop", "피드백 루프"], 
             ["internet of things", "IoT"], ["it asset", "IT 에셋"], ["it asset management practice", "IT 에셋 메니지먼트 프락티스"], ["it infrastructure", "IT 인프라"], ["it service", "IT 서비스"], ["ITIL guiding principle", "ITIL 가이딩 프린시플"],
             ["itil service value chain", "ITIL 서비스 발류체인"], ["key performance indicator", "키 퍼포먼스 인디케이터"], ["knowledge management practice", "놀레지 메니지먼트 프락티스"], ["live environment", "라이브 환경"], ["management system", "메니지먼트 시스템"], 
             ["mean time between failure", "민 타임 비트윈 페일류어"], ["mean time to restore service", "민 타임 투 리스토어 서비스"], ["measurement and reporting", "메셔멘트와 리포팅"], ["minimum viable product", "미니멈 비아블 프로덕트"], 
             ["operational technology", "오퍼레이셔널 테크놀로지"], ["organizational velocity", "기업 벨로시티"], ["portfolio management practice", "포트폴리오 메니지먼트 프락티스"],
             ["post-implementation review", "포스트 임플레멘테이션 리뷰"], ["problem management practice", "프러블럼 메니지먼트 프락티스"], ["production environment", "프로덕션 환경"], ["project management practice", "프로젝트 메니지먼트 프락티스"], ["quick win", "퀵윈"], 
             ["recovery point objective", "리커버리 포인트 오브젝티브"], ["recovery time objective", "리커버리 타임 오브젝티브"], ["relationship management practice", "리레이션십 메니지먼트 프락티스"], ["release management practice", "릴리즈 메니지먼트 프락티스"], 
             ["request catalogue", "리케스트 카탈로그"], ["request catalog", "리케스트 카탈로그"], ["risk assessment", "리스크 어세스멘트"],
             ["risk management practice", "리스크 메니지먼트 프락티스"], ["service action", "서비스 액션"], ["service architecture", "서비스 아키텍쳐"], ["service catalogue", "서비스 카탈로그"], ["service catalog", "서비스 카탈로그"], 
             ["service catalog management practice", "서비스 카탈로그 메니지먼트 프락티스"], ["service catalog management practice", "서비스 카탈로그 메니지먼트 프락티스"], ["service configuration management practice", "서비스 컨피겨레이션 메니지먼트 프락티스"], 
             ["service consumption", "서비스 컨섬션"], ["service continuity management practice", "서비스 컨티뉴이티 메니지먼트 프락티스"], ["service design practice", "서비스디자인 프락티스"], ["service desk practice", "서비스데스크 프락티스"],
             ["service financial management practice", "서비스 파이낸셜 메니지먼트 프락티스"], ["service level management practice", "서비스 레벨 메니지먼트 프락티스"], ["service management", "서비스 메니지먼트"], ["service offering", "서비스 오퍼링"], 
             ["service owner", "서비스오너"], ["service portfolio", "서비스 포트폴리오"], ["service provider", "서비스 프로바이더"], ["service provision", "서비스 프로비션"], 
             ["service relationship", "서비스 리레이션십"], 
             ["service relationship management", "서비스 리레이션십 메니지먼트"], ["service request", "서비스 리케스트"], ["service request management practice", "서비스 리케스트 메니지먼트 프락티스"],
             ["service validation and testing practice", "서비스 발리데이션 및 테스팅 프락티스"], ["service value system", "서비스 발류 시스템"], ["software development and management practice", "소프트웨어 디플로이멘트와 메니지먼트 프락티스"], 
             ["strategy management practice", "전략 메니지먼트 프락티스"], ["supplier management practice", "서플라이어 메니지먼트 프락티스"], ["support team", "서포트 팀"],
             ["systems thinking", "시스템 싱킹"], ["technical debt", "기술부채"], ["test environment", "테스트 환경"], ["use case", "유스 케이스"], ["utility requirement", "유틸리티 리콰이어멘트"], 
             ["value stream", "발류스트림"], ["value streams and processes", "발류스트림 및 프로세스"], ["warranty requirements", "워런티 리콰이어멘트"], ["waterfall method", "워터폴 메소드"], 
             ["workforce and talent management practice", "워크포스와 텔런트 메니지먼트 프락티스"]]
    terminology = pd.DataFrame(terms, columns=['term', 'term_kor'])
    terms = [["activity", "액티비티"], ["client", "클라이언트"], ["function", "펑션"], ["impact", "임팩트"], ["priority", "프라이오리티"], ["process", "프로세스"], 
             ["resolution", "레솔루션"], ["role", "롤"], ["service", "서비스"], ["urgency", "어젠시"], ["user", "유저"], ["escalation", "에스컬레이션"], ["incident", "인시던트"],
             ["problem", "프러블럼"], ["workaround", "워크어라운드"], ["back-out", "백아웃"], ["backout", "백아웃"], ["change", "체인지"], ["attribute", "어트리뷰트"], ["alert", "알러트"], 
             ["event", "이벤트"], ["monitoring", "모니터링"], ["lifecycle", "라이프사이클"], ["agile", "어자일"], ["availability", "어베일러빌리티"], ["baseline", "베이스라인"], ["call", "콜"], ["capability", "카파빌리티"], ["charging", "차징"], 
             ["compliance", "컴플라이언스"], ["confidentiality", ""], ["configuration", "컨피겨레이션"], ["control", "컨트롤"], ["governance", "거버넌스"], ["identity", "아이덴티티"], 
             ["deployment", "디플로이"], ["devops", "뎁옵스"], ["kanban", "칸반"], ["outsourcing", "아웃소싱"], ["partnership", "파트너십"], ["performance", "퍼포먼스"], 
             ["pilot", "파일럿"], ["policy", "폴리시"], ["procedure", "프로시져"], ["project", "프로젝트"], ["record", "레코드"], ["recovery", "리커버리"],
             ["release", "릴리즈"], ["resource", "리소스"], ["retire", "리타이어"], ["risk", "리스크"], ["sourcing", "소싱"], ["specification", "스펙"],
             ["sponsor", "스폰서"], ["status", "스타투스"], ["user", "유저"], ["utility", "유틸리티"], ["warranty", "워런티"]]
    short_terms = pd.DataFrame(terms, columns=['term', 'term_kor'])
    specialSymbols = [["IT", "IT", "아이티"], ["itil", "ITIL", "아이틸"], ["sr", "SR", "에스알"], ["sla", "SLA", "에스엘레이"], ["cab", "CAB", "씨에이비"], ["ecab", "ECAB", "이씨에이비"], 
                      ["rfc", "RFC", "알에프씨"], ["ci", "CI", "씨아이"], ["cmdb", "CMDB", "씨엠디비"], ["itsm", "ITSM", "아이티에스엠"], ['iaas', 'IaaS', '아이에이에스'],
                      ["bia", "BIA", "비아이에이"], ["brm", "BRM", "비알엠"], ["cms", "CMS", "시엠에스"], ["csf", "CSF", '시에스에프'], ["cx", "CX", '시엑스'], ["kpi", "KPI", '케이피아이'], 
                      ["mtbf", "MTBF", '엠티비에프'], ["mtrs", "MTRS", '엠티알에스'], ["mvp", "MVP", '엠브이피'], ["pir", "PIR", '파아이알'], ["rpo", "RPO", '알피오'], ["rto", "RTO", '알티오'], 
                      ["svs", "SVS", '에스브이에스']]
    special_symbols = pd.DataFrame(specialSymbols, columns=['term', 'term_kor', 'kor_pronunciation'])
    return [terminology, short_terms, special_symbols]

def pluralize_terminology(terms):
    long_term = terms[0]
    short_term = terms[1]
    special_symbols = terms[2]
    plural_form = pluralize_long_terms(long_term)
    for idx, ele in enumerate(plural_form):
        long_term.loc[len(long_term), 'term'] = ele
        long_term.loc[len(long_term)-1, 'term_kor'] = long_term.loc[idx, 'term_kor']
    long_term['code'] = np.nan
    for i, x in long_term.iterrows():
        long_term.loc[i, 'code'] = random_number()
    for i, x in long_term.iterrows():
        long_term.loc[i, 'code'] = random_number()
    short_term['code'] = np.nan
    for i, x in short_term.iterrows():
        short_term.loc[i, 'code'] = random_number()
    special_symbols['code'] = np.nan
    for i, x in special_symbols.iterrows():
        special_symbols.loc[i, 'code'] = random_number()
    return [long_term, short_term, special_symbols]

def add_conjugation(line, long_term, short_term, special_symbols):
    long_terms, short_terms, acronyms = [], [], []
    korean_vowels = ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ', 'ㅐ', 'ㅔ', 'ㅒ', 'ㅖ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅞ', 'ㅝ', 'ㅟ', 'ㅢ']
    korean_conjugations = ['하는', '하기', '하다', '할', '하며', '하고']
    korean_conjugations_002 = ['되어야하며', '되어야하고', '되어야하는데', '되어야하지만', '되어야하되', '돼야하며', '돼야하고', '돼야하는데', '돼야하지만', '돼야하되', '됩니다', '된다', 
                               '되게', '될']
    for i, x in long_term.iterrows():
        long_terms.append(x['term_kor'])
    for i, x in short_term.iterrows():
        short_terms.append(x['term_kor'])
    for i, x in special_symbols.iterrows():
        acronyms.append(x['term_kor'])
    for term in long_terms:
        if len(term.split(" ")) > 1:
            _term = term.replace(" ", "_&&_")
            line = line.replace(term, _term)
    for word in line.split(" "):
        for term in long_terms:
            if len(term.split(" ")) > 1:
                term = term.replace(" ", "_&&_")
            if word == term:
                if len(term.split(" ")) == len(line.split(" ")):
                    break
                pos = line.split(" ").index(term)
                last_word = line.split(" ")[pos]
                if "를" in last_word:
                    continue
                elif "을" in last_word:
                    continue
                elif "가" in last_word:
                    continue
                elif "이" in last_word:
                    continue
                elif pos+1 == len(line.split(" ")):
                    continue
                next_word = line.split(" ")[pos+1]
                for kor_conjugation in korean_conjugations:
                    if kor_conjugation in next_word:
                        jamos = split_syllables(term)
                        if jamos[len(jamos)-1] in korean_vowels:
                            line_1 = line.split(" ")[:pos+1]
                            line_2 = line.split(" ")[pos+1:]
                            line = " ".join(line_1) + "를 " + " ".join(line_2)
                        else:
                            line_1 = line.split(" ")[:pos+1]
                            line_2 = line.split(" ")[pos+1:]
                            line = " ".join(line_1) + "을 " + " ".join(line_2)
                for kor_conjugation in korean_conjugations_002:
                    if kor_conjugation in next_word:
                        jamos = split_syllables(term)
                        if jamos[len(jamos)-1] in korean_vowels:
                            line_1 = line.split(" ")[:pos+1]
                            line_2 = line.split(" ")[pos+1:]
                            line = " ".join(line_1) + "가 " + " ".join(line_2)
                        else:
                            line_1 = line.split(" ")[:pos+1]
                            line_2 = line.split(" ")[pos+1:]
                            line = " ".join(line_1) + "이 " + " ".join(line_2)
        for term in acronyms:
            if len(term.split(" ")) == len(line.split(" ")):
                    break
            if word == term:
                pos = line.split(" ").index(term)
                last_word = line.split(" ")[pos]
                if "를" in last_word:
                    continue
                elif "을" in last_word:
                    continue
                elif "가" in last_word:
                    continue
                elif "이" in last_word:
                    continue
                elif pos+1 == len(line.split(" ")):
                    continue
                else:
                    next_word = line.split(" ")[pos+1]
                    for kor_conjugation in korean_conjugations:
                        if kor_conjugation in next_word:
                            kor_pronunciation = special_symbols[special_symbols['term_kor']==term]['kor_pronunciation']
                            jamos = split_syllables(kor_pronunciation)
                            if jamos[len(jamos)-1] in korean_vowels:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "를 " + " ".join(line_2)
                            else:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "을 " + " ".join(line_2)
                    for kor_conjugation in korean_conjugations_002:
                        if kor_conjugation in next_word:
                            jamos = split_syllables(term)
                            if jamos[len(jamos)-1] in korean_vowels:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "가 " + " ".join(line_2)
                            else:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "이 " + " ".join(line_2)
        for term in short_terms:
            if word == term:
                pos = line.split(" ").index(term)
                last_word = line.split(" ")[pos]
                if "를" in last_word:
                    continue
                elif "을" in last_word:
                    continue
                elif "가" in last_word:
                    continue
                elif "이" in last_word:
                    continue
                elif pos+1 == len(line.split(" ")):
                    continue
                else:
                    next_word = line.split(" ")[pos+1]
                    for kor_conjugation in korean_conjugations:
                        if kor_conjugation in next_word:
                            jamos = split_syllables(last_word)
                            if jamos[len(jamos)-1] in korean_vowels:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "를 " + " ".join(line_2)
                            else:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "을 " + " ".join(line_2)
                    for kor_conjugation in korean_conjugations_002:
                        if kor_conjugation in next_word:
                            jamos = split_syllables(term)
                            if jamos[len(jamos)-1] in korean_vowels:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "가 " + " ".join(line_2)
                            else:
                                line_1 = line.split(" ")[:pos+1]
                                line_2 = line.split(" ")[pos+1:]
                                line = " ".join(line_1) + "이 " + " ".join(line_2)
    line = line.replace("_&&_", " ")
    return line

def korean_grammar(input):
    output = input.replace("수", " 수 ")
    return output.replace("  ", " ")

def edit_with_style(ln, style):
    output=""
    korean_vowels = ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ', 'ㅐ', 'ㅔ', 'ㅒ', 'ㅖ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅞ', 'ㅝ', 'ㅟ', 'ㅢ']
    if style == "style_001":
        for line in ln.split(". "):
            last_word = line.split(" ")[-1]
            if "." in last_word:
                last_word = last_word.replace(".", "")
            if "니다" in last_word:
                line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                output += line
            elif len(last_word) > 0 and last_word[len(last_word)-1:] == '요':
                if len(last_word) >=3 and last_word[len(last_word)-3:] == "이에요":
                    last_word = last_word[:len(last_word)-3] + "입니다"
                elif len(last_word) >= 2 and last_word[len(last_word)-2:] == "어요":
                    if last_word[len(last_word)-3:len(last_word)-2] == "되":
                        last_word = last_word[:len(last_word)-2] + "었습니다"
                    else:
                        last_word = last_word[:len(last_word)-2] + "습니다"
                elif len(last_word) >= 1 and last_word[len(last_word)-1:] == "요":
                    if last_word[len(last_word)-2:len(last_word)-1] == "돼":
                        last_word = last_word[:len(last_word)-2] + "됩니다"
                    elif last_word[len(last_word)-2:len(last_word)-1] == "해":
                        last_word = last_word[:len(last_word)-2] + "합니다"
                    elif split_syllables(last_word[:len(last_word)-1])[-1] == "ㅕ":
                        jamos = split_syllables(last_word[:len(last_word)-1])
                        jamos = jamos[:len(jamos)-1] + "ㅣㅂ"
                        last_word = join_jamos(jamos) + "니다"
                line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                output += line
            else:
                jamos = split_syllables(last_word)
                if jamos[len(jamos)-1:] == "ㅁ":
                    if last_word[-1] == "음":
                        last_word = last_word[:len(last_word)-1] + "습니다"
                    else:
                        jamos = split_syllables(last_word)
                        jamos = jamos[:len(jamos)-1] + "ㅂ"
                        last_word = join_jamos(jamos) + "니다"
                    line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                    output += line
    elif style == "style_002":
        for line in ln.split(". "):
            last_word = line.split(" ")[-1]
            if "." in last_word:
                last_word = last_word.replace(".", "")
            if "니다" in last_word:
                last_word = last_word.replace("니다", "")
                jamos = split_syllables(last_word)
                if jamos[-1] == "ㅂ":
                    jamos = jamos[:len(jamos)-1] + "ㅁ"
                    last_word = join_jamos(jamos)
                    second_to_last = last_word[len(last_word)-2:len(last_word)-1]
                    jamos = split_syllables(second_to_last)
                    if jamos[-1] == "ㅆ":
                        last_word = last_word[:len(last_word)-1] + "음"
                line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                output += line
            elif len(last_word) > 0 and last_word[len(last_word)-1:] == '요':
                if len(last_word) >= 3 and last_word[len(last_word)-3:] == "었어요":
                    last_word = last_word[:len(last_word)-3]
                    jamos = split_syllables(last_word) + "ㅁ"
                    last_word = join_jamos(jamos)
                elif len(last_word) >=2 and last_word[len(last_word)-2:] == "어요":
                    last_word = last_word[:len(last_word)-2]
                    jamos = split_syllables(last_word)
                    if jamos[-1] in korean_vowels:
                        jamos = jamos + "ㅁ"
                    else:
                        jamos = jamos[:len(jamos)-1] + "ㅁ"
                    last_word = join_jamos(jamos)
                elif len(last_word) >= 2 and last_word[len(last_word)-2:] == "에요":
                    jamos = split_syllables(last_word[:len(last_word)-2]) + "ㅁ"
                    last_word = join_jamos(jamos)
                else:
                    last_word = last_word[:len(last_word)-1]
                    if last_word[-1] == "돼":
                        jamos = split_syllables(last_word)
                        jamos = jamos[:len(jamos)-1] + "ㅚㅁ"
                        last_word = join_jamos(jamos)
                    elif last_word[-1] == "해":
                        jamos = split_syllables(last_word)
                        jamos = jamos[:len(jamos)-1] + "ㅏㅁ"
                        last_word = join_jamos(jamos)
                        pass
                    else:
                        jamos = split_syllables(last_word)
                        if jamos[-1] == 'ㅕ':
                            jamos = jamos[:len(jamos)-1] + "ㅣㅁ"
                            last_word = join_jamos(jamos)
                line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                output += line
            else:
                jamos = split_syllables(last_word)
                if jamos[len(jamos)-1:] == "ㅁ":
                    line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                    output += line
    elif style == "style_003":
        for line in ln.split(". "):
            last_word = line.split(" ")[-1]
            if "." in last_word:
                last_word = last_word.replace(".", "")
            if "니다" in last_word:
                last_word = last_word.replace("니다", "")
                jamos = split_syllables(last_word)
                if jamos[-1] == "ㅂ":
                    jamos = jamos[:len(jamos)-1]
                    if jamos[-1] == "ㅣ":
                        if jamos[-2] == "ㅇ":
                            last_word = join_jamos(jamos) + "에요"
                        else:
                            jamos = jamos[:len(jamos)-1] + "ㅕ"
                            last_word = join_jamos(jamos) + "요"
                    elif jamos[-2] == "ㅎ":
                        jamos = jamos[:len(jamos)-1] + "ㅐ"
                        last_word = join_jamos(jamos) + "요"
                    elif jamos[-1] == "ㅙ":
                        last_word = join_jamos(jamos) + "요"
                    elif last_word[-1] == "습":
                        last_word = last_word[:len(last_word)-1] + "어요"
                    else:
                        last_word = join_jamos(jamos) + "어요"
                line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                output += line
            elif len(last_word) > 0 and last_word[len(last_word)-1:] == '요':
                line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                output += line
            else:
                jamos = split_syllables(last_word)
                if jamos[len(jamos)-1:] == "ㅁ":
                    if last_word[-1] == "음":
                        last_word = last_word[:len(last_word)-1] + "어요"
                    elif last_word[-1] == '함':
                        last_word = last_word[:len(last_word)-1] + '해요'
                    elif last_word[-1] == "임":
                        last_word = last_word[:len(last_word)-1] + "이에요"
                    elif last_word[-1] == "돼":
                        last_word = last_word[:len(last_word)-1] + "요"
                    else:
                        last_word = join_jamos(jamos[:len(jamos)-1]) + "어요"
                    line = " ".join(line.split(" ")[:len(line.split(" "))-1]) + " " + last_word + ". "
                    output += line
    return output

def format_sentences(input):
    output=""
    for word in input.split(" "):
        if "." in word:
            if detect_link(word) == False:
                output += " " + word.split(".")[0] + ". " + word.split(".")[1]
            else:
                output += " " + word
        else:
            output += " " + word
    return output

def dictionaries():
    dictionary = ["ITIL"]
    return dictionary

def translate(text, grammar_style, selected_dictionary):
    terms = terminology()
    terms = pluralize_terminology(terms)
    long_term = terms[0]
    short_term = terms[1]
    special_symbols = terms[2]
    lines=""
    for ln in text.split("\n"):
        output = detect_long_words(ln.lower(), long_term)
        lines += "\n" + output
    output=""
    for ln in lines.strip().split("\n"):
        output += "\n" + detect_word(ln, short_term)
    output = remove_duplicate_symbols(output)
    lines=""
    for ln in output.strip().split("\n"):
        lines += "\n" + detect_acronyms(ln, special_symbols)
    output=""
    for ln in lines.strip().split("\n"):
        if ln.strip() != "":
            output += "\n" + extract_parentheses(ln)
    lines=""
    for ln in output.strip().split("\n"):
        lines += "\n" + filter_text(ln, long_term, short_term, special_symbols)
    output=""
    for ln in lines.strip().split("\n"):
        output += "\n" + add_conjugation(ln, long_term, short_term, special_symbols)
    output = korean_grammar(output)
    lines=""
    for ln in output.strip().split("\n"):
        lines += "\n" + format_sentences(ln)
    output=""
    for ln in lines.strip().split("\n"):
        output += "\n" + edit_with_style(ln, grammar_style) # 문법없는경우
    return output
