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

# 1분마다 함수 실행
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
                    html.H5("GPU DashBoard"),
                    html.H6("Control and optimization GPU")
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
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Specification Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Control Charts Dashboard",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
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
                id = "card1",
                children = [
                    html.P("AVG Freq"),
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
                id = "card2",
                children = [
                    html.P("Time to next refresh"),
                    daq.Gauge(
                        id = "progress-gauge",
                        max = 60,
                        min = 0,
                        showCurrentValue = True, #default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id = "utility-card",
                children = [daq.StopButton(id = "stop-button", size = 160, n_clicks = 0)],
            ),
        ],
    )

def generate_metric_row(id, style, col1, col2, col3, col4, col5):
    if style is None:
        style = {"height": "8rem", "width": "100%"}
    
    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="one column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
            html.Div(
                id=col4["id"],
                style={},
                className="one column",
                children=col4["children"],
            ),
            html.Div(
                id=col5["id"],
                style={"height": "100%", "margin-top": "5rem"},
                className="three columns",
                children=col5["children"],
            ),
        ],
    )

def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height" : "3rem", "margin" : "1rem 0", "textAlign" : "center"},
        {"id" : "m_header_1", "children" : html.Div("GPU Clock [MHz]")},
        {"id" : "m_header_2", "children" : html.Div("GPU Power [W]")},
        {"id" : "m_header_3", "children" : html.Div("Memory Clock [MHz]")},
        {"id" : "m_header_4", "children" : html.Div("GPU Temperature [C]")},
        {"id" : "m_header_5", "children" : html.Div("GPU Load [%]")},
    )

def generate_metric_row_helper(stopped_interval, index):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count
    ooc_percentage_id = item + suffix_ooc_n
    ooc_graph_id = item + suffix_ooc_g
    indicator_id = item + suffix_indicator

    return generate_metric_row(
        div_id,
        None,
        {
            "id": item,
            "className": "metric-row-button-text",
            "children": html.Button(
                id=button_id,
                className="metric-row-button",
                children=item,
                title="Click to visualize live SPC chart",
                n_clicks=0,
            ),
        },
        {"id": count_id, "children": "0"},
        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id=sparkline_graph_id,
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": state_dict["Batch"]["data"].tolist()[
                                    :stopped_interval
                                ],
                                "y": state_dict[item]["data"][:stopped_interval],
                                "mode": "lines+markers",
                                "name": item,
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },
        {"id": ooc_percentage_id, "children": "0.00%"},
        {
            "id": ooc_graph_id + "_container",
            "children": daq.GraduatedBar(
                id=ooc_graph_id,
                color={
                    "ranges": {
                        "#92e0d3": [0, 3],
                        "#f4d44d ": [3, 7],
                        "#f45060": [7, 15],
                    }
                },
                showCurrentValue=False,
                max=15,
                value=0,
            ),
        },
        {
            "id": item + "_pf",
            "children": daq.Indicator(
                id=indicator_id, value=True, color="#91dfd2", size=12
            ),
        },
    )

#may contain interval
def build_top_panel():
    return html.Div(
        id = "top-section-container",
        className = "row",
        children = [
            html.Div(
                id = "metric-summary-session",
                className = "eight columns",
                children = [
                    generate_section_banner("GPU Info Summary"),
                    html.Div(
                        id = "metric-div",
                        children = [
                            generate_metric_list_header(),
                            html.Div(
                                id = "metric-rows",
                                children=[

                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
# Dash 애플리케이션 생성
app = dash.Dash("GPU DASHBOARD")

# Dash 애플리케이션 레이아웃 설정
app.layout = html.Div(
    id = "big-app-container",
    children = [
        build_banner(),
        # 다른 열의 그래프도 필요한 경우 추가 가능
        dcc.Interval(
            id='interval-component',
            interval=1*60*1000,  # 1분마다 업데이트
            n_intervals=0
        ),
        html.Div(
            id = "app-container",
            children = [
                build_tabs(),
                html.Div(id="app-content"),
                html.Div([
                    dcc.Graph(id='gpu-clock-graph'),
                    ]),
                html.Div([
                    dcc.Graph(id='memory-clock-graph'),
                    ]),
                html.Div([        
                    dcc.Graph(id='gpu-temperature-graph')
                    ]),
                html.Div([        
                    dcc.Graph(id='gpu-load-graph')
                    ]),
                html.Div([        
                    dcc.Graph(id='gpu-power-graph')
                    ]),
            ],
        ),
    ]
)



# GPU Clock 그래프 콜백 함수
@app.callback(
    Output('gpu-clock-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_gpu_clock_graph(n):
    # GPU Clock 열의 데이터를 사용하여 그래프 그리기
    figure = {
        'data': [
            {'x': df['Date'], 'y': df['GPU Clock [MHz]'], 'type': 'line', 'name': 'GPU Clock [MHz]'}
        ],
        'layout': {
            'title': 'GPU Clock [MHz] Over Time'
        }
    }
    return figure

# Memory Clock 그래프 콜백 함수
@app.callback(
    Output('memory-clock-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_memory_clock_graph(n):
    # Memory Clock 열의 데이터를 사용하여 그래프 그리기
    figure = {
        'data': [
            {'x': df['Date'], 'y': df['Memory Clock [MHz]'], 'type': 'line', 'name': 'Memory Clock [MHz]'}
        ],
        'layout': {
            'title': 'Memory Clock [MHz] Over Time'
        }
    }
    return figure
# GPU Temperature 그래프 콜백 함수
@app.callback(
    Output('gpu-temperature-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_gpu_temperature_graph(n):
    # GPU Temperature 열의 데이터를 사용하여 그래프 그리기
    figure = {
        'data': [
            {'x': df['Date'], 'y': df['GPU Temperature [C]'], 'type': 'line', 'name': 'GPU Temperature [C]'}
        ],
        'layout': {
            'title': 'GPU Temperature [C] Over Time'
        }
    }
    return figure
# GPU Load 그래프 콜백 함수
@app.callback(
    Output('gpu-load-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_gpu_load_graph(n):
    # GPU Load 열의 데이터를 사용하여 그래프 그리기
    figure = {
        'data': [
            {'x': df['Date'], 'y': df['GPU Load [%]'], 'type': 'line', 'name': 'GPU Load [%]'}
        ],
        'layout': {
            'title': 'GPU Load [%] Over Time'
        }
    }
    return figure
# GPU Power 그래프 콜백 함수
@app.callback(
    Output('gpu-power-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_gpu_power_graph(n):
    # GPU Power 열의 데이터를 사용하여 그래프 그리기
    figure = {
        'data': [
            {'x': df['Date'], 'y': df['GPU Power [W]'], 'type': 'line', 'name': 'GPU Power [W]'}
        ],
        'layout': {
            'title': 'GPU Power [W] Over Time'
        }
    }
    return figure

# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)