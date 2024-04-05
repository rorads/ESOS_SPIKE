import marimo

__generated_with = "0.3.4"
app = marimo.App(width="full")


@app.cell
def __():
    import logging

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    from esos_spike.parse import ParseDirectory
    from esos_spike import utils
    return ParseDirectory, logging, mo, np, pd, plt, utils


@app.cell
def __(ParseDirectory, logging):
    # Process reports
    parse_dir = ParseDirectory('data/raw-ESOS-reports/', mock=False, logging_info_level=logging.INFO)

    parse_dir.process_documents()

    parse_dir.enhance_documents(from_cache=True)

    parse_dir.load_results_df()
    return parse_dir,


@app.cell
def __(mo):
    mo.vstack([
        mo.md("# ESOS Report Assessment Toolkit"),
        mo.md("## How to use this toolkit:"),
        mo.md("""
    The ESOS Report Assessment Toolkit provides a comprehensive environment for analyzing Energy Savings Opportunity Scheme (ESOS) reports against a set of predetermined questions derived from government guidelines. This dashboard displays:

    1. Overall scores and statistics across the whole dataset
    2. A breakdown by question of scores
    3. Detailed scores and rationales for a selected document

    We also detail our research methodology at the bottom of the page.

    """)
              ])
    return


@app.cell
def __(mo):
    mo.md("---")
    return


@app.cell
def __(logging, parse_dir, pd):
    mean_scores_per_doc = []
    for id, _ in parse_dir.documents_df.iterrows():
        try:
            mean_scores_per_doc.append({
                "id": id,
                "mean_score": parse_dir.results_df.loc[id]["score_out_of_10"].mean()
            })
        except KeyError:
            logging.info(f"No scores for {id}")

    mean_scores_per_doc_df = pd.DataFrame(mean_scores_per_doc)
    mean_scores_per_doc_df.set_index("id", inplace=True)
    return id, mean_scores_per_doc, mean_scores_per_doc_df


@app.cell
def __(mean_scores_per_doc_df, parse_dir):
    processed_files_table = parse_dir.documents_df[["file_name", "num_tokens"]]
    processed_files_table["num_pages"] = parse_dir.documents_df["metadata"].apply(lambda x: x["xmpTPg:NPages"])

    processed_files_table = processed_files_table.join(mean_scores_per_doc_df)
    return processed_files_table,


@app.cell
def __(mo, np, parse_dir, pd, processed_files_table):
    mo.vstack([
        mo.md("## 1. Documents overview"),
        mo.hstack([
            mo.vstack([
                mo.md(f"Total documents: {len(parse_dir.documents_df)}"),
                mo.stat(
                    value=f"{np.mean(parse_dir.results_df['score_out_of_10']):.1f}", 
                    label="Average score",
                    bordered=True
                )
            ]),
            mo.vstack([
                mo.md("List of files:"),
                mo.ui.tabs({
                "Processed files": mo.ui.table(processed_files_table[["file_name", "num_pages", "mean_score"]]),
                "Skipped files": mo.ui.table(pd.DataFrame(parse_dir.skip_files))
                    })
            ])
            
        ])
    ])
    return


@app.cell
def __(id, logging, parse_dir, pd):
    # Create questions dataframe with mean score
    questions = pd.DataFrame(parse_dir.questions["questions"])[["key", "question_text"]]
    questions.set_index("key", inplace=True)

    mean_scores_per_q = []

    for key, _ in questions.iterrows():
        try:
            mean_scores_per_q.append({
                "key": key,
                "mean_score": parse_dir.results_df.loc[parse_dir.results_df["key"] == key]["score_out_of_10"].mean()
            })
        except KeyError:
            logging.info(f"No scores for {id}")

    mean_scores_per_q_df = pd.DataFrame(mean_scores_per_q)
    mean_scores_per_q_df.set_index("key", inplace=True)
    questions_df = questions.join(mean_scores_per_q_df)
    return (
        key,
        mean_scores_per_q,
        mean_scores_per_q_df,
        questions,
        questions_df,
    )


@app.cell
def __(np, plt, questions_df):
    def create_questions_score_plot():
        fig, ax = plt.subplots(tight_layout=True)
        y_pos = np.arange(len(questions_df))
        ax.barh(y_pos, questions_df["mean_score"])
        ax.set_yticks(y_pos, labels=questions_df.index)
        ax.invert_yaxis()

        return fig

    questions_score_plot = create_questions_score_plot()
    return create_questions_score_plot, questions_score_plot


@app.cell
def __(mo, questions_df):
    selected_question = mo.ui.dropdown(questions_df["question_text"], allow_select_none=False, value="Has the ESOS report been produced before the compliance date for the relevant compliance period?")
    return selected_question,


@app.cell
def __(parse_dir, plt, selected_question):
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
    question_histogram = create_histogram(parse_dir.results_df, selected_question.value)
    return create_histogram, question_histogram


@app.cell
def __(mo, parse_dir, question_histogram, questions_df, selected_question):
    # Question selector view
    selected_question_id = questions_df[questions_df['question_text'] == selected_question.value].index[0]
    question_selector_view = mo.vstack([
        mo.md("### View stats for a single question:"),
        selected_question,
        mo.hstack([
            mo.vstack([
                mo.stat(f"{questions_df[questions_df['question_text'] == selected_question.value]['mean_score'].iloc[0]:.1f}", bordered=True, label="Average score"),
                mo.md("### Distribution of scores"),
                question_histogram
            ]),
            mo.vstack([
                mo.md("### List of scores for this question"),
                mo.ui.table(parse_dir.results_df.loc[parse_dir.results_df["key"] == selected_question_id][["score_out_of_10", "rationale"]])
            ])
            
        ])
    ])

    return question_selector_view, selected_question_id


@app.cell
def __(mo):
    mo.md("---")
    return


@app.cell
def __(mo, question_selector_view, questions_df, questions_score_plot):
    mo.vstack([
        mo.md("## 2. Question detail view"),
        mo.hstack([
            mo.vstack([
                mo.md("### Average score by question"),
                questions_score_plot,
            ]),
            mo.vstack([
                mo.md("### List of questions"),
                mo.ui.table(questions_df[["question_text", "mean_score"]])
            ])
            
        ]),
        question_selector_view
    ], )
    return


@app.cell
def __(mo, processed_files_table):
    selected_doc = mo.ui.dropdown(processed_files_table["file_name"], allow_select_none=False, value="(ESOS 01) Harsco Steelphalt Site Energy Assessment 2019 V1.0.pdf")
    return selected_doc,


@app.cell
def __(parse_dir, processed_files_table, selected_doc):
    selected_doc_id = processed_files_table.loc[processed_files_table["file_name"] == selected_doc.value].index[0]
    doc_results = parse_dir.results_df.loc[selected_doc_id]

    return doc_results, selected_doc_id


@app.cell
def __(mo, questions_df):
    selected_doc_question = mo.ui.dropdown(questions_df["question_text"], allow_select_none=False, value="Has the ESOS report been produced before the compliance date for the relevant compliance period?")
    return selected_doc_question,


@app.cell
def __(doc_results, mo, questions_df, selected_doc_question):
    selected_doc_question_id = questions_df[questions_df['question_text'] == selected_doc_question.value].index[0]

    doc_question_view = mo.vstack([
        selected_doc_question,
        mo.stat(f"{doc_results[doc_results['key'] == selected_doc_question_id]['score_out_of_10'].iloc[0]}", bordered=True, label="Question score"),
        mo.ui.table(doc_results[doc_results['key'] == selected_doc_question_id][['rationale', 'quotes']])
    ])
    return doc_question_view, selected_doc_question_id


@app.cell
def __(mo):
    mo.md("---")
    return


@app.cell
def __(
    doc_question_view,
    mo,
    parse_dir,
    processed_files_table,
    selected_doc,
    selected_doc_id,
):
    # Document detail view
    mo.vstack([
        mo.md("## 3. Document detail view"),
        mo.md("### Select a document to view scores:"),
        selected_doc,
        mo.hstack([
            mo.stat(f"{processed_files_table.loc[selected_doc_id]['mean_score']:1f}", bordered=True, label="Average score"),
            mo.stat(f"{processed_files_table.loc[selected_doc_id]['num_pages']}", bordered=True, label="Pages"),
        ]),

        mo.hstack([
            mo.vstack([
                mo.md("### Question scores for this document:"),
                mo.ui.table(parse_dir.results_df.loc[selected_doc_id][["question_text", "score_out_of_10"]])
            ]),
            mo.vstack([
                mo.md("### View document performance for a question"),
                doc_question_view
            ])
        ])
    ])
    return


@app.cell
def __(mo):
    show_method = mo.ui.switch(label="Show methodology")
    show_method
    return show_method,


@app.cell
def __(mo, show_method):
    if show_method.value:
        method = mo.vstack([
            mo.md(open("docs/method.md").read())
        ])
    else:
        method = mo.vstack(
            [mo.md("*Methodology hidden*")]
        )
    return method,


@app.cell
def __(method):
    method
    return


if __name__ == "__main__":
    app.run()
