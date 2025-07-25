import streamlit as st
import pandas as pd
from PIL import Image
import io
import numpy as np

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
@st.cache_data
def load_dataset():
    """Load and cache the Excel dataset"""
    try:
        df = pd.read_excel("Alpha_Omega_Agency_Pay_Chart_with_Diamonds.xlsx", sheet_name="Sheet1")
        # Clean column names - remove extra spaces
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("Data file 'Alpha_Omega_Agency_Pay_Chart_with_Diamonds.xlsx' not found.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load data file: {e}")
        st.stop()

# Load data once at startup
if 'df' not in st.session_state:
    st.session_state.df = load_dataset()

df = st.session_state.df

# === Preprocess: Add Bean-to-USD Conversion ===
try:
    if 'Broadcaster Remuneration (USD)' in df.columns and 'Target Beans' in df.columns:
        # Safely handle division by zero
        df['Bean_to_USD_Rate'] = np.where(
            df['Target Beans'] != 0,
            df['Broadcaster Remuneration (USD)'] / df['Target Beans'],
            0
        )
    else:
        st.warning("Missing columns for Bean-to-USD conversion. Available columns: " + ", ".join(df.columns))
except Exception as e:
    st.warning(f"Error in Bean-to-USD conversion: {e}")

# === Styling ===
st.markdown("""
    <style>
    div.stDownloadButton > button {
        background-color: #6B4E9B;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 8px 20px;
        border: none;
    }
    div.stDownloadButton > button:hover {
        background-color: #553B7A;
        color: #FFDDEE;
    }
    .main > div {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# === Helper Functions ===
def create_excel_download(dataframe, sheet_name='Sheet1'):
    """Create Excel file for download with error handling"""
    if dataframe is None or dataframe.empty:
        st.error("No data to export")
        return None
    
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name=sheet_name)
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error creating Excel file: {e}")
        return None

def greedy_bean_to_diamond(beans, packages):
    """Convert beans to diamonds using greedy algorithm with validation"""
    if not packages or beans <= 0:
        return 0, beans, {}
    
    total_diamonds = 0
    remaining = int(beans)
    counts = {}
    
    try:
        for bean_cost, dia_return in sorted(packages, reverse=True, key=lambda x: x[0]):
            if remaining >= bean_cost:
                cnt = remaining // bean_cost
                if cnt > 0:
                    counts[f"{bean_cost}→{dia_return}"] = cnt
                    total_diamonds += cnt * dia_return
                    remaining -= cnt * bean_cost
    except Exception as e:
        st.error(f"Error in bean conversion: {e}")
        return 0, beans, {}
    
    return total_diamonds, remaining, counts

def reward_breakdown(pk_points):
    """Calculate optimal PK reward breakdown with validation"""
    if pk_points <= 0:
        return None, 0, [], 0, pk_points
    
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
    
    best_type = None
    best_win = 0
    best_steps = []
    diamonds_used = 0
    remainder = pk_points
    
    try:
        for pk_type, rewards in pk_data.items():
            rewards_sorted = sorted(rewards, reverse=True, key=lambda x: x[0])
            temp_points = pk_points
            temp_win = 0
            steps = []
            temp_used = 0
            
            for cost, win in rewards_sorted:
                if temp_points >= cost:
                    count = temp_points // cost
                    if count > 0:
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
    except Exception as e:
        st.error(f"Error in PK calculation: {e}")
        return None, 0, [], 0, pk_points
    
    return best_type, best_win, best_steps, diamonds_used, remainder

# === Initialize Session State ===
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 0

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["📊 Filtered Pay Chart", "🫘→💎 Beans to Diamonds", "💎 PK Diamond Optimizer"])

# === TAB 1: Filtered Pay Chart ===
with tab1:
    st.session_state.current_tab = 1
    
    # Clear sidebar
    with st.sidebar:
        st.header("🔎 Filter Criteria")
        
        # Check if required columns exist
        required_columns = ['Ranking', 'Salary in Beans', 'Convertible Diamonds']
        available_columns = [col for col in required_columns if col in df.columns]
        
        if not available_columns:
            
        
        # Rank filter
        selected_ranks = []
        if 'Ranking' in df.columns:
            try:
                rank_options = sorted([r for r in df['Ranking'].dropna().unique() if pd.notna(r)])
                if rank_options:
                    selected_ranks = st.multiselect(
                        "Select Rank(s)", 
                        rank_options, 
                        default=rank_options[:min(5, len(rank_options))],  # Limit default selection
                        key="tab1_ranks"
                    )
            except Exception as e:
                st.error(f"Error processing rankings: {e}")

        # Salary filter
        salary_range = (0, 0)
        if 'Salary in Beans' in df.columns:
            try:
                salary_col = df['Salary in Beans'].dropna()
                if not salary_col.empty:
                    min_salary = int(salary_col.min())
                    max_salary = int(salary_col.max())
                    if min_salary < max_salary:
                        salary_range = st.slider(
                            "Salary in Beans Range", 
                            min_salary, 
                            max_salary, 
                            (min_salary, max_salary), 
                            step=max(1000, (max_salary - min_salary) // 100),
                            key="tab1_salary"
                        )
            except Exception as e:
                st.error(f"Error processing salary data: {e}")

        # Diamonds filter
        diamonds_range = (0, 0)
        if 'Convertible Diamonds' in df.columns:
            try:
                diamonds_col = df['Convertible Diamonds'].dropna()
                if not diamonds_col.empty:
                    min_diamonds = int(diamonds_col.min())
                    max_diamonds = int(diamonds_col.max())
                    if min_diamonds < max_diamonds:
                        diamonds_range = st.slider(
                            "Convertible Diamonds Range", 
                            min_diamonds, 
                            max_diamonds, 
                            (min_diamonds, max_diamonds), 
                            step=max(1000, (max_diamonds - min_diamonds) // 100),
                            key="tab1_diamonds"
                        )
            except Exception as e:
                st.error(f"Error processing diamonds data: {e}")

    st.title("📊 Filtered Pay Chart")
    
    # Apply filters safely
    try:
        filtered_df = df.copy()
        
        if selected_ranks and 'Ranking' in df.columns:
            filtered_df = filtered_df[filtered_df['Ranking'].isin(selected_ranks)]
        
        if 'Salary in Beans' in df.columns and salary_range != (0, 0):
            filtered_df = filtered_df[
                filtered_df['Salary in Beans'].between(salary_range[0], salary_range[1])
            ]
        
        if 'Convertible Diamonds' in df.columns and diamonds_range != (0, 0):
            filtered_df = filtered_df[
                filtered_df['Convertible Diamonds'].between(diamonds_range[0], diamonds_range[1])
            ]

        # Display results
        if filtered_df.empty:
            st.warning("No matching data found. Try adjusting your filters.")
        else:
            st.success(f"Showing {len(filtered_df)} result(s) based on filters:")
            
            # Prepare display dataframe
            columns_to_exclude = ['Effective Broadcasting Limit', 'Billable Hours Limit', 'Bean_to_USD_Rate']
            display_df = filtered_df.drop(columns=[col for col in columns_to_exclude if col in filtered_df.columns])
            
            st.dataframe(display_df, use_container_width=True)

            # Download button
            excel_data = create_excel_download(display_df, 'Filtered Data')
            if excel_data:
                st.download_button(
                    label="📥 Download Filtered Data as Excel",
                    data=excel_data,
                    file_name="filtered_agency_pay_chart.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="tab1_download"
                )
    except Exception as e:
        st.error(f"Error filtering data: {e}")

# === TAB 2: Beans to Diamonds Converter ===
with tab2:
    st.session_state.current_tab = 2
    
    st.title("🫘 → 💎 Beans to Diamonds Converter")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        
        # Package options
        all_packages = {
            "10999 → 3045 Diamonds": (10999, 3045),
            "3999 → 1105 Diamonds": (3999, 1105),
            "999 → 275 Diamonds": (999, 275),
            "109 → 29 Diamonds": (109, 29),
            "8 → 2 Diamonds": (8, 2),
        }
        
        selected_labels = st.multiselect(
            "Choose conversion packages:",
            options=list(all_packages.keys()),
            default=list(all_packages.keys()),
            key="tab2_packages"
        )
        
        beans_input = st.number_input(
            "Enter Beans amount:", 
            min_value=0, 
            value=0, 
            step=1,
            key="tab2_beans",
            help="Enter the number of beans you want to convert"
        )
        
        convert_button = st.button("🔄 Convert Beans → Diamonds", key="tab2_convert")
    
    with col2:
        st.subheader("Results")
        
        if convert_button:
            if not selected_labels:
                st.warning("Please select at least one conversion package.")
            elif beans_input <= 0:
                st.warning("Please enter a valid number of beans.")
            else:
                try:
                    active_packages = [all_packages[label] for label in selected_labels]
                    diamonds, leftover, breakdown = greedy_bean_to_diamond(beans_input, active_packages)
                    
                    # Display metrics
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("💎 Total Diamonds", f"{diamonds:,}")
                    with col_b:
                        st.metric("🫘 Beans Leftover", f"{leftover:,}")
                    
                    # Display breakdown
                    if breakdown:
                        st.subheader("📊 Conversion Breakdown")
                        breakdown_data = []
                        for pkg, cnt in breakdown.items():
                            try:
                                parts = pkg.split('→')
                                cost = int(parts[0])
                                diamonds_gained = int(parts[1])
                                breakdown_data.append({
                                    "Package": pkg,
                                    "Times Used": cnt,
                                    "Total Cost": cost * cnt,
                                    "Diamonds Gained": diamonds_gained * cnt
                                })
                            except (ValueError, IndexError):
                                continue
                        
                        if breakdown_data:
                            breakdown_df = pd.DataFrame(breakdown_data)
                            st.dataframe(breakdown_df, use_container_width=True)
                            
                            # Download breakdown
                            excel_data = create_excel_download(breakdown_df, 'Beans to Diamonds Breakdown')
                            if excel_data:
                                st.download_button(
                                    label="📥 Download Breakdown as Excel",
                                    data=excel_data,
                                    file_name="Beans_to_Diamonds_Breakdown.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="tab2_download"
                                )
                    else:
                        st.info("Not enough beans to use any selected packages.")
                except Exception as e:
                    st.error(f"Error in conversion: {e}")

# === TAB 3: PK Diamond Optimizer ===
with tab3:
    st.session_state.current_tab = 3
    
    st.title("💎 PK Diamond Optimizer")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Input")
        diamonds_input = st.number_input(
            "Enter diamond amount:", 
            min_value=0, 
            step=100,
            key="tab3_diamonds",
            help="Enter the number of diamonds you want to optimize"
        )
        
        optimize_button = st.button("⚡ Optimize PK Strategy", key="tab3_optimize")
    
    with col2:
        st.subheader("Optimization Results")
        
        if optimize_button:
            if diamonds_input <= 0:
                st.warning("Please enter a valid number of diamonds.")
            else:
                try:
                    pk_points = diamonds_input * 10
                    pk_type, win_total, steps, diamonds_used, remainder = reward_breakdown(pk_points)
                    
                    if pk_type:
                        # Summary
                        st.markdown("### 🎯 Optimization Summary")
                        summary_data = {
                            "🏆 Best PK Type": pk_type,
                            "💎 Diamonds Used": f"{diamonds_used:,}",
                            "📈 PK Points Used": f"{diamonds_used * 10:,}",
                            "🫘 Total Beans Won": f"{win_total:,}",
                            "🔸 Unused Diamonds": f"{remainder // 10:,}"
                        }
                        
                        for key, value in summary_data.items():
                            st.markdown(f"**{key:
