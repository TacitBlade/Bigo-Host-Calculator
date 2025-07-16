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

st.markdown("---")
st.header("🏆 Diamond Optimizer — Maximize PK Event Rewards")

# === User Input ===
total_diamonds = st.number_input("Enter your total diamonds:", min_value=0, step=100)

# === Load Rules & Rewards Sheet ===
try:
    pk_df = pd.read_excel("July 2025 UK Agency&Host Events .xlsx", sheet_name="rules and rewards")
except Exception as e:
    st.error(f"Could not load 'rules and rewards' sheet: {e}")
    st.stop()

# === Prepare Win Data ===
win_columns = [col for col in pk_df.columns if "Win" in col]
pk_df['Max Win'] = pk_df[win_columns].max(axis=1)

reward_table = pk_df[['PK Type', 'Max Win']].copy()
reward_table = reward_table.dropna(subset=['Max Win'])
reward_table = reward_table.sort_values(by='Max Win', ascending=False).reset_index(drop=True)

# === Allocate Diamonds ===
remaining_diamonds = total_diamonds
allocations = []

for _, row in reward_table.iterrows():
    if remaining_diamonds == 0:
        break

    allocated = remaining_diamonds
    allocations.append({
        "PK Type": row['PK Type'],
        "Diamonds Allocated": allocated,
        "Estimated Reward": row['Max Win']
    })

    remaining_diamonds = 0  # spent entirely on the highest reward

# === Results Display ===
st.subheader("💎 Reward Allocation Summary")
if allocations:
    st.table(pd.DataFrame(allocations))
    st.success(f"Total diamonds allocated: {total_diamonds}")
else:
    st.info("Enter diamonds above to view your optimal reward allocation.")
        # === Footer ===
st.markdown("""
<hr style="margin-top: 50px;">
<div style="text-align: center; font-size: 14px; color: #6B4E9B;">
    <strong>Alpha Agency 752</strong> — Streamlined. Strategic. Alpha.<br>
    Contact: info@alphaagency752.com | © 2025
</div>
""", unsafe_allow_html=True)