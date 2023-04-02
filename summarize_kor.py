import re
import nltk
import heapq

def clean_text(paragraph):
    total_cleaned_content = re.sub(r'\[[0-9]*\]', ' ', paragraph)
    total_cleaned_content = re.sub(r'\s+', ' ', total_cleaned_content)
    sentence_tokens = nltk.sent_tokenize(total_cleaned_content)
    total_cleaned_content = re.sub(r'\s+', ' ', total_cleaned_content)
    return total_cleaned_content, sentence_tokens

def get_total_lines(paragraph):
    lines = len(paragraph.split(". ")) + 1
    if lines < 5:
        return 1
    else:
        return round(lines / 5)

def get_stopwords_ko():
    # 영문 요약에 사용된 nltk 라이브러리에는 한문 리소스가 없기에 수작업으로 모은 단어집
    stopwords_ko = "stopwords-ko.txt"
    stopwords_ko = open(stopwords_ko, 'r', encoding="utf-8")
    stopwords=[]
    for word in stopwords_ko:
        if word != "":
            stopwords.append(word.strip())
    return stopwords

def summarize_kor(text):
    stopwords = get_stopwords_ko()
    final_summary=""
    for paragraph in text.strip().split("\n"):
        if paragraph == "":
            continue
        total_lines = get_total_lines(paragraph)
        cleaned_text = clean_text(paragraph)
        cleaned_paragraph = cleaned_text[0]
        sentence_tokens = cleaned_text[1]
        words_tokens = nltk.word_tokenize(cleaned_paragraph)
        word_frequencies = {}
        for word in words_tokens:
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
        maximum_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
        sentence_scores = {}
        for sentence in sentence_tokens:
            for word in nltk.word_tokenize(sentence.lower()):
                if word in word_frequencies.keys():
                    if (len(sentence.split(' '))) < 30:  
                        if sentence not in sentence_scores.keys():
                            sentence_scores[sentence] = word_frequencies[word]
                        else:
                            sentence_scores[sentence] += word_frequencies[word]
        summary = heapq.nlargest(total_lines, sentence_scores, key=sentence_scores.get)
        s = ""                      
        for i in summary:
            s += i
        final_summary += "\n\n" + s
    return final_summary
