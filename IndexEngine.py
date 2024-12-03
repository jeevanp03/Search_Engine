import os
import gzip
import json
from datetime import datetime
import argparse
import re
from PorterStemmer import PorterStemmer

def unzip_file_and_read(file_path, output_dir, use_stemming=False):
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        raise ValueError(f"The folder '{output_dir}' already exists.")

    os.makedirs(output_dir, exist_ok=True)
    current_directory = output_dir

    metadata_dir = output_dir + "/MetaData"
    os.makedirs(metadata_dir, exist_ok=True)

    list_doc_no = []

    lexicon = {}

    inverted_index = {}

    list_doc_lengths = []
    
    stemmer = PorterStemmer() if use_stemming else None

    with gzip.open(file_path, "rt") as f:
        string_buffer = []
        string_buffer_headline = []
        string_buffer_important_content = []
        in_text = False
        in_graphic = False
        in_headline = False
        internal_id = 0
        doc_no = None
        dict_temp = {"internal_id": "", "date": "", "headline":""}

        for line in f:
            string_buffer.append(line)
            if "<DOC>" in line:
                dict_temp["internal_id"] = internal_id

            if "<DOCNO>" in line:
                doc_no = line.replace("<DOCNO>", "").replace("</DOCNO>", "").strip()
                list_doc_no.append(doc_no)
                date = doc_no.split("-")[0].replace("LA", "")
                date_obj = datetime.strptime(date, "%m%d%y")
                dict_temp["date"] = date_obj.strftime("%B %-d, %Y")
                date_list = list(date)

                year_path = os.path.join(current_directory, date_list[4]+date_list[5])
                os.makedirs(year_path, exist_ok=True)

                month_path = os.path.join(year_path, date_list[0]+date_list[1])
                os.makedirs(month_path, exist_ok=True)

                day_path = os.path.join(month_path, date_list[2]+date_list[3])
                os.makedirs(day_path, exist_ok=True)
            
            if "<HEADLINE>" in line:
                in_headline = True

            if "</HEADLINE>" in line:
                headline = "".join(string_buffer_headline)
                dict_temp["headline"] = re.sub(r'[\s\n]+', ' ', headline).strip()
                in_headline = False
            
            if "<TEXT>" in line:
                in_text = True

            if "</TEXT>" in line:
                in_text = False

            if "<GRAPHIC>" in line:
                in_graphic = True
            
            if "</GRAPHIC>" in line:
                in_graphic = False
            
            if in_headline:
                if "<" not in line and ">" not in line:
                    string_buffer_headline.append(line)
                    string_buffer_important_content.append(line)
            
            if in_text:
                if "<" not in line and ">" not in line:
                    string_buffer_important_content.append(line)
            
            if in_graphic:
                if "<" not in line and ">" not in line:
                    string_buffer_important_content.append(line)

            if "</DOC>" in line:
                if not string_buffer_headline:
                    dict_temp["headline"] = ""
                content = "".join(string_buffer)  
                full_file_path = os.path.join(day_path, doc_no + ".txt")
                with open(full_file_path, "w") as file:
                    file.write(content)
                
                meta_data_path = os.path.join(metadata_dir, doc_no+'.json')
                with open(meta_data_path, 'w') as fp:
                    json.dump(dict_temp, fp)
                
                filtered_content = "".join(string_buffer_important_content)

                tokens = []

                TokenizeStrings(filtered_content.split(" "), tokens, stemmer)

                list_doc_lengths.append(len(tokens))

                token_ids = ConvertTokensToIds(tokens, lexicon)

                word_counts = CountWords(token_ids)

                AddToPostings(word_counts, internal_id, inverted_index)

                string_buffer = []
                string_buffer_headline = []
                string_buffer_important_content = []
                dict_temp = {}
                doc_no = None
                internal_id += 1
    
    data = {'doc_nos': list_doc_no}
    
    with open('mapping.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    
    with open(os.path.join(output_dir,'doc-lengths.txt'), 'w') as file:
        for length in list_doc_lengths:
            file.write(f"{length}\n")
    
    with open(os.path.join(output_dir,'lexicon.json'), 'w') as file:
        json.dump(lexicon, file, indent=4)
    
    with open(os.path.join(output_dir,'inverted-index.json'), 'w') as file:
        json.dump(inverted_index, file, indent=4)


def AddToPostings(word_counts, doc_id, inverted_index):
    for term_id in word_counts:
        count = word_counts[term_id]
        if term_id in inverted_index:
            postings = inverted_index[term_id]
            postings.append(doc_id)
            postings.append(count)
        else:
            inverted_index[term_id] = [doc_id]
            inverted_index[term_id].append(count)


def CountWords(token_ids):
    word_counts = {}
    for token_id in token_ids:
        if token_id in word_counts:
            word_counts[token_id] += 1
        else:
            word_counts[token_id] = 1
    return word_counts


def ConvertTokensToIds(tokens, lexicon):
    token_ids = []

    for token in tokens:
        if token in lexicon:
            token_ids.append(lexicon[token])
        else:
            id = len(lexicon)
            lexicon[token] = id
            token_ids.append(id)
    return token_ids


def Tokenize(text, tokens):
    text = text.lower() 

    start = 0 
    i = 0

    for currChar in text:
        if not currChar.isdigit() and not currChar.isalpha():
            if start != i:
                token = text[start:i]
                tokens.append(token)
                
            start = i + 1

        i = i + 1

    if start != i:
        tokens.append(text[start:i])


def TokenizeStrings(strings, tokens, stemmer=None):
    for string in strings:
        Tokenize(string, tokens)
    if stemmer:
        tokens[:] = [stemmer.stem(token, 0, len(token) - 1) for token in tokens]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process latimes.gz file and store documents and metadata.')

    parser.add_argument('input_file', type=str,
                        help='Path to the latimes.gz file')
    parser.add_argument('output_dir', type=str,
                        help='Path to the output directory where documents and metadata will be stored')
    parser.add_argument('--use_stemming', action='store_true',
                        help='If set, the tokens will be stemmed using Porter Stemmer.')

    args = parser.parse_args()

    unzip_file_and_read(args.input_file, args.output_dir, use_stemming=args.use_stemming)
