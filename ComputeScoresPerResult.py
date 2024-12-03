import os
import math
from collections import defaultdict
import argparse

def read_qrels(file_path):
    qrels = defaultdict(lambda: defaultdict(int))
    total_relevant_docs = defaultdict(int)
    idcg_per_topic = defaultdict(lambda: defaultdict(float))
    topic_ids = set()

    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.split()
                if len(parts) != 4:
                    print(f"Improper format in qrels file: {line.strip()}")
                    return "bad format", None, None, None
                topic_id, _, docno, judgment = parts
                if not topic_id.isdigit() or not (401 <= int(topic_id) <= 450):
                    print(f"Invalid topicID in qrels file: {line.strip()}")
                    return "bad format", None, None, None
                if not judgment.isdigit():
                    print(f"Invalid judgment in qrels file: {line.strip()}")
                    return "bad format", None, None, None

                topic_id = int(topic_id)
                topic_ids.add(topic_id)
                qrels[topic_id][docno] = int(judgment)

                if int(judgment) > 0:
                    total_relevant_docs[topic_id] += 1

        for topic_id, doc_judgments in qrels.items():
            relevances = sorted(doc_judgments.values(), reverse=True)
            idcg_10 = sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances[:10]))
            idcg_1000 = sum(rel / math.log2(i + 2) for i, rel in enumerate(relevances[:1000]))
            idcg_per_topic[topic_id]['10'] = idcg_10
            idcg_per_topic[topic_id]['1000'] = idcg_1000

    except Exception as e:
        print(f"Error reading qrels file: {e}")
        return "bad format", None, None, None

    return qrels, total_relevant_docs, idcg_per_topic, sorted(topic_ids)

def read_results(file_path):
    results = defaultdict(list)
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.split()
                if len(parts) != 6:
                    print(f"Improper format in results file: {line.strip()}")
                    return "bad format"
                topic_id, q0, docno, rank, score, run_tag = parts
                if not topic_id.isdigit():
                    print(f"Invalid topicID in results file: {line.strip()}")
                    return "bad format"
                if q0 != "Q0":
                    print(f"Missing or incorrect Q0 in results file: {line.strip()}")
                    return "bad format"
                if not rank.isdigit() or int(rank) < 1:
                    print(f"Invalid rank in results file: {line.strip()}")
                    return "bad format"
                try:
                    float(score)
                except ValueError:
                    print(f"Invalid score in results file: {line.strip()}")
                    return "bad format"
                if not run_tag.isalnum() or len(run_tag) > 12:
                    print(f"Invalid runTag in results file: {line.strip()}")
                    return "bad format"
                results[int(topic_id)].append((docno, float(score)))
    except Exception as e:
        print(f"Error reading results file: {e}")
        return "bad format"

    for topic_id in results:
        results[topic_id].sort(key=lambda x: (-x[1], x[0]))
    return results

def average_precision(qrels, results, topic_id, total_relevant):
    if total_relevant == 0:
        return 0.0

    relevant_docs = {doc for doc, rel in qrels[topic_id].items() if rel > 0}
    retrieved_docs = [doc for doc, _ in results.get(topic_id, [])[:1000]]
    num_retrieved = 0
    sum_precision = 0.0

    for rank, doc in enumerate(retrieved_docs, start=1):
        if doc in relevant_docs:
            num_retrieved += 1
            sum_precision += num_retrieved / rank

    return sum_precision / total_relevant

def precision_at_k(qrels, results, topic_id, k):
    relevant_docs = {doc for doc, rel in qrels[topic_id].items() if rel > 0}
    if not relevant_docs:
        return 0.0

    retrieved_docs = [doc for doc, _ in results.get(topic_id, [])[:k]]
    relevant_retrieved = sum(1 for doc in retrieved_docs if doc in relevant_docs)
    return relevant_retrieved / k

def dcg_at_k(relevances, k):
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        dcg += rel / math.log2(i + 2)
    return dcg

def ndcg_at_k(qrels, results, topic_id, k, idcg):
    if idcg == 0:
        return 0.0

    relevances = [qrels[topic_id].get(doc, 0) for doc, _ in results.get(topic_id, [])[:k]]
    dcg = dcg_at_k(relevances, k)

    return dcg / idcg

def main(qrels_folder, results_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for qrels_file in os.listdir(qrels_folder):
        qrels_path = os.path.join(qrels_folder, qrels_file)
        qrels, total_relevant_docs, idcg_per_topic, topic_ids = read_qrels(qrels_path)
        if qrels == "bad format":
            print(f"Qrels file {qrels_file} is improperly formatted.")
            continue

        for results_file in os.listdir(results_folder):
            results_path = os.path.join(results_folder, results_file)
            results = read_results(results_path)

            output_lines = ["Topic,Average Precision,P@10,NDCG@10,NDCG@1000\n"]

            if results == "bad format":
                print(f"Results file {results_file} is improperly formatted.")
                output_lines.append("bad format,bad format,bad format,bad format\n")
            else:
                for topic_id in topic_ids:
                    total_relevant = total_relevant_docs.get(topic_id, 0)
                    idcg_10 = idcg_per_topic[topic_id]['10']
                    idcg_1000 = idcg_per_topic[topic_id]['1000']

                    ap = average_precision(qrels, results, topic_id, total_relevant)
                    p10 = precision_at_k(qrels, results, topic_id, 10)
                    ndcg10 = ndcg_at_k(qrels, results, topic_id, 10, idcg_10)
                    ndcg1000 = ndcg_at_k(qrels, results, topic_id, 1000, idcg_1000)

                    output_lines.append(f"{topic_id},{ap:.4f},{p10:.4f},{ndcg10:.4f},{ndcg1000:.4f}\n")

            output_file_name = f"{results_file}_scores.txt"
            output_file_path = os.path.join(output_folder, output_file_name)
            with open(output_file_path, 'w') as out_file:
                out_file.writelines(output_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Qrels and Results files to calculate evaluation metrics.")
    parser.add_argument("qrels_folder", type=str, help="Path to the folder containing qrels files")
    parser.add_argument("results_folder", type=str, help="Path to the folder containing results files")
    parser.add_argument("output_folder", type=str, help="Path to the folder to store output files")

    args = parser.parse_args()

    main(args.qrels_folder, args.results_folder, args.output_folder)
