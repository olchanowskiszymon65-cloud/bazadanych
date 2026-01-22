import streamlit as st
from supabase import create_client, Client

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Magazyn Pro", layout="wide")

# --- STYLIZACJA (Maksymalna czytelność) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.93), rgba(255, 255, 255, 0.93)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    /* Ciemna czcionka dla kontrastu */
    h1, h2, h3, span, label, p {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    .stMetric {
        background-color: #ffffff !important;
        border: 2px solid #eeeeee;
        border-radius: 10px;
    }
    div[data-testid="stExpander"], div[data-testid="stForm"] {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Pobieranie danych bezpośrednio z Supabase
try:
    res_p = supabase.table("produkty").select("*, kategorie(nazwa)").order("id").execute()
    produkty = res_p.data
    res_k = supabase.table("kategorie").select("*").execute()
    kategorie = res_k.data
except:
    produkty, kategorie = [], []

# --- NAGŁÓWEK ---
st.title("🛡️ Panel Administracyjny Magazynu")

if produkty:
    # Proste statystyki bez pandas
    total_qty = sum(item['liczba'] for item in produkty)
    total_val = sum(item['liczba'] * item['cena'] for item in produkty)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("📦 Liczba pozycji", len(produkty))
    col_m2.metric("🔢 Łączny stan", f"{total_qty} szt.")
    col_m3.metric("💰 Wartość towaru", f"{total_val:,.2f} zł")

    # Wykresy natywne (Streamlit)
    st.subheader("📊 Wykres stanów magazynowych")
    chart_data = {item['nazwa']: item['liczba'] for item in produkty}
    st.bar_chart(chart_data)

st.markdown("---")

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["🛒 Zarządzanie Towarem", "📂 Kategorie"])

with tab1:
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("➕ Dodaj produkt")
        kat_map = {k['nazwa']: k['id'] for k in kategorie}
        with st.form("add_p"):
            name = st.text_input("Nazwa produktu")
            qty = st.number_input("Ilość", min_value=0)
            price = st.number_input("Cena (zł)", min_value=0.0)
            cat = st.selectbox("Kategoria", options=list(kat_map.keys()))
            if st.form_submit_button("Zapisz do bazy") and name:
                supabase.table("produkty").insert({
                    "nazwa": name, "liczba": qty, "cena": price, "kategoria_id": kat_map[cat]
                }).execute()
                st.rerun()

    with c2:
        st.subheader("📋 Stan magazynu")
        for p in produkty:
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([3, 2, 1])
                k_name = p['kategorie']['nazwa'] if p.get('kategorie') else "Brak"
                col_a.write(f"**{p['nazwa']}**\n\nKat: {k_name}")
                col_b.write(f"{p['liczba']} szt. x {p['cena']} zł")
                if col_c.button("Usuń", key=f"d_{p['id']}"):
                    supabase.table("produkty").delete().eq("id", p["id"]).execute()
                    st.rerun()

with tab2:
    st.subheader("Kategorie")
    ck1, ck2 = st.columns([1, 2])
    with ck1:
        with st.form("add_k"):
            new_k = st.text_input("Nazwa nowej kategorii")
            if st.form_submit_button("Dodaj") and new_k:
                supabase.table("kategorie").insert({"nazwa": new_k}).execute()
                st.rerun()
    with ck2:
        for k in kategorie:
            st.code(f"📁 {k['nazwa']}")
