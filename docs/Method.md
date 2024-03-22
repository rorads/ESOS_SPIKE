# Methodology

## Data Pre-Processing

For this I used Apache Tika, an open-source content analysis toolkit that allows for the detection, extraction, and analysis of various file formats, including but not limited to text, audio, video, and image files. It provides a straightforward API that enables developers to parse content from files, thereby facilitating the process of understanding, indexing, and managing large collections of data. Tika supports extraction from over a thousand different file types, making it a versatile tool for content-based application development, search engine creation, content management systems, and data analysis tasks. It also offers language detection, metadata extraction, and content type identification capabilities, making it a comprehensive solution for processing and analyzing unstructured data.

For this, I wrote a Python class `ParseDirectory`, which is designed to process documents within a specified directory. Its primary functions include:

1. Identifying all the files within a given directory.
2. Filtering these files to focus on PDFs and DOC(X) formats.
3. Extracting the content from these files.
4. Calculating the number of tokens (words/pieces of text) in these contents using a specific encoding, presumably for further text analysis or processing.
5. Converting file names into a standardized ID format by replacing certain characters with underscores, to potentially use these IDs in databases or as part of a structured dataset.
6. Compiling important information about each file, including its new ID, original file name, token count, file size, metadata, and extracted content, into a pandas DataFrame for analysis and manipulation.
7. Handling exceptions by skipping files that cannot be processed or supported and documenting the reasons for skipping these files.

Ultimately, it automates the extraction and initial analysis of textual data from documents in a directory, preparing the data for further analysis or machine learning tasks.


## Getting questions from ChatGPT

I started with this page: https://www.gov.uk/government/publications/comply-with-the-energy-savings-opportunity-scheme-esos/complying-with-the-energy-savings-opportunity-scheme-esos#completing-the-esos-report

My thinking was to create a qualitative and quantitative evaluation framework which could be used by an LLM to evaluate each document.

To set up a structure for questions, I took section 10 and kicked off the following dialogue with ChatGPT via the API (gpt-4-turbo)

**User**:

> consider the following guidance. please compile a set of questions which can be used to evaluate a given report against these requrements
> 
> =============
> 
> `<section 10 from the linked document above was pasted here>`

**Assistant**:

Based on the provided requirements, here's a set of questions that can be used to evaluate an ESOS report:

> ### General Compliance and Reporting Structure
> 1. Has the ESOS report been produced before the compliance date for the relevant compliance period?
> 2. Is the report structured to include all mandatory information as specified in the guidelines? 
> 
> ### Organisational Details
> 3. Are the organisational name, the number of companies within the participant group, and a corporate group structure chart or equivalent information accurately provided?
> 4. Is there a detailed description of the relationship between organisations in the participant group?
> 5. If applicable, are changes in the participant group (both additions and removals) between the qualification date and the compliance date accurately documented?
> 
> ### Personnel Involved
> 6. Are the details of the board level director(s) responsible for sign-off, the lead assessor, and any other significant personnel involved accurately listed?
> 
> ### Energy Consumption and Savings
> 7. Does the report correctly detail the total energy consumption, significant energy consumption calculations, energy subtotals by organisational purpose, and energy intensity ratios?
> 8. Are the estimates of energy savings achieved by the participant since the previous compliance period clearly outlined and properly estimated?
> 
> ### Energy Audits and Compliance Routes
> 9. For each energy audit and/or alternative compliance route used, does the report properly cover scope and coverage, summary of outputs, energy savings measures identified, and estimated savings achievable?
> 10. Is relevant information regarding the implementation of energy savings measures provided?
> 
> ### ISO 50001 Certification Details (if applicable)
> 11. For participants with ISO 50001 certification covering all energy supplies, does the report include the required information regarding total energy consumption, energy intensity ratios, and details of energy performance improvements?
> 12. Are documented outcomes of performance evaluations and identified opportunities for improving energy performance properly included and detailed?
> 
> ### Additional Information and Sharing
> 13. Does the report include any additional, relevant information that supports the ESOS assessment or findings?
> 14. Has the report, or relevant parts of it, been shared with other undertakings within the participant group as required?
> 
> ### Specific Details for Participants Using Alternative Compliance Routes
> 15. For each alternative compliance route used, does the report correctly detail the coverage and percentage of total energy consumption?
> 16. Is there a proper summary of the measures for reducing energy consumption recommended through alternative compliance routes, including potential annual reductions in energy spend and consumption?
> 
> ### Implementation Details
> 17. Does the report include suggested programmes for implementing energy savings opportunities, including timescales, costs and benefits, and a payback period?
> 18. Are considerations related to minimum energy efficiency standards, availability of funding and support for energy savings opportunities, and other possible sources of support adequately addressed?
> 
> Ensuring these questions are thoroughly addressed in the evaluation can help assess whether an ESOS report meets the specified requirements comprehensively.

**User**:

> Create a json file which has each question here represented with a key which represents both the section and the question itself. Each question entry should have a question number, the question text itself, a score out of 5, and a 'rationale' answer which is free text (which will be filled after the evaluation), and a 'quotes' array which can have one or more direct quotes from the document). Leave the values empty apart from key, question text and question number.

**Assistant**:

> Below is a representation of the requested JSON structure with empty values for "score", "rationale", and "quotes", except for the mentioned fields:

> ```json
> {
>   "questions": [
>     {
>       "key": "GeneralCompliance_1",
>       "question_number": 1,
>       "question_text": "Has the ESOS report been produced before the compliance date for the relevant compliance period?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "ReportStructure_2",
>       "question_number": 2,
>       "question_text": "Is the report structured to include all mandatory information as specified in the guidelines?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "OrganisationalDetails_3",
>       "question_number": 3,
>       "question_text": "Are the organisational name, the number of companies within the participant group, and a corporate group structure chart or equivalent information accurately provided?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "OrganisationalDetails_4",
>       "question_number": 4,
>       "question_text": "Is there a detailed description of the relationship between organisations in the participant group?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "OrganisationalChanges_5",
>       "question_number": 5,
>       "question_text": "If applicable, are changes in the participant group (both additions and removals) between the qualification date and the compliance date accurately documented?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "PersonnelInvolved_6",
>       "question_number": 6,
>       "question_text": "Are the details of the board level director(s) responsible for sign-off, the lead assessor, and any other significant personnel involved accurately listed?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "EnergyConsumptionSavings_7",
>       "question_number": 7,
>       "question_text": "Does the report correctly detail the total energy consumption, significant energy consumption calculations, energy subtotals by organisational purpose, and energy intensity ratios?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "EnergyConsumptionSavings_8",
>       "question_number": 8,
>       "question_text": "Are the estimates of energy savings achieved by the participant since the previous compliance period clearly outlined and properly estimated?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "EnergyAuditsComplianceRoutes_9",
>       "question_number": 9,
>       "question_text": "For each energy audit and/or alternative compliance route used, does the report properly cover scope and coverage, summary of outputs, energy savings measures identified, and estimated savings achievable?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "EnergyAuditsComplianceRoutes_10",
>       "question_number": 10,
>       "question_text": "Is relevant information regarding the implementation of energy savings measures provided?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "ISO50001CertificationDetails_11",
>       "question_number": 11,
>       "question_text": "For participants with ISO 50001 certification covering all energy supplies, does the report include the required information regarding total energy consumption, energy intensity ratios, and details of energy performance improvements?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "ISO50001CertificationDetails_12",
>       "question_number": 12,
>       "question_text": "Are documented outcomes of performance evaluations and identified opportunities for improving energy performance properly included and detailed?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "AdditionalInformationSharing_13",
>       "question_number": 13,
>       "question_text": "Does the report include any additional, relevant information that supports the ESOS assessment or findings?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "AdditionalInformationSharing_14",
>       "question_number": 14,
>       "question_text": "Has the report, or relevant parts of it, been shared with other undertakings within the participant group as required?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "AlternativeComplianceRoutes_15",
>       "question_number": 15,
>       "question_text": "For each alternative compliance route used, does the report correctly detail the coverage and percentage of total energy consumption?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "AlternativeComplianceRoutes_16",
>       "question_number": 16,
>       "question_text": "Is there a proper summary of the measures for reducing energy consumption recommended through alternative compliance routes, including potential annual reductions in energy spend and consumption?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "ImplementationDetails_17",
>       "question_number": 17,
>       "question_text": "Does the report include suggested programmes for implementing energy savings opportunities, including timescales, costs and benefits, and a payback period?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     },
>     {
>       "key": "ImplementationDetails_18",
>       "question_number": 18,
>       "question_text": "Are considerations related to minimum energy efficiency standards, availability of funding and support for energy savings opportunities, and other possible sources of support adequately addressed?",
>       "score": "",
>       "rationale": "",
>       "quotes": []
>     }
>   ]
> }
> ```