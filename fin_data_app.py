import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="TimkaFin", page_icon="🪙")
st.title("Financial dashboard")

uploaded_file_Sankey = st.file_uploader("Sankey data file:")

if uploaded_file_Sankey is None:
    st.warning("🤷‍♂️ file")
    st.stop()

df_sankey = pd.read_excel(uploaded_file_Sankey, engine='openpyxl')

# Создание списков для узлов и связей
nodes = []
link = dict(source=[], target=[], value=[])

# Добавление уникальных узлов
for index, row in df_sankey.iterrows():
    nodes.extend([row['s'], row['t']])
nodes = list(set(nodes))

# Заполнение данных о связях
for index, row in df_sankey.iterrows():
    link['source'].append(nodes.index(row['s']))
    link['target'].append(nodes.index(row['t']))
    link['value'].append(row['a'])

# Создание Sankey chart
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=10,
        line=dict(color="black", width=0.5),
        label=nodes
    ),
    link=link
)])

# Отображение графика
fig.update_layout(
    width=1000,  # Указываем ширину графика
    height=600,  # Указываем высоту графика
    title_text="Sankey Chart потоков денежных средств в бизнесе"
)

st.plotly_chart(fig, use_container_width = True)
st.dataframe(df_sankey, hide_index= True)
# Создаем функцию для скачивания файла
def download_file(file_content, file_name):
    with open(file_name, "wb") as f:
        f.write(file_content)
    st.success(f"Файл '{file_name}' успешно скачан!")

# Загружаем файл, который будет доступен для скачивания
file_contents = b"hello world"
file_name = "Sankey.xlsx"

# Добавляем кнопку для скачивания файла
if st.button("Скачать файл"):
    download_file(file_contents, file_name)
