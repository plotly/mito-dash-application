import dash_mantine_components as dmc
from dash import Dash, html, callback, Input, Output, dcc, dash_table
import base64
import pandas as pd
import dash_table
import dash_pivottable

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
                                        "text-align": "left",
                                        "margin-bottom": "10px",
                                        "color": "#333",
                                    },
                                ),
                                dmc.Title(
                                    "Portfolio Analysis Example - without Mito",
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
                dcc.Markdown(
                    """
                    ### Using this app
                    1.  Click the "Upload Files" button in the upper right corner of this app.
                    2.  Upload the Tesla Stock and S&P500 data linked above from your Downloads folder.
                    3.  When uploaded, scroll below to see automatically generated graphs and a correlation table. **Note** - _this will only work for these two datasets_.
                    """
                ),
            ],
            style={
                "padding": "10px",
                "margin": "auto",
                "maxWidth": "80%",
                "font-size": "1.2em",
            },
        ),
        dmc.Center(
            [
                html.Div(
                    className="pivot-container",
                    children=[
                        dash_pivottable.PivotTable(
                            id="pivot-table",
                            # ... (keep the rest of your settings here)
                        ),
                    ],
                ),
            ]
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


def empty_dataframe_list():
    return [["No Data"]]


def empty_div():
    return html.Div("")


@callback(
    Output("graph-output", "children"),
    Output("pivot-table", "data"),
    Output("data_analysis_title", "children"),
    Input("upload-data", "contents"),
)
def update_output(uploaded_contents):
    if uploaded_contents is None or len(uploaded_contents) != 2:
        return (
            empty_div(),
            empty_dataframe_list(),
            html.Div(),
        )

    dataframes = []
    for content in uploaded_contents:
        content_type, content_string = content.split(",")
        decoded = base64.b64decode(content_string)

        try:
            # Try UTF-8 decoding first
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        except UnicodeDecodeError:
            try:
                # If UTF-8 fails, try ISO-8859-1 decoding
                df = pd.read_csv(io.StringIO(decoded.decode("ISO-8859-1")))
            except:
                return (
                    empty_div(),
                    empty_dataframe_list(),
                    html.Div(),
                )

        dataframes.append(df)

    # Define column sets for each schema
    schema1_columns = set(
        ["Date", "open_sp", "high_sp", "low_sp", "close_sp", "volume_sp"]
    )
    schema2_columns = set(
        ["Date", "close_tsla", "volume_tsla", "open_tsla", "high_tsla", "low_tsla"]
    )

    # Identify dataframes based on columns
    if set(dataframes[0].columns) == schema1_columns:
        df_sp = dataframes[0]
        df_tsla = dataframes[1]
    elif set(dataframes[0].columns) == schema2_columns:
        df_sp = dataframes[1]
        df_tsla = dataframes[0]
    else:
        return (
            empty_div(),
            empty_dataframe_list(),
            html.Div(),
        )

    # Convert date columns (for safety, in case they're not in datetime format)
    df_sp["Date"] = pd.to_datetime(df_sp["Date"])
    df_tsla["Date"] = pd.to_datetime(df_tsla["Date"])

    # Merge using an outer join on the Date column
    merged_df = df_sp.merge(df_tsla, on="Date", how="outer")
    cols_to_convert = [col for col in merged_df.columns if col != "Date"]
    merged_df[cols_to_convert] = merged_df[cols_to_convert].astype(float)
    merged_df_list = [merged_df.columns.tolist()] + merged_df.values.tolist()

    if not merged_df.empty:
        # Time Series Plot for Closing Prices
        fig1 = px.line(
            merged_df,
            x="Date",
            y="close_sp",
            labels={"close_sp": "S&P Close Price"},
            title="Close Price Comparison",
        )
        fig1.add_scatter(
            x=merged_df["Date"],
            y=merged_df["close_tsla"],
            mode="lines",
            name="TSLA Close Price",
            yaxis="y2",
        )
        fig1.update_layout(
            yaxis=dict(title="S&P Close Price"),
            yaxis2=dict(title="TSLA Close Price", overlaying="y", side="right"),
        )

        # Volume Bar Chart
        fig2 = px.line(
            merged_df,
            x="Date",
            y="volume_sp",
            labels={"volume_sp": "S&P Volume"},
            title="Trading Volume Comparison",
        )

        # Add TSLA volume with secondary y-axis
        fig2.add_scatter(
            x=merged_df["Date"],
            y=merged_df["volume_tsla"],
            mode="lines",
            name="TSLA Volume",
            yaxis="y2",
        )

        # Update layout to specify y-axis properties
        fig2.update_layout(
            yaxis=dict(title="S&P Volume"),
            yaxis2=dict(title="TSLA Volume", overlaying="y", side="right"),
        )

        # Moving Average Plot
        merged_df["S&P_MA30"] = merged_df["close_sp"].rolling(window=30).mean()
        merged_df["TSLA_MA30"] = merged_df["close_tsla"].rolling(window=30).mean()
        fig3 = px.line(
            merged_df,
            x="Date",
            y="S&P_MA30",
            labels={"S&P_MA30": "S&P 30-Day MA"},
            title="30-Day Moving Average Comparison",
        )

        fig3.add_scatter(
            x=merged_df["Date"],
            y=merged_df["TSLA_MA30"],
            mode="lines",
            name="TSLA 30-Day MA",
            yaxis="y2",
        )

        fig3.update_layout(
            yaxis=dict(title="S&P 30-Day Moving Average"),
            yaxis2=dict(
                title="TSLA 30-Day Moving Average", overlaying="y", side="right"
            ),
        )
        # Compute the correlation coefficients
        correlations = {
            "Metric": ["Open", "Close", "Volume"],
            "Pearson Correlation": [
                merged_df["open_sp"].corr(merged_df["open_tsla"]),
                merged_df["close_sp"].corr(merged_df["close_tsla"]),
                merged_df["volume_sp"].corr(merged_df["volume_tsla"]),
            ],
        }

        correlations_df = pd.DataFrame(correlations)

        layout = [
            dash_table.DataTable(
                data=correlations_df.to_dict("records"),
                style_cell={"textAlign": "center"},
            ),
            dmc.Group(
                children=[dcc.Graph(figure=fig1), dcc.Graph(figure=fig2)],
                position="center",
                grow=True,
            ),
            dcc.Graph(figure=fig3),
        ]
    else:
        layout = []

    return (
        layout,
        merged_df_list,
        html.Div(  # Add a container for the section below the pivot table
            className="data-table-container",
            children=[
                # Here you can add elements for the data table and related items
                html.H3(
                    "Data Analysis",
                    style={
                        "text-align": "center",
                        "margin-top": "20px",
                        "color": "#333",
                        "width": "100%",
                    },
                ),
                # Here is where you'd add the 'data_table' and any other elements
                # Example:
                # dash_table.DataTable(id='data_table')
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
    )


if __name__ == "__main__":
    app.run_server(debug=True)
