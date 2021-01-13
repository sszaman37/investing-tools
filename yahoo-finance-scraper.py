import sys
import re
import json
import csv
from io import StringIO
from bs4 import BeautifulSoup
import requests


# url templates
url_stats = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'
url_profile = 'https://finance.yahoo.com/quote/{}/profile?p={}'
url_financials = 'https://finance.yahoo.com/quote/{}/financials?p={}'

# Stock ticker
stock = ''

# Output type: is = (income statement), cf = (cashflows), bs = (balance sheet)
report_type = '' 

# Period: a = annual, q = quarterly
period = ''

if len(sys.argv) != 4:
    print("Not enough args")
    sys.exit(1)

stock = sys.argv[1]
report_type = sys.argv[2]
period = sys.argv[3]

# make requests
response = requests.get(url_financials.format(stock, stock))
soup = BeautifulSoup(response.text, 'html.parser')
pattern = re.compile(r'\s--\sData\s--\s')
script_data = soup.find('script', text=pattern).contents[0]

# find the starting position of the json string
start = script_data.find("context")-2

# slice the json string
json_data = json.loads(script_data[start:-12])

json_data['context'].keys()

json_data['context']['dispatcher']['stores']['QuoteSummaryStore'].keys()

# income statement
annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory']
quarterly_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistoryQuarterly']['incomeStatementHistory']

# cash flow statement
annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements']
quarterly_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistoryQuarterly']['cashflowStatements']

# balance sheet
annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements']
quarterly_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistoryQuarterly']['balanceSheetStatements']


# example of income statmement accounts
# print(annual_is[0])

# annual_is[0]['operatingIncome']
output_statements = []
chosen_statements = []
if report_type == 'is':
    if period == 'a':
        chosen_statements = annual_is
        print('annual_is')
    else:
        chosen_statements = quarterly_is
        print('quarterly_is')

if report_type == 'cf':
    if period == 'a':
        chosen_statements = annual_cf
        print('annual_cf')
    else:
        chosen_statements = quarterly_cf
        print('quarterly_cf')

if report_type == 'bs':
    if period == 'a':
        chosen_statements = annual_bs
        print('annual_bs')
    else:
        chosen_statements = quarterly_bs
        print('quarterly_bs')


# consolidate annual
for s in chosen_statements:
    statement = {}
    for key, val in s.items():
        try:
            # {'raw': 2658000000, 'fmt': '2.66B', 'longFmt': '2,658,000,000'}
            statement[key] = val['raw'] 
        except TypeError:
            continue
        except KeyError:
            continue
    output_statements.append(statement)
# json.dumps(json_object, indent=2)
print(json.dumps(output_statements[0], indent=2))

