import gzip
import shutil
import re
import argparse
import json

def gzip_file(input_file_path, output_file_path):
    """
    Compresses a file using gzip.

    Parameters:
    - input_file_path: Path to the input file to be compressed.
    - output_file_path: Path where the compressed file will be saved.
    """
    with open(input_file_path, 'rb') as f_in:
        with gzip.open(output_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"Compressed {input_file_path} to {output_file_path}")

def create_queries(base_file, output_file):
    """
    Extracts topic titles from the base file and saves them as a JSON object 
    where the keys are the topic numbers and the values are the queries.
    
    Parameters:
    - base_file: The path to the base file containing topics.
    """
    with open(base_file, 'r') as file:
        data = file.read()

    matches = re.findall(r'<number>(\d+)</number>\s*<title>([^<]+)</title>', data)

    excluded_topics = {416, 423, 437, 444, 447}

    queries_dict = {}
    for number, title in matches:
        topic_num = int(number)
        if topic_num not in excluded_topics:
            queries_dict[topic_num] = title.strip()

    with open(output_file, 'w') as json_file:
        json.dump(queries_dict, json_file, indent=4)

    print("Queries have been saved to 'queries.json'")


def main():
    parser = argparse.ArgumentParser(description="Gzip file compression and topic queries extraction.")
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run. Use 'gzip' or 'query'")
    
    parser_gzip = subparsers.add_parser('gzip', help="Compress a file using gzip.")
    parser_gzip.add_argument('--gzip-input', '-gi', help="Path to the input file to be compressed.", required=True)
    parser_gzip.add_argument('--gzip-output', '-go', help="Path to save the compressed output file.", required=True)
    
    parser_query = subparsers.add_parser('query', help="Extract topics from the base file and create queries.")
    parser_query.add_argument('--base-file', '-b', help="Path to the base file containing topics for query extraction.", required=True)
    parser_query.add_argument('--output-file', '-o', help="Path to the output json of queries.", required=True)
    
    args = parser.parse_args()

    if args.command == 'gzip':
        gzip_file(args.gzip_input, args.gzip_output)
    elif args.command == 'query':
        create_queries(args.base_file, args.output_file)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
