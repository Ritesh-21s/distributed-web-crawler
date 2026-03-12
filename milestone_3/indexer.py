import os
import json
import math
import re
from bs4 import BeautifulSoup
from collections import defaultdict, Counter

PAGES_FOLDER = "pages"
INVERTED_INDEX_FILE = "inverted_index.json"
IDF_FILE = "idf.json"

def extract_visible_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    return text


def tokenize_and_clean(text):

    text = text.lower()
 
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    tokens = text.split()

    return tokens


def main():
    inverted_index = defaultdict(list)
    document_frequency = defaultdict(int)
    total_documents = 0

    if not os.path.exists(PAGES_FOLDER):
        print("Pages folder not found!")
        return

    files = sorted(os.listdir(PAGES_FOLDER))

    for filename in files:
        if not filename.endswith(".html"):
            continue

        doc_id = filename
        filepath = os.path.join(PAGES_FOLDER, filename)

        total_documents += 1

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

        text = extract_visible_text(html_content)

        tokens = tokenize_and_clean(text)

        term_freq = Counter(tokens)

        for word, freq in term_freq.items():
            inverted_index[word].append((doc_id, freq))

    for word in inverted_index:
        document_frequency[word] = len(inverted_index[word])

    idf = {}
    for word, df in document_frequency.items():
        idf[word] = math.log(total_documents / df)


    inverted_index = dict(inverted_index)

    with open(INVERTED_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(inverted_index, f, indent=2)

    with open(IDF_FILE, "w", encoding="utf-8") as f:
        json.dump(idf, f, indent=2)


    print("\nIndexing Complete!\n")
    print("Total Documents Indexed:", total_documents)
    print("Total Unique Terms:", len(inverted_index))

    print("\nSample Inverted Index Entries:")
    for i, (word, postings) in enumerate(inverted_index.items()):
        print(word, "->", postings[:3])
        if i == 4:
            break

    print("\nSample IDF Values:")
    for i, (word, value) in enumerate(idf.items()):
        print(word, "->", round(value, 4))
        if i == 4:
            break


if __name__ == "__main__":
    main()