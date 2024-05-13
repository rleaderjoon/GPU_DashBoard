import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import dash
from dash import dcc, html,Input, Output, State
import plotly.express as px
import pandas as pd
import dash_daq as daq
import dash_mantine_components as dmc
import plotly.graph_objs as go
from apscheduler.schedulers.background import BackgroundScheduler
import json

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
avg_freq = 0

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
    print(df)


#1분마다 함수 실행
scheduler.add_job(load_data, 'interval', minutes=1)

# 스케줄러 시작
scheduler.start()

def cal_avg_freq():
    global df
    print(df)

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        style = {'backgroundColor' : 'black'},
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H1("GPU DashBoard"),
                    html.H2("Control and optimization GPU")
                ]
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        className="github-button",
                        href="https://github.com/rleaderjoon/GPU_DashBoard",
                        children=[
                            html.Button(children="GITHUB",style = {'backgroundColor' : 'white', 'color' : 'black'}),
                        ],
                    ),
                    html.Button(
                        id="read-about-project", children="read-about-project", style = {'backgroundColor' : 'white', 'color' : 'black'}
                    ),
                ],
            ),
        ],
    )

def build_tabs():
    return html.Div(
        children=[
            dcc.Tabs(
                id = 'tab-value',
                value = 'tab-1',
                children=[
                    dcc.Tab(
                        label="OverView",
                        style = {'backgroundColor' : 'black'},
                        selected_style = {"color" : "black", 'borderTop': '10px solid #808080','backgroundColor' : 'white'},
                        value = 'tab-1',
                    ),
                    dcc.Tab(
                        label="Control Setting",
                        style = {'backgroundColor' : 'black'},
                        selected_style = {"color" : "black", 'borderTop': '10px solid #808080','backgroundColor' : 'white'},
                        value = 'tab-2',
                    ),
                    dcc.Tab(
                        label="Show Exp",
                        style = {'backgroundColor' : 'black'},
                        selected_style = {"color" : "black", 'borderTop': '10px solid #808080','backgroundColor' : 'white'},
                        value = 'tab-3',
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
                        color = "#ffffff",
                        backgroundColor = "#000000",
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
            style = {"flex" : 1, "background-color" : "black"},
        ),
        html.Div(
            style = {"flex" : 4, "background-color" : "black"},
            children = [
                html.Div(
                    style = {"display" : "flex", "flex-direction" : "row", "height" : "80vh"},
                    children = [
                        html.Div(
                            style = {"flex" : 1, "background-color" : "black"},
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
                            style = {"flex" : 4, "background-color" : "black"},
                            children = [
                                html.Div(
                                    style = {"display" : "flex", "flex-direction" : "column", "height" : "80vh"},
                                    children = [
                                        html.Div(
                                            style = {"background-color" : "black"},
                                            children = [
                                                html.Div(
                                                    style={"justify-content" : "center"},
                                                    children=build_tabs(),
                                                )
                                            ]
                                        ),
                                        # 이 부분을 콜백으로 해결해야 함
                                        html.Div(
                                            id = 'tabs-contents'
                                        )
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
    title = feature.replace('_', ' ').title()

    # 그래프 생성
    figure = {
        'data': [{'x': df['Date'], 'y': y_data, 'mode': 'lines', 'line': {'color': 'white'}, 'type': 'scatter'}],
        'layout' : {
            'xaxis' : {'showticklabels' : False},
            'plot_bgcolor': 'black',  # 그래프 영역 배경색 설정
            'paper_bgcolor': 'black',  # 그래프 바깥 영역(페이퍼) 배경색 설정
            'title' : title,
            'title_font': {'color': 'white'}  # 제목 글자 색상 설정
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


# gpu-clock-gauge 콜백 함수
@app.callback(
    Output('gpu-clock-gauge', 'value'),
    [Input("gpu-clock", 'value')]
)
def update_gpu_clock_gauge(value):
    return value

# memory-clock-gauge 콜백 함수
@app.callback(
    Output('memory-clock-gauge', 'value'),
    [Input("memory-clock", 'value')]
)
def update_memory_clock_gauge(value):
    return value
@app.callback(
    Output('power-limit-gauge', 'value'),
    [Input("power-limit", 'value')]
)
def update_power_limit_gauge(value):
    return value

# dcc.Tab 콜백 함수
# Tab을 눌렀을 때 렌더되는 창은 아래의 함수로 구현
@app.callback(Output('tabs-contents', 'children'),
              Input('tab-value', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return  html.Div(
                style = {"flex" : 1, "background-color" : "black", "overflow" : "auto"},
                children = [
                    dcc.Graph(
                        id='gpu-clock-graph',
                        style = {'height' : '300px'}
                        ),
                    dcc.Graph(
                        id='memory-clock-graph',
                        style = {'height' : '300px'}
                        ),
                    dcc.Graph(
                        id='gpu-temperature-graph',
                        style = {'height' : '300px'}
                        ),
                    dcc.Graph(
                        id='gpu-load-graph',
                        style = {'height' : '300px'}
                        ),
                    dcc.Graph(
                        id='gpu-power-graph',
                        style = {'height' : '300px'}
                        )
                ]
            )
    elif tab == 'tab-2':
        return html.Div(
            # 화면을 3등분 하기 위해서 제일 위의 Div Style에 "display" : "flex"
            # 이후 각각의 children의 children의 style에 "flex" : 1을 넣어주면 3개를 사용하면 3등분
                style = {"display" : "flex" , "flex-direction" : "row", "height" : "100vh"},
                children = [
                    html.Div(
                        style={"flex": 1, "padding": "10px"},
                        children=[
                            daq.Gauge(
                                id = 'gpu-clock-gauge',
                                label = 'gpu-clock-gauge',
                                value = 1800,
                                max = 2000,
                                min = 200,
                                showCurrentValue = True,
                            ),
                            html.H3("GPU Clock"),
                            dcc.Slider(
                                id='gpu-clock',  # 다이얼의 고유 식별자
                                min=200,
                                max=2000,
                                step=200,
                                value=1800,  # 초기 값
                                marks={i: str(i) for i in range(200, 2000, 200)}  # 슬라이더 눈금 설정
                            ),
                            html.Div(id = 'gpu-clock-output'),
                ]),
                    html.Div(
                        style={"flex": 1, "padding": "10px"},
                        children=[
                            daq.Gauge(
                                id = 'memory-clock-gauge',
                                label = 'memory-clock-gauge',
                                value = 7000,
                                max = 7800,
                                min = 3000,
                                showCurrentValue = True,
                            ),
                        html.H3("Memory Clock"),
                            dcc.Slider(
                                id='memory-clock',  # 다이얼의 고유 식별자
                                min=3000,
                                max=7800,
                                step=800,
                                value=7000,  # 초기 값
                                marks={i: str(i) for i in range(3000, 7800, 800)}  # 슬라이더 눈금 설정
                            ),
                            html.Div(id='memory-clock-output'),
                ]),
                    html.Div(
                        style={"flex": 1, "padding": "10px"},
                        children=[
                            daq.Gauge(
                                id = 'power-limit-gauge',
                                label = 'power-limit-gauge',
                                value = 0,
                                max = 20,
                                min = -20,
                                showCurrentValue = True,
                            ),
                        html.H3("Power Limit"),
                            dcc.Slider(
                                id='power-limit',  # 다이얼의 고유 식별자
                                min=-20,
                                max=20,
                                step=10,
                                value=0,  # 초기 값
                                marks={i: str(i) for i in range(-20, 20, 10)}  # 슬라이더 눈금 설정
                            ),
                            html.Div(id='power-limit-output')  # 슬라이더 값 표시를 위한 빈 Div
                ])
                ]
            )   
    elif tab == 'tab-3':
        return html.Div([
            html.H3("h3")
        ])
    
@app.callback(
    dash.dependencies.Output('gpu-clock-output', 'children'),
    [dash.dependencies.Input('gpu-clock','value')]
)
def update_gpu_clock_output(value):
    return f'{value}'

# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)