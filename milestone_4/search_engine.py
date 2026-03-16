import json
import string

class SearchEngine:

    def __init__(self, index_file="inverted_index.json", idf_file="idf_values.json"):
        
        with open(index_file, "r") as f:
            self.inverted_index = json.load(f)

        with open(idf_file, "r") as f:
            self.idf = json.load(f)


    # Query Processing
    def tokenize_query(self, query):

        query = query.lower()

        query = query.translate(str.maketrans('', '', string.punctuation))

        tokens = query.split()

        return tokens


    # Search Logic
    def search(self, query, top_n=10):

        tokens = self.tokenize_query(query)

        scores = {}

        for word in tokens:

            if word in self.inverted_index:

                postings = self.inverted_index[word]

                for doc_id, tf in postings:

                    score = tf * self.idf.get(word, 0)

                    if doc_id not in scores:
                        scores[doc_id] = 0

                    scores[doc_id] += score


        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []

        for doc, score in ranked_docs[:top_n]:

            results.append({
                "document": doc,
                "score": round(score, 4)
            })

        return results