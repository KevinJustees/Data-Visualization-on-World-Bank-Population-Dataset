# plot_population.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ============ CONFIG =============
csv_path = r"C:\Users\kevin\Desktop\population_viz\API_SP.POP.TOTL_DS2_en_csv_v2_23043.csv"
# output image names
hist_out = "population_histogram.png"
bar_out = "population_top10.png"
# choose year: set to None to auto-pick latest available numeric year
YEAR = None
# ==================================

def load_worldbank_population(path):
    # World Bank CSVs often have 4 header rows before the data table. Skip them.
    # If your file is different, adjust skiprows.
    df = pd.read_csv(path, skiprows=4)
    return df

def tidy_long_format(df):
    # Typical columns: ['Country Name','Country Code','Indicator Name','Indicator Code','1960','1961',...]
    # Convert wide years to long format
    id_cols = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    year_cols = [c for c in df.columns if c not in id_cols]
    long = df.melt(id_vars=id_cols, value_vars=year_cols,
                   var_name='Year', value_name='Value')
    # drop non-year rows (if any) and convert Year to int where possible
    long = long[long['Year'].str.match(r'^\d{4}$')]
    long['Year'] = long['Year'].astype(int)
    # numeric value
    long['Value'] = pd.to_numeric(long['Value'], errors='coerce')
    return long

def pick_year(long_df, preferred_year=None):
    if preferred_year is not None:
        if preferred_year in long_df['Year'].unique():
            return preferred_year
        else:
            print(f"Preferred year {preferred_year} not found; auto-selecting latest year.")
    # pick latest year that has at least some non-null values
    years = sorted(long_df['Year'].unique())
    for y in reversed(years):
        if long_df.loc[long_df['Year'] == y, 'Value'].notna().sum() > 0:
            return y
    raise RuntimeError("No year with data found.")

def plot_histogram(values, year, outpath):
    plt.figure(figsize=(10,6))
    sns.histplot(values.dropna(), bins=40)
    plt.title(f'Population Distribution across Countries — {year}')
    plt.xlabel('Population')
    plt.ylabel('Number of countries')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
    print(f"Saved histogram to {outpath}")

def plot_top_bar(df_year, year, outpath, top_n=10):
    top = df_year.sort_values('Value', ascending=False).head(top_n)
    plt.figure(figsize=(10,6))
    sns.barplot(data=top, x='Value', y='Country Name')
    plt.title(f'Top {top_n} Countries by Population — {year}')
    plt.xlabel('Population')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
    print(f"Saved bar chart to {outpath}")

def main():
    print("Loading data...")
    df = load_worldbank_population(csv_path)
    print("Tidying to long format...")
    long = tidy_long_format(df)
    chosen_year = pick_year(long, YEAR)
    print("Using year:", chosen_year)

    df_year = long[long['Year'] == chosen_year].copy()
    # optionally remove aggregates like "World" or region codes if present:
    # filter out rows where Country Code is NaN or looks like aggregates (WB uses 3-letter codes for countries)
    df_year = df_year[df_year['Country Code'].notna()]

    # Histogram (distribution)
    plot_histogram(df_year['Value'], chosen_year, hist_out)

    # Bar chart top 10
    plot_top_bar(df_year, chosen_year, bar_out, top_n=10)

    # Print where files are saved
    print("Done. Output files in current directory:", os.getcwd())

if __name__ == "__main__":
    main()
