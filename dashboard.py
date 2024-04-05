import marimo

__generated_with = "0.3.4"
app = marimo.App(width="medium", layout_file="layouts/dashboard.grid.json")


@app.cell
def __():
    import pandas as pd
    from esos_spike.parse import ParseDirectory
    import logging
    import marimo as mo
    import matplotlib.pyplot as plt
    import altair as alt
    import os
    return ParseDirectory, alt, logging, mo, os, pd, plt


@app.cell
def __(ParseDirectory, logging):
    parse_dir = ParseDirectory('data/raw-ESOS-reports/', mock=False, logging_info_level=logging.INFO)

    parse_dir.process_documents()

    parse_dir.enhance_documents(from_cache=True)

    parse_dir.load_results_df()
    return parse_dir,


@app.cell
def __(mo, parse_dir):
    mo.vstack([
        mo.md("Distribution of document lengh in tokens"),
        parse_dir.documents_df['num_tokens'].plot(kind='hist')
    ])
    return


@app.cell
def __(mo, parse_dir):
    avg_score_table = mo.ui.table(parse_dir.results_df.pivot_table(index='question_text', values='score_out_of_10', aggfunc='mean'), selection=None)

    full_table = mo.ui.table(parse_dir.documents_df, selection=None)

    unique_questions = parse_dir.results_df['question_text'].unique()
    question = mo.ui.dropdown(unique_questions, unique_questions[0], full_width=True)

    unique_documents = parse_dir.documents_df['id'].unique()
    document = mo.ui.dropdown(unique_documents, unique_documents[0], full_width=True)
    return (
        avg_score_table,
        document,
        full_table,
        question,
        unique_documents,
        unique_questions,
    )


@app.cell
def __(parse_dir, plt, question):
    # use matplotlib to plot a histogram of the score distribution for the selected question

    def create_histogram(df, question_value):
        # Filter the dataframe
        df_filtered = df[df['question_text'] == question_value]

        # Create a new figure
        fig, ax = plt.subplots()

        # Create a histogram on the ax
        ax.hist(df_filtered['score_out_of_10'], bins=10)

        # Set the axis labels
        ax.set_xlabel('Score out of 10')
        ax.set_ylabel('Frequency')

        # Return the figure
        return fig

    # Usage:
    fig = create_histogram(parse_dir.results_df, question.value)
    return create_histogram, fig


@app.cell
def __():
    # mo.ui.table(parse_dir.results_df[parse_dir.results_df['key'] == 'ReportStructure_2'], selection=None)
    return


@app.cell
def __(fig, mo, question):
    score_tab = mo.vstack([
        mo.md("### Histogram of Scores"),
        question,
        fig
    ])

    # document_tab = mo.vstack([
    #     mo.md("### Document Table"),
    #     document,
    #     mo.md(f"#### Table of all questions and scores for {document.value}"),
    #     parse_dir.results_df[document.value] if document.value in parse_dir.results_df.index else mo.md("Document not parsed.")
    # ])

    mo.ui.tabs({
        "Scores by Question":score_tab,
        "Test": mo.md("Ipsum")
    })
    return score_tab,


@app.cell
def __(mo):
    mo.ui.tabs({
        "Readme": mo.md(open('README.md').read()),
        "Methodology": mo.md(open("docs/method.md").read())
    })
    return


@app.cell
def __(mo, parse_dir):
    mo.ui.table(parse_dir.results_df.pivot_table(index=['key', 'question_text'], values='score_out_of_10', aggfunc='mean').sort_values('score_out_of_10', ascending=False), selection=None)
    return


@app.cell
def __(parse_dir):
    parse_dir.results_df.head()
    return


@app.cell
def __(mo):
    mo.md(
        """
        # UI elements sandbox
        UI ideas displayed below:
        """
    )
    return


@app.cell
def __(mo):
    mo.md("# Documents overview")
    return


@app.cell
def __(mo, parse_dir):
    # How long are files?
    out_table = parse_dir.documents_df[["file_name", "num_tokens"]]
    out_table["num_pages"] = parse_dir.documents_df["metadata"].apply(lambda x: x["xmpTPg:NPages"])

    mo.vstack([
        mo.md("How long are files?"),
        mo.ui.table(out_table)
    ])

    return out_table,


@app.cell
def __(mo, parse_dir, pd):
    mo.vstack(
        [mo.md("Which files have been rejected and why?"),
        mo.ui.table(pd.DataFrame(parse_dir.skip_files))]
    )
    return


@app.cell
def __(mo):
    mo.md("# One page document summary")
    return


@app.cell
def __(parse_dir):
    file_name = "AD Comms_ESOS 2019_Signed ESOS185262_20190912.pdf"
    file_id = parse_dir.documents_df.loc[parse_dir.documents_df["file_name"] == file_name]["id"].iloc[0]
    return file_id, file_name


@app.cell
def __(file_name, mo, os):
    # PDF viewer doesn't seem to work :(
    with open(os.path.join("data/raw-ESOS-reports", file_name), "rb") as file_obj:
        mo.pdf(src=file_obj)
    return file_obj,


@app.cell
def __(file_id, file_name, mo, out_table):
    # One page document summary

    mo.vstack([
        mo.md(f"## Document summary for {file_name}"),
        mo.md(f"Document length (pages): {out_table.loc[out_table['file_name'] == file_name]['num_pages'].iloc[0]}"),
        mo.md(f"Document length (tokens): {out_table.loc[out_table['file_name'] == file_name]['num_tokens'].iloc[0]}"),
        mo.md(f"Document id: {file_id}")
    ])

    return


@app.cell
def __(file_id, mo, parse_dir, pd):
    # Question scores for this document
    file_results = parse_dir.results_df.loc[file_id]
    questions = pd.DataFrame(parse_dir.questions["questions"])["question_text"]
    selected_question = mo.ui.dropdown(questions)
    return file_results, questions, selected_question


@app.cell
def __(file_results, mo, selected_question):
    mo.vstack([
        mo.md("### Question scores for this document"),
        mo.ui.table(file_results[["question_text", "score_out_of_10"]]),
        selected_question,

        
    ])
    return


@app.cell
def __(file_results, mo, selected_question):
    mo.vstack([
        
        mo.hstack([
            mo.md(f"{selected_question.value}"),
            mo.md(f"Score: {file_results.loc[file_results['question_text'] == selected_question.value]['score_out_of_10'].iloc[0]}")
        ]),
        mo.md("... Placeholder for a comparison to other documents for this question")
    ])



    return


@app.cell
def __(mo):
    # Dropdown for overall navigation
    views = ["Overview", "Document detailed view"]


    view_selector = mo.ui.dropdown(views, allow_select_none=False, value="Overview")
    view_selector


    return view_selector, views


@app.cell
def __(mo, view_selector):
    text_form = mo.ui.text(value="test")

    if view_selector.value == "Overview":
        title_elem = mo.vstack([
            mo.md("# Overview"),
            text_form
        ])

    elif view_selector.value == "Document detailed view":
        title_elem = mo.vstack([
            mo.md("# Document detailed view"),
            
        ])

    return text_form, title_elem


@app.cell
def __(title_elem):
    # Display all input elements
    title_elem

    return


@app.cell
def __(mo, text_form, view_selector):
    if view_selector == "Overview":
        display_text_input = mo.vstack([mo.md(f"Text inputted: {text_form.value}")])
    else:
        display_text_input = None
    return display_text_input,


@app.cell
def __(display_text_input):
    # Sadly we can't display secondary UI elements conditionally
    display_text_input
    return


if __name__ == "__main__":
    app.run()
