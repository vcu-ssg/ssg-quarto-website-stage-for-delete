"""
Main entry code for the cli
"""
import os
import sys
import json
import gspread
import loguru
import click
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
from IPython.display import Markdown
from tabulate import tabulate

# define scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# create credentials object
credential_file = os.path.join(os.path.expanduser("~"), ".gsecrets", "gsheets-credentials.json")
if not os.path.isfile( credential_file ):
  print("Missing credential file:",credential_file)
  sys.exit()

creds = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)
client = gspread.authorize(creds)

@click.group
@click.pass_context
def cli(ctx):
    pass

@cli.command
@click.pass_context
def bios(ctx):
    # Course data: open the google sheet and tab
    spreadsheet_key = "19I04Ljy8X8f1mqhpEh5-XRmj4iIEv1huaijqy60a42E"
    worksheet_name = "Biographies"
    sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data.pop(0)
    bios_df = pd.DataFrame(data, columns=headers)
    bios_filepath = 'bios.xlsx'
    bios_df.to_excel(bios_filepath, index=False)
    # build list of users to create pages
    list = {}
    for i,bio in bios_df.iterrows():
        item = {"item_name":bio["item_name"],"item_description":bio["item_description"]}
        category = {"cat_name":bio["item_name"],"items":[]}
        b = {"person_name":bio["person_name"],"person_eid":bio["person_eid"],"categories":{}}
        if bio["person_eid"] not in list.keys():
            list[bio["person_eid"]] = b
        if category["cat_name"] not in list[bio["person_eid"]]["categories"].keys():
            list[bio["person_eid"]]["categories"][category["cat_name"]] = category
        list[bio["person_eid"]]["categories"][category["cat_name"]]["items"].append( item )

    destination_folder = "../website/about/"
    for name in list.keys():

        filename = f'{destination_folder}{name}.qmd'
        with open(filename, 'w',encoding="utf-8") as file:
            file.write(f"""---
title: "{list[name]["person_name"]}"
date: last-modified
format:
  html:
    toc: false
---
""")
            if "bio" in list[name]["categories"].keys():
                for item in list[name]["categories"]["bio"]["items"]:
                    file.write(f"\n{item['item_description']}\n")

            if "education" in list[name]["categories"].keys():
                file.write("\n## Education\n\n")
                for item in list[name]["categories"]["education"]["items"]:
                    file.write(f"* {item['item_description']}\n")

            if "experience" in list[name]["categories"].keys():
                file.write("\n## Experience\n\n")
                for item in list[name]["categories"]["experience"]["items"]:
                    file.write(f"* {item['item_description']}\n")


        file.close()


if __name__=="__main__":
    cli()

