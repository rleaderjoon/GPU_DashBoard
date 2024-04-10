import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import dash
from dash import dcc, html,Input, Output
import plotly.express as px
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

cred = credentials.Certificate('gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
# 스케줄러 초기화
scheduler = BackgroundScheduler()
data = []
df = pd.read_csv("sorted_firebase_data.csv")

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

# Dash 애플리케이션 생성
app = dash.Dash("GPU DASHBOARD")

# Dash 애플리케이션 레이아웃 설정
app.layout = html.Div([
    html.H1("GPU Data Visualization"),
    dcc.Graph(id='gpu-clock-graph'),
    dcc.Graph(id='memory-clock-graph'),
    dcc.Graph(id='gpu-temperature-graph'),
    dcc.Graph(id='gpu-load-graph'),
    dcc.Graph(id='gpu-power-graph'),
    # 다른 열의 그래프도 필요한 경우 추가 가능
    dcc.Interval(
        id='interval-component',
        interval=1*60*1000,  # 1분마다 업데이트
        n_intervals=0
    ),
])

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