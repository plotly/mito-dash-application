import pandas as pd
import dash_mantine_components as dmc
from dash import Dash, html, callback, Input, Output, dcc, dash_table, State
from dash.exceptions import PreventUpdate
import base64
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback, activate_mito
import plotly.express as px

from utils import get_correlations, get_date_and_matching_columns, get_graphs

app = Dash(__name__)
activate_mito(app)

app.layout = dmc.MantineProvider(
    [
        dmc.Header(
            height="10%",
            children=[
                html.Div(
                    [
                        html.Div(
                            [
                                dmc.Title(
                                    "Mito for Dash",
                                    order=1,
                                    style={
                                        "text-align": "left",
                                        "margin-bottom": "10px",
                                        "color": "#333",
                                    },
                                ),
                                dmc.Title(
                                    "Portfolio Analysis Example",
                                    order=3,
                                    style={
                                        "text-align": "left",
                                        "color": "#555",
                                        "font-weight": "normal",
                                    },
                                ),
                            ],
                            style={"flex": "1", "padding": "10px"},
                        ),
                        html.Div(
                            [
                                dcc.Upload(
                                    id="upload-data",
                                    children=[
                                        html.I(
                                            className="fa fa-upload"
                                        ),  # Using Font Awesome icon
                                        html.Span("Upload files"),
                                    ],
                                    style={
                                        "display": "inline-block",
                                        "width": "auto",
                                        "height": "40px",
                                        "lineHeight": "40px",
                                        "borderWidth": "1px",
                                        "borderStyle": "solid",
                                        "borderColor": "#ccc",
                                        "borderRadius": "5px",
                                        "textAlign": "center",
                                        "margin": "10px",
                                        "padding": "0 15px",
                                        "cursor": "pointer",
                                        "background-color": "#f7f7f7",
                                    },
                                    # Allow multiple files to be uploaded
                                    multiple=True,
                                ),
                            ],
                            style={"text-align": "right", "padding": "10px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "space-between",
                        "align-items": "center",
                        "background-color": "#f9f9f9",
                        "box-shadow": "0px 2px 5px rgba(0, 0, 0, 0.1)",
                        "border-bottom": "1px solid #eee",
                    },
                ),
            ],
            style={"backgroundColor": "#f6e5ff"},
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
                    ### Using this app
                    1.  Use the **Upload Files** button in the top right to import both the Tesla Stock and S&P500 data.
                    2.  Use Mito to convert the **Date columns** in both sheets to a datetime, using the **Dtype dropdown** in the Mito toolbar.
                    3.  Click **Dataframes > Merge dataframes** to join the data together.
                    4.  Take a look at the graphs generated below.
                    5.  Explore the data in the spreadsheet (maybe applying a filter or two) and see how the graphs change.
                    """
                ),  
            ],
            style={
                "padding": "10px",
                "margin": "auto",
                "maxWidth": "80%",
                "font-size": "1.2em",
            }
        ),
        
        html.Div(
            [
                Spreadsheet(id={'type': 'spreadsheet', 'id': 'sheet'}, import_folder='data'),
            ],
            style={"height": "80%", "maxWidth": "80%", "margin": "auto", "padding": "10px"},
        ),
        dmc.Center(
            id="data_analysis_title",
            children=[],
            style={
                "padding": "10px"
            },  # Add some padding around the Center for better spacing
        ),
        html.Div(
            [
                html.H3(
                    "Data Analysis",
                    style={
                        "text-align": "center",
                        "margin-top": "20px",
                        "color": "#333",
                        "width": "100%",
                    },
                ),
                html.Div(
                    id="correlation-table",
                    style={
                        "text-align": "center",
                        "margin-top": "20px",
                        "color": "#333",
                        "width": "100%",
                    }
                )
            ],
            style={
                "margin-top": "20px",
                "padding": "10px",
                "background-color": "#f9f9f9",
                "box-shadow": "0px 2px 5px rgba(0, 0, 0, 0.1)",
                "border-radius": "5px",
                "width": "100%",
            },  
        ),
        html.Div(id="graph-output"),
    ]
)

@callback(
    Output({'type': 'spreadsheet', 'id': 'sheet'}, "data"), 
    [Input("upload-data", "contents")], 
)
def update_spreadsheet_data(uploaded_contents):
    if uploaded_contents is None:
        raise PreventUpdate

    csv_data = [
        base64.b64decode(contents.split(",")[1]).decode("utf-8")
        for contents in uploaded_contents
    ]
    
    return csv_data

@mito_callback(
    Output("graph-output", "children"),
    Output("correlation-table", "children"),
    Input({'type': 'spreadsheet', 'id': 'sheet'}, "spreadsheet_result"),
)
def update_outputs(spreadsheet_result):
    if spreadsheet_result is None or len(spreadsheet_result.dfs()) == 0:
        raise PreventUpdate
    
    if len(spreadsheet_result.dfs()) == 0:
        raise PreventUpdate
    
    if len(spreadsheet_result.dfs()) < 3:
        raise PreventUpdate


    # We graph the final dataset in the spreadsheet
    final_df = spreadsheet_result.dfs()[-1]

    # Build some figures to display
    date_column, matching_columns = get_date_and_matching_columns(final_df)
    figures = get_graphs(final_df, date_column, matching_columns)

    # Build the correlation table
    correlations = get_correlations(final_df, matching_columns)

    return html.Div(
        children=[
            dmc.Title("Stock Comparison Graphs"),
            html.Div(
                children=[dcc.Graph(figure=fig) for fig in figures],
                style={
                    "display": "grid",
                    "grid-template-columns": "1fr 1fr",
                    "grid-gap": "20px",
                }
            ),
        ],
        style={
            "display": "flex",
            "flex-direction": "column",
            "justify-content": "center",
            "text-align": "center",
        }
    ), dash_table.DataTable(
        data=correlations,
        style_cell={"textAlign": "center"},
    ),

if __name__ == "__main__":
    app.run_server(debug=True)