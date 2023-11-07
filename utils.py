import pandas as pd
import plotly.express as px
from dash import dcc, html
import dash_mantine_components as dmc


def get_correlation_df(df):

    columns = list(df.columns)

    # Check if all required columns exist before creating matrix
    if not all([col in columns for col in [ "open_sp", "close_sp", "volume_sp", "open_tsla", "close_tsla", "volume_tsla"]]):
        return None

    correlations =  {
        "Metric": ["Open", "Close", "Volume"],
        "Pearson Correlation": [
            df["open_sp"].corr(df["open_tsla"]),
            df["close_sp"].corr(df["close_tsla"]),
            df["volume_sp"].corr(df["volume_tsla"]),
        ]
    }

    correlations_df = pd.DataFrame(correlations)
    return correlations_df


def get_side_by_side_graphs(df, date_columns):
    # Make a time series plot for closing prices, based on the first date column
    fig1 = px.line(
        df,
        x=date_columns[0],
        y=[col for col in df.columns if "close" in col.lower()],
        title="Close Price Comparison",
    )

    # Make a bar chart for volume, based on the first date column
    fig2 = px.line(
        df,
        x=date_columns[0],
        y=[col for col in df.columns if "volume" in col.lower()],
        title="Trading Volume Comparison",
    )

    # Make the y axis on fig2 a log scale to make it easier to read
    fig2.update_yaxes(type="log")

    graph_group = dmc.Group(
        children=[dcc.Graph(figure=fig1), dcc.Graph(figure=fig2)],
        position="center",
        grow=True,
    )

    return graph_group

def get_moving_average_graph(df):
    df = df.copy()
    columns = list(df.columns)

    # Check if all required columns exist before creating graph
    if not all([col in columns for col in [ "close_sp", "close_tsla", "Date"]]):
        return None

    df["S&P_MA30"] = df["close_sp"].rolling(window=30).mean()
    df["TSLA_MA30"] = df["close_tsla"].rolling(window=30).mean()
    fig3 = px.line(
        df,
        x="Date",
        y="S&P_MA30",
        labels={"S&P_MA30": "S&P 30-Day MA"},
        title="30-Day Moving Average Comparison",
    )

    fig3.add_scatter(
        x=df["Date"],
        y=df["TSLA_MA30"],
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

    return dcc.Graph(figure=fig3)


def get_graph_group(df, date_columns): 
    side_by_side_graphs = get_side_by_side_graphs(df, date_columns)
    moving_average_graph = get_moving_average_graph(df)

    return html.Div(
        [
            side_by_side_graphs,
            moving_average_graph
        ]
    )