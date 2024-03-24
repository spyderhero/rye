import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title("米国株可視化アプリ")

st.sidebar.write("""
#GAFA株価 こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""表示日数選択""")

days = st.sidebar.slider('日数', 1, 100, 50)
st.write(f"""
### 過去 **{days}日間**のGAFA株価 ###
"""
)

tickers = {
    'Apple': 'AAPL',
    'Meta': 'META',
    'Google': 'GOOGL',
    'Microsoft': 'MSFT',
    'Netflix': 'NFLX',
    'Amazon': 'AMZN',
    'Sony': 'SONY',
    'Disney': 'DIS'
}

@st.cache_data #これを入れることで以下の関数の読み取り速度が上がる！
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

df = get_data(days, tickers)

try:
    st.sidebar.write("""
    ## 株価の範囲指定 ##
    """
    )
    y_min, y_max = st.sidebar.slider(
        "範囲を指定してください。",
        0.0, 1000.0, (0.0, 1000.0)
        )

    companies = st.multiselect(
        "会社名を選択してください。",
        ['Google', 'Amazon', 'Meta', 'Apple','Microsoft','Netflix','Sony','Disney'],
        default = ['Google', 'Amazon', 'Meta', 'Apple']
    )

    if not companies:
        st.error('少なくとも１社は選んでください。')
    else:
        data = df.loc[companies] #選んだ会社のdataを取得
        st.write("### 株価(USD) ###", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars = ['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )

        chart = (
        alt.Chart(data)
        .mark_line(opacity = 0.8)
        .encode(
            x = 'Date:T',
            y = alt.Y("Stock Prices(USD):Q", stack = None, scale = alt.Scale(domain = [y_min, y_max])),
            color = 'Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "ERROR: opps! Something wrong happened!"
    )
