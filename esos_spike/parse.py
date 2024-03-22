import tiktoken
from tika import parser
import pandas as pd
import os
import openai


class ParseDirectory:
    def __init__(self, raw_files_directory):
        self.raw_files_directory = raw_files_directory
        self.data_file_path = 'documents.json'
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

if __name__ == '__main__':
   
    parse_dir = ParseDirectory('data/raw-ESOS-reports/')
    parse_dir.process_documents()

    print(parse_dir.documents_df.describe())

    