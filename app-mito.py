import pandas as pd
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
        html.Div(id="graphs-or-error"),  # Container for the graphs, or error message if there is one
        dash_table.DataTable(id="correlation-table"),
    ]
)

@callback(
    Output("spreadsheet", "data"),
    Input("upload-data", "contents"),
)
def update_spreadsheet(uploaded_contents):
    if uploaded_contents is None:
        raise PreventUpdate
    
    csv_data = [
        base64.b64decode(contents.split(",")[1]).decode("utf-8")
        for contents in uploaded_contents
    ]
    
    return csv_data


def get_error_container(error_message):
    return dmc.Group(
        children=[
            dmc.Text(
                error_message,
                style={
                    'color': 'red'
                }
            ),
            dmc.Text(
                'To see a full tutorial on how to use Mito for Dash, click here: https://docs.mito.ai/tutorials/dash'
            )
        ],
        style={
            'display': 'flex',
            'flex-direction': 'column',
            'justify-content': 'center',
        }
    )


@mito_callback(
    Output("graphs-or-error", "children"),
    Input("spreadsheet", "spreadsheet_result"),
)
def update_graphs(spreadsheet_result):
    if spreadsheet_result is None or len(spreadsheet_result.dfs()) == 0:
        raise PreventUpdate
    
    if len(spreadsheet_result.dfs()) == 0:
        return get_error_container(
            "There is no data in your spreadsheet. Use the upload button in the upper left corner to upload to stock datasets to compare."
        )
    
    if len(spreadsheet_result.dfs()) < 3:
        return get_error_container(
            "After importing two stock datasets, you need to merge them together using Dataframes > Merge dataframes. If you are merging on date, make sure to convert the date column to datetime first."
        )

    # We graph the final dataset in the spreadsheet
    final_df = spreadsheet_result.dfs()[-1]

    # First, we find the date column. If there isn't one, we can't graph it, so we bail on it
    date_columns = [col for col in final_df.columns if final_df[col].dtype == "datetime64[ns]"]
    close_columns = [col for col in final_df.columns if "close" in col.lower()]
    volume_columns = [col for col in final_df.columns if "volume" in col.lower()]
    open_columns = [col for col in final_df.columns if "open" in col.lower()]

    if len(date_columns) == 0:
        return get_error_container(
            "There is not datetime column in your dataset. Use Mito to change any date columns to datetime, and then try again."
        )
    
    if len(close_columns) < 2 and len(open_columns) < 2 and len(volume_columns) < 2:
        return get_error_container("There are not enough columns in your dataset to graph. You must have at least two columns named Close, Open, or Volume for comparisons between these stock datasets to be performed")

    date_column = date_columns[0]

    graph_data = {
        'Close Price': close_columns,
        'Open Price': open_columns,
        'Volume': volume_columns,
    }

    figures = []

    # Build graphs for all of the graph data
    for graph_title, columns in graph_data.items():

        first_column = columns[0]
        second_column = columns[1]

        fig = px.line(
            final_df,
            x=date_column,
            y=first_column,
            title=f"{graph_title} Comparison",
        )
        fig.add_scatter(
            x=final_df[date_column],
            y=final_df[second_column],
            mode="lines",
            yaxis="y2",
        )
        fig.update_layout(
            yaxis=dict(title=first_column),
            yaxis2=dict(title=second_column, overlaying="y", side="right"),
        )

        figures.append(fig)

    return [
        dmc.Group(
            children=[dcc.Graph(figure=fig) for fig in figures],
            position="center",
            grow=True,
        ),
    ]

if __name__ == "__main__":
    app.run_server(debug=True)
