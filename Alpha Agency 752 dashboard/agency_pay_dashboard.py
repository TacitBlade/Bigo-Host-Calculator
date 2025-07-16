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

import streamlit as st
import pandas as pd

# --- Conversion Logic ---

def greedy_bean_to_diamond(beans, packages):
    """
    Greedily convert Beans to Diamonds using the provided packages.
    Returns total diamonds, leftover beans, and package usage counts.
    """
    total_diamonds = 0
    remaining = beans
    counts = {}

    # Sort packages descending by bean cost
    for bean_cost, dia_return in sorted(packages, reverse=True):
        if remaining >= bean_cost:
            cnt = remaining // bean_cost
            counts[f"{bean_cost}→{dia_return}"] = cnt
            total_diamonds += cnt * dia_return
            remaining -= cnt * bean_cost

    return total_diamonds, remaining, counts

# --- Streamlit UI ---

def main():
    st.title("Bean → Diamond Converter")

    # Define all available packages
    all_packages = {
        "10999 → 3045 Diamonds": (10999, 3045),
        "3999 → 1105 Diamonds":  (3999, 1105),
        "999 → 275 Diamonds":    (999, 275),
        "109 → 29 Diamonds":     (109, 29),
        "8 → 2 Diamonds":        (8, 2),
    }

    # Sidebar: select which packages to include
    st.sidebar.header("Select Conversion Packages")
    selected_labels = st.sidebar.multiselect(
        "Choose tiers to include",
        options=list(all_packages.keys()),
        default=list(all_packages.keys())
    )

    # Build the active package list
    active_packages = [all_packages[label] for label in selected_labels]

    # Main input
    beans = st.number_input(
        "Enter how many Beans you have",
        min_value=0,
        value=0,
        step=1
    )

    # Perform conversion when button is clicked
    if st.button("Convert Beans → Diamonds"):
        if not active_packages:
            st.warning("Please select at least one package in the sidebar.")
            return

        diamonds, leftover, breakdown = greedy_bean_to_diamond(beans, active_packages)

        # Display results
        st.metric("Total Diamonds Gained", diamonds)
        st.metric("Beans Leftover", leftover)

        st.subheader("Breakdown by Package")
        if breakdown:
            df = pd.DataFrame([
                {"Package (Beans → Diamonds)": pkg, "Times Used": cnt}
                for pkg, cnt in breakdown.items()
            ])
            st.table(df)
        else:
            st.info("Not enough Beans to use any of the selected packages.")

if __name__ == "__main__":
    main()

    # === Footer ===
st.markdown("""
<hr style="margin-top: 50px;">
<div style="text-align: center; font-size: 14px; color: #6B4E9B;">
    <strong>Alpha Agency 752</strong> — Streamlined. Strategic. Alpha.<br>
    Contact: info@alphaagency752.com | © 2025
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from io import BytesIO

# --- PK Rebate Dataset ---
rebate_data = {
    "Daily PK": [
        {"PK points": 7000, "Diamonds": 700, "Win Beans": 210, "Rebate %": 0.3},
        {"PK points": 10000, "Diamonds": 1000, "Win Beans": 300, "Rebate %": 0.3},
        {"PK points": 20000, "Diamonds": 2000, "Win Beans": 600, "Rebate %": 0.3},
        {"PK points": 30000, "Diamonds": 3000, "Win Beans": 900, "Rebate %": 0.3},
        {"PK points": 50000, "Diamonds": 5000, "Win Beans": 1000, "Rebate %": 0.2},
        {"PK points": 100000, "Diamonds": 10000, "Win Beans": 1800, "Rebate %": 0.18},
        {"PK points": 150000, "Diamonds": 15000, "Win Beans": 2700, "Rebate %": 0.18},
    ],
    "Talent PK": [
        {"PK points": 5000, "Diamonds": 500, "Win Beans": 150, "Rebate %": 0.3},
        {"PK points": 10000, "Diamonds": 1000, "Win Beans": 350, "Rebate %": 0.35},
        {"PK points": 20000, "Diamonds": 2000, "Win Beans": 700, "Rebate %": 0.35},
        {"PK points": 30000, "Diamonds": 3000, "Win Beans": 1000, "Rebate %": 0.333},
        {"PK points": 50000, "Diamonds": 5000, "Win Beans": 1700, "Rebate %": 0.34},
    ],
    "Star Tasks": [
        {"PK points": 2000, "Diamonds": 200, "Win Beans": 60, "Rebate %": 0.3},
        {"PK points": 10000, "Diamonds": 1000, "Win Beans": 320, "Rebate %": 0.32},
        {"PK points": 50000, "Diamonds": 5000, "Win Beans": 1700, "Rebate %": 0.34},
        {"PK points": 80000, "Diamonds": 8000, "Win Beans": 2800, "Rebate %": 0.35},
        {"PK points": 100000, "Diamonds": 10000, "Win Beans": 3500, "Rebate %": 0.35},
        {"PK points": 120000, "Diamonds": 12000, "Win Beans": 4000, "Rebate %": 0.333},
    ]
}

# --- Helpers ---
def sanitize_data(data):
    all_entries = []
    for pk_type, tiers in data.items():
        for e in tiers:
            entry = {**e, "PK Type": pk_type}
            all_entries.append(entry)
    return pd.DataFrame(all_entries)

def filter_by_diamonds(df, diamond_limit):
    return df[df["Diamonds"] <= diamond_limit].copy()

def generate_excel_download(df, filename):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    st.download_button("📥 Download Excel", data=buffer, file_name=filename,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Streamlit App ---
st.set_page_config(page_title="PK Rebate Explorer", layout="centered")
st.title("💎 PK Rebate Explorer")

diamond_input = st.number_input("Enter your available Diamonds", min_value=0, value=1000, step=100)
sort_by = st.selectbox("Sort by", ["Win Beans", "Rebate %"])

df_all = sanitize_data(rebate_data)
df_filtered = filter_by_diamonds(df_all, diamond_input)

if not df_filtered.empty:
    df_sorted = df_filtered.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
    st.subheader("📊 Matching PK Tiers")
    st.dataframe(df_sorted)
    generate_excel_download(df_sorted, f"pk_tiers_{diamond_input}.xlsx")
else:
    st.warning("No PK tiers available within that diamond budget.")

with st.expander("🛠 Debug Panel", expanded=False):
    st.json({k: v[:1] for k, v in rebate_data.items()})
        # === Footer ===
st.markdown("""
<hr style="margin-top: 50px;">
<div style="text-align: center; font-size: 14px; color: #6B4E9B;">
    <strong>Alpha Agency 752</strong> — Streamlined. Strategic. Alpha.<br>
    Contact: info@alphaagency752.com | © 2025
</div>
""", unsafe_allow_html=True)