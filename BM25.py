import json
import argparse
from IndexEngine import TokenizeStrings
from math import log
import os
from objects import RetrievalTestingOutput, RetrievalOutput
from PorterStemmer import PorterStemmer

def bm_25(k1=1.2, b=0.75, top_retrieved = 1000, use_stemming=False, testing = True, **kwargs):
    if testing and (not os.path.exists(kwargs["directory_path"]) or not os.path.exists(kwargs["queries_path"])):
        raise ValueError("Please provide a valid path to the contents being retrieved")
    
    ps = PorterStemmer() if use_stemming else None
    queries = read_json(kwargs["queries_path"]) if testing else kwargs["queries"]
    lexicon = read_json(os.path.join(kwargs["directory_path"], "lexicon.json")) if testing else kwargs["lexicon"]
    inverted_index = read_json(os.path.join(kwargs["directory_path"], "inverted-index.json")) if testing else kwargs["inverted_index"]
    mapping_to_docno = read_json("mapping.json")["doc_nos"] if testing else kwargs["mapping_to_docno"]
    doc_lengths = read_doc_lengths(os.path.join(kwargs["directory_path"], "doc-lengths.txt")) if testing else kwargs["doc_lengths"]
    N = len(doc_lengths)
    avdl = sum(doc_lengths.values()) / N
    
    list_output = []

    if testing:
        for topic_number, query_text in queries.items():
            tokens = []
            TokenizeStrings(query_text.split(" "), tokens)
            if ps:
                tokens[:] = [ps.stem(token, 0, len(token) - 1) for token in tokens]
            
            scores = {}
            for token in tokens:
                if token not in lexicon:
                    continue
                token_id = lexicon[token]
                postings = inverted_index[str(token_id)]
                ni = len(postings) // 2  

                for i in range(0, len(postings), 2):
                    doc_id = postings[i]
                    fi = postings[i + 1] 
                    dl = doc_lengths[str(doc_id)]
                    score = bm_25_score(fi, N, ni, dl, avdl, k1, b)
                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += score

            ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_retrieved] 
            for rank, (doc_id, score) in enumerate(ranked_docs):
                list_output.append(RetrievalTestingOutput(topic_number, mapping_to_docno[doc_id], rank + 1, score))

        write_to_txt(list_output, kwargs["file_output"])
    else:
        tokens = []
        TokenizeStrings(queries.split(" "), tokens)
        if ps:
            tokens[:] = [ps.stem(token, 0, len(token) - 1) for token in tokens]
        
        scores = {}
        for token in tokens:
            if token not in lexicon:
                continue
            token_id = lexicon[token]
            postings = inverted_index[str(token_id)]
            ni = len(postings) // 2  

            for i in range(0, len(postings), 2):
                doc_id = postings[i]
                fi = postings[i + 1] 
                dl = doc_lengths[str(doc_id)]
                score = bm_25_score(fi, N, ni, dl, avdl, k1, b)
                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += score

        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_retrieved] 
        for rank, (doc_id, score) in enumerate(ranked_docs):
            meta_data = read_json(os.path.join("IndexEngine","MetaData",mapping_to_docno[doc_id]+".json"))
            list_output.append(RetrievalOutput(rank+1, meta_data["headline"], meta_data["date"], mapping_to_docno[doc_id]))
        return list_output



def read_doc_lengths(file_path):
    doc_lengths = {}
    with open(file_path, 'r') as file:
        for idx, line in enumerate(file, start=1):
            doc_lengths[str(idx-1)] = int(line.strip()) 
    return doc_lengths


def bm_25_score(fi, N, ni, dl, avdl, k1, b):
    K = k1 * ((1 - b) + b * (dl / avdl))
    frequency_saturation = fi / (fi + K)
    idf = log((N - ni + 0.5) / (ni + 0.5))
    return idf * frequency_saturation


def write_to_txt(list_output, file_output):
    if ".txt" not in file_output:
        file_output += ".txt"
    with open(file_output, 'w') as f:
        for output in list_output:
            line = f"{output.topicID} {output.Q} {output.docno} {output.rank} {output.score} {output.runTag}\n"
            f.write(line)


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Perform BM25 retrieval on an inverted index.'
    )

    parser.add_argument('directory_path', type=str,
                        help='Path to the directory containing the index files.')
    parser.add_argument('queries_path', type=str,
                        help='Path to the queries JSON file.')
    parser.add_argument('file_output', type=str,
                        help='Path to the output file where results will be stored.')
    parser.add_argument('--use_stemming', action='store_true',
                        help='If set, the query will be stemmed using Porter Stemmer.')

    args = parser.parse_args()

    if not args.directory_path or not args.queries_path or not args.file_output:
        raise ValueError(
            "Please input the path to the directory that has the output from the IndexEngine\n" 
            "as well as the path for the file where the queries are stored\n"
            "and the path for the output file.\n"
            "Would look something like this:\n"
            "python bm25.py /home/smucker/latimes-index queries.txt hw2-results-WatIAMUserID.txt" 
        )

    bm_25(directory_path = args.directory_path, queries_path = args.queries_path, file_output = args.file_output, k1=1.2, b=0.75, use_stemming=args.use_stemming)


