import dash_mantine_components as dmc
from dash import Dash, html, callback, Input, Output, dcc, dash_table, State
from dash.exceptions import PreventUpdate
import base64
from mitosheet.mito_dash.v1 import Spreadsheet, mito_callback, activate_mito
from utils import get_correlation_df, get_graph_group

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
                    1.  Use the Upload Files button in the top right to import both the Tesla Stock and S&P500 data.
                    2.  Use Mito to convert the Date column in both sheets to a datetime, using the Dtype dropdown in the Mito toolbar.
                    3.  Click Dataframes > Merge dataframes to join the data together.
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
        html.Div(id="graph-output"),  # Container for the graphs
        html.Div(id="moving-average-graph-output"),  # Container for the graphs
    ]
)

@callback(
    Output({'type': 'spreadsheet', 'id': 'sheet'}, "data"), 
    [Input("upload-data", "contents")], 
    [State({'type': 'spreadsheet', 'id': 'sheet'}, "data")]
)
def update_spreadsheet_data(uploaded_contents, data):
    if uploaded_contents is None:
        raise PreventUpdate

    # If the user has already uploaded a file, pass both the original 
    # data and new data to the spreadsheet component 
    all_data = [data] if data is not None else []
    
    csv_data = [
        base64.b64decode(contents.split(",")[1]).decode("utf-8")
        for contents in uploaded_contents
    ]

    all_data.extend(csv_data)
    
    return all_data
    

@mito_callback(
    Output("graph-output", "children"),
    Output("correlation-table", "children"),
    Input({'type': 'spreadsheet', 'id': 'sheet'}, "spreadsheet_result"),
)
def update_outputs(spreadsheet_result):
    if spreadsheet_result is None or len(spreadsheet_result.dfs()) == 0:
        raise PreventUpdate

    # We graph the final dataset in the spreadsheet
    final_df = spreadsheet_result.dfs()[-1]

    # First, we find the date column. If there isn't one, we can't graph it, so we bail on it
    date_columns = [col for col in final_df.columns if "date" in col.lower()]

    if len(date_columns) == 0:
        raise PreventUpdate

    graph_group = get_graph_group(final_df, date_columns)

    correlations_df = get_correlation_df(final_df)
    correlation_table = None 
    
    if correlations_df is not None:
        correlation_table = dash_table.DataTable(
            data=correlations_df.to_dict("records"),
            style_cell={"textAlign": "center"},
        )
        
    return graph_group, correlation_table


if __name__ == "__main__":
    app.run_server(debug=True)
