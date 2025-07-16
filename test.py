import pandas as pd
import streamlit as st
import io

def load_pk_rewards(file_path, sheet_name="rules and rewards"):
    """Safely load and validate PK rewards sheet from Excel"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.rename(columns=lambda x: str(x).strip(), inplace=True)
    except Exception as e:
        st.error(f"❌ Failed to load sheet '{sheet_name}' from '{file_path}': {e}")
        return None

    columns = df.columns.tolist()

    if "PK Type" not in columns:
        st.error("❌ Column 'PK Type' not found in sheet.")
        st.write("Available columns:", columns)
        return None

    win_columns = [col for col in columns if "Win" in col]
    if not win_columns:
        st.error("❌ No 'Win' columns found in sheet.")
        st.write("Available columns:", columns)
        return None

    df["Max Win"] = df[win_columns].max(axis=1)
    reward_table = df[["PK Type", "Max Win"]].dropna().sort_values(by="Max Win", ascending=False).reset_index(drop=True)

    return reward_table


def export_excel(df, sheet_name="Filtered Data"):
    """Convert a DataFrame to a downloadable Excel file"""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buffer.seek(0)
    return buffer


def style_buttons():
    """Inject custom CSS styles for dashboard buttons"""
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