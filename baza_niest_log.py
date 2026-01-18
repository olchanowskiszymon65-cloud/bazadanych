import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Panel Magazynowy", layout="wide", page_icon="📦")

# Pobieranie danych
res_prod = supabase.table("produkty").select("*, kategorie(nazwa)").order("id").execute()
df_prod = pd.DataFrame(res_prod.data)
res_kat = supabase.table("kategorie").select("*").execute()
kat_list = res_kat.data

# --- NAGŁÓWEK I STATYSTYKI ---
st.title("📊 System Zarządzania Magazynem")

if not df_prod.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Wszystkie Produkty", len(df_prod))
    m2.metric("Suma Sztuk", int(df_prod['liczba'].sum()))
    m3.metric("Wartość (PLN)", f"{sum(df_prod['liczba'] * df_prod['cena']):,.2f}")

    # Wykres w tle
    st.subheader("Stan ilościowy produktów")
    st.bar_chart(df_prod, x="nazwa", y="liczba", color="#0083B8")

# --- PODZIAŁ NA ZAKŁADKI ---
tab1, tab2 = st.tabs(["📦 Produkty", "📂 Kategorie"])

# --- ZAKŁADKA: PRODUKTY ---
with tab1:
    col_form, col_list = st.columns([1, 2])

    with col_form:
        st.subheader("Dodaj Produkt")
        kat_options = {k["nazwa"]: k["id"] for k in kat_list}
        
        with st.form("add_product", clear_on_submit=True):
            n = st.text_input("Nazwa")
            l = st.number_input("Ilość", min_value=0, step=1)
            c = st.number_input("Cena", min_value=0.0, format="%.2f")
            k = st.selectbox("Kategoria", options=list(kat_options.keys()))
            
            if st.form_submit_button("Dodaj do bazy") and n:
                supabase.table("produkty").insert({
                    "nazwa": n, "liczba": l, "cena": c, "kategoria_id": kat_options[k]
                }).execute()
                st.rerun()

    with col_list:
        st.subheader("Lista Magazynowa")
        if not df_prod.empty:
            for _, row in df_prod.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    kat_n = row['kategorie']['nazwa'] if row.get('kategorie') else "Brak"
                    c1.write(f"**{row['nazwa']}** ({kat_n})")
                    c2.write(f"{row['liczba']} szt. / {row['cena']} zł")
                    if c3.button("Usuń", key=f"p_{row['id']}"):
                        supabase.table("produkty").delete().eq("id", row["id"]).execute()
                        st.rerun()

# --- ZAKŁADKA: KATEGORIE ---
with tab2:
    st.subheader("Zarządzanie Kategoriami")
    c_k1, c_k2 = st.columns([1, 2])

    with c_k1:
        with st.form("add_kat", clear_on_submit=True):
            n_k = st.text_input("Nazwa nowej kategorii")
            o_k = st.text_area("Opis")
            if st.form_submit_button("Dodaj") and n_k:
                supabase.table("kategorie").insert({"nazwa": n_k, "opis": o_k}).execute()
                st.rerun()

    with c_k2:
        for kat in kat_list:
            with st.container(border=True):
                ck1, ck2 = st.columns([4, 1])
                ck1.write(f"**{kat['nazwa']}**")
                if ck2.button("Usuń", key=f"k_{kat['id']}"):
                    supabase.table("kategorie").delete().eq("id", kat["id"]).execute()
                    st.rerun()
