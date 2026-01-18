import streamlit as st
from supabase import create_client, Client

# Konfiguracja Supabase (Streamlit Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Zarządzanie Bazą Supabase", layout="wide")

tab1, tab2 = st.tabs(["📦 Produkty", "📂 Kategorie"])

# --- TAB: KATEGORIE ---
with tab2:
    st.header("Zarządzanie Kategoriami")
    
    with st.form("form_kat"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        opis_kat = st.text_area("Opis")
        if st.form_submit_button("Dodaj Kategorię") and nazwa_kat:
            supabase.table("kategorie").insert({"nazwa": nazwa_kat, "opis": opis_kat}).execute()
            st.rerun()

    res_kat = supabase.table("kategorie").select("*").order("id").execute()
    for kat in res_kat.data:
        col1, col2 = st.columns([5, 1])
        col1.write(f"**{kat['nazwa']}** — {kat['opis']}")
        if col2.button("Usuń", key=f"del_k_{kat['id']}"):
            supabase.table("kategorie").delete().eq("id", kat["id"]).execute()
            st.rerun()

# --- TAB: PRODUKTY ---
with tab1:
    st.header("Zarządzanie Produktami")
    
    kat_list = supabase.table("kategorie").select("id, nazwa").execute().data
    kat_options = {k["nazwa"]: k["id"] for k in kat_list}

    with st.form("form_prod"):
        nazwa_prod = st.text_input("Nazwa produktu")
        liczba = st.number_input("Liczba", min_value=0, step=1)
        cena = st.number_input("Cena", min_value=0.0, format="%.2f")
        wybrana_kat = st.selectbox("Kategoria", options=list(kat_options.keys()))
        
        if st.form_submit_button("Dodaj Produkt") and nazwa_prod:
            payload = {
                "nazwa": nazwa_prod,
                "liczba": liczba,
                "cena": cena,
                "kategoria_id": kat_options[wybrana_kat]
            }
            supabase.table("produkty").insert(payload).execute()
            st.rerun()

    res_prod = supabase.table("produkty").select("*, kategorie(nazwa)").order("id").execute()
    for p in res_prod.data:
        c1, c2 = st.columns([5, 1])
        kat_label = p['kategorie']['nazwa'] if p.get('kategorie') else "Brak"
        c1.write(f"**{p['nazwa']}** | Ilość: {p['liczba']} | Cena: {p['cena']} | Kat: {kat_label}")
        if c2.button("Usuń", key=f"del_p_{p['id']}"):
            supabase.table("produkty").delete().eq("id", p["id"]).execute()
            st.rerun()
