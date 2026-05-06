import yfinance as yf
import pandas as pd

# -----------------------------
# Tickers (removed ANSS to avoid error)
# -----------------------------
tickers = [
"AAPL","MSFT","AMZN","NVDA","META","GOOGL","GOOG","TSLA","AVGO","COST",
"NFLX","ASML","AMD","PEP","ADBE","LIN","CSCO","TMUS","CMCSA","INTC",
"TXN","INTU","AMGN","QCOM","HON","AMAT","BKNG","ISRG","PANW","ADP",
"VRTX","GILD","SBUX","MU","ADI","REGN","LRCX","MDLZ","KLAC","PYPL",
"SNPS","CDNS","MAR","MELI","CSX","ORLY","ABNB","FTNT","ADSK","NXPI",
"CHTR","MNST","AEP","MRVL","PCAR","WDAY","CPRT","PAYX","ROST","MCHP",
"FAST","ODFL","AZN","KDP","CTSH","EA","DXCM","CTAS","VRSK","GEHC",
"EXC","KHC","LULU","TEAM","XEL","IDXX","FANG","BKR","CCEP","CSGP",
"TTWO","ZS","ON","BIIB","DDOG","CDW","ILMN","GFS","MDB",
"WBD","MRNA","ARM","CRWD","SMCI","DLTR","DASH","CEG","TTD"
]

# -----------------------------
# Date range
# -----------------------------
start_date = "2025-01-01"
end_date = "2026-04-30"

output_file = "../excel/nasdaq100_prices_raw.xlsx"

print("Downloading data...")

# -----------------------------
# Download in batch
# -----------------------------
data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    group_by='ticker',
    progress=False
)

print("Processing data...")

all_rows = []

for ticker in tickers:
    try:
        if ticker not in data:
            print(f"Skipping {ticker} (no data)")
            continue

        df = data[ticker].copy()

        if df.empty:
            continue

        # Keep only Close
        df = df[['Close']]

        # 🔥 Remove timestamp → keep only date
        df.index = df.index.date

        # Transpose (dates → columns)
        df = df.T

        # Set row name
        df.index = [ticker]

        all_rows.append(df)

    except Exception as e:
        print(f"Error with {ticker}: {e}")

# -----------------------------
# Combine all
# -----------------------------
final_df = pd.concat(all_rows)

# Make ticker a column
final_df.reset_index(inplace=True)
final_df.rename(columns={'index': 'Company'}, inplace=True)

# -----------------------------
# Save
# -----------------------------
final_df.to_excel(output_file, index=False)

print(f"\n✅ Done! File saved as: {output_file}")