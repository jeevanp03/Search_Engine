This document explains the sequence and usage of the provided Python programs to process documents, index them, and retrieve relevant results using different methods.

---

## Testing and Validating

### **0. Utils.py**

**Purpose**:

- Create the `query.json` file(s) containing query terms for retrieval.
- Compress files into gzip format.

**Usage**:

```bash
python utils.py --create-query <output_query_json_path> --gzip <input_file> <output_file>
```

**Arguments**:

- `--create-query`: Specify the path for the query JSON file to be created.
- `--gzip`: Specify the input file to be compressed and the output gzip file name.

**Example**:

```bash
python utils.py --create-query queries.json
python utils.py --gzip input.txt input.gz
```

---

### **1. IndexEngine.py**

**Purpose**:
Processes the provided `.gz` file, tokenizes the content, and creates:

- Document metadata.
- An inverted index.
- Document lengths.

**Usage**:

```bash
python IndexEngine.py <input_gz_file> <output_directory> [--use_stemming]
```

**Arguments**:

- `<input_gz_file>`: Path to the `.gz` file containing the documents.
- `<output_directory>`: Directory where the processed files and indices will be stored.
- `--use_stemming`: Optional. If specified, applies stemming to the tokens during indexing.

**Example**:
Without stemming:

```bash
python IndexEngine.py latimes.gz output_dir
```

With stemming:

```bash
python IndexEngine.py latimes.gz output_dir --use_stemming
```

---

### **2. Retrieval Methods**

Two methods are available for retrieving relevant documents based on the queries.

#### a. BooleanAND.py

**Purpose**:
Performs retrieval using Boolean AND logic.

**Usage**:

```bash
python BooleanAND.py <directory_path> <queries_path> <file_output>
```

**Arguments**:

- `<directory_path>`: Path to the directory containing the index files.
- `<queries_path>`: Path to the JSON file containing queries.
- `<file_output>`: Path to the output file where results will be stored.

**Example**:

```bash
python BooleanAND.py output_dir queries.json results_booleanAND.txt
```

#### b. BM25.py

**Purpose**:
Performs retrieval using the BM25 algorithm.

**Usage**:

```bash
python BM25.py <directory_path> <queries_path> <file_output> [--use_stemming]
```

**Arguments**:

- `<directory_path>`: Path to the directory containing the index files.
- `<queries_path>`: Path to the JSON file containing queries.
- `<file_output>`: Path to the output file where results will be stored.
- `--use_stemming`: Optional. If specified, applies stemming to query terms.

**Example**:
Without stemming:

```bash
python BM25.py output_dir queries.json results_BM25.txt
```

With stemming:

```bash
python BM25.py output_dir queries.json results_BM25_stemmed.txt --use_stemming
```

---

### **3. GetDoc.py**

**Purpose**:
Retrieve the document text for a given list of document IDs.

**Usage**:

```bash
python GetDoc.py <input_directory> <doc_ids_file> <output_file>
```

**Arguments**:

- `<input_directory>`: Path to the directory containing document files.
- `<doc_ids_file>`: Path to a file containing document IDs to retrieve.
- `<output_file>`: Path to the output file to save retrieved document content.

**Example**:

```bash
python GetDoc.py output_dir/documents doc_ids.txt retrieved_docs.txt
```

---

### **4. ComputeScoresPerResult.py**

**Purpose**:
Computes evaluation metrics (e.g., precision, recall) for each document based on the retrieval results.
This program uses the results from the retrieval runs (programs `2a` and `2b`). To use this program, you must move these
results to a folder (maybe labeled `retrieval_results`) to be able to run the program.

**Usage**:

```bash
python ComputeScoresPerResult.py <qrels_folder> <retrieval_results_folder> <scores_per_results>
```

**Arguments**:

- `<qrels_folder>`: Path to the folder containing relevance judgments.
- `<retrieval_results_folder>`: Path to the folder containing retrieval results.
- `<scores_per_results>`: Path to the folder where metrics for each document will be saved.

**Example**:

```bash
python ComputeScoresPerResult.py qrels_folder retrieval_results_folder scores_per_results
```

---

### **5. ComputeMeanScores.py**

**Purpose**:
Computes the mean evaluation metrics for a retrieval run.

**Usage**:

```bash
python ComputeMeanScores.py <scores_per_results> <mean_scores_output_file>
```

**Arguments**:

- `<scores_per_results>`: Path to the file containing metrics for each document.
- `<mean_scores_output_file>`: Path to the file where mean metrics will be saved.

**Example**:

```bash
python ComputeMeanScores.py scores_per_results mean_scores.txt
```

---

### **Execution Workflow**

1. **Prepare Data**:

   - Use `utils.py` to create queries (`query.json`) and compress input files.

2. **Index the Documents**:

   - Run `IndexEngine.py` to generate the document index and metadata. Optionally, use stemming with `--use_stemming`.

3. **Retrieve Documents**:

   - Use either `BooleanAND.py` or `BM25.py` to retrieve documents based on queries. Optionally, use stemming with `--use_stemming` in BM25.

4. **Extract Document Text**:

   - Use `GetDoc.py` to retrieve the full content of relevant documents.

5. **Evaluate Metrics**:
   - Compute per-document metrics using `ComputeScoresPerResult.py`.
   - Calculate mean metrics using `ComputeMeanScores.py`.

---

### **Dependencies**

Ensure the following Python libraries are installed:

- `argparse`
- `gzip`
- `json`
- `datetime`
- `re`

For stemming (optional):

- `PorterStemmer` (custom implementation in the provided code).

## Running Engine in "Production"

### **1. Interactive Search Engine**

**Purpose**:

This program provides an **interactive search engine** experience, allowing users to input queries, retrieve documents ranked by relevance using the BM25 algorithm, and display query-biased snippets for each result. Users can also retrieve the full content of a document based on its rank or issue new queries.

**Usage**:

```bash
python interactive_search.py
```

**Features**:

- Input a query to retrieve the top 10 relevant documents.
- View results ranked by BM25 relevance.
- See query-biased snippets for each document.
- Retrieve the full content of a document by specifying its rank.
- Issue new queries or quit the program interactively.

---

**Execution Flow**:

1. **Start the Interactive Engine**:

   - When you run the program, you will see the prompt:
     ```
     Welcome to the search engine!
     Enter a query:
     ```
   - Input your query to start the retrieval process.

2. **View Results**:

   - The program will display the top 10 ranked results in the following format:
     ```
     Rank. Snippet Headline (Date)
     Query-Biased Snippet (Docno)
     ```

   Example:

   ```
   1. Chernobyl accident sparks safety concerns (Jan 1, 1989)
   The Chernobyl disaster revealed flaws in reactor designs. Efforts to improve safety measures have since increased. (LA010189-0001)
   ```

3. **Interactive Commands**:

   - After viewing results, the program will prompt:

     ```
     Enter rank to retrieve the document of that retrieved rank, "N" for new query, or "Q" to quit:
     ```

   - **Options**:
     - Enter a **rank (1-10)** to retrieve the full content of the corresponding document.
     - Enter `"N"` to input a new query.
     - Enter `"Q"` to quit the program.

4. **Full Content Retrieval**:

   - If you enter a valid rank, the program will retrieve the full content of the corresponding document and display it.

5. **New Query**:

   - If you enter `"N"`, you can input a new query and repeat the process.

6. **Quit**:
   - If you enter `"Q"`, the program will terminate.

---

**Example Session**:

```bash
$ python interactive_search.py
Welcome to the search engine!
Enter a query: nuclear safety
Query: nuclear safety
Results:
1. Chernobyl disaster sparks global concerns (Jan 1, 1989)
The Chernobyl accident revealed flaws in Soviet reactor designs. Efforts to improve safety measures have since increased. (LA010189-0001)

2. Nuclear power risks debated globally (Mar 15, 1995)
Aging reactors spark public concerns. Experts stress the need for modernizing facilities. (LA031595-0003)

Time taken: 0.34 seconds

Enter rank to retrieve the document of that retrieved rank, "N" for new query, or "Q" to quit: 1

[Document Content for Docno LA010189-0001]

Enter rank to retrieve the document of that retrieved rank, "N" for new query, or "Q" to quit: N
Enter a query: renewable energy
Query: renewable energy
Results:
1. Solar power adoption increases globally (Feb 2, 2021)
Solar panels become affordable, boosting renewable energy adoption in developing countries. (LA020221-0005)

2. Wind energy revolutionizes electricity generation (Apr 10, 2022)
Offshore wind farms now produce electricity for millions. (LA041022-0007)

Time taken: 0.45 seconds

Enter rank to retrieve the document of that retrieved rank, "N" for new query, or "Q" to quit: Q
Goodbye!
```

---

### **Dependencies**

Ensure the following Python libraries are available:

- `argparse`
- `os`
- `math`
- `time`
- `textwrap`
- Custom modules: `BM25`, `IndexEngine`, and `GetDoc`.

**File Structure**:
Ensure the following files exist in the working directory or are properly referenced:

- `latimes.gz`: Input file for creating indices.
- `IndexEngine`: Directory containing the processed index files.

**Customization**:
Modify the `latimes.gz` file or the indexing logic if using a different dataset.
