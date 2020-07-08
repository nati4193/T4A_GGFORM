from __future__ import print_function
import gspread
import pandas as pd
import json
import numpy as np
import os
from google.oauth2.service_account import Credentials
'''
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    'client_secret_429565361689-lop25k5deenjr1gj24scntuqsa6im9or.apps.googleusercontent.com.json',
    scopes=scopes
)

gc = gspread.authorize(credentials)

print("The following sheets are available")
for sheet in gc.openall():
    print("{} - {}".format(sheet.title, sheet.id))
'''

gc = gspread.oauth()

sh = gc.open("Example spreadsheet")

print(sh.sheet1.get('A1'))