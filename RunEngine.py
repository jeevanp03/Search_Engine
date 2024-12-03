from BM25 import read_doc_lengths, read_json, bm_25
from IndexEngine import unzip_file_and_read, TokenizeStrings
from GetDoc import return_data, retrieve_data
import os
from math import sqrt, log
import time
import argparse
import textwrap

def create_and_load_data_structures():
    if not os.path.exists("IndexEngine"):
        unzip_file_and_read("latimes.gz", "IndexEngine")
    inverted_index = read_json("IndexEngine/inverted-index.json")
    lexicon = read_json("IndexEngine/lexicon.json")
    mapping_to_docno = read_json("mapping.json")["doc_nos"]
    doc_lengths = read_doc_lengths("IndexEngine/doc-lengths.txt")
    return inverted_index, lexicon, mapping_to_docno, doc_lengths

def compute_tfidf_vector(tokens, sentence_tokens_list, num_sentences):
    vector = {}
    for token in tokens:
        ni = sum(1 for sentence_tokens in sentence_tokens_list if token in sentence_tokens)
        if ni > 0:
            tf = tokens.count(token)  
            idf = log((num_sentences + 1) / (1 + ni))  
            vector[token] = tf * idf
    return vector

def cosine_similarity(vec1, vec2):
    dot_product = sum(vec1[token] * vec2.get(token, 0) for token in vec1)
    magnitude1 = sqrt(sum(weight ** 2 for weight in vec1.values()))
    magnitude2 = sqrt(sum(weight ** 2 for weight in vec2.values()))
    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0

def find_and_add_snippets(list_output, query, k=3):
    for output in list_output:
        doc_id = output.docno

        doc_content = return_data(doc_id, "IndexEngine")
        
        sentences = doc_content.split(".")
        num_sentences = len(sentences)
        
        sentence_tokens_list = []
        for sentence in sentences:
            tokens = []
            TokenizeStrings(sentence.split(" "), tokens)
            sentence_tokens_list.append(tokens)
        
        query_tokens = []
        TokenizeStrings(query.split(" "), query_tokens)

        query_vector = compute_tfidf_vector(query_tokens, sentence_tokens_list, num_sentences)
        
        sentence_similarities = []

        for sentence, sentence_tokens in zip(sentences, sentence_tokens_list):

            sentence_vector = compute_tfidf_vector(sentence_tokens, sentence_tokens_list, num_sentences)
            
            similarity = cosine_similarity(query_vector, sentence_vector)

            sentence_similarities.append((sentence.strip(), similarity))
        
        top_k_sentences = sorted(sentence_similarities, key=lambda x: x[1], reverse=True)[:k]
        
        best_snippet = " ".join([sentence for sentence, _ in top_k_sentences])
        best_snippet = best_snippet.replace("\n", "")
        if not best_snippet.endswith(".") or not best_snippet.endswith("!") or not best_snippet.endswith("?"):
            best_snippet += "."
        if not output.headline:
            output.headline = best_snippet[:50] + "..."
        formatted_snippet = textwrap.fill(best_snippet, width=80)
        output.add_snippet(formatted_snippet)


def query_flow(inverted_index, lexicon, mapping_to_docno, doc_lengths):
    query = input("\033[94mEnter a query: \033[0m")
    start_time = time.time()
    list_output = bm_25(inverted_index=inverted_index, lexicon=lexicon, mapping_to_docno=mapping_to_docno, doc_lengths=doc_lengths, queries=query, top_retrieved=10, testing=False)
    end_time = time.time()
    find_and_add_snippets(list_output, query)
    print("Results:\n")
    if len(list_output) == 0:
        print(f"\033[91mNo documents found for the query: {query} \033[0m\n")
    for output in list_output:
        print(f"{output.rank}. {output.headline} ({output.date})")
        print(f"{output.query_biased_snippet} ({output.docno})\n")
    
    print(f"\033[92mTime taken: {end_time - start_time:.2f} seconds\033[0m\n")

    return list_output

def interactive_experience():
    print("Welcome to the search engine!")
    print("Loading Data Structures...")
    inverted_index, lexicon, mapping_to_docno, doc_lengths = create_and_load_data_structures()
    print("Data Structures loaded successfully!")
    list_output = query_flow(inverted_index, lexicon, mapping_to_docno, doc_lengths)
    user_input = input('\033[94mEnter rank to retrieve the document of that retrieved rank, "N" for new query, or "Q" to quit: \033[0m').upper()
    while user_input != "Q":
        if user_input.isdigit():
            rank = int(user_input)
            if 1 <= rank <= 10:
                retrieve_data(list_output[rank-1].docno, "IndexEngine")
            else:
                print("\033[91mInvalid rank, please try again.\033[0m")
        elif user_input == "N":
            list_output = query_flow(inverted_index, lexicon, mapping_to_docno, doc_lengths)
        else:
            print("\033[91mInvalid input, please try again.\033[0m")
        user_input = input('\033[94mEnter rank to retrieve the document of that retrieved rank, "N" for new query, or "Q" to quit: \033[0m').upper()
    
    print("Thank you for using the search engine, goodbye!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive Search Engine")
    
    parser.parse_args()

    interactive_experience()