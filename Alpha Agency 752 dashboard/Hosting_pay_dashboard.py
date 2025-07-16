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

rank_options = sorted(df['Ranking'].dropna().unique())
selected_ranks = st.sidebar.multiselect("Select Rank(s)", rank_options, default=rank_options)

min_salary, max_salary = int(df['Salary in Beans'].min()), int(df['Salary in Beans'].max())
salary_range = st.sidebar.slider("Salary in Beans Range", min_salary, max_salary, (min_salary, max_salary), step=1000)

min_diamonds, max_diamonds = int(df['Convertible Diamonds'].min()), int(df['Convertible Diamonds'].max())
diamonds_range = st.sidebar.slider("Convertible Diamonds Range", min_diamonds, max_diamonds, (min_diamonds, max_diamonds), step=1000)

# === Apply Filters ===
filtered_df = df[
    df['Ranking'].isin(selected_ranks) &
    df['Salary in Beans'].between(*salary_range) &
    df['Convertible Diamonds'].between(*diamonds_range)
]

# === Styling ===
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

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["📊 Filtered Pay Chart", "🫘→💎 Beans to Diamonds", "💎 PK Diamond Optimizer"])

with tab1:
    st.title("📊 Filtered Pay Chart")
    if filtered_df.empty:
        st.warning("No matching data found. Try adjusting your filters.")
    else:
        st.write(f"Showing {len(filtered_df)} result(s) based on filters:")
        columns_to_exclude = ['Effective Broadcasting Limit', 'Billable Hours Limit', 'Bean_to_USD_Rate']
        display_df = filtered_df.drop(columns=[col for col in columns_to_exclude if col in filtered_df.columns])
        st.dataframe(display_df)

        with io.BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                display_df.to_excel(writer, index=False, sheet_name='Filtered Data')
            buffer.seek(0)
            st.download_button(
                label="📥 Download Filtered Data as Excel",
                data=buffer,
                file_name="filtered_agency_pay_chart.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# === Beans → Diamonds Converter Logic ===
def greedy_bean_to_diamond(beans, packages):
    total_diamonds = 0
    remaining = beans
    counts = {}
    for bean_cost, dia_return in sorted(packages, reverse=True):
        if remaining >= bean_cost:
            cnt = remaining // bean_cost
            counts[f"{bean_cost}→{dia_return}"] = cnt
            total_diamonds += cnt * dia_return
            remaining -= cnt * bean_cost
    return total_diamonds, remaining, counts

with tab2:
    st.title("🫘 → 💎 Beans to Diamonds Converter")
    all_packages = {
        "10999 → 3045 Diamonds": (10999, 3045),
        "3999 → 1105 Diamonds":  (3999, 1105),
        "999 → 275 Diamonds":    (999, 275),
        "109 → 29 Diamonds":     (109, 29),
        "8 → 2 Diamonds":        (8, 2),
    }

    st.sidebar.header("Select Conversion Packages")
    selected_labels = st.sidebar.multiselect(
        "Choose tiers to include",
        options=list(all_packages.keys()),
        default=list(all_packages.keys())
    )
    active_packages = [all_packages[label] for label in selected_labels]
    beans = st.number_input("Enter how many Beans you have", min_value=0, value=0, step=1)

    if st.button("Convert Beans → Diamonds"):
        if not active_packages:
            st.warning("Please select at least one package in the sidebar.")
        else:
            diamonds, leftover, breakdown = greedy_bean_to_diamond(beans, active_packages)
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

# === PK Diamond Optimizer Logic ===
pk_data = {
    "Daily PK": [(7000, 210), (10000, 300), (20000, 600), (30000, 900),
                 (50000, 1000), (100000, 1800), (150000, 2700)],
    "Talent PK": [(5000, 150), (10000, 350), (20000, 700), (30000, 1000),
                  (50000, 1700)],
    "Agency 2 vs 2 PK": [(5000, 150), (10000, 300), (25000, 800), (50000, 1700),
                         (70000, 2300), (100000, 3500)],
    "Star Tasks PK": [(2000, 60), (10000, 320), (50000, 1700), (80000, 2800),
                      (100000, 3500), (120000, 4000)]
}

def reward_breakdown(pk_points):
    best_type = None
    best_win = 0
    best_steps = []
    diamonds_used = 0
    remainder = pk_points
    for pk_type, rewards in pk_data.items():
        rewards_sorted = sorted(rewards, reverse=True)
        temp_points = pk_points
        temp_win = 0
        steps = []
        temp_used = 0
        for cost, win in rewards_sorted:
            count = temp_points // cost
            if count:
                temp_points -= count * cost
                temp_win += count * win
                temp_used += count * cost
                steps.append((count, cost, win))
        if temp_win > best_win:
            best_win = temp_win
            best_type = pk_type
            best_steps = steps
            diamonds_used = temp_used // 10
            remainder = temp_points
    return best_type, best_win, best_steps, diamonds_used, remainder

def breakdown_to_dataframe(steps):
    return pd.DataFrame([
        {
            "Matches": count,
            "PK Points Used": count * cost,
            "Win per Match": win,
            "Total Win Points": count * win
        }
        for count, cost, win in steps
    ])

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='PK Breakdown')
    return output.getvalue()

with tab3:
    st.title("💎 PK Diamond Optimizer")
    diamonds = st.number_input("Enter your diamond amount", min_value=0, step=100)

    if st.button("💎 Submit PK Diamond"):
        pk_points = diamonds * 10
        pk_type, win_total, steps, diamonds_used, remainder = reward_breakdown(pk_points)
        df = breakdown_to_dataframe(steps)
        excel_data = convert_df_to_excel(df)

        st.subheader("🎯 Optimization Summary")
        st.markdown(f"**🏆 PK Type:** {pk_type}")
        st.markdown(f"**💎 Diamonds Used:** {diamonds_used}")
        st.markdown(f"**📈 PK Score (Used):** {diamonds_used * 10}")
        st.markdown(f"**🫘 Total Win (Beans):** {win_total}")
        st.markdown(f"**🔸 Unused Diamonds:** {remainder // 10}")

        st.subheader("📊 Reward Breakdown")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            label="📥 Download Breakdown as Excel",
            data=excel_data,
            file_name="PK_Reward_Breakdown.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.caption("All calculations based on max win logic using your available diamonds.")

# === Footer ===
st.markdown("""
<hr style="margin-top: 50px;">
<div style="text-align: center; font-size: 14px; color: #6B4E9B;">
    <strong>Alpha Agency 752</strong> — Streamlined. Strategic. Alpha.<br>
    Contact: info@alphaagency752.com | © 2025
</div>
""", unsafe_allow_html=True)
