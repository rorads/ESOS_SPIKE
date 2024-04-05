import pandas as pd


def find_in_dataframe(dataframe, **kwargs):
    condition = True
    for column_name, value in kwargs.items():
        condition = condition & (dataframe[column_name] == value)

    return dataframe.loc[condition]
