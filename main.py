# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from tkinter import filedialog
import tkinter as tk
import openpyxl
import pandas as pd
import plotly
from plotly import graph_objects as go
import os

root = tk.Tk()
tsr_excel = filedialog.askopenfilename(title='Select the Oasis TSR Report File',
                                       filetypes=[('Excel', '*.xls *.xlsx *.xlsb')])
root.destroy()

tsr_df = pd.read_excel(tsr_excel)
for c in tsr_df.columns:
    if len(c.strip()) < len(c):
        tsr_df[c.strip()] = tsr_df[c]
        tsr_df.drop(columns=c, inplace=True)
# Convert Start Date and Stop Date to datetime format
tsr_df['Start Time'] = pd.to_datetime(tsr_df['Start Time'], errors='coerce')
tsr_df['Stop Time'] = pd.to_datetime(tsr_df['Stop Time'], errors='coerce')
tsr_df.dropna(subset=['Start Time', 'Stop Time'], how='any', axis=0, inplace=True)


def describe_path(x):
    if not pd.isna(x['Source']):
        if not pd.isna(x['Sink']):
            return f'{x["POR"]} ({x["Source"]}) -- {x["POD"]} ({x["Source"]})'
    return f'{x["POR"]} -- {x["POD"]}'


tsr_df['Path'] = tsr_df.apply(lambda x: describe_path(x), axis=1)


def g(df):
    """
  Expands the dataframe to include rows for each year between Start Date and Stop Date.

  Args:
      df: A pandas dataframe with columns 'Start Date', 'Stop Date', 'Amount', and 'Name'.

  Returns:
      A pandas dataframe with additional columns 'Year Amount' and 'Year Name'.
  """
    new_df = pd.DataFrame()
    for index, row in df.iterrows():
        start_date = max(row['Start Time'], pd.to_datetime('01/01/2020'), key=lambda x: x)
        end_date = row['Stop Time']
        year_range = pd.date_range(start_date, end_date, freq='Y')
        for date in year_range.date:
            if start_date <= pd.to_datetime(date) <= end_date:
                new_row = row.to_dict()
                new_row['Date'] = date
                new_df = pd.concat([new_df, pd.Series(new_row)], axis=1)
    return new_df.T


tsr_df = g(tsr_df.copy())
for c in tsr_df['Customer'].unique():
    customer_sink_list = tsr_df[tsr_df.Customer == c]['POD'].unique()
    # customer_sink = ['PSEI.SYSTEM', 'BPAT.PGE', 'BPAT.SCL', 'BPAT.TPU'][['PSEM', 'PGEM', 'SCLM', 'TPWP'].index(c)]
    for customer_sink in customer_sink_list:
        if customer_sink == 'PSEI.SYSTEM':
            pass
        data = []
        first_mask = (tsr_df['Customer'] == c) & (tsr_df['POD'] == customer_sink)
        for tp in tsr_df[first_mask].TP.unique():
            second_mask = first_mask & (tsr_df['TP'] == tp)
            for s in tsr_df[second_mask].Service.unique():
                third_mask = second_mask & (tsr_df['Service'] == s)
                for p in tsr_df[third_mask].Path.unique():
                    forth_mask = third_mask & (tsr_df['Path'] == p)
                    area_df = tsr_df[forth_mask]
                    if not area_df.empty:
                        area_df = area_df.groupby(['TP', 'Date'])['MW Grant'].sum().reset_index()
                        trace = go.Scatter(x=area_df['Date'], y=area_df['MW Grant'], name=f'{tp} {p} ({s})',
                                           stackgroup='one', hovertext=f'{tp} {p} ({s})')
                        data.append(trace)
        if data:
            # Create the plot layout
            title = f'Total MW Transmission Rights by Date for {c} to {customer_sink}'
            layout = go.Layout(title=title, xaxis_title='Date', yaxis_title='MW')
            # Create the figure
            fig = go.Figure(data=data, layout=layout)
            # Display the plot
            plotly.offline.plot(fig, filename=os.path.join(os.path.split(tsr_excel)[0], f'{title}.html'),
                                auto_open=False)
