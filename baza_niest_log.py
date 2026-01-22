import streamlit as st
from supabase import create_client, Client

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Magazyn & Logistyka", layout="wide", page_icon="🚚")

# --- STYLIZACJA (Wyraźne tło i czarny tekst) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.75)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Czcionki - czarne i pogrubione dla widoczności */
    h1, h2, h3, p, label, span, .stMarkdown {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    /* Białe, nieprzezroczyste panele dla formularzy i list */
    div[data-testid="stExpander"], div[data-testid="stForm"], .st-emotion-cache-12w0u9p {
        background-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        border-radius: 15px !important;
    }
    /* Stylizacja metryk */
    [data-testid="stMetricValue"] {
        color: #d32f2f !important; /* Czerwony akcent dla liczb */
    }
    .stMetric {
        background-color: #FFFFFF !important;
        border: 2px solid #000000;
        border-radius: 12px;
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

# --- NAGŁÓWEK Z IKONĄ ---
st.title("🚚 System Logistyczny - Magazyn Główny")

if produkty:
    # Statystyki
    t_qty = sum(i['liczba'] for i in produkty)
    t_val = sum(i['liczba'] * i['cena'] for i in produkty)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Pozycje", len(produkty))
    m2.metric("🔢 Ilość całkowita", f"{t_qty} szt.")
    m3.metric("💰 Wartość zasobów", f"{t_val:,.2f} zł")

    # Wykres
    st.subheader("📊 Podgląd stanów towarowych")
    c_data = {i['nazwa']: i['liczba'] for i in produkty}
    st.bar_chart(c_data, color="#d32f2f")

st.markdown("---")

# --- ZAKŁADKI ---
t1, t2 = st.tabs(["🏗️ Zarządzanie Magazynem", "🗂️ Konfiguracja Kategorii"])

with t1:
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("➕ Przyjmij towar")
        k_map = {k['nazwa']: k['id'] for k in kategorie}
        with st.form("new_product_form", clear_on_submit=True):
            name = st.text_input("Nazwa artykułu")
            qty = st.number_input("Ilość dostawy", min_value=0)
            price = st.number_input("Cena zakupu", min_value=0.0)
            cat = st.selectbox("Kategoria", options=list(k_map.keys()))
            if st.form_submit_button("➕ DODAJ DO STANU"):
                if name:
                    supabase.table("produkty").insert({
                        "nazwa": name, "liczba": qty, "cena": price, "kategoria_id": k_map[cat]
                    }).execute()
                    st.rerun()

    with col_b:
        st.subheader("📋 Inwentaryzacja")
        for p in produkty:
            with st.container(border=True):
                ca, cb, cc = st.columns([3, 2, 1])
                kn = p['kategorie']['nazwa'] if p.get('kategorie') else "Ogólna"
                ca.write(f"### {p['nazwa']}\n*{kn}*")
                cb.write(f"**Stan:** {p['liczba']} szt.\n\n**Cena:** {p['cena']} zł")
                if cc.button("Usuń", key=f"del_{p['id']}"):
                    supabase.table("produkty").delete().eq("id", p["id"]).execute()
                    st.rerun()

with t2:
    st.subheader("Zarządzanie strukturą")
    ck1, ck2 = st.columns([1, 2])
    with ck1:
        with st.form("new_kat"):
            n_k = st.text_input("Nazwa nowej sekcji/kategorii")
            if st.form_submit_button("Utwórz"):
                if n_k:
                    supabase.table("kategorie").insert({"nazwa": n_k}).execute()
                    st.rerun()
    with ck2:
        for k in kategorie:
            st.success(f"📂 Sekcja: {k['nazwa']}")
