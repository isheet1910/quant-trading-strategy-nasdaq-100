import pandas as pd
import numpy as np

file_path = "../excel/nasdaq100_with_indicators.xlsx"

# -----------------------------
# 1. Load data
# -----------------------------
df = pd.read_excel(file_path, sheet_name="Price")

# -----------------------------
# 2. Set index (Company)
# -----------------------------
df = df.set_index("Company")

# -----------------------------
# 3. Convert columns to datetime
# -----------------------------
df.columns = pd.to_datetime(df.columns)

# Sort columns (dates)
df = df.sort_index(axis=1)

# -----------------------------
# 4. RSI function (Wilder)
# -----------------------------
def compute_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# -----------------------------
# 5. Apply RSI row-wise
# -----------------------------
rsi_df = df.apply(compute_rsi, axis=1)

# -----------------------------
# 6. Filter required dates
# -----------------------------
rsi_df = rsi_df.loc[:, "2025-01-15":"2026-04-29"]

# -----------------------------
# 7. Reset index for Excel
# -----------------------------
rsi_df.reset_index(inplace=True)

# -----------------------------
# 8. Save to SAME file (new sheet)
# -----------------------------
with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    rsi_df.to_excel(writer, sheet_name="RSI", index=False)

print("Done. RSI sheet created in required format.")