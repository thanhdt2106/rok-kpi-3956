import streamlit as st
import pandas as pd

# --- 1. CẤU HÌNH TRANG & GIAO DIỆN HTML/CSS ---
st.set_page_config(page_title="ROK KPI Management 3956", layout="wide")

st.markdown("""
    <style>
    /* Tổng thể */
    .main {
        background-color: #0e1117;
    }
    /* Tiêu đề chính */
    .main-title {
        color: #f29b05;
        font-family: 'Black Ops One', cursive;
        text-align: center;
        text-shadow: 2px 2px #000000;
        font-size: 45px !important;
        margin-bottom: 30px;
    }
    /* Khung thông tin cá nhân */
    .player-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #f29b05;
        margin-bottom: 20px;
    }
    /* Tùy chỉnh Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    /* Tùy chỉnh bảng dữ liệu */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. QUẢN LÝ NGÔN NGỮ ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'Tiếng Việt'

def change_lang():
    st.session_state.lang = st.session_state.lang_select

with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_6uY6xW_u5mK6FzR0f_Z9i9wY8wE-9Fw0wA&s", width=100) # Logo ROK mẫu
    st.title("🌐 SETTINGS")
    st.selectbox("Ngôn ngữ / Language:", ['Tiếng Việt', 'English'], key='lang_select', on_change=change_lang)
    st.divider()
    st.info("Alliance: Fight to Dead\nKingdom: 3956")

texts = {
    'Tiếng Việt': {
        'title': "🛡️ HỆ THỐNG QUẢN LÝ KPI - 3956",
        'search_label': "🔍 Tra cứu thành viên:",
        'search_default': "-- Chọn tên người chơi --",
        'table_header': "📋 BẢNG THỐNG KÊ CHI TIẾT",
        'popup_title': "HỒ SƠ KPI CHIẾN BINH",
        'power_rank': "Mốc Sức Mạnh",
        'kills': "Điểm Tiêu Diệt",
        'deads': "Điểm Chết",
        'increased': "Đã tăng",
        'target': "Mục tiêu",
        'total_progress': "TỔNG TIẾN ĐỘ KPI",
        'tabs': ["Bảng Tổng Hợp", "Top Cống Hiến", "Mốc KPI"],
        'col_name': 'Tên Tài khoản', 'col_id': 'ID', 'col_all': 'Liên minh',
        'col_pow': 'Sức mạnh', 'col_k': 'Điểm tiêu diệt', 'col_d': 'Điểm chết',
        'col_ki': 'Kill tăng', 'col_di': 'Dead tăng', 'col_kpi': '% KPI'
    },
    'English': {
        'title': "🛡️ KPI MANAGEMENT SYSTEM - 3956",
        'search_label': "🔍 Member Lookup:",
        'search_default': "-- Select Player Name --",
        'table_header': "📋 DETAILED STATISTICS TABLE",
        'popup_title': "WARRIOR KPI PROFILE",
        'power_rank': "Power Rank",
        'kills': "Kill Points",
        'deads': "Dead Units",
        'increased': "Increased",
        'target': "Target",
        'total_progress': "TOTAL KPI PROGRESS",
        'tabs': ["Summary Table", "Top Contribution", "KPI Targets"],
        'col_name': 'Account Name', 'col_id': 'ID', 'col_all': 'Alliance',
        'col_pow': 'Power', 'col_k': 'Kill Points', 'col_d': 'Dead Units',
        'col_ki': 'Kill Incr.', 'col_di': 'Dead Incr.', 'col_kpi': '% KPI'
    }
}
L = texts[st.session_state.lang]

# --- 3. KẾT NỐI DỮ LIỆU GOOGLE SHEET ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID_TRUOC = '731741617' # Scan 1
GID_SAU = '371969335'   # Scan 2

URL_TRUOC = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_TRUOC}'
URL_SAU = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_SAU}'

def get_kpi_targets(power):
    if power < 15_000_000: return 10_000_000, 200_000
    elif power < 20_000_000: return 20_000_000, 250_000
    elif power < 30_000_000: return 25_000_000, 300_000
    else: return 30_000_000, 400_000

@st.cache_data(ttl=30)
def load_data():
    try:
        df_t = pd.read_csv(URL_TRUOC).rename(columns=lambda x: x.strip())
        df_s = pd.read_csv(URL_SAU).rename(columns=lambda x: x.strip())
        df_t['ID'] = df_t['ID'].astype(str).str.replace('.0', '', regex=False)
        df_s['ID'] = df_s['ID'].astype(str).str.replace('.0', '', regex=False)
        
        df = pd.merge(df_t.drop_duplicates('ID'), df_s.drop_duplicates('ID'), on='ID', suffixes=('_Dau', '_Cuoi'))
        
        # Ép kiểu số
        cols = ['Sức Mạnh_Cuoi', 'Tổng Tiêu Diệt_Cuoi', 'Điểm Chết_Cuoi', 'Tổng Tiêu Diệt_Dau', 'Điểm Chết_Dau']
        for c in cols: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        df['Tăng Tiêu Diệt'] = df['Tổng Tiêu Diệt_Cuoi'] - df['Tổng Tiêu Diệt_Dau']
        df['Tăng Điểm Chết'] = df['Điểm Chết_Cuoi'] - df['Điểm Chết_Dau']
        
        def calc(row):
            gk, gd = get_kpi_targets(row['Sức Mạnh_Cuoi'])
            pk = max(0, min(row['Tăng Tiêu Diệt'] / gk, 1.0)) if gk > 0 else 0
            pd_v = max(0, min(row['Tăng Điểm Chết'] / gd, 1.0)) if gd > 0 else 0
            return round(((pk + pd_v) / 2) * 100, 1)

        df['% KPI Đạt'] = df.apply(calc, axis=1)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- 4. GIAO DIỆN CHÍNH ---
df_final = load_data()

if df_final is not None:
    st.markdown(f'<h1 class="main-title">{L["title"]}</h1>', unsafe_allow_html=True)
    
    # Khu vực tìm kiếm chuyên nghiệp
    names = sorted([str(x) for x in df_final['Tên_Cuoi'].unique()])
    sel = st.selectbox(L['search_label'], [L['search_default']] + names)
    
    if sel != L['search_default']:
        @st.dialog(L['popup_title'])
        def show_popup(name, df):
            d = df[df['Tên_Cuoi'] == name].iloc[0]
            gk, gd = get_kpi_targets(d['Sức Mạnh_Cuoi'])
            st.markdown(f"""
                <div class="player-card">
                    <h2 style="color:#f29b05;margin:0;">👤 {name}</h2>
                    <p>ID: <code>{d['ID']}</code> | {L['power_rank']}: <b>{int(d['Sức Mạnh_Cuoi']):,}</b></p>
                </div>
            """, unsafe_allow_html=True)
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

    # Hệ thống Tab chuyên nghiệp
    t1, t2, t3 = st.tabs(L['tabs'])
    
    with t1:
        view_df = df_final[['Tên_Cuoi', 'ID', 'Liên Minh_Cuoi', 'Sức Mạnh_Cuoi', 'Tổng Tiêu Diệt_Cuoi', 'Điểm Chết_Cuoi', 'Tăng Tiêu Diệt', 'Tăng Điểm Chết', '% KPI Đạt']].copy()
        view_df.columns = [L['col_name'], L['col_id'], L['col_all'], L['col_pow'], L['col_k'], L['col_d'], L['col_ki'], L['col_di'], L['col_kpi']]
        st.dataframe(view_df.style.format({
            L['col_pow']: '{:,.0f}', L['col_k']: '{:,.0f}', L['col_d']: '{:,.0f}',
            L['col_ki']: '{:,.0f}', L['col_di']: '{:,.0f}', L['col_kpi']: '{:.1f}%'
        }), use_container_width=True, height=500)

    with t2:
        st.subheader("🏆 TOP 10 CONTRIBUTIONS")
        col_kill, col_dead = st.columns(2)
        with col_kill:
            st.write("🔥 **Top Kills Increased**")
            st.table(view_df.sort_values(L['col_ki'], ascending=False).head(10)[[L['col_name'], L['col_ki']]])
        with col_dead:
            st.write("💀 **Top Deads Increased**")
            st.table(view_df.sort_values(L['col_di'], ascending=False).head(10)[[L['col_name'], L['col_di']]])

    with t3:
        st.markdown("""
        ### 📌 Bảng mục tiêu KPI hiện tại
        | Sức mạnh | Điểm Tiêu Diệt | Điểm Chết |
        | :--- | :--- | :--- |
        | < 15M | 10M | 200K |
        | < 20M | 20M | 250K |
        | < 30M | 25M | 300K |
        | > 30M | 30M | 400K |
        """)
