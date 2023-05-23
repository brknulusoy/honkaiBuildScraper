from bs4 import BeautifulSoup
import requests
import pandas as pd
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Create window using tkinter


url = "https://www.prydwen.gg/star-rail/light-cones"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# Get all h4 #text from div class="hsr-set-name" inside div class="relic-set-container row row-cols-xxl-2 row-cols-1"
light_cones = soup.find("div", class_="relic-set-container row row-cols-xxl-2 row-cols-1")
# Find all h4 texts inside lightcones and separate them into a list
light_cones = light_cones.find_all("h4")
light_cones = [cone.get_text() for cone in light_cones]

# Export the list into an excell file. First column is the light cone name, second column is a checkbox for the user
# to check if they have it or not.
df = pd.DataFrame({"Light Cones": light_cones})

# Create GUI
root = Tk()
root.title("Build Helper")
root.geometry("1200x730")
root.resizable(True, True)

# Create a tab called "Light Cones" and add it to the notebook
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Light Cones")
tab_control.pack(expand=1, fill="both")

# Create a checkbutton for each light cone in the list
for i in range(len(light_cones)):
    Checkbutton(tab1, text=light_cones[i]).grid(row=i, column=0, sticky=W)
    








root.mainloop()
