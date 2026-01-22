import streamlit as st
from supabase import create_client, Client

# Konfiguracja Supabase
SUPABASE_URL = "https://rbyoztsgjuxcnwwneasu.supabase.co"
SUPABASE_KEY = "sb_publishable_xlkem_D_yo3xIlTLRHsLMw_HpB0jEdS"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="System Logistyczny PRO", layout="wide", page_icon="🚚")

# --- ZAAWANSOWANA STYLIZACJA UI (MAKSYMALNA CZYTELNOŚĆ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700;900&display=swap');

    .stApp {
        background-image: url("https://images.unsplash.com/photo-1587293852726-70cdb56c2866?q=80&w=2072");
        background-attachment: fixed;
        background-size: cover;
    }

    /* Ustawienia czcionek */
    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }

    h1, h2, h3 {
        color: #FFFFFF !important;
        text-shadow: 4px 4px 8px #000000 !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Panele - Bardzo ciemne szkło dla kontrastu */
    div[data-testid="stForm"], div[data-testid="stMetric"], .st-emotion-cache-12w0u9p, div[data-testid="stExpander"], .stTabs {
        background-color: rgba(0, 0, 0, 0.88) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        backdrop-filter: blur(15px);
    }

    /* Teksty w panelach - Czysta biel */
    p, label, span, .stMarkdown, li {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 2px #000000;
    }

    /* Przyciski - Styl Alertowy */
    .stButton>button {
        background: linear-gradient(45deg, #d32f2f, #f44336) !important;
        color: white !important;
        border: 2px solid white !important;
        border-radius: 10px !important;
        font-weight: 900 !important;
        height: 3em !important;
        text-transform: uppercase;
    }

    /* Wygląd metryk */
    [data-testid="stMetricValue"] {
        color: #00FF00 !important;
        font-size: 3rem !important;
        font-weight: 900 !important;
    }
    
    /* Naprawienie widoczności zakładek */
    button[data-baseweb="tab"] {
        color: white !important;
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Pobieranie danych
try:
    res_p = supabase.table("produkty").select("*, kategorie(nazwa)").order("id").execute()
    produkty = res_p.data
    res_k = supabase.table("kategorie").select("*").execute()
    kategorie = res_k.data
except Exception as e:
    st.error(f"Błąd bazy: {e}")
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
        # Obliczenia z poprawionym nawiasowaniem
        t_qty = sum(item.get('liczba', 0) for item in produkty)
        t_val = sum((item.get('liczba', 0) * item.get('cena', 0)) for item in produkty)
        
        c1.metric("📦 POZYCJE", len(produkty))
        c2.metric("🔢 ILOŚĆ ŁĄCZNA", f"{t_qty} szt.")
        c3.metric("💰 WARTOŚĆ NETTO", f"{t_val:,.2f} zł")

        st.markdown("### 📈 ANALIZA ZASOBÓW")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.write("**Ilość sztuk na stanie:**")
            chart_qty = {f"🚚 {i['nazwa']}": i['liczba'] for i in produkty}
            st.bar_chart(chart_qty, color="#FF4B4B")
            
        with col_c2:
            st.write("**Wartość finansowa towaru:**")
            chart_val = {f"🚚 {i['nazwa']}": (i['liczba'] * i['cena']) for i in produkty}
            st.area_chart(chart_val, color="#00FF00")
    else:
        st.warning("Brak danych w bazie. Przejdź do zakładki DOSTAWY, aby dodać towar.")

# --- ZAKŁADKA: MAGAZYN (Lista) ---
with tab_magazyn:
    st.subheader("📋 AKTUALNA LISTA INWENTARYZACYJNA")
    if produkty:
        for p in produkty:
            with st.container():
                ca, cb, cc = st.columns([3, 2, 1])
                k_label = p['kategorie']['nazwa'] if p.get('kategorie') else "BRAK SEKCJI"
                ca.markdown(f"### 🚚 {p['nazwa']}")
                ca.write(f"LOKALIZACJA: {k_label}")
                cb.write(f"**STAN:** {p['liczba']} SZT.")
                cb.write(f"**CENA:** {p['cena']} PLN")
                if cc.button("USUŃ", key=f"del_{p['id']}"):
                    supabase.table("produkty").delete().eq("id", p["id"]).execute()
                    st.rerun()
                st.markdown("---")

# --- ZAKŁADKA: DOSTAWY (Formularz) ---
with tab_dostawy:
    st.subheader("🚛 PRZYJĘCIE NOWEJ DOSTAWY")
    if kategorie:
        k_map = {k['nazwa']: k['id'] for k in kategorie}
        with st.form("dostawa_form", clear_on_submit=True):
            f_name = st.text_input("NAZWA TOWARU (np. Opony)")
            f_qty = st.number_input("ILOŚĆ PRZYJĘTA", min_value=1, step=1)
            f_price = st.number_input("CENA JEDNOSTKOWA (PLN)", min_value=0.0)
            f_cat = st.selectbox("PRZYPISZ DO SEKCJI", options=list(k_map.keys()))
            
            if st.form_submit_button("✅ DODAJ DO EWIDENCJI"):
                if f_name:
                    supabase.table("produkty").insert({
                        "nazwa": f_name, 
                        "liczba": f_qty, 
                        "cena": f_price, 
                        "kategoria_id": k_map[f_cat]
                    }).execute()
                    st.success(f"Dodano: {f_name}")
                    st.rerun()
    else:
        st.error("BŁĄD: Musisz najpierw utworzyć przynajmniej jedną SEKCJĘ w panelu obok.")

# --- ZAKŁADKA: KATEGORIE ---
with tab_kategorie:
    st.subheader("🗂️ KONFIGURACJA SEKCJI MAGAZYNOWYCH")
    ck1, ck2 = st.columns([1, 2])
    with ck1:
        with st.form("kat_nowa"):
            n_k = st.text_input("NAZWA NOWEJ SEKCJI")
            if st.form_submit_button("UTWÓRZ SEKCJĘ"):
                if n_k:
                    supabase.table("kategorie").insert({"nazwa": n_k}).execute()
                    st.rerun()
    with ck2:
        for k in kategorie:
            st.info(f"AKTYWNA SEKCJA: {k['nazwa']}")

# --- ZAKŁADKA: RAPORTY ---
with tab_raporty:
    st.subheader("📄 EKSPORT I ANALIZA TABELARYCZNA")
    if produkty:
        st.dataframe(produkty, use_container_width=True)
        # Prosty generator CSV
        csv_data = "ID,NAZWA,ILOSC,CENA\n" + "\n".join([f"{i['id']},{i['nazwa']},{i['liczba']},{i['cena']}" for i in produkty])
        st.download_button(
            label="📥 POBIERZ RAPORT CSV",
            data=csv_data,
            file_name="raport_magazynowy.csv",
            mime="text/csv"
        )
