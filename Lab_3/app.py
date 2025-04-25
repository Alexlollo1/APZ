import streamlit as st
import pandas as pd
import plotly.express as px
import glob
import os

# --- Мапа номерів областей до назв ---
area_map = {
    "1": "Вінницька", "2": "Волинська", "3": "Дніпропетровська", "4": "Донецька", "5": "Житомирська",
    "6": "Закарпатська", "7": "Запорізька", "8": "Івано-Франківська", "9": "Київська", "10": "Кіровоградська",
    "11": "Луганська", "12": "Львівська", "13": "Миколаївська", "14": "Одеська", "15": "Полтавська",
    "16": "Рівенська", "17": "Сумська", "18": "Тернопільська", "19": "Харківська", "20": "Херсонська",
    "21": "Хмельницька", "22": "Черкаська", "23": "Чернівецька", "24": "Чернігівська", "25": "Республіка Крим"
}

# --- Завантаження даних ---
@st.cache_data
def load_data():
    data_path = "data/*.csv"
    all_files = glob.glob(data_path)
    dfs = []
    for file in all_files:
        basename = os.path.basename(file)
        area_num = basename.split("_")[2]
        if area_num in area_map:
            area_name = area_map[area_num]
            df = pd.read_csv(file, header=1, names=['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty'])
            df = df.drop(columns=['empty'], errors='ignore')
            df["area"] = area_name
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'area'])

VHI = load_data()

# Очистка даних
VHI = VHI.dropna(subset=["VCI", "TCI", "VHI"])
VHI["Year"] = VHI["Year"].astype(str).str.extract(r'(\d{4})').astype(int)

# --- Бічна панель ---
with st.sidebar:
    st.title("🔧 Фільтри")
    index_type = st.selectbox("Оберіть індекс", ["VCI", "TCI", "VHI"])
    area = st.selectbox("Оберіть область", list(area_map.values()))
    week_range = st.slider("Інтервал тижнів", 1, 52, (1, 52))
    year_range = st.slider("Інтервал років", int(VHI['Year'].min()), int(VHI['Year'].max()),
                           (int(VHI['Year'].min()), int(VHI['Year'].max())))
    sort_asc = st.checkbox("Сортувати за зростанням")
    sort_desc = st.checkbox("Сортувати за спаданням")
    if st.button("🔄 Скинути фільтри"):
        st.experimental_rerun()

# --- Фільтрація ---
filtered_df = VHI[
    (VHI['area'] == area) &
    (VHI['Week'] >= week_range[0]) & (VHI['Week'] <= week_range[1]) &
    (VHI['Year'] >= year_range[0]) & (VHI['Year'] <= year_range[1])
]

# --- Сортування ---
if sort_asc and not sort_desc:
    filtered_df = filtered_df.sort_values(by=index_type, ascending=True)
elif sort_desc and not sort_asc:
    filtered_df = filtered_df.sort_values(by=index_type, ascending=False)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📋 Таблиця", "📈 Графік по області", "📊 Порівняння з іншими"])

with tab1:
    st.subheader("📋 Відфільтровані дані")
    st.dataframe(filtered_df)

with tab2:
    st.subheader(f"{index_type} по тижнях у {area}")
    fig = px.line(filtered_df, x="Week", y=index_type, color="Year",
                  markers=True, title=f"{index_type} у {area}")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader(f"Порівняння {index_type} по всіх областях")
    comparison_df = VHI[
        (VHI['Week'] >= week_range[0]) & (VHI['Week'] <= week_range[1]) &
        (VHI['Year'] >= year_range[0]) & (VHI['Year'] <= year_range[1])
    ]
    fig_comp = px.line(comparison_df, x="Week", y=index_type, color="area",
                       line_group="area", title=f"Порівняння {index_type} по областях")
    st.plotly_chart(fig_comp, use_container_width=True)