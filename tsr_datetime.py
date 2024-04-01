""" This takes a standardized OASIS OATI transmission reservation summary dataframe and plots the transmission
rights over time."""
import pandas as pd
import plotly
from plotly import graph_objects as go
import os


def plot_tsr_over_time(df, pod, customer='', directory=''):
    """Plot the Transmission Service over time for each point of delivery"""
    tsr_df = df[df['POD'] == pod].copy()
    if not customer:
        customer_list = tsr_df.Customer.unique()
    else:
        customer_list = [customer]
    tsr_df = tsr_df[tsr_df.Customer.isin(customer_list)]

    def expand_datetime(df):
        """Expands the dataframe to include rows for each year between Start Date and Stop Date."""
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

    tsr_df = expand_datetime(tsr_df.copy())
    for c in customer_list:
        data = []
        first_mask = tsr_df['Customer'] == c
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
            title = f'Total MW Transmission Rights by Date for {c} to {pod}'
            layout = go.Layout(title=title, xaxis_title='Date', yaxis_title='MW')
            # Create the figure
            fig = go.Figure(data=data, layout=layout)
            # Display the plot
            plotly.offline.plot(fig, filename=os.path.join(directory, f'{title}.html'), auto_open=False)

