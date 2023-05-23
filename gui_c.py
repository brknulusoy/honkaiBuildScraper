import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from functools import partial
from bs4 import BeautifulSoup
import requests
from get_lc_db import get_lc_db
import pandas as pd
from get_user_lc import get_excel_df

def get_data_relics(build_data):
    relics = []
    descriptions = []
    for col in build_data:

        # Get all acordion-items
        build_relics_accordion_item = col.find_all("div", class_="accordion-item")

        # Print the text and span class="cone-priority" for each accordion-item and catch if there are any errors
        for accordion_item in build_relics_accordion_item:
            try:
                # If first character of h2 is a digit, remove it and print the #text information
                if accordion_item.h2.get_text()[0].isdigit():

                    relic_set = accordion_item.find("span",
                                                    class_="cone-priority").get_text() + " " + accordion_item.h2.get_text()[
                                                                                               1:]
                    relic_desc = accordion_item.find("div", class_="accordion-body").get_text()

                    relics.append(relic_set)
                    descriptions.append(relic_desc)

                    # Add
                else:

                    relic_set = accordion_item.find("span",
                                                    class_="cone-priority").get_text() + " " + accordion_item.h2.get_text()
                    relic_desc = accordion_item.find("div", class_="accordion-body").get_text()

                    relics.append(relic_set)
                    descriptions.append(relic_desc)

            except AttributeError:

                relic_set = accordion_item.h2.get_text()
                relic_desc = accordion_item.find("div", class_="accordion-body").get_text()

                relics.append(relic_set)
                descriptions.append(relic_desc)

    return relics, descriptions


def get_data_stats(build_stats):
    # Get all box #Text from div class="box" inside div class="build-stats"
    build_stats_box = build_stats.find_all("div", class_="box")

    # Separate the first 4 elements of build_stats_box into a list relic_stats
    relic_stats = [box.get_text() for box in build_stats_box[:4]]
    relic_sub_stats = [box.get_text() for box in build_stats_box[4:5]]
    trace_prio_stats = [box.get_text() for box in build_stats_box[5:6]]

    return relic_stats, relic_sub_stats, trace_prio_stats
def program_call(character_name):
    url = "https://www.prydwen.gg/star-rail/characters/{}".format(character_name)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # Get info from div class="section-build"
    build = soup.find("div", class_="section-build")

    # Separate the build into 3 parts: build-cones, build-relics, build-stats
    build_relics = build.find("div", class_="build-relics")
    build_stats = build.find("div", class_="build-stats")

    # ------------------- Build Stats -------------------
    relic_stats, relic_sub_stats, trace_prio_stats = get_data_stats(build_stats)

    # ------------------- Build Relics and Cones -------------------

    # Separate relics row row-cols-xxl-2 row-cols-xl-2 row-cols-1 into 2 columns
    build_relics_col = build_relics.find_all("div", class_="col")
    build_cones = build.find("div", class_="build-cones")

    relics, desc = get_data_relics(build_relics_col)
    lightcones, desc2 = get_data_relics(build_cones)

    # ------------------- pandas df -------------------
    # Turn lightcones into a pandas dataframe
    lc_df = pd.DataFrame({"Light Cones": lightcones, "Have it? (Yes or No)": "", "Description": desc2})
    # Format the lightcones column to remove the first character (the priority number) and the brackets with S1, S2, S3
    lc_df["Light Cones"] = lc_df["Light Cones"].str[2:].str.replace(r"\(.*\)", "", regex=True)

    # Turn relics into a pandas dataframe
    relics_df = pd.DataFrame({"Relics": relics, "Description": desc})

    # Turn stats into separate pandas dataframes
    stats_df = pd.DataFrame({"Relic Stats": relic_stats})
    sub_stats_df = pd.DataFrame({"Relic Sub Stats": relic_sub_stats})
    trace_prio_df = pd.DataFrame({"Trace Prio": trace_prio_stats})

    # ------------------- Compare lightcones -------------------
    # Get the users lightcones
    lc_user = get_excel_df()
    # Show entire dataframe
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    # Copy the value of the "Have it? (Yes or No)" column from lc_user to lc_df if their lightcone name matches
    lc_df["Have it? (Yes or No)"] = lc_df["Light Cones"].map(lc_user.set_index("Light Cones")["Have it? (Yes or No)"])
    # print(lc_df)

    display_dataframes(lc_df, relics_df,character_name, stats_df, sub_stats_df, trace_prio_df)
def motion_handler(tree, event):
    f = Font(font='TkDefaultFont')
    # A helper function that will wrap a given value based on column width
    def adjust_newlines(val, width, pad=0):
        if not isinstance(val, str):
            return val
        else:
            words = val.split()
            lines = [[],]
            for word in words:
                line = lines[-1] + [word,]
                if f.measure(' '.join(line)) < (width - pad):
                    lines[-1].append(word)
                else:
                    lines[-1] = ' '.join(lines[-1])
                    lines.append([word,])

            if isinstance(lines[-1], list):
                lines[-1] = ' '.join(lines[-1])

            return '\n'.join(lines)

    if (event is None) or (tree.identify_region(event.x, event.y) == "separator"):
        # You may be able to use this to only adjust the two columns that you care about
        # print(tree.identify_column(event.x))

        col_widths = [tree.column(cid)['width'] for cid in tree['columns']]

        for iid in tree.get_children():
            new_vals = []
            for (v,w) in zip(tree.item(iid)['values'], col_widths):
                new_vals.append(adjust_newlines(v, 600))
            tree.item(iid, values=new_vals)
def relaunch(root,character_name):
    root.destroy()  # Destroy the existing window
    program_call(character_name)  # Recreate the GUI
def display_dataframes(df1, df2, character_name, relic_stats, relic_sub_stats, trace_prio_stats):
    root = tk.Tk()
    root.geometry("1200x730")
    root.title("Dataframe Display")

    # Create a notebook widget with two tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Create the first tab for the first dataframe
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Ligt Cones")

    # Create a treeview widget for the first dataframe
    treeview1 = ttk.Treeview(tab1, show="headings")  # Set show="headings" to hide the empty column
    s = ttk.Style()
    s.configure('Treeview', rowheight=60)

    #Change font size of treeview columns
    s.configure('Treeview', font=('Calibri', 11, "bold"))
    s.configure('Treeview.Heading', font=('Calibri', 11, "bold"))

    treeview1.pack(fill=tk.X, expand=True)

    # Configure the treeview column names
    treeview1["columns"] = list(df1.columns)
    for column in df1.columns:
        treeview1.heading(column, text=column)

    max_width_lc = 0
    # Insert the data rows into the treeview
    for _, row in df1.iterrows():
        treeview1.insert("", tk.END, values=list(row))
        # If length of row 0 is greater than max_width_lc, set max_width_lc to length of row 0
        if len(row[0]) > max_width_lc:
            max_width_lc = len(row[0])

    treeview1.column("Light Cones", width=max_width_lc * 7, minwidth=max_width_lc, stretch=tk.NO, anchor=tk.CENTER)

    # Set the column "Have it? (Yes or No)" to the width of the header
    treeview1.column("Have it? (Yes or No)", width=150, minwidth=150, stretch=tk.NO, anchor=tk.CENTER)

    treeview1.bind('<B1-Motion>', partial(motion_handler, treeview1))
    motion_handler(treeview1, None)  # Perform initial wrapping

    # Stretch rows to fit data
    treeview1.pack(fill=tk.BOTH, expand=True)

    # Add button to bottom of tab1 that will call get_lc_db
    button = tk.Button(tab1, text="Get Light Cone Spreadsheet", command=get_lc_db, font=('Calibri', 11, "bold"))
    button.pack(side=tk.BOTTOM, anchor= "w")


    # Add button that calls the relaunch function
    button2 = tk.Button(tab1, text="Update Sheet", command=lambda: relaunch(root, character_name), font=('Calibri', 11, "bold"))
    button2.pack(side=tk.BOTTOM, anchor="center")

    button2.config(height=10, width=30)

    # Create the second tab for the second dataframe
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Relics")

    # Create a treeview widget for the second dataframe
    treeview2 = ttk.Treeview(tab2, show="headings")  # Set show="headings" to hide the empty column
    treeview2.pack(fill=tk.X, expand=True)

    # Configure the treeview column names
    treeview2["columns"] = list(df2.columns)
    for column in df2.columns:
        treeview2.heading(column, text=column)

    max_width_r = 0
    # Insert the data rows into the treeview
    for _, row in df2.iterrows():
        treeview2.insert("", tk.END, values=list(row))
        if len(row[0]) > max_width_r:
            max_width_r = len(row[0])

    # Set the column "Relics" in treeview2 to max_width_r
    treeview2.column("Relics", width=max_width_r * 7, minwidth=max_width_r, stretch=tk.NO, anchor=tk.CENTER)

    treeview2.bind('<B1-Motion>', partial(motion_handler, treeview2))
    motion_handler(treeview2, None)  # Perform initial wrapping

    # Create third tab for relic stats
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Relic Stats")

    # Create a treeview widget for the third dataframe
    treeview3 = ttk.Treeview(tab3, show="headings")  # Set show="headings" to hide the empty column
    treeview3.pack(fill=tk.X, expand=True)

    # Configure the treeview column names
    treeview3["columns"] = list(relic_stats.columns)
    for column in relic_stats.columns:
        treeview3.heading(column, text=column)

    # Add data to treeview3
    for _, row in relic_stats.iterrows():
        treeview3.insert("", tk.END, values=list(row))

    # Create fourth tab for relic sub stats
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="Relic Sub Stats")

    # Create a treeview widget for the fourth dataframe
    treeview4 = ttk.Treeview(tab4, show="headings")  # Set show="headings" to hide the empty column
    treeview4.pack(fill=tk.X, expand=True)

    # Configure the treeview column names
    treeview4["columns"] = list(relic_sub_stats.columns)
    for column in relic_sub_stats.columns:
        treeview4.heading(column, text=column)

    # Add data to treeview4
    for _, row in relic_sub_stats.iterrows():
        treeview4.insert("", tk.END, values=list(row))

    # Create fifth tab for relic sub stats
    tab5 = ttk.Frame(notebook)
    notebook.add(tab5, text="Trace Prio Stats")

    # Create a treeview widget for the fifth dataframe
    treeview5 = ttk.Treeview(tab5, show="headings")  # Set show="headings" to hide the empty column
    treeview5.pack(fill=tk.X, expand=True)

    # Configure the treeview column names
    treeview5["columns"] = list(trace_prio_stats.columns)
    for column in trace_prio_stats.columns:
        treeview5.heading(column, text=column)

    # Add data to treeview5
    for _, row in trace_prio_stats.iterrows():
        treeview5.insert("", tk.END, values=list(row))

    root.mainloop()
