# ESOS Report Assessment Toolkit

The ESOS Report Assessment Toolkit provides a comprehensive environment for analyzing Energy Savings Opportunity Scheme (ESOS) reports against a set of predetermined questions derived from government guidelines. This README outlines what the software does, how to set it up, and how to quickly start using it.

## Overview

This toolkit parses and analyzes ESOS reports, extracting key information to evaluate their compliance with ESOS guidelines. Using a combination of PDF and DOC(X) parsing, machine learning model queries (via OpenAI's API), and a structured set of questions, it automates the assessment of these reports, providing quantitative and qualitative insights.

### Features

- **Report Parsing**: Automatically extracts text content from PDF and DOC(X) reports in the `data/raw-ESOS-reports/` directory.
- **Automated Analysis**: Utilizes OpenAI's API to analyze the extracted content against a set of structured questions.
- **Comprehensive Assessment**: Produces both a detailed understanding of each document's compliance and highlights areas needing improvement.

## Prerequisites

To use this toolkit, you'll need:
- Python 3.8 or newer.
- An active internet connection for API requests.
- An OpenAI API key (make sure you have access to OpenAI and have generated an API key).
- Poetry 
- Java 8 or higher

## Quickstart

Follow these setup steps to get started with the ESOS Report Assessment Toolkit:

1. **Clone the Repository**:
   Ensure you have this repository cloned or downloaded to your local machine.

2. **Install Dependencies**:
   Install the required Python libraries listed in `pyproject.toml`. Using Poetry, you can install these by running:
   ```bash
   poetry install
   ```

3. **Set Up Your `.env` File**:
   Copy the `.env.template` file to a new file named `.env`, and insert your OpenAI API key:
   ```plaintext
   OPENAI_API_KEY=<your_openai_api_key_here>
   ```

4. **Run the Software**:
   Start the Poetry environment with 
   ```bash
   poetry shell
   ```

   You can start the analysis by running the `dashboard.py` file with Marimo:
   ```bash
   marimo edit dashboard.py
   ```
   This script initializes the process of parsing documents, submitting content to OpenAI for evaluation, and storing the results.

5. **View the Results**:
   After processing, check the `data/processed` directory to see the assessment's output. The toolkit provides JSON files with detailed evaluations for each document, including compliance scores, rationales, and highlighted quotes.

## Understanding the Output

The processed files contain a wealth of information derived from each ESOS report, including:

- **Compliance Scores**: Numerical scores evaluating how well the document meets specific criteria.
- **Rationale**: Text entries providing reasoning behind each score.
- **Quotes**: Direct quotes from the documents supporting the rationale.

Refer to `docs/method.md` for a detailed understanding of the assessment methodology and how scores and rationales are derived.

## Contributing

Contributions to the ESOS Report Assessment Toolkit are welcome. Please refer to the project's issues tab to find areas where you can help. Make sure to follow the existing code structure and document any changes you make.

## Disclaimer

This toolkit is designed to assist in the analysis of ESOS reports but does not replace professional judgment or regulatory advice. Always consult a qualified professional for ESOS compliance matters.

## Support

For help or questions regarding the toolkit, please open an issue in the repository. Feedback and suggestions are greatly appreciated as we look to improve the tool's effectiveness and usability.

# How did I create these docs?

```sh
(echo "Please write a README.md from the following, which is a custom printout of the directory structure and some specific files. Focus on quickstart and setup steps, as well as providing an overview of what the code does. Assume the user has access to the files which would be needed in the data/raw-ESOS-reports/ directory"; sh custom_repo_describe.sh) | llm
```

