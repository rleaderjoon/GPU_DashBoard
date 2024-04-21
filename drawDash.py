import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import dash
from dash import dcc, html,Input, Output
import plotly.express as px
import pandas as pd
import dash_daq as daq
import dash_mantine_components as dmc
import plotly.graph_objs as go
from apscheduler.schedulers.background import BackgroundScheduler

cred = credentials.Certificate('gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# 스케줄러 초기화
scheduler = BackgroundScheduler()
data = []
df = pd.read_csv("sorted_firebase_data.csv")

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

params = list(df)
max_length = 60
time = 0

def load_data():
    global data
    global df
    # Firebase에서 데이터 가져오기
    collection_ref = db.collection('csvLog')
    docs = collection_ref.stream()
    # 데이터를 담을 리스트 초기화
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    # 데이터를 DataFrame으로 변환
    df = pd.DataFrame(data)
    # CSV 파일로 저장
    df.to_csv('firebase_data.csv', index=False)
    # Date 열을 datetime 형식으로 변환
    df['Date'] = pd.to_datetime(df['Date'])
    # Date 열을 기준으로 DataFrame 정렬
    df_sorted = df.sort_values(by='Date')
    # 정렬된 DataFrame을 CSV 파일로 저장
    df_sorted.to_csv("sorted_firebase_data.csv", index=False)
    df = pd.read_csv("sorted_firebase_data.csv")


#1분마다 함수 실행
scheduler.add_job(load_data, 'interval', minutes=1)

# 스케줄러 시작
scheduler.start()

def build_banner():
    return html.Div(
        id = "banner",
        className = "banner",
        children = [
            html.Div(
                id = "banner-text",
                children = [
                    html.H1("GPU DashBoard"),
                    html.H2("Control and optimization GPU")
                ]
            ),
            html.Div(
                id = "banner-logo",
                children = [
                    html.A(
                        html.Button(children = "GITHUB"),
                        href="https://github.com/rleaderjoon/GPU_DashBoard",
                    ),
                    html.Button(
                        id = "read-about-project", children = "read-about-project"
                    ),
                ],
            ),
        ],
    )

def build_tabs():
    return html.Div(
        children=[
            dcc.Tabs(
                children=[
                    dcc.Tab(
                        label="Specification Settings",
                        selected_style = {"color" : "black", 'borderTop': '10px solid #000000',},
                    ),
                    dcc.Tab(
                        label="Control Charts Dashboard",
                        selected_style = {"color" : "black", 'borderTop': '10px solid #000000',},
                    ),
                    dcc.Tab(
                        label="Show Exp",
                        selected_style = {"color" : "black", 'borderTop': '10px solid #000000',},
                    ),
                ],
            )
        ],
    )

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_side_panel():
    return html.Div(
        id = "side_panel",
        className = "row",
        children = [
            html.Div(
                children = [
                    html.H2("AVG Freq"),
                    daq.LEDDisplay(
                        id = "operator-led",
                        value = "1704",
                        color = "#92e0d3",
                        backgroundColor = "#1e2130",
                        size = 50,
                    ),
                ],
            ),
            html.Div(
                children = [
                    html.H2("Time to next refresh"),
                    daq.Gauge(
                        id = "gauge",
                        value = 0,
                        max = 60,
                        min = 0,
                        showCurrentValue = True,
                    ),
                ],
            ),
        ],
    )

# Dash 애플리케이션 생성
app = dash.Dash("GPU DASHBOARD")

# Dash 애플리케이션 레이아웃 설정
app.layout = html.Div(
    style = {"display" : "flex", "flex-direction" : "column", "height" : "100vh"},
    children = [
         dcc.Interval(
            id='interval-component',
            interval=1*1000,  # 1초마다 콜백 함수 호출
            n_intervals=0
        ),
        html.Div(
            style = {"height" : "100%"},
            children = build_banner(),
        ),
        html.Div(
            style = {"flex" : 1, "background-color" : "lightblue"},
        ),
        html.Div(
            style = {"flex" : 4, "background-color" : "lightgreen"},
            children = [
                html.Div(
                    style = {"display" : "flex", "flex-direction" : "row", "height" : "80vh"},
                    children = [
                        html.Div(
                            style = {"flex" : 1, "background-color" : "red"},
                            children = [
                                html.Div(
                                    style = {"display" : "flex", "justify-content" : "center", "align-items" : "center"},
                                    children = [
                                        build_side_panel()
                                    ]
                                ),
                            ]
                        ),
                        html.Div(
                            style = {"flex" : 4, "background-color" : "blue"},
                            children = [
                                html.Div(
                                    style = {"display" : "flex", "flex-direction" : "column", "height" : "80vh"},
                                    children = [
                                        html.Div(
                                            style = {"background-color" : "orange"},
                                            children = [
                                                html.Div(
                                                    style={"justify-content" : "center"},
                                                    children=build_tabs(),
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            style = {"flex" : 1, "background-color" : "yellow"},
                                        ),
                                    ]
                                )
                            ]
                        ),
                    ]
                )
            ]
        ),
    ],
)

@app.callback(
    Output("gauge", "value"),
    [Input("interval-component", "n_intervals")],
)
def update_gauge(n):
    global time
    time += 1
    if time > 60:
        time = 0
    return time

# 그래프 업데이트 함수
def update_graph(feature):
    # feature에 따라 그래프를 그리기 위해 해당 열의 데이터를 선택
    y_data = df[feature]
    title = feature.replace('_', ' ').title() + ' Over Time'  # 그래프 제목 설정

    # 그래프 생성
    figure = {
        'data': [{'x': df['Date'], 'y': y_data, 'mode': 'lines', 'line': {'color': 'yellow'}, 'type': 'scatter'}],
        'layout': {
            'title': title,
            'xaxis': {'showticklabels': False},  # X축 눈금 표시하지 않음
            'yaxis': {'showticklabels': False},  # Y축 눈금 표시하지 않음
            'margin': {'l': 0, 'r': 0, 't': 30, 'b': 0},  # 여백 조정
            'height': "8rem"  # 그래프 높이 조정
        }
    }
    return figure

# GPU Clock 그래프 콜백 함수
@app.callback(Output('gpu-clock-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_gpu_clock_graph(n):
    return update_graph('GPU Clock [MHz]')

# Memory Clock 그래프 콜백 함수
@app.callback(Output('memory-clock-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_memory_clock_graph(n):
    return update_graph('Memory Clock [MHz]')

# GPU Temperature 그래프 콜백 함수
@app.callback(Output('gpu-temperature-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_gpu_temperature_graph(n):
    return update_graph('GPU Temperature [C]')

# GPU Load 그래프 콜백 함수
@app.callback(Output('gpu-load-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_gpu_load_graph(n):
    return update_graph('GPU Load [%]')

# GPU Power 그래프 콜백 함수
@app.callback(Output('gpu-power-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_gpu_power_graph(n):
    return update_graph('GPU Power [W]')



# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)