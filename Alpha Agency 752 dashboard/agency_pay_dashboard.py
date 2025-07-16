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
from pathlib import Path

# === Load Dataset ===
try:
    df = pd.read_excel("RulesAndRewards.xlsx", sheet_name="Sheet1")
except Exception as e:
    st.error(f"Failed to load data file: {e}")
    st.stop()

def compute_allocation(diamonds: int, pk_df: pd.DataFrame):
    """
    Allocate diamonds across sorted PK events,
    returning a DataFrame breakdown, total rebate, and leftover.
    """
    records, remaining, total_rebate = [], diamonds, 0

    for _, row in pk_df.iterrows():
        cost, rebate = int(row['Cost']), int(row['Rebate'])
        if remaining < cost:
            records.append({
                'PK Type': row['PK Type'],
                'Cost': cost,
                'Rebate': rebate,
                'Count': 0,
                'Spent': 0,
                'Earned': 0,
                'Leftover': remaining
            })
            continue

        count = remaining // cost
        spent = count * cost
        earned = count * rebate
        remaining -= spent
        total_rebate += earned

        records.append({
            'PK Type': row['PK Type'],
            'Cost': cost,
            'Rebate': rebate,
            'Count': count,
            'Spent': spent,
            'Earned': earned,
            'Leftover': remaining
        })

    df = pd.DataFrame(records)
    return df, total_rebate, remaining

def main():
    st.title("💎 Diamond-to-PK Reward Planner (Local File)")

    st.markdown("""
    - Place your Excel file (sheet named `RulesAndRewards`)  
      in this app’s directory or specify its path.  
    - Enter the path and your diamond balance.  
    - Click **Calculate** to see your reward breakdown.
    """)

    file_path = st.text_input(
        "Enter Excel file path:", 
        value="RulesAndRewards.xlsx",
        help="e.g., ./data/RulesAndRewards.xlsx"
    )

    diamonds = st.number_input(
        "Your diamond balance:", 
        min_value=0, 
        step=1, 
        value=0
    )

    if st.button("Calculate"):
        pk_df = pd.read_excel("RulesAndRewards.xlsx", sheet_name="Sheet1")

        if pk_df.empty:
            st.warning("No PK data to process.")
            return

        allocation_df, total_rebate, leftover = compute_allocation(diamonds, pk_df)

        st.subheader("📊 Allocation Breakdown")
        st.dataframe(allocation_df)

        st.markdown(f"""
        **Total Diamonds Spent:** {diamonds - leftover}  
        **Total Rebate Earned:** {total_rebate}  
        **Diamonds Remaining:** {leftover}
        """)

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