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

def compute_optimal_conversion(diamonds, packages):
    """
    Dynamic programming to maximize beans for given diamonds.
    Returns total beans, counts per package, and leftover diamonds.
    """
    # dp[d] = max beans using up to d diamonds
    dp = [0] * (diamonds + 1)
    # last_choice[d] = index of package used last to achieve dp[d]
    last_choice = [-1] * (diamonds + 1)

    for i, (cost, beans) in enumerate(packages):
        for d in range(cost, diamonds + 1):
            candidate = dp[d - cost] + beans
            if candidate > dp[d]:
                dp[d] = candidate
                last_choice[d] = i

    # Reconstruct package counts
    counts = [0] * len(packages)
    d = diamonds
    while d > 0 and last_choice[d] != -1:
        pkg_idx = last_choice[d]
        counts[pkg_idx] += 1
        d -= packages[pkg_idx][0]

    leftover = d
    total_beans = dp[diamonds]
    return total_beans, counts, leftover

def main():
    st.title("Bean Conversion Optimizer")

    st.markdown("Enter how many Diamonds you have, and get the best mix of packages:")

    # Input
    diamonds = st.number_input(
        "Available Diamonds",
        min_value=0,
        step=1,
        value=0
    )

    # Define conversion packages as (diamonds_cost, beans_returned)
    packages = [
        (2, 8),
        (29, 109),
        (275, 999),
        (1105, 3999),
        (3045, 10999),
    ]

    if st.button("Compute Optimal Conversion"):
        total_beans, counts, leftover = compute_optimal_conversion(diamonds, packages)

        st.metric("Total Beans Gained", total_beans)
        st.metric("Diamonds Leftover", leftover)

        # Show breakdown
        st.subheader("Package Breakdown")
        breakdown_data = []
        for (cost, beans), cnt in zip(packages, counts):
            if cnt > 0:
                breakdown_data.append({
                    "Package (Diamonds → Beans)": f"{cost} → {beans}",
                    "Times Used": cnt
                })
        if breakdown_data:
            st.table(breakdown_data)
        else:
            st.info("No packages can be applied with current Diamonds.")

if __name__ == "__main__":
    main()