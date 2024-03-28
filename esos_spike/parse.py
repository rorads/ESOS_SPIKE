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
import logging
import concurrent.futures
from tqdm import tqdm
import pickle

# Create a cache directory
doc_cache = diskcache.Cache(".doc_cache")

# load openai api key from .env file
load_dotenv()

client = OpenAI()


class ParseDirectory:
    def __init__(
        self, raw_files_directory, mock=False, logging_info_level=logging.INFO
    ):
        self.raw_files_directory = raw_files_directory
        self.data_file_path = "documents.json"
        self.questions = json.load(open("esos_spike/llm_static_files/questions.json"))
        self.documents_df = None
        self.skip_files = None
        self.mock = mock
        self.mock_answers = json.load(
            open("esos_spike/llm_static_files/mock_response.json")
        )
        self.row_ids = None
        self.results = None
        self.results_df = None
        logging.basicConfig(level=logging_info_level)

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

        file_type = file_name.split(".")[-1].lower()

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

        parsed = parser.from_file(op_path, headers={"X-Tika-Skip-Embedded": "true"})
        return parsed

    def num_tokens_from_string(
        self, string: str, encoding_name: str = "gpt-4-turbo"
    ) -> int:
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
        return (
            file_name.replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
            .replace(".", "_")
        )

    def process_documents(self):
        """
        Process the documents in the raw files directory return the documents in a big dict.
        """
        documents = []
        skip_files = []

        file_names = self.get_filenames_from_directory()

        logging.info(f"Processing {len(file_names)} files")

        for file_name in file_names:
            if self.extract_filetype(file_name) not in [".pdf", ".docx", ".doc"]:
                logging.info(f"Skipping {file_name} as filetype not supported.")
                skip_files.append({file_name: "Unsupported file type"})
                continue

            try:
                parsed = self.parse_document(file_name)
            except Exception as e:
                skip_files.append({file_name: str(e)})
                continue

            try:
                num_tokens = self.num_tokens_from_string(parsed["content"])
            except Exception as e:
                skip_files.append({file_name: str(e)})
                continue

            documents.append(
                {
                    "id": self.file_name_to_id(file_name),
                    "file_name": file_name,
                    "num_tokens": num_tokens,
                    "file_size": os.path.getsize(self.raw_files_directory + file_name),
                    "metadata": parsed["metadata"],
                    "content": parsed["content"],
                }
            )

        self.documents_df = pd.DataFrame(documents)
        self.skip_files = skip_files

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

        # Create a hash of the document content
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Create the cache file path
        cache_file_path = f"data/processed/{document_id}_{content_hash}.json"

        # If the cache file exists, load the data from the file
        if os.path.exists(cache_file_path):
            logging.debug(f"Loading data from cache for document_id: {document_id}")
            with open(cache_file_path, "r") as f:
                return json.load(f)

        # If the cache file does not exist, process the document and save the data to the file
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

        if not self.mock:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
                # Add more messages here
            ]

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                temperature=0.5,
                messages=messages,
                max_tokens=4096,
            )

            # parse the response to get the JSON string, and return it as a dict
            response_dict = json.loads(response.choices[0].message.content)

            # check te response_dict is not None. If it is, print the document_id
            if response_dict is None:
                logging.error(f"response_dict is None for document_id: {document_id}")
        else:
            response_dict = self.mock_answers

        # Save the data to the cache file
        with open(cache_file_path, "w") as f:
            json.dump(response_dict, f, indent=4)

        return response_dict

    def paralell_enhance_documents(self):
        """
        Enhance documents in parallel using OpenAI API.

        This function wraps the enhance_openai method in a function that takes a single argument,
        then uses a ThreadPoolExecutor to execute this function on each row of the documents dataframe in parallel.
        It uses a maximum of 60 concurrent threads.
        If the enhance_openai method raises a ValueError for a row (for example, if the document is too long),
        it logs an error message and skips that row.
        It displays a progress bar for the parallel execution using tqdm.
        It collects the results from the futures as they complete and returns them as a list.

        Returns:
        list: A list of tuples, where each tuple contains a document ID and the result of the enhance_openai method for that document.
        """

        # wrap the function to be executed with a single argument
        def process_row(row):
            try:
                return row["id"], self.enhance_openai(row["content"], row["id"])
            except ValueError as e:
                logging.error(f"skipping {row['id']}: {str(e)}")

        # Define the maximum number of concurrent threads to use
        max_threads = 60

        # Use the ThreadPoolExecutor to execute the function on each item in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit the function to the executor for each item in the series
            futures = [
                executor.submit(process_row, row)
                for id, row in self.documents_df.iterrows()
            ]

            # Use tqdm to display a progress bar for the parallel execution
            for _ in tqdm(
                concurrent.futures.as_completed(futures), total=len(self.documents_df)
            ):
                pass

            # Collect the results from the futures as they complete
            results = [future.result() for future in as_completed(futures)]

        return results

    def enhance_documents(self, from_cache=True):
        """
        Wrapper function to run paralell_enhance_documents and save the results to a pickle file.
        By default, it loads the results from the cache file. Sett from_cache to False to re-run
        the process and overwrite the cache file.

        Note that this is independed from the document level caching which is used in
        `enhance_openai()`. To clear this cache you will need to manually delete
        the files in `data/processed`.

        Parameters:
        from_cache (bool): Load the results from the cache file. Default is True.

        Returns:
        list: A list of tuples, where each tuple contains a document ID and the result of the enhance_openai method for that document.
        """

        if from_cache:
            logging.debug("Loading results from cache held in data/cached/results.pkl")
            try:
                with open("data/cached/results.pkl", "rb") as f:
                    results = pickle.load(f)
            except FileNotFoundError as e:
                logging.error("No cache file was found. Set `from_cache=False`...")
                raise e
        else:
            logging.debug("Running enhancement and saving to data/cached/results.pkl")
            results = self.paralell_enhance_documents()
            with open("data/cached/results.pkl", "wb+") as f:
                pickle.dump(results, f)

        # Remove none values from the results list
        results_cleaned = [result for result in results if result is not None]
        self.results = results_cleaned

    def load_results_df(self):
        """
        Load the results into a pandas DataFrame.

        This function iterates over the results, which is expected to be a list of tuples.
        Each tuple contains a document ID and a dictionary with a 'questions' key.
        The value of the 'questions' key is a list of dictionaries, where each dictionary represents a question.
        The function normalizes each list of questions into a DataFrame, sets the index of the DataFrame to the document ID,
        and appends the DataFrame to a list.
        Finally, it concatenates all the DataFrames in the list into a single DataFrame and stores it in the results_df attribute.
        """

        result_df_list = []

        for result in self.results:
            result_df = pd.json_normalize(result[1]["questions"])
            result_df.index = [result[0] for _ in range(len(result_df))]
            result_df_list.append(result_df)

        self.results_df = pd.concat(result_df_list)


if __name__ == "__main__":

    parse_dir = ParseDirectory(
        "data/raw-ESOS-reports/", mock=False, logging_info_level=logging.DEBUG
    )

    parse_dir.process_documents()

    parse_dir.enhance_documents(from_cache=True)

    parse_dir.load_results_df()

    print(len(parse_dir.results_df))
