import json

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from bs4 import BeautifulSoup

with open("utils/config_constants.json", "r") as file_handle:
    config_dict = json.load(file_handle)
    period_column_mapping = config_dict["period_column_mapping"]


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
        color=df_change["positive_" + column_name],
        color_discrete_map={True: "green", False: "red"},
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
        csv: csv file
            CSV file that will be downloaded.
    """
    csv = df.to_csv(index=False).encode("utf-8")
    return csv


@st.cache_data
def get_insights(df):
    """
    Function to get quick insights about the data.

    Args:
        df: pandas dataframe
            The dataframe that will be downloaded.

    Returns:
        (most_traded, highest_ytd, steady_growth)
            most_traded: five most traded by volume in the past 24 hours
            highest_ytd: five highest ytd growth
            steady_growth: five highest steady positive growth over the past week

    """
    most_traded = ", ".join(
        df.sort_values(by="Volume24h", ascending=False)["Cryptocurrency"]
        .iloc[:5]
        .tolist()
    )

    highest_ytd = ", ".join(
        df.sort_values(by="YTDPricePercentChange", ascending=False)["Cryptocurrency"]
        .iloc[:5]
        .tolist()
    )

    steady_df = df[
        ["Cryptocurrency", "PercentChange1h", "PercentChange24h", "PercentChange7d"]
    ][
        (df["PercentChange1h"] < df["PercentChange24h"])
        & (df["PercentChange24h"] < df["PercentChange7d"])
        & (df["PercentChange1h"] > 0)
        & (df["PercentChange24h"] > 0)
        & (df["PercentChange7d"] > 0)
    ]

    if len(steady_df):
        steady_df["7d_24h_diff"] = (
            steady_df["PercentChange7d"] - steady_df["PercentChange24h"]
        )
        steady_df["24h_1h_diff"] = (
            steady_df["PercentChange24h"] - steady_df["PercentChange1h"]
        )
        steady_df["sum_diff"] = steady_df["7d_24h_diff"] + steady_df["24h_1h_diff"]

        crypto_list = (
            steady_df.sort_values(by="sum_diff", ascending=False)["Cryptocurrency"]
            .iloc[:5]
            .tolist()
        )
        steady_growth = ", ".join(crypto_list)
    else:
        steady_growth = "None"

    return (most_traded, highest_ytd, steady_growth)
