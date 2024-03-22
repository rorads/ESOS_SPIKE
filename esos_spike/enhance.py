import openai
import parse

parse_dir = parse.ParseDirectory('data/raw-ESOS-reports/')
parse_dir.process_documents()

print(parse_dir.documents_df.describe())