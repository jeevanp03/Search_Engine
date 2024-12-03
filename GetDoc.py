import os
import json
import argparse
import re

def get_doc(folder_path, input_type, key):
    if input_type == "docno" and len(key) != 13:
        raise ValueError("Please provide a valid doc no, the length of a valid doc no is 13")
    
    # if input_type == "docno" and re.match(r"^LA", key):
    #     raise ValueError("Please provide a valid doc no, a valid docno contains LA at the start")

    if input_type == "id" and bool(re.search(r'[A-Za-z]', key)):
        raise ValueError("Please provide a valid id, there should be no letters")
    
    if input_type == "id" and int(key) < 0:
        raise ValueError("Please provide a valid id, it should not be negative")
    
    if input_type != "docno" and input_type != "id":
        raise ValueError(f"Please provide a valid type, it must be either docno or id, not: {input_type}")
    
    if not os.path.exists(folder_path):
        raise ValueError("please provide a valid path to the contents being retrieved")

    if input_type == "docno": 

        path_to_metadata = os.path.join(folder_path, f"MetaData/{key}.json")

        if not os.path.exists(path_to_metadata):
            raise ValueError("the doc no given does not exist, input a valid doc no")
        
        with open(path_to_metadata, 'r') as file:
            metadata = json.load(file)

        id = metadata["internal_id"]
        output_data(key, id, metadata, folder_path)

    else:
        with open('mapping.json', 'r') as file:
            data = json.load(file)

        # dict_id_mapping = {}

        # for i, doc_no in enumerate(doc_no_list):
        #     dict_id_mapping[doc_no] = i
    
        doc_no_list = data["doc_nos"]
        if len(doc_no_list) - 1 < int(key):
            raise ValueError("Please provide a valid internal id, the current one provided is not found")
        
        doc_no = doc_no_list[int(key)]
        with open(folder_path + f"/MetaData/{doc_no}.json", 'r') as file:
            metadata = json.load(file)
        output_data(doc_no, key, metadata, folder_path)

def output_data(doc_no, id, meta_data, folder_path):
    date_list = list(doc_no.replace("LA", ""))
    year = date_list[4] + date_list[5]
    month = date_list[0]+date_list[1]
    day = date_list[2]+date_list[3]
    raw_text_path = os.path.join(folder_path, year, month, day, doc_no + ".txt")
    with open(raw_text_path, 'r') as file:
        raw_text = file.read()
    
    print("Docno: ",doc_no)
    print("Internal id: ",id)
    print("Date: ",meta_data["date"])
    print("Headline: ",meta_data["headline"].strip())
    print("raw document: ")
    print(raw_text)

def return_data(doc_no, folder_path):
    date_list = list(doc_no.replace("LA", ""))
    year = date_list[4] + date_list[5]
    month = date_list[0]+date_list[1]
    day = date_list[2]+date_list[3]
    raw_text_path = os.path.join(folder_path, year, month, day, doc_no + ".txt")
    with open(raw_text_path, 'r') as file:
        raw_text = file.read()

    
    return remove_tags(raw_text).strip()

def retrieve_data(doc_no, folder_path):
    date_list = list(doc_no.replace("LA", ""))
    year = date_list[4] + date_list[5]
    month = date_list[0]+date_list[1]
    day = date_list[2]+date_list[3]
    raw_text_path = os.path.join(folder_path, year, month, day, doc_no + ".txt")
    with open(raw_text_path, 'r') as file:
        raw_text = file.read()
    
    print(raw_text)

def remove_tags(input_string):
    return re.sub(r"<.*?>", "", input_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Retrieve and display document information.'
    )

    parser.add_argument('folder_path', type=str,
                        help='Path to the location of the documents and metadata store')
    parser.add_argument('input_type', choices=['id', 'docno'],
                        help='Specify the type of key: "id" or "docno"')
    parser.add_argument('key', type=str,
                        help='The internal integer id of a document or a docno')

    args = parser.parse_args()

    if not args.folder_path or not args.input_type:
        raise ValueError(
            "Please input both the path to the input file as well as the desired path of the output.\n"
            "Would look something like this:\n"
            "python get_doc.py /path/to/latimes-index docno LA010189-0001\n" 
            "or\n"
            "python get_doc.py /path/to/latimes-index id 6832"
        )

    get_doc(args.folder_path, args.input_type.lower(), args.key.strip().upper())
