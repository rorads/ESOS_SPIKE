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

    return ParseDirectory, alt, logging, mo, pd, plt


@app.cell
def __(ParseDirectory, logging):
    parse_dir = ParseDirectory('data/raw-ESOS-reports/', mock=False, logging_info_level=logging.INFO)

    parse_dir.process_documents()

    parse_dir.enhance_documents(from_cache=True)

    parse_dir.load_results_df()
    return parse_dir,


@app.cell
def __(parse_dir):
    set(list(parse_dir.results_df.index))
    return


@app.cell
def __(mo, parse_dir):
    avg_score_table = mo.ui.table(parse_dir.results_df.pivot_table(index='question_text', values='score_out_of_10', aggfunc='mean'), selection=None)

    full_table = mo.ui.table(parse_dir.results_df, selection=None)

    unique_questions = parse_dir.results_df['question_text'].unique()
    question = mo.ui.dropdown(unique_questions, unique_questions[0], full_width=True)

    unique_documents = parse_dir.results_df['document_id'].unique()
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
    return


@app.cell
def __(document, fig, full_table, mo, question):
    score_tab = mo.vstack([
        mo.md("### Histogram of Scores"),
        question,
        fig
    ])

    document_tab = mo.vstack([
        mo.md("### Document Table"),
        document,
        mo.md(f"#### Table of all questions and scores for {document.value}"),
        full_table[full_table['document_name'] == document.value]
    ])

    mo.tabs({
        "Scores by Question":score_tab,
        "Document Table":document_tab,
    })
    return document_tab, score_tab


@app.cell
def __():
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
