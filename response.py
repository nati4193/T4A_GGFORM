#Import Library
import re
import pandas as pd
import numpy as np
print("Pandas version", pd.__version__)

url = 'https://docs.google.com/spreadsheets/d/1SN2lYQLvXx6H9FjYAtdPCpT_L0SJzcxfCGmgI7kv_ao/edit#gid=283051997'
class get_response:
    def __init__(self,url):
        self.url = url

    def gsheet2pandas(self):
        e = 'export?format=xlsx&'
        excel_url = self.replace('edit',e)
        print(excel_url)
        df = pd.read_csv(excel_url)
        return df

df1 = get_response.gsheet2pandas(url)


