import tiktoken
from tika import parser
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from concurrent.futures import as_completed
import diskcache
import hashlib

# Create a cache directory
doc_cache = diskcache.Cache('.doc_cache')
answer_cache = diskcache.Cache('.answer_cache')

# load openai api key from .env file
load_dotenv()

client = OpenAI()


class ParseDirectory:
    def __init__(self, raw_files_directory):
        self.raw_files_directory = raw_files_directory
        self.data_file_path = 'documents.json'
        self.questions = json.load(open('esos_spike/llm_static_files/questions.json'))
        self.documents_df = None
        self.skip_files = None

    def get_filenames_from_directory(self):
        """
        Get the names of all files in the directory.

        Returns:
        list: The names of all files in the directory.
        """
        return os.listdir(self.raw_files_directory)
    
    def extract_filetype(self, file_name):
        """
        Extract the filetype from a file name.

        Parameters:
        file_name (str): The name of the file.

        Returns:
        str: The filetype of the file.
        """

        file_type = file_name.split('.')[-1].lower()

        return f".{file_type}"

    @doc_cache.memoize(ignore=["self"])
    def parse_document(self, document_path):
        """
        Parse a PDF or DOC(X) file and return its content.

        Parameters:
        document_path (str): The path to the PDF file to be parsed.

        Returns:
        str: The content of the PDF file as a string.
        """

        op_path = self.raw_files_directory + document_path

        parsed = parser.from_file(op_path, headers={'X-Tika-Skip-Embedded': 'true'})
        return parsed
    

    def num_tokens_from_string(self, string: str, encoding_name: str = 'gpt-4-turbo') -> int:
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def file_name_to_id(self, file_name: str) -> str:
        """
        Transform a file name into an ID. This is done by replacing characters that are 
        not allowed in an ID with an underscore. These characters are: /, \, whitespace, and .

        Parameters
        ----------
        file_name : str
            The file name to transform into an ID.

        Returns
        -------
        str
            The transformed ID.
        """
        return file_name.replace('/', '_').replace('\\', '_').replace(' ', '_').replace('.', '_')
    

    def process_documents(self):
        """
        Process the documents in the raw files directory return the documents in a big dict.
        """
        documents = []
        skip_files = []

        file_names = self.get_filenames_from_directory()
        for file_name in file_names:
            if self.extract_filetype(file_name) not in ['.pdf', '.docx', '.doc']:
                skip_files.append({file_name: "Unsupported file type"})
                continue

            try:
                parsed = self.parse_document(file_name)
            except Exception as e:
                skip_files.append({file_name: str(e)})
                continue

            try:
                num_tokens = self.num_tokens_from_string(parsed['content'])
            except Exception as e:
                skip_files.append({file_name: str(e)})
                continue

            documents.append({
                'id': self.file_name_to_id(file_name),
                'file_name': file_name,
                'num_tokens': num_tokens,
                'file_size' : os.path.getsize(self.raw_files_directory + file_name),
                'metadata': parsed['metadata'],
                'content': parsed['content']
            })

        self.documents_df = pd.DataFrame(documents)
        self.skip_files = skip_files
    
    
    @answer_cache.memoize(ignore=["self", "document_content"])
    def enhance_openai(self, document_content, document_id):
        """
        Enhance a document with OpenAI API.

        Parameters:
        document_row (Series): A row from the documents dataframe.

        Returns:
        dict: The data structure containing questions with responses from OpenAI.
        """

        content = document_content
        num_tokens = self.num_tokens_from_string(content)

        if num_tokens > 120000:
            raise ValueError("The document is too long to process.")
        
        prompt = f"""
        Below is a json representation of a set of questions which I want you to answer about the document which follows. 
        
        It is crucial that you respect structure of the JSON string. 
        
        Be sure to answer all the questions in the JSON string. If a document looks like it should include 
        something a question requires, but it is not there, set the score to 0 and provide a rationale.
        
        For the quotes, ensure that enough context is provided to understand the quote and to use ctrl+f to find it in the document.
        
        Do not include newlines or extra spaces in the JSON string, and do not include the code block markers 
        (```) in the JSON string. 
        
        JUST RETURN THE JSON AND MAKE SURE IT'S VALID.
        
        JSON String:
        
        ```
        {json.dumps(self.questions)}
        ```
        
        Document to evaluate:
        {content}
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
            # Add more messages here
        ]

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            temperature=0.5,
            messages=messages,
            max_tokens=4096
        )
        
        # parse the response to get the JSON string, and return it as a dict
        response_dict = json.loads(response.choices[0].message.content)

        # check te response_dict is not None. If it is, print the document_id
        if response_dict is None:
            print(f"response_dict is None for document_id: {document_id}")
        
        return response_dict
    
    
    def paralell_enhance_documents(self):
        """
        """
        
        import concurrent.futures
        from tqdm import tqdm
        
        # wrap the function to be executed with a single argument
        def process_row(row):
            try:
                return self.enhance_openai(row['content'], row['id'])
            except ValueError as e:
                print(f"skipping {row['id']}: {str(e)}")

        # Define the maximum number of concurrent threads to use
        max_threads = 60 

        # Use the ThreadPoolExecutor to execute the function on each item in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit the function to the executor for each item in the series
            futures = [executor.submit(process_row, row) for id,row in self.documents_df.iterrows()]

            # Use tqdm to display a progress bar for the parallel execution
            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(self.documents_df)):
                pass

            # Collect the results from the futures as they complete
            results = [future.result() for future in as_completed(futures)]

        return results
    
    
    def clear_none_cache_entries(self):
        """
        Clear the cache of entries that are None.
        """
        for key in answer_cache.iterkeys():
            # if cache[key] is None:
            #     cache.pop(key)
            pass

if __name__ == '__main__':
   
    parse_dir = ParseDirectory('data/raw-ESOS-reports/')
    parse_dir.clear_none_cache_entries()
    parse_dir.process_documents()

    # # Enhance the first document with OpenAI
    # document_row = parse_dir.documents_df.iloc[3]
    # print(f"Document ID: {document_row['id']}")
    # print("\n\n--------\n\n")
    # enhanced_document = parse_dir.enhance_openai(document_row)
    # print(json.dumps(enhanced_document))
    
    results = parse_dir.paralell_enhance_documents()
    print(results)

    answer_cache.get()
    