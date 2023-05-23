from bs4 import BeautifulSoup
import requests
from get_lc_db import get_lc_db
import pandas as pd
from get_user_lc import get_excel_df
from gui_c import display_dataframes, program_call

if __name__ == '__main__':
    print("Welcome to the Build helper. To exit type 'exit' into the character name field.\n")
    while True:
        try:

            character_name = input("Enter your character name: ").lower()
            if character_name == "exit":
                break
            else:
                program_call(character_name)
        except AttributeError:
            print("Character not found. Please try again.")




