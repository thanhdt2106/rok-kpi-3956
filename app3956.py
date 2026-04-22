import streamlit as st
import pandas as pd

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI Management 3956", layout="wide")

# --- QUẢN LÝ NGÔN NGỮ ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'Tiếng Việt'

def change_lang():
    if st.session_state.lang_select == 'Tiếng Việt':
        st.session_state.lang = 'Tiếng Việt'
    else:
        st.session_state.lang = 'English'

with st.sidebar:
    st.title("🌐 Language / Ngôn ngữ")
    st.selectbox("Chọn ngôn ngữ:", ['Tiếng Việt', 'English'], key='lang_select', on_change=change_lang)

# Từ điển đa ngôn ngữ
texts = {
    'Tiếng Việt': {
        'title': "🛡️ HỆ THỐNG QUẢN LÝ KPI KINGDOM 3956",
        'search_label': "🔍 Tra cứu chi tiết thành viên:",
        'search_default': "-- Chọn tên --",
        'table_header': "📋 Bảng Tổng Hợp Dữ Liệu",
        'popup_title': "Chi tiết tiến độ KPI",
        'power_rank': "Phân hạng sức mạnh",
        'kills': "Tiêu Diệt",
        'deads': "Điểm Chết",
        'increased': "Tăng",
        'target': "Mục tiêu",
        'total_progress': "Tổng tiến độ KPI",
        'col_name': 'Tên Tài khoản',
        'col_id': 'ID',
        'col_alliance': 'Liên minh',
        'col_power': 'Sức mạnh',
        'col_kill': 'điểm tiêu diệt',
        'col_dead': 'điểm chết',
        'col_kill_inc': 'điểm tiêu diệt đã tăng',
        'col_dead_inc': 'điểm chết đã tăng',
        'col_kpi': '% KPI đã đạt',
        'error_load': "Lỗi hệ thống khi tải dữ liệu",
        'loading': "Đang tải dữ liệu..."
    },
    'English': {
        'title': "🛡️ KINGDOM 3956 KPI MANAGEMENT SYSTEM",
        'search_label': "🔍 Member Detailed Lookup:",
        'search_default': "-- Select Name --",
        'table_header': "📋 Data Summary Table",
        'popup_title': "KPI Progress Details",
        'power_rank': "Power Rank",
        'kills': "Kill Points",
        'deads': "Dead Units",
        'increased': "Increased",
        'target': "Target",
        'total_progress': "Total KPI Progress",
        'col_name': 'Account Name',
        'col_id': 'ID',
        'col_alliance': 'Alliance',
        'col_power': 'Power',
        'col_kill': 'Kill Points',
        'col_dead': 'Dead Units',
        'col_kill_inc': 'Kill Points Increased',
        'col_dead_inc': 'Dead Units Increased',
        'col_kpi': '% KPI Achieved',
        'error_load': "System error while loading data",
        'loading': "Loading data..."
    }
}

L = texts[st.session_state.lang]

# --- KẾT NỐI DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID_TRUOC = '731741617'        
GID_SAU = '371969335'

URL_TRUOC = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_TRUOC}'
URL_SAU = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_SAU}'

def get_kpi_targets(power):
    if power < 15_000_000: goal_dead, goal_kill = 200_000, 10_000_000
    elif power < 20_000_000: goal_dead, goal_kill = 250_000, 20_000_000
    elif power < 30_000_000: goal_dead, goal_kill = 300_000, 25_000_000
    else: goal_dead, goal_kill = 400_000, 30_000_000
    return goal_kill, goal_dead

@st.cache_data(ttl=60)
def load_data():
    try:
        df_t = pd.read_csv(URL_TRUOC)
        df_s = pd.read_csv(URL_SAU)
        df_t.columns = df_t.columns.str.strip()
        df_s.columns = df_s.columns.str.strip()
        df_t['ID'] = df_t['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        df_s['ID'] = df_s['ID'].astype(str).str.strip().str.replace('.0', '', regex=False)
        
        df = pd.merge(df_t.drop_duplicates('ID'), df_s.drop_duplicates('ID'), on='ID', suffixes=('_Dau', '_Cuoi'))
        
        cols_to_fix = ['Sức Mạnh_Cuoi', 'Tổng Tiêu Diệt_Cuoi', 'Điểm Chết_Cuoi', 'Tổng Tiêu Diệt_Dau', 'Điểm Chết_Dau']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Tăng Tiêu Diệt'] = df['Tổng Tiêu Diệt_Cuoi'] - df['Tổng Tiêu Diệt_Dau']
        df['Tăng Điểm Chết'] = df['Điểm Chết_Cuoi'] - df['Điểm Chết_Dau']
        
        def calculate_progress(row):
            gk, gd = get_kpi_targets(row['Sức Mạnh_Cuoi'])
            pk = max(0, min(row['Tăng Tiêu Diệt'] / gk, 1.0)) if gk > 0 else 0
            pd_val = max(0, min(row['Tăng Điểm Chết'] / gd, 1.0)) if gd > 0 else 0
            return round(((pk + pd_val) / 2) * 100, 1)

        df['% KPI Đạt'] = df.apply(calculate_progress, axis=1)
        return df
    except Exception as e:
        st.error(f"{L['error_load']}: {e}")
        return None

# --- GIAO DIỆN ---
df_final = load_data()

if df_final is not None:
    st.title(L['title'])
    
    # Popup logic
    names = sorted([str(x) for x in df_final['Tên_Cuoi'].unique()])
    sel = st.selectbox(L['search_label'], [L['search_default']] + names)
    
    if sel != L['search_default']:
        @st.dialog(L['popup_title'])
        def show_popup(name, df):
            d = df[df['Tên_Cuoi'] == name].iloc[0]
            gk, gd = get_kpi_targets(d['Sức Mạnh_Cuoi'])
            st.markdown(f"### 👤 {name}")
            st.write(f"{L['power_rank']}: **{int(d['Sức Mạnh_Cuoi']):,}**")
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"⚔️ **{L['kills']}**")
                st.write(f"{L['increased']}: {int(d['Tăng Tiêu Diệt']):,}")
                st.progress(max(0, min(d['Tăng Tiêu Diệt']/gk, 1.0)) if gk > 0 else 0)
                st.caption(f"{L['target']}: {gk:,}")
            with c2:
                st.write(f"💀 **{L['deads']}**")
                st.write(f"{L['increased']}: {int(d['Tăng Điểm Chết']):,}")
                st.progress(max(0, min(d['Tăng Điểm Chết']/gd, 1.0)) if gd > 0 else 0)
                st.caption(f"{L['target']}: {gd:,}")
            st.metric(L['total_progress'], f"{d['% KPI Đạt']}%")
        
        show_popup(sel, df_final)

    st.divider()
    st.subheader(L['table_header'])
    
    # Chuẩn bị bảng
    view_df = df_final[['Tên_Cuoi', 'ID', 'Liên Minh_Cuoi', 'Sức Mạnh_Cuoi', 'Tổng Tiêu Diệt_Cuoi', 'Điểm Chết_Cuoi', 'Tăng Tiêu Diệt', 'Tăng Điểm Chết', '% KPI Đạt']].copy()
    view_df.columns = [L['col_name'], L['col_id'], L['col_alliance'], L['col_power'], L['col_kill'], L['col_dead'], L['col_kill_inc'], L['col_dead_inc'], L['col_kpi']]
    
    st.dataframe(
        view_df.style.format({
            L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}',
            L['col_kill_inc']: '{:,.0f}', L['col_dead_inc']: '{:,.0f}', L['col_kpi']: '{:.1f}%'
        }), use_container_width=True, height=600
    )
