import streamlit as st
from supabase import create_client, Client

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="System Logistyczny PRO", layout="wide", page_icon="🚚")

# --- ZAAWANSOWANA STYLIZACJA UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700;900&display=swap');

    .stApp {
        background-image: url("https://images.unsplash.com/photo-1587293852726-70cdb56c2866?q=80&w=2072");
        background-attachment: fixed;
        background-size: cover;
    }

    /* Ustawienia czcionek dla maksymalnej czytelności */
    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }

    h1, h2, h3 {
        color: #FFFFFF !important;
        text-shadow: 3px 3px 6px #000000 !important;
        font-weight: 900 !important;
        text-transform: uppercase;
    }

    /* Panele - Ciemne szkło */
    div[data-testid="stForm"], div[data-testid="stMetric"], .st-emotion-cache-12w0u9p, div[data-testid="stExpander"] {
        background-color: rgba(0, 0, 0, 0.85) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
    }

    /* Teksty w panelach */
    p, label, span, .stMarkdown {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Przyciski */
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF8F8F) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 900 !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.5);
    }

    /* Personalizacja metryk */
    [data-testid="stMetricValue"] {
        color: #00FF00 !important;
        font-size: 2.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Pobieranie danych
try:
    res_p = supabase.table("produkty").select("*, kategorie(nazwa)").order("id").execute()
    produkty = res_p.data
    res_k = supabase.table("kategorie").select("*").execute()
    kategorie = res_k.data
except:
    produkty, kategorie = [], []

# --- NAGŁÓWEK ---
st.title("🚚 SYSTEM LOGISTYCZNY - CENTRUM OPERACYJNE")

# --- ZAKŁADKI ---
tab_dashboard, tab_magazyn, tab_dostawy, tab_kategorie, tab_raporty = st.tabs([
    "📊 PULPIT ANALITYCZNY", 
    "📦 STAN MAGAZYNU", 
    "🚛 NOWA DOSTAWA", 
    "🗂️ SEKCJE",
    "📄 RAPORTY"
])

# --- ZAKŁADKA: PULPIT (Wykresy) ---
with tab_dashboard:
    if produkty:
        c1, c2, c3 = st.columns(3)
        t_qty = sum(i['liczba'] for i in produkty)
        t_val = sum(
