import plotly.express as px
from dash import dcc, html
from dash.exceptions import PreventUpdate


def get_date_and_matching_columns(df):
    """
    Returns the date column, and a dictonary of columns that match the following criteria:
    - Close price column
    - Open price column
    - Volume column 
    """
    # First, we find the date column. If there isn't one, we can't graph it, so we bail on it
    date_columns = [col for col in df.columns if df[col].dtype == "datetime64[ns]"]
    close_columns = [col for col in df.columns if "close" in col.lower()]
    volume_columns = [col for col in df.columns if "volume" in col.lower()]
    open_columns = [col for col in df.columns if "open" in col.lower()]

    if len(date_columns) == 0:
        raise PreventUpdate
    
    if len(close_columns) < 2 and len(open_columns) < 2 and len(volume_columns) < 2:
        raise PreventUpdate
    
    date_column = date_columns[0] if len(date_columns) > 0 else None

    matching_columns = {
        'Close Price': close_columns if len(close_columns) > 1 else None,
        'Open Price': open_columns if len(open_columns) > 1 else None,
        'Volume': volume_columns if len(volume_columns) > 1 else None,
    }

    return date_column, matching_columns


def get_graphs(df, date_column, matching_columns):

    df = df.copy()

    if date_column is None:
        raise PreventUpdate
    
    if len(matching_columns['Close Price']) < 2 and len(matching_columns['Open Price']) < 2 and len(matching_columns['Volume']) < 2:
        raise PreventUpdate

    figures = []

    # Build all the standard comparison graphs
    for graph_title, columns in matching_columns.items():

        first_column = columns[0]
        second_column = columns[1]

        fig = px.line(
            df,
            x=date_column,
            y=first_column,
            title=f"{graph_title} Comparison",
        )
        fig.add_scatter(
            x=df[date_column],
            y=df[second_column],
            mode="lines",
            yaxis="y2",
            name=f"{second_column}",
        )
        fig.update_layout(
            yaxis=dict(title=first_column),
            yaxis2=dict(title=second_column, overlaying="y", side="right"),
        )

        figures.append(fig)

    # Build the rolling average plots
    for graph_title, columns in matching_columns.items():

        first_column = columns[0]
        second_column = columns[1]

        df[f"{first_column}_MA30"] = df[first_column].rolling(window=30).mean()
        df[f"{second_column}_MA30"] = df[second_column].rolling(window=30).mean()
        fig = px.line(
            df,
            x=date_column,
            y=f"{first_column}_MA30",
            title=f"{graph_title} 30-Day Moving Average Comparison",
        )
        fig.add_scatter(
            x=df[date_column],
            y=df[f"{second_column}_MA30"],
            mode="lines",
            name=f"{second_column} 30-Day MA",
            yaxis="y2",
        )

        fig.update_layout(
            yaxis=dict(title=f"{first_column} 30-Day Moving Average"),
            yaxis2=dict(
                title=f"{second_column} 30-Day Moving Average", overlaying="y", side="right"
            ),
        )

        figures.append(fig)

    return figures

def get_correlations(df, matching_columns):
    return [
        {"Metric": title, "Pearson Correlation": df[columns[0]].corr(df[columns[1]])}
        for title, columns in matching_columns.items()
    ]