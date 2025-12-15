# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Fronteira Eficiente", layout="wide")
st.title("Simulação de Portfólios - Fronteira Eficiente (Monte Carlo)")

# ====== Sidebar ======
st.sidebar.header("Parâmetros")
tickers_str = st.sidebar.text_input("Tickers (sep. por vírgula)", "PETR4.SA,VALE3.SA,WEGE3.SA,B3SA3.SA")
tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]

col1, col2 = st.sidebar.columns(2)
with col1:
    start = st.date_input("Início", pd.to_datetime("2023-01-01"))
with col2:
    end = st.date_input("Fim", pd.Timestamp.today())

n_sims = st.sidebar.number_input("Nº simulações", 100, 20000, 2000, 100)
rf = st.sidebar.number_input("Taxa livre de risco (a.a.)", 0.0, 1.0, 0.10, step=0.005, format="%.4f")

rodar = st.sidebar.button("Rodar")

# ====== Funções pequenas ======
@st.cache_data(ttl=3600)
def baixa_precos(tickers, start, end):
    # auto_adjust=True devolve 'Close' já ajustado
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame()
    # Padroniza para DataFrame colunas simples (mesmo 1 ticker)
    if isinstance(df.columns, pd.MultiIndex):
        px = df["Close"].copy()
    else:
        px = df[["Close"]].copy()
        px.columns = tickers
    return px.dropna(how="all").dropna()

def retornos_diarios(px):
    return px.pct_change().dropna()

def simula_monte_carlo(ret, n_sims, rf):
    if ret.empty:
        return pd.DataFrame(), None, None, None

    mu = ret.mean() * 252
    cov = ret.cov() * 252
    n = len(ret.columns)

    resultados = np.zeros((3 + n, n_sims))
    for i in range(n_sims):
        w = np.random.random(n)
        w /= w.sum()
        port_ret = float(np.dot(mu.values, w))
        port_vol = float(np.sqrt(np.dot(w.T, np.dot(cov.values, w))))
        sharpe = (port_ret - rf) / port_vol if port_vol > 0 else np.nan

        resultados[0, i] = port_ret
        resultados[1, i] = port_vol
        resultados[2, i] = sharpe
        resultados[3:, i] = w

    cols = ["Retorno", "Volatilidade", "Sharpe"] + list(ret.columns)
    df = pd.DataFrame(resultados.T, columns=cols)

    # 1/N
    w_eq = np.ones(n) / n
    ret_eq = float(np.dot(mu.values, w_eq))
    vol_eq = float(np.sqrt(np.dot(w_eq.T, np.dot(cov.values, w_eq))))
    shp_eq = (ret_eq - rf) / vol_eq if vol_eq > 0 else np.nan
    eq = {"Retorno": ret_eq, "Volatilidade": vol_eq, "Sharpe": shp_eq, "Pesos": pd.Series(w_eq, index=ret.columns)}
    return df, mu, cov, eq

def portfolios_otimos(df):
    if df.empty:
        return None, None
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["Volatilidade"])
    msp = df.loc[df["Sharpe"].idxmax()] if df["Sharpe"].notna().any() else None
    mvp = df.loc[df["Volatilidade"].idxmin()] if not df["Volatilidade"].empty else None
    return msp, mvp

def grafico_fr_nteira(df, msp, mvp, p_eq):
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=df["Volatilidade"], y=df["Retorno"], mode="markers",
        marker=dict(size=6, opacity=0.6, color=df["Sharpe"], colorscale="Plasma", showscale=True),
        name="Portfólios"
    ))
    if msp is not None:
        fig.add_trace(go.Scattergl(x=[msp["Volatilidade"]], y=[msp["Retorno"]], mode="markers",
                                   marker=dict(size=12, symbol="star", line=dict(width=1), color="deepskyblue"),
                                   name="Máx. Sharpe"))
    if mvp is not None:
        fig.add_trace(go.Scattergl(x=[mvp["Volatilidade"]], y=[mvp["Retorno"]], mode="markers",
                                   marker=dict(size=12, symbol="diamond", line=dict(width=1), color="lightgreen"),
                                   name="Mín. Volatilidade"))
    if p_eq is not None:
        fig.add_trace(go.Scattergl(x=[p_eq["Volatilidade"]], y=[p_eq["Retorno"]], mode="markers",
                                   marker=dict(size=10, symbol="triangle-up", line=dict(width=1), color="gold"),
                                   name="1/N"))
    fig.update_layout(
        title="Fronteira (Monte Carlo)",
        xaxis_title="Volatilidade (a.a.)",
        yaxis_title="Retorno (a.a.)",
        xaxis_tickformat=".1%",
        yaxis_tickformat=".1%",
        legend_orientation="h"
    )
    return fig

# ====== Fluxo ======
if rodar:
    if not tickers:
        st.warning("Informe pelo menos um ticker.")
    elif start >= end:
        st.warning("A data final deve ser posterior à inicial.")
    else:
        st.info(f"Baixando preços de {', '.join(tickers)}...")
        px = baixa_precos(tickers, start, end)
        if px.empty:
            st.error("Falha ao obter preços.")
        else:
            ret = retornos_diarios(px)
            if ret.empty or len(ret) < 2:
                st.warning("Poucos dados para calcular retornos.")
            else:
                df_sims, mu, cov, eq = simula_monte_carlo(ret, n_sims, rf)
                if df_sims.empty:
                    st.error("Simulação não retornou resultados.")
                else:
                    msp, mvp = portfolios_otimos(df_sims)
                    st.success("Simulação concluída!")

                    # Gráfico
                    fig = grafico_fr_nteira(df_sims, msp, mvp, eq)
                    st.plotly_chart(fig, use_container_width=True)

                    # Resultados-chave
                    c1, c2, c3 = st.columns(3)
                    if msp is not None:
                        with c1:
                            st.subheader("Máx. Sharpe")
                            st.metric("Retorno", f"{msp['Retorno']:.2%}")
                            st.metric("Volatilidade", f"{msp['Volatilidade']:.2%}")
                            st.metric("Sharpe", f"{msp['Sharpe']:.2f}")
                            w = msp.drop(["Retorno","Volatilidade","Sharpe"])
                            st.dataframe(w.map(lambda x: f"{x:.2%}"))
                    if mvp is not None:
                        with c2:
                            st.subheader("Mín. Volatilidade")
                            st.metric("Retorno", f"{mvp['Retorno']:.2%}")
                            st.metric("Volatilidade", f"{mvp['Volatilidade']:.2%}")
                            st.metric("Sharpe", f"{mvp['Sharpe']:.2f}")
                            w = mvp.drop(["Retorno","Volatilidade","Sharpe"])
                            st.dataframe(w.map(lambda x: f"{x:.2%}"))
                    if eq is not None:
                        with c3:
                            st.subheader("Portfólio 1/N")
                            st.metric("Retorno", f"{eq['Retorno']:.2%}")
                            st.metric("Volatilidade", f"{eq['Volatilidade']:.2%}")
                            st.metric("Sharpe", f"{eq['Sharpe']:.2f}")
                            st.dataframe(eq["Pesos"].map(lambda x: f"{x:.2%}"))

                    with st.expander("Top 10 portfólios simulados"):
                        st.dataframe(df_sims.sort_values("Sharpe", ascending=False).head(10))

                    with st.expander("Preços (fech. ajustado)"):
                        st.dataframe(px)
else:
    st.info("Defina os parâmetros na barra lateral e clique em **Rodar**.")

