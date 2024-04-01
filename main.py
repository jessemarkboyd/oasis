"""Calling function for tsr_datetime and tsr_network. User selects analysis desired to be performed on the OASIS OATI
transmission summary reports."""
from tkinter import filedialog
import tkinter as tk
import pandas as pd
from advanced_listbox import select_from_listbox
from tsr_datetime import plot_tsr_over_time
from tsr_network import plot_tsr_network

if __name__ == "__main__":
    root = tk.Tk()
    tsr_excel = filedialog.askopenfilename(title='Select the Oasis TSR Report File',
                                           filetypes=[('Excel', '*.xls *.xlsx *.xlsb')])
    root.destroy()
    tsr_df = pd.read_excel(tsr_excel, header=None)
    # Identify the header row
    header_row_idx = None
    for index, row in tsr_df.iterrows():
        if 'Start Time' in row.values:
            header_row_idx = index
            break
    # Adjust the existing dataframe (uncomment the following lines if you prefer this option)
    new_header = tsr_df.iloc[header_row_idx]  # Grab the header row
    tsr_df = tsr_df[header_row_idx + 1:]  # Take the data below the header row
    tsr_df.columns = new_header  # Set the header row as the dataframe header
    tsr_df.reset_index(drop=True, inplace=True)  # Reset the index
    tsr_df.columns = [col.strip() if isinstance(col, str) else col for col in tsr_df.columns]
    tsr_df['POD'] = tsr_df['POD'].fillna(tsr_df['Sink'])
    tsr_df['POR'] = tsr_df['POR'].fillna(tsr_df['Source'])
    # Convert Start Date and Stop Date to datetime format
    tsr_df['Start Time'] = pd.to_datetime(tsr_df['Start Time'], errors='coerce')
    tsr_df['Stop Time'] = pd.to_datetime(tsr_df['Stop Time'], errors='coerce')
    tsr_df.dropna(subset=['Start Time', 'Stop Time'], how='any', axis=0, inplace=True)

    def describe_path(x):
        """Provide a fuller description of the path, including the four columns that specificy the path."""
        if not pd.isna(x['Source']):
            if not pd.isna(x['Sink']):
                return f'{x["POR"]} ({x["Source"]}) -- {x["POD"]} ({x["Source"]})'
        return f'{x["POR"]} -- {x["POD"]}'

    tsr_df['Path'] = tsr_df.apply(lambda x: describe_path(x), axis=1)
    analyses_list = select_from_listbox('What analysis would you like to perform?',
                                        ['Timeline', 'Network'])
    if 'Timeline' in analyses_list:
        # Timeline requires a POD
        for pod in select_from_listbox('Select Point of Delivery', tsr_df['POD'].unique().tolist(), multiple=True):
            plot_tsr_over_time(tsr_df, pod)
    if 'Network' in analyses_list:
        # Network requires a Customer
        customer_list = tsr_df['Customer'].unique().tolist()
        if len(customer_list) > 1:
            customer_list = select_from_listbox('Select Customer', customer_list, multiple=True)
        for customer in customer_list:
            plot_tsr_network(tsr_df, customer)

