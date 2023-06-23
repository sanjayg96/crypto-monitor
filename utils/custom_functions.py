import json
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

period_column_mapping = {
    "1h": "PercentChange1h",
    "24h": "PercentChange24h",
    "7d": "PercentChange7d",
    "30d": "PercentChange30d",
    "60d": "PercentChange60d",
    "90d": "PercentChange90d",
}


@st.cache_data
def get_data():
    """
    Scrape data from CoinMarketCap.

    Args:
        None

    Returns:
        df: pandas dataframe
            Dataframe containing the crypto-currency data
    """
    cmc = requests.get("https://coinmarketcap.com")
    soup = BeautifulSoup(cmc.content, "html.parser")

    data = soup.find("script", id="__NEXT_DATA__", type="application/json")
    coin_data = json.loads(data.contents[0])
    listings = json.loads(coin_data["props"]["initialState"])["cryptocurrency"][
        "listingLatest"
    ]["data"]

    df = pd.DataFrame(listings[1:], columns=listings[0]["keysArr"] + ["none"])

    return df


def price_plot(df, column_object):
    """
    Generate plot for current price of the the cryptocurrencies.

    Args:
        df: pandas dataframe
            Data frame containing the crypto data

        column_object: streamlit column object
            To access the column and its methods to generate the plot.

    Returns:
        None
    """
    df = df.sort_values(by="Price")
    fig = px.bar(
        df,
        y="Cryptocurrency",
        x="Price",
        text_auto=".2s",
        # title="Current Price of Cryptocurrencies",
    )
    fig.update_traces(
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
    )
    fig.update_layout(showlegend=False, xaxis_title="Price (USD)")
    column_object.plotly_chart(fig, use_container_width=True)

    return None


def percentage_change_plot(df_change, percent_timeframe, column_object):
    """
    Generate percentage price change plot for the selected time frame.

    Args:
        df_change: pandas dataframe
            Data frame containing the crypto data

        percent_timeframe: str
            Selected timeframe like 1h, 7d, 30d etc.

        column_object: streamlit column object
            To access the column and its methods to generate the plot.

    Returns:
        None
    """
    column_name = period_column_mapping[percent_timeframe]
    df_change = df_change.sort_values(by=[column_name])

    column_object.write("*" + percent_timeframe + " period*")

    fig = px.bar(
        df_change,
        y=df_change[column_name],
        x=df_change.index,
        # orientation="h",
        # color=df_change["positive_" + column_name].map({True: "g", False: "r"}),
        color=df_change["positive_" + column_name],
        color_discrete_map={True: "green", False: "red"},
        # height=25,
        # labels={"y": "Percentage Change"},
    )
    fig.update_layout(showlegend=False, yaxis_title="Percentage Change")
    fig.update_xaxes(tickangle=-50)
    column_object.plotly_chart(fig, use_container_width=True)

    return None


@st.cache_data
def file_download(df):
    """
    Function to allow CSV file download from the web page.

    Args:
        df: pandas dataframe
            The dataframe that will be downloaded.

    Returns:
        href: hyperlink
    """
    csv = df.to_csv(index=False).encode("utf-8")
    return csv
