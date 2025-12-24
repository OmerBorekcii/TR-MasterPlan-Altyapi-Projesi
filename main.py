import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import networkx as nx
import time
import math
import matplotlib.pyplot as plt

# --- SAYFA VE STİL AYARLARI ---
st.set_page_config(page_title="TR MasterPlan: Mühendislik Karar Destek Sistemi", layout="wide", page_icon="🏗️")

# 1. HAFIZA YÖNETİMİ
if 'hesaplandi' not in st.session_state: st.session_state['hesaplandi'] = False
if 'test_bitti' not in st.session_state: st.session_state['test_bitti'] = False
if 'analiz_verileri' not in st.session_state: st.session_state['analiz_verileri'] = {}

# -----------------------------------------------------------------------------
# 2. VERİ SETİ (81 İL + DEPREM RİSKİ)
# Risk Puanı: 1 (Düşük) - 5 (Çok Yüksek/Fay Hattı)
# -----------------------------------------------------------------------------
sehirler_veri = {
    'Adana': {'coords': (37.00, 35.32), 'risk': 4}, 'Adıyaman': {'coords': (37.76, 38.27), 'risk': 4},
    'Afyonkarahisar': {'coords': (38.75, 30.54), 'risk': 2}, 'Ağrı': {'coords': (39.71, 43.02), 'risk': 2},
    'Aksaray': {'coords': (38.36, 34.02), 'risk': 5}, 'Amasya': {'coords': (40.65, 35.83), 'risk': 5},
    'Ankara': {'coords': (39.92, 32.85), 'risk': 4}, 'Antalya': {'coords': (36.88, 30.70), 'risk': 2},
    'Ardahan': {'coords': (41.11, 42.70), 'risk': 2}, 'Artvin': {'coords': (41.18, 41.81), 'risk': 3},
    'Aydın': {'coords': (37.84, 27.84), 'risk': 5}, 'Balıkesir': {'coords': (39.64, 27.88), 'risk': 5},
    'Bartın': {'coords': (41.63, 32.33), 'risk': 1}, 'Batman': {'coords': (37.88, 41.12), 'risk': 2},
    'Bayburt': {'coords': (40.25, 40.22), 'risk': 3}, 'Bilecik': {'coords': (40.14, 29.97), 'risk': 4},
    'Bingöl': {'coords': (38.88, 40.49), 'risk': 5}, 'Bitlis': {'coords': (38.40, 42.10), 'risk': 4},
    'Bolu': {'coords': (40.73, 31.58), 'risk': 5}, 'Burdur': {'coords': (37.72, 30.28), 'risk': 5},
    'Bursa': {'coords': (40.18, 29.06), 'risk': 5}, 'Çanakkale': {'coords': (40.15, 26.41), 'risk': 5},
    'Çankırı': {'coords': (40.60, 33.61), 'risk': 3}, 'Çorum': {'coords': (40.54, 34.95), 'risk': 3},
    'Denizli': {'coords': (37.77, 29.08), 'risk': 5}, 'Diyarbakır': {'coords': (37.91, 40.23), 'risk': 2},
    'Düzce': {'coords': (40.84, 31.15), 'risk': 5}, 'Edirne': {'coords': (41.67, 26.55), 'risk': 4},
    'Elazığ': {'coords': (38.68, 39.22), 'risk': 5}, 'Erzincan': {'coords': (39.75, 39.49), 'risk': 5},
    'Erzurum': {'coords': (39.90, 41.27), 'risk': 4}, 'Eskişehir': {'coords': (39.77, 30.52), 'risk': 2},
    'Gaziantep': {'coords': (37.06, 37.38), 'risk': 3}, 'Giresun': {'coords': (40.91, 38.38), 'risk': 4},
    'Gümüşhane': {'coords': (40.46, 39.47), 'risk': 3}, 'Hakkari': {'coords': (37.57, 43.74), 'risk': 5},
    'Hatay': {'coords': (36.20, 36.16), 'risk': 5}, 'Iğdır': {'coords': (39.91, 44.04), 'risk': 2},
    'Isparta': {'coords': (37.76, 30.55), 'risk': 5}, 'İstanbul': {'coords': (41.00, 28.97), 'risk': 4},
    'İzmir': {'coords': (38.41, 27.13), 'risk': 5}, 'Kahramanmaraş': {'coords': (37.57, 36.93), 'risk': 5},
    'Karabük': {'coords': (41.20, 32.62), 'risk': 1}, 'Karaman': {'coords': (37.17, 33.21), 'risk': 5},
    'Kars': {'coords': (40.60, 43.09), 'risk': 2}, 'Kastamonu': {'coords': (41.38, 33.77), 'risk': 1},
    'Kayseri': {'coords': (38.73, 35.48), 'risk': 3}, 'Kırıkkale': {'coords': (39.84, 33.50), 'risk': 1},
    'Kırklareli': {'coords': (41.73, 27.22), 'risk': 4}, 'Kırşehir': {'coords': (39.14, 34.17), 'risk': 1},
    'Kilis': {'coords': (36.71, 37.11), 'risk': 3}, 'Kocaeli': {'coords': (40.85, 29.88), 'risk': 5},
    'Konya': {'coords': (37.87, 32.48), 'risk': 5}, 'Kütahya': {'coords': (39.41, 29.98), 'risk': 5},
    'Malatya': {'coords': (38.35, 38.30), 'risk': 5}, 'Manisa': {'coords': (38.61, 27.42), 'risk': 5},
    'Mardin': {'coords': (37.32, 40.74), 'risk': 3}, 'Mersin': {'coords': (36.80, 34.64), 'risk': 3},
    'Muğla': {'coords': (37.21, 28.36), 'risk': 5}, 'Muş': {'coords': (38.74, 41.49), 'risk': 5},
    'Nevşehir': {'coords': (38.62, 34.71), 'risk': 3}, 'Niğde': {'coords': (37.96, 34.68), 'risk': 4},
    'Ordu': {'coords': (40.98, 37.88), 'risk': 3}, 'Osmaniye': {'coords': (37.07, 36.24), 'risk': 4},
    'Rize': {'coords': (41.02, 40.51), 'risk': 4}, 'Sakarya': {'coords': (40.75, 30.37), 'risk': 5},
    'Samsun': {'coords': (41.29, 36.33), 'risk': 2}, 'Siirt': {'coords': (37.93, 41.94), 'risk': 1},
    'Sinop': {'coords': (42.02, 35.15), 'risk': 4}, 'Sivas': {'coords': (39.74, 37.01), 'risk': 3},
    'Şanlıurfa': {'coords': (37.16, 38.79), 'risk': 3}, 'Şırnak': {'coords': (37.51, 42.45), 'risk': 3},
    'Tekirdağ': {'coords': (40.97, 27.51), 'risk': 4}, 'Tokat': {'coords': (40.31, 36.55), 'risk': 5},
    'Trabzon': {'coords': (41.00, 39.71), 'risk': 4}, 'Tunceli': {'coords': (39.10, 39.54), 'risk': 4},
    'Uşak': {'coords': (38.68, 29.40), 'risk': 5}, 'Van': {'coords': (38.49, 43.37), 'risk': 5},
    'Yalova': {'coords': (40.65, 29.27), 'risk': 5}, 'Yozgat': {'coords': (39.81, 34.80), 'risk': 3},
    'Zonguldak': {'coords': (41.45, 31.79), 'risk': 1}
}
isimler = sorted(list(sehirler_veri.keys()))

# -----------------------------------------------------------------------------
# 3. MÜHENDİSLİK HESAPLAMALARI
# -----------------------------------------------------------------------------
def haversine(coord1, coord2):
    """Gerçek Coğrafi Mesafe Hesaplama (KM)"""
    R = 6371.0 
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def a_star_heuristic(node1, node2):
    return haversine(sehirler_veri[node1]['coords'], sehirler_veri[node2]['coords'])

# -----------------------------------------------------------------------------
# 4. GRAF OLUŞTURMA (DUYARLILIK ANALİZİ)
# -----------------------------------------------------------------------------
@st.cache_data
def grafi_hazirla(guvenlik_onceligi):
    """
    guvenlik_onceligi (0.0 - 1.0): Kullanıcının seçtiği Güvenlik vs Maliyet dengesi.
    Eğer 1.0 ise: Algoritma riskten kaçmak için her şeyi yapar.
    Eğer 0.0 ise: Algoritma en ucuz yolu seçer, fayı umursamaz.
    """
    G = nx.Graph()
    for sehir, data in sehirler_veri.items():
        G.add_node(sehir, pos=data['coords'], risk=data['risk'])
    
    # 10 Komşu Bağlantısı (Topoloji Garantisi)
    for s1 in sehirler_veri:
        uzakliklar = []
        for s2 in sehirler_veri:
            if s1 != s2:
                dist = haversine(sehirler_veri[s1]['coords'], sehirler_veri[s2]['coords'])
                uzakliklar.append((dist, s2))
        
        uzakliklar.sort()
        for d, s2 in uzakliklar[:10]: 
            # AĞIRLIK FORMÜLÜ (Multi-Objective)
            avg_risk = (sehirler_veri[s1]['risk'] + sehirler_veri[s2]['risk']) / 2.0
            
            # Risk Faktörü: Kullanıcı güvenliği seçerse bu katsayı katlanarak artar
            risk_penalti = 1 + (avg_risk * guvenlik_onceligi * 2.0) 
            
            agirlik = d * risk_penalti
            
            G.add_edge(s1, s2, weight=agirlik, distance=d, risk_val=avg_risk)
    return G

def proje_analizi(algo, baslangic, bitis, birim_maliyet, max_butce, yillik_gelir, guvenlik_katsayisi):
    G = grafi_hazirla(guvenlik_katsayisi) # Grafı kullanıcı tercihine göre oluştur
    t1 = time.perf_counter()
    
    try:
        # Algoritma Çalıştırma
        if algo == "A* (A-Star)":
            path = nx.astar_path(G, baslangic, bitis, heuristic=a_star_heuristic, weight='weight')
        elif algo == "Dijkstra":
            path = nx.dijkstra_path(G, baslangic, bitis, weight='weight')
        else: 
            path = nx.bellman_ford_path(G, baslangic, bitis, weight='weight')
            
        t2 = time.perf_counter()
        
        # --- DETAYLI FİZİBİLİTE RAPORU ---
        gercek_km = 0
        toplam_risk_ort = 0
        
        for i in range(len(path)-1):
            edge = G[path[i]][path[i+1]]
            gercek_km += edge['distance']
            toplam_risk_ort += edge['risk_val']
            
        avg_risk = toplam_risk_ort / (len(path)-1)
        
        # Teknik Gereksinimler
        istasyon_sayisi = math.ceil(gercek_km / 70) # Her 70 km'de bir istasyon
        istasyon_maliyeti = istasyon_sayisi * 50000 # İstasyon başı 50k$ varsayım
        
        # Maliyet Kalemleri
        hafriyat = gercek_km * birim_maliyet * 0.4
        malzeme = gercek_km * birim_maliyet * 0.3
        iscilik = gercek_km * birim_maliyet * 0.2
        # Risk Primi: Risk arttıkça sigorta maliyeti üstel artar
        sigorta = gercek_km * birim_maliyet * 0.1 * (1 + avg_risk/2)
        
        toplam_maliyet = hafriyat + malzeme + iscilik + sigorta + istasyon_maliyeti
        
        # Amortisman (ROI)
        roi_yil = toplam_maliyet / yillik_gelir if yillik_gelir > 0 else 0
        
        # Sonuçları Kaydet
        st.session_state['hesaplandi'] = True
        st.session_state['rota_yolu'] = path
        st.session_state['analiz_verileri'] = {
            'km': gercek_km,
            'sure': (t2 - t1) * 1000,
            'maliyet': toplam_maliyet,
            'risk_ort': avg_risk,
            'istasyon': istasyon_sayisi,
            'roi': roi_yil,
            'butce_durumu': toplam_maliyet <= max_butce,
            'detaylar': {'Hafriyat': hafriyat, 'Malzeme': malzeme, 'İşçilik': iscilik, 'Sigorta (Risk)': sigorta, 'İstasyonlar': istasyon_maliyeti}
        }
        
    except nx.NetworkXNoPath:
        st.error("🚫 Yol bulunamadı! Lütfen farklı şehirler seçiniz.")

def benchmark_test(baslangic, bitis, guvenlik_katsayisi):
    G_bench = grafi_hazirla(guvenlik_katsayisi)
    res = {}
    for alg in ['A*', 'Dijkstra', 'Bellman']:
        t_start = time.perf_counter()
        func = nx.astar_path if alg == 'A*' else (nx.dijkstra_path if alg == 'Dijkstra' else nx.bellman_ford_path)
        args = {'heuristic': a_star_heuristic} if alg == 'A*' else {}
        for _ in range(1000): 
            func(G_bench, baslangic, bitis, weight='weight', **args)
        res[alg] = (time.perf_counter() - t_start) * 1000
    st.session_state['test_bitti'] = True
    st.session_state['test_sonuclari'] = res

# -----------------------------------------------------------------------------
# 5. ARAYÜZ (SOL PANEL - KONTROL)
# -----------------------------------------------------------------------------
st.title("🇹🇷 MasterPlan: Altyapı Yatırım Analiz Sistemi")
st.markdown("Sismik risk analizi, bütçe optimizasyonu ve teknik kısıtları içeren **Profesyonel Karar Destek Sistemi**.")

col1, col2 = st.columns([1.2, 2.8])

with col1:
    st.subheader("🛠️ Proje Konfigürasyonu")
    
    # 1. ROTA
    c1, c2 = st.columns(2)
    start_city = c1.selectbox("Başlangıç", isimler, index=isimler.index("İstanbul"))
    end_city = c2.selectbox("Hedef", isimler, index=isimler.index("Van"))
    
    # 2. DUYARLILIK ANALİZİ (EN ÖNEMLİ KISIM)
    st.info("📊 **Duyarlılık Analizi (Sensitivity)**")
    guvenlik_onceligi = st.slider("Güvenlik Önceliği (%)", 0, 100, 50, help="0: En Ucuz Yolu Seç (Riskleri Yoksay) | 100: En Güvenli Yolu Seç (Maliyet Artsa Bile)")
    
    # 3. FİNANSAL PARAMETRELER
    st.write("💰 **Finansal Kısıtlar**")
    birim_maliyet = st.number_input("Birim Maliyet ($/KM)", value=2000, step=100)
    max_butce = st.number_input("Maksimum Bütçe ($)", value=5000000, step=500000)
    yillik_gelir = st.number_input("Beklenen Yıllık Gelir ($)", value=800000, step=100000)
    
    # 4. ALGORİTMA
    st.write("🧠 **Çözüm Motoru**")
    algo = st.radio("", ["A* (A-Star)", "Dijkstra", "Bellman-Ford"], horizontal=True)
    
    # BUTONLAR
    if st.button("🚀 Fizibilite Raporu Oluştur", type="primary"):
        proje_analizi(algo, start_city, end_city, birim_maliyet, max_butce, yillik_gelir, guvenlik_onceligi/100.0)
        st.session_state['test_bitti'] = False 

    if st.button("🔥 Stress Testi (1000x)"):
        with st.spinner('Simülasyon çalışıyor...'):
            benchmark_test(start_city, end_city, guvenlik_onceligi/100.0)
            
    if st.session_state['test_bitti']:
        res = st.session_state['test_sonuclari']
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(res.keys(), res.values(), color=['#2ca02c', '#1f77b4', '#ff7f0e'])
        ax.set_title('Performans (ms)')
        st.pyplot(fig)

# -----------------------------------------------------------------------------
# 6. ARAYÜZ (SAĞ PANEL - DASHBOARD)
# -----------------------------------------------------------------------------
with col2:
    if st.session_state['hesaplandi']:
        data = st.session_state['analiz_verileri']
        
        # ÜST KPI KARTLARI
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Proje Mesafesi", f"{data['km']:.1f} KM")
        k2.metric("Toplam Yatırım", f"${data['maliyet']:,.0f}", delta_color="normal" if data['butce_durumu'] else "inverse", delta="Bütçe Uygun" if data['butce_durumu'] else "BÜTÇE AŞILDI!")
        k3.metric("Amortisman (ROI)", f"{data['roi']:.1f} Yıl")
        k4.metric("Teknik İstasyon", f"{data['istasyon']} Adet")
        
        # GRAFİKLER
        t1, t2 = st.columns([1, 2])
        
        with t1:
            st.markdown("###### 💸 Maliyet Dağılımı")
            fig1, ax1 = plt.subplots(figsize=(4, 4))
            ax1.pie(data['detaylar'].values(), labels=data['detaylar'].keys(), autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
            st.pyplot(fig1)
            
        with t2:
            # HARİTA
            m = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles="CartoDB positron")
            
            # KATMAN 1: DEPREM RİSKİ ISI HARİTASI (HEATMAP)
            heat_data = [[v['coords'][0], v['coords'][1], v['risk']*2] for k,v in sehirler_veri.items()]
            HeatMap(heat_data, radius=15, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)
            
            # KATMAN 2: ALTYAPI AĞI
            for u, v, d in grafi_hazirla(guvenlik_onceligi/100.0).edges(data=True):
                color = "#ff4b4b" if d['risk_val'] > 3 else "#cccccc"
                op = 0.5 if d['risk_val'] > 3 else 0.2
                folium.PolyLine([sehirler_veri[u]['coords'], sehirler_veri[v]['coords']], color=color, weight=1, opacity=op).add_to(m)
            
            # KATMAN 3: ROTA
            path = st.session_state['rota_yolu']
            coords = [sehirler_veri[p]['coords'] for p in path]
            folium.PolyLine(coords, color="blue", weight=5, opacity=0.9, tooltip="Ana Hat").add_to(m)
            
            # İKONLAR
            folium.Marker(sehirler_veri[path[0]]['coords'], icon=folium.Icon(color="green", icon="play"), popup="Başlangıç").add_to(m)
            folium.Marker(sehirler_veri[path[-1]]['coords'], icon=folium.Icon(color="red", icon="flag"), popup="Bitiş").add_to(m)
            
            st_folium(m, width=800, height=450)
            
        # RAPORLAMA
        csv_row = f"{start_city},{end_city},{data['km']:.2f},{data['maliyet']:.2f},{data['roi']:.1f}"
        st.download_button("📄 Resmi Fizibilite Raporunu İndir (CSV)", data=f"Rota,Hedef,KM,Maliyet,ROI\n{csv_row}", file_name="fizibilite_raporu.csv")

    else:
        # AÇILIŞ EKRANI
        st.info("👈 Lütfen sol panelden proje parametrelerini girip 'Fizibilite Raporu Oluştur' butonuna basın.")
        # Boş harita ve heatmap gösterimi
        m_start = folium.Map(location=[39.0, 35.0], zoom_start=6, tiles="CartoDB positron")
        heat_data = [[v['coords'][0], v['coords'][1], v['risk']*2] for k,v in sehirler_veri.items()]
        HeatMap(heat_data, radius=15, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}, name="Sismik Risk Haritası").add_to(m_start)
        st_folium(m_start, width=900, height=500)


        st.markdown("---")
with st.expander("ℹ️ Algoritmalar ve Hesaplama Mantığı (Teknik Detay)"):
    st.markdown("""
    Bu proje 4 ana disiplini birleştirir:
    1.  **Coğrafi Analiz:** İki nokta arası mesafe *Haversine Formülü* (Küresel Geometri) ile hesaplanır.
    2.  **Sismik Risk:** AFAD verilerine dayalı risk puanları, kenar ağırlıklarına (edge weights) ceza puanı olarak eklenir.
    3.  **Ekonomi:** İlk yatırım maliyeti (CAPEX) ve işletme amortismanı (ROI) hesaplanır.
    4.  **Algoritmalar:**
        * **Dijkstra:** Tüm düğümleri tarayarak kesin en kısa yolu bulur (Garantili ama yavaş).
        * **A* (A-Star):** *Heuristic* (sezgisel) fonksiyon kullanarak hedefe yönelir (Çok hızlı ve isabetli).
        * **Bellman-Ford:** Negatif ağırlıkları yönetebilir ancak bu topolojide en yavaş çalışandır.
    """)