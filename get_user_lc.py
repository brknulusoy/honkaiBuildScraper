import pandas as pd

def get_excel_df():
    # Get excell file as input and put it into a dataframe
    df = pd.read_excel("light_cones.xlsx")
    return df