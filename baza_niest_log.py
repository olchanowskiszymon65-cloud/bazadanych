import streamlit as st
from supabase import create_client, Client

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Warehouse Pro", layout="wide", page_icon="📦")

# --- DARK UI & CLEAR BACKGROUND (Wyraźne tło, ciemne panele) ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1553413077-190dd305871c?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    
    /* Stylizacja nagłówków */
    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }

    /* Przezroczyste, ciemne panele (Glassmorphism) */
    div[data-testid="stForm"], div[data-testid="stMetric"], .st-emotion-cache-12w0u9p, div[data-testid="stExpander"] {
        background-color: rgba(30, 30, 30, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(5px);
        color: white !important;
    }

    /* Napisy wewnątrz paneli */
    p, label, span {
        color: #eeeeee !important;
    }

    /* Stylizacja przycisków */
    .stButton>button {
        background-color: #2e7d32 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    /* Tabela danych */
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.05);
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
st.title("📦 System Logistyczny - Magazyn Główny")

# --- STATYSTYKI ---
if produkty:
    t_qty = sum(i['liczba'] for i in produkty)
    t_val = sum(i['liczba'] * i['cena'] for i in produkty)
    
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("📦 Pozycje", len(produkty))
    with m2: st.metric("🔢 Łączna ilość", f"{t_qty} szt.")
    with m3: st.metric("💰 Wartość zasobów", f"{t_val:,.2f} zł")

    st.subheader("📊 Podgląd stanów towarowych")
    c_data = {i['nazwa']: i['liczba'] for i in produkty}
    st.bar_chart(c_data, color="#4CAF50")

st.markdown("---")

# --- ZAKŁADKI ---
tab_mag, tab_kat = st.tabs(["🏗️ Zarządzaj Magazynem", "⚙️ Konfiguracja"])

with tab_mag:
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("➕ Przyjmij towar")
        k_map = {k['nazwa']: k['id'] for k in kategorie}
        with st.form("new_p"):
            name = st.text_input("Nazwa artykułu")
            qty = st.number_input("Ilość", min_value=0)
            price = st.number_input("Cena", min_value=0.0)
            cat = st.selectbox("Kategoria", options=list(k_map.keys()))
            if st.form_submit_button("DODAJ DO STANU"):
                if name:
                    supabase.table("produkty").insert({"nazwa": name, "liczba": qty, "cena": price, "kategoria_id": k_map[cat]}).execute()
                    st.rerun()

    with col_right:
        st.subheader("📋 Inventaryzacja")
        for p in produkty:
            with st.container(border=True):
                ca, cb, cc = st.columns([3, 2, 1])
                k_label = p['kategorie']['nazwa'] if p.get('kategorie') else "Ogólna"
                ca.write(f"### {p['nazwa']}\n*{k_label}*")
                cb.write(f"**Stan:** {p['liczba']} szt.\n**Cena:** {p['cena']} zł")
                if cc.button("Usuń", key=f"del_{p['id']}"):
                    supabase.table("produkty").delete().eq("id", p["id"]).execute()
                    st.rerun()

with tab_kat:
    st.subheader("Sekcje Magazynowe")
    ck1, ck2 = st.columns([1, 2])
    with ck1:
        with st.form("new_k"):
            n_k = st.text_input("Nazwa nowej sekcji")
            if st.form_submit_button("Utwórz"):
                if n_k:
                    supabase.table("kategorie").insert({"nazwa": n_k}).execute()
                    st.rerun()
    with ck2:
        for k in kategorie:
            st.info(f"📂 Sekcja: {k['nazwa']}")
