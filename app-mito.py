import dash_mantine_components as dmc
from dash import Dash, html, callback, Input, Output, dcc, dash_table
from dash.exceptions import PreventUpdate
import base64
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback

import io
import plotly.express as px

app = Dash(__name__)

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
                                        "text-align": "center",
                                        "margin-bottom": "10px",
                                        "color": "#333",
                                    },
                                ),
                                dmc.Title(
                                    "Portfolio Analysis Example",
                                    order=3,
                                    style={
                                        "text-align": "center",
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
                                        html.Span(" Upload files"),
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
                Spreadsheet(id='spreadsheet'),
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
        html.Div(id="graph-output"),  # Container for the graphs
        dash_table.DataTable(id="correlation-table"),
    ]
)

@callback(
    Output("spreadsheet", "data"),
    Input("upload-data", "contents"),
)
def update_output(uploaded_contents):
    if uploaded_contents is None:
        raise PreventUpdate
    
    csv_data = [
        base64.b64decode(contents.split(",")[1]).decode("utf-8")
        for contents in uploaded_contents
    ]
    
    return csv_data

@mito_callback(
    Output("graph-output", "children"),
    Input("spreadsheet", "spreadsheet_result"),
)
def update_graphs(spreadsheet_result):
    if spreadsheet_result is None or len(spreadsheet_result.dfs()) == 0:
        raise PreventUpdate

    # We graph the final dataset in the spreadsheet
    final_df = spreadsheet_result.dfs()[-1]

    # First, we find the date column. If there isn't one, we can't graph it, so we bail on it
    date_columns = [col for col in final_df.columns if "date" in col.lower()]

    if len(date_columns) == 0:
        raise PreventUpdate
    
    # Make a time series plot for closing prices, based on the first date column
    fig1 = px.line(
        final_df,
        x=date_columns[0],
        y=[col for col in final_df.columns if "close" in col.lower()],
        title="Close Price Comparison",
    )

    # Make a bar chart for volume, based on the first date column
    fig2 = px.bar(
        final_df,
        x=date_columns[0],
        y=[col for col in final_df.columns if "volume" in col.lower()],
        title="Trading Volume Comparison",
    )
    
    return [
        dmc.Group(
            children=[dcc.Graph(figure=fig1), dcc.Graph(figure=fig2)],
            position="center",
            grow=True,
        ),
    ]

if __name__ == "__main__":
    app.run_server(debug=True)
