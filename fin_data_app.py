import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

import plotly.graph_objects as go

st.set_page_config( page_title = "TimkaFin", page_icon = "🪙") #layout = "wide",
st.title("Financial dashboard")
@st.cache_data
def load_data(file):
    data = pd.read_excel(file, engine='openpyxl')
    return data

uploaded_file = st.sidebar.file_uploader("drag&drop file:")

if uploaded_file is None:
    st.warning("🤷‍♂️ file")
    st.stop()

df = load_data(uploaded_file)


with st.expander("DataFrame"):
    st.dataframe(df,
                 column_config = {
                     "Year" : st.column_config.NumberColumn(format = "%d")
                 })

all_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def plot_bottom_left_first():
    sales_data = duckdb.sql(
        f"""
        SELECT
            Scenario,{','.join(all_months)}
            FROM df
            WHERE Year = '2023'
            AND Account = 'Sales'
            AND business_unit = 'Software'
            """
    ).df()
    st.dataframe(sales_data)

def plot_bottom_left_second():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            SELECT 
            Scenario,{','.join(all_months)} 
            FROM df 
            WHERE Year='2023' 
            AND Account='Sales'
            AND business_unit='Software'
        )

        UNPIVOT sales_data 
        ON {','.join(all_months)}
        INTO
            NAME month
            VALUE sales
    """
    ).df()
    st.dataframe(sales_data)
    fig = px.line(
        sales_data,
        x = "month",
        y = "sales",
        color = "Scenario",
        title = "Monthly budget vs forecat 2023"
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width = True)
plot_bottom_left_second()

def plot_bottom_right():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT ( 
                SELECT 
                    Account,Year,{','.join([f'ABS({month}) AS {month}' for month in all_months])}
                    FROM df 
                    WHERE Scenario='Actuals'
                    AND Account!='Sales'
                ) 
            ON {','.join(all_months)}
            INTO
                NAME year
                VALUE sales
        ),

        aggregated_sales AS (
            SELECT
                Account,
                Year,
                SUM(sales) AS sales
            FROM sales_data
            GROUP BY Account, Year
        )
        
        SELECT * FROM aggregated_sales
    """
    ).df()

    fig = px.bar(
        sales_data,
        x="Year",
        y="sales",
        color="Account",
        title="Actual Yearly Sales Per Account",
    )
    st.plotly_chart(fig, use_container_width=True)

plot_bottom_right()


#sankey chart
#uploaded_file_sankey = st.sidebar.file_uploader("drag&drop file:")
#if uploaded_file_sankey is None:
    #st.warning("🤷‍♂️ file")
    #st.stop()


# Данные о денежных потоках


uploaded_file_Sankey = st.file_uploader("Sankey data file:")
if uploaded_file_Sankey is None:
    st.warning("🤷‍♂️ file")
    st.stop()

df_sankey = load_data(uploaded_file_Sankey)

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

