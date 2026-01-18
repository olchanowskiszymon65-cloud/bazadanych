import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Panel Magazynowy", layout="wide", page_icon="📦")

# --- STYLIZACJA TŁA (Magazyn w tle) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    [data-testid="stExpander"], [data-testid="stForm"], .st-emotion-cache-12w0u9p {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Pobieranie danych
res_prod = supabase.table("produkty").select("*, kategorie(nazwa)").order("id").execute()
df_prod = pd.DataFrame(res_prod.data)
res_kat = supabase.table("kategorie").select("*").execute()
kat_list = res_kat.data

# --- NAGŁÓWEK I STATYSTYKI ---
st.title("🏭 Zarządzanie Zasobami Magazynu")

if not df_prod.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Pozycje", len(df_prod))
    m2.metric("🔢 Łączna ilość", int(df_prod['liczba'].sum()))
    m3.metric("💰 Wartość netto", f"{sum(df_prod['liczba'] * df_prod['cena']):,.2f} zł")

    st.subheader("📊 Stan zapasów")
    st.bar_chart(df_prod, x="nazwa", y="liczba", color="#1f77b4")

# --- ZAKŁADKI ---
tab1, tab2 = st.tabs(["📝 Ewidencja Produktów", "🗂️ Kategorie"])

# --- TAB 1: PRODUKTY ---
with tab1:
    col_f, col_l = st.columns([1, 2])

    with col_f:
        st.write("### ➕ Nowy Produkt")
        k_opts = {k["nazwa"]: k["id"] for k in kat_list}
        with st.form("p_form", clear_on_submit=True):
            n = st.text_input("Nazwa towaru")
            l = st.number_input("Ilość", min_value=0)
            c = st.number_input("Cena jedn.", min_value=0.0)
            k = st.selectbox("Wybierz kategorię", options=list(k_opts.keys()))
            if st.form_submit_button("Dodaj do kartoteki") and n:
                supabase.table("produkty").insert({"nazwa": n, "liczba": l, "cena": c, "kategoria_id": k_opts[k]}).execute()
                st.rerun()

    with col_l:
        st.write("### 📋 Aktualna Lista")
        if not df_prod.empty:
            for _, r in df_prod.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    kn = r['kategorie']['nazwa'] if r.get('kategorie') else "Niezdefiniowana"
                    c1.write(f"**{r['nazwa']}**\n\n*{kn}*")
                    c2.write(f"**{r['liczba']}** szt. | **{r['cena']}** zł")
                    if c3.button("🗑️", key=f"del_{r['id']}"):
                        supabase.table("produkty").delete().eq("id", r["id"]).execute()
                        st.rerun()

# --- TAB 2: KATEGORIE ---
with tab2:
    st.write("### 📂 Zarządzanie strukturą kategorii")
    ck1, ck2 = st.columns([1, 2])
    
    with ck1:
        with st.form("k_form"):
            nk = st.text_input("Nowa kategoria")
            if st.form_submit_button("Dodaj kategorię") and nk:
                supabase.table("kategorie").insert({"nazwa": nk}).execute()
                st.rerun()

    with ck2:
        for kt in kat_list:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                col1.write(f"📁 **{kt['nazwa']}**")
                if col2.button("Usuń", key=f"kdel_{kt['id']}"):
                    supabase.table("kategorie").delete().eq("id", kt["id"]).execute()
                    st.rerun()
                   
