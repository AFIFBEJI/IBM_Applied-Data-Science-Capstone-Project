# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

launch_sites = [*spacex_df['Launch Site'].unique()]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites',
                                         'value': 'ALL'}]
                                        + [{'label': site,
                                        'value': site} for site in launch_sites],
                                    value='ALL',
                                    placeholder="Select a site",
                                    searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={_: f'{_}' for _ in range(0, 10001, 2500)},
                                                value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df.groupby('Launch Site')[['class']].mean()*100
    if entered_site == 'ALL':
        fig = px.pie(
            filtered_df,
            values='class',
            names=spacex_df['Launch Site'].unique(), 
            title='Total Success Lauches By Site')
        return fig    
    
    else:
        # return the outcomes piechart for a selected site
        # Keep observations corresponding to the entered site
        df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Group data by entered site
        row = df['class'].mean()*100
        
        fig = px.pie(
            values=[100-row, row],
            names=df['class'].unique(), 
            title='Total Success Launches for site ' + entered_site
            )
        return fig
        
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_plot(entered_site, payload_range):
    filtered_df = spacex_df[['Payload Mass (kg)', 'class', 'Booster Version Category']]
    filtered_df = filtered_df[
            (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= payload_range[-1])
        ]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites')
        return fig    
    
    else:
        # return the outcomes piechart for a selected site
        # Keep observations corresponding to the entered site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site][['Payload Mass (kg)', 'class', 'Booster Version Category']]
        filtered_df = filtered_df[
            (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= payload_range[-1])
        ]
        
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for ' + entered_site
            )
        
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()