import json
import argparse
from IndexEngine import TokenizeStrings
import os
from objects import RetrievalTestingOutput

def boolean_and(directory_path, queries_path, file_output):
    if not os.path.exists(directory_path) or not os.path.exists(queries_path):
        raise ValueError("please provide a valid path to the contents being retrieved")
    
    queries = read_json(queries_path)
    lexicon = read_json(os.path.join(directory_path, "lexicon.json"))
    inverted_index = read_json(os.path.join(directory_path, "inverted-index.json"))
    mapping_to_docno =read_json("mapping.json")["doc_nos"]
    list_output = []
    
    for topic_number, query_text in queries.items():
        tokens = []
        TokenizeStrings(query_text.split(" "), tokens)
        postings_list = []
        not_found = False
        for token in tokens:
            if token not in lexicon:
                not_found = True
                break
            token_id = lexicon[token]
            postings = inverted_index[str(token_id)]
            postings_list.append(postings)
        sorted_lists = sorted(postings_list, key=lambda x: len(x))
        if not not_found:
            intersection = merge_and_find_intersection_set(sorted_lists)
            if intersection:
                for i, docID in enumerate(intersection):
                    list_output.append(RetrievalTestingOutput(topic_number, mapping_to_docno[docID], i+1, len(intersection)-(i+1)))
        
    write_to_txt(list_output, file_output)

def merge_and_find_intersection_set(lists: list[list[int]]) -> list[int]:
    if not lists:
        return []
    if len(lists) == 1:
        return lists[0][::2]
    
    sets_of_docIDs = [set(lst[::2]) for lst in lists]
    
    intersection = set.intersection(*sets_of_docIDs)
    
    return list(sorted(intersection))

def merge_and_find_intersection(lists: list[list[int]]) -> list[int]:
    if not lists:
        return []
    if len(lists) == 1:
        return lists[0][::2]
    intersection = lists[0][::2]
    for current_list in lists:
        intersection = intersection_of_2(intersection, current_list)
        if not intersection:
            return [] 
    return intersection

def intersection_of_2(list1: list[int], list2: list[int]) -> list[int]:
    i, j = 0, 0
    intersection = []
    while i < len(list1) and j < len(list2):
        docID1 = list1[i]
        docID2 = list2[j]
        if docID1 == docID2:
            intersection.append(docID1)
            i += 1
            j += 2
        elif docID1 < docID2:
            i += 1
        else:
            j += 2
    return intersection

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
        description='Perform Boolean AND retrieval on an inverted index.'
    )

    parser.add_argument('directory_path', type=str,
                        help='Path to the directory containing the index files.')
    parser.add_argument('queries_path', type=str,
                        help='Path to the queries JSON file.')
    parser.add_argument('file_output', type=str,
                        help='Path to the output file where results will be stored.')

    args = parser.parse_args()

    if not args.directory_path or not args.queries_path or not args.file_output:
        raise ValueError(
            "Please input the path to the directory that has the output from the IndexEngine\n" 
            "as well as the path for the file where the queries are stored\n"
            "and the path for the output file.\n"
            "Would look something like this:\n"
            "python BooleanAND.py /home/smucker/latimes-index queries.txt hw2-results-WatIAMUserID.txt" 
        )

    boolean_and(args.directory_path, args.queries_path, args.file_output)