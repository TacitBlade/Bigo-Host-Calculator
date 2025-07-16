import streamlit as st
import pandas as pd
from PIL import Image
import io

# === Page Setup ===
st.set_page_config(page_title="Alpha Agency 752 Dashboard", layout="wide")

# === Load Banner Image ===
try:
    banner = Image.open("alpha_agency_banner.png")
    st.image(banner, use_container_width=True)
except FileNotFoundError:
    st.error("Banner image not found. Please make sure 'alpha_agency_banner.png' is in the project folder.")

# === Welcome Message ===
st.markdown("""
### _Streamlined. Strategic. Alpha._
Explore pay tiers, Beans, and Diamonds. Filter rankings dynamically, download your custom dataset, and discover broadcaster value across the agency.
""")

# === Load Dataset ===
try:
    df = pd.read_excel("Alpha_Omega_Agency_Pay_Chart_with_Diamonds.xlsx", sheet_name="Sheet1")
except Exception as e:
    st.error(f"Failed to load data file: {e}")
    st.stop()

# === Preprocess: Add Bean-to-USD Conversion ===
df['Bean_to_USD_Rate'] = df['Broadcaster Remuneration (USD)'] / df['Target Beans']

# === Sidebar Filters ===
st.sidebar.header("🔎 Filter Criteria")

# Filter 1: Rank
rank_options = sorted(df['Ranking'].dropna().unique())
selected_ranks = st.sidebar.multiselect("Select Rank(s)", rank_options, default=rank_options)

# Filter 2: Salary Range
min_salary, max_salary = int(df['Salary in Beans'].min()), int(df['Salary in Beans'].max())
salary_range = st.sidebar.slider("Salary in Beans Range", min_salary, max_salary, (min_salary, max_salary), step=1000)

# Filter 3: Convertible Diamonds Range
min_diamonds, max_diamonds = int(df['Convertible Diamonds'].min()), int(df['Convertible Diamonds'].max())
diamonds_range = st.sidebar.slider("Convertible Diamonds Range", min_diamonds, max_diamonds, (min_diamonds, max_diamonds), step=1000)

# === Apply Filters ===
filtered_df = df[
    df['Ranking'].isin(selected_ranks) &
    df['Salary in Beans'].between(*salary_range) &
    df['Convertible Diamonds'].between(*diamonds_range)
]

# === Styling: Custom Buttons & UI Cleanup ===
st.markdown("""
    <style>
    div.stDownloadButton > button {
        background-color: #6B4E9B;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 8px 20px;
    }
    div.stDownloadButton > button:hover {
        background-color: #553B7A;
        color: #FFDDEE;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# === Main Content ===
st.title("📊 Filtered Pay Chart")

if filtered_df.empty:
    st.warning("No matching data found. Try adjusting your filters.")
else:
    st.write(f"Showing {len(filtered_df)} result(s) based on filters:")
    st.dataframe(filtered_df)

    # Convert to Excel for download
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')
        buffer.seek(0)
        st.download_button(
            label="📥 Download Filtered Data as Excel",
            data=buffer,
            file_name="filtered_agency_pay_chart.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# === Footer ===
st.markdown("""
<hr style="margin-top: 50px;">
<div style="text-align: center; font-size: 14px; color: #6B4E9B;">
    <strong>Alpha Agency 752</strong> — Streamlined. Strategic. Alpha.<br>
    Contact: info@alphaagency752.com | © 2025
</div>
""", unsafe_allow_html=True)
