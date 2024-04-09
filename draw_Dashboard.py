import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

cred = credentials.Certificate('gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Dash 앱 초기화
app = dash.Dash("GPU_DASHBOARD")

# Firestore에서 COUNT 컬렉션의 count 값을 가져오는 함수
def fetch_count():
    count_doc = db.collection("COUNT").document("count").get().to_dict()
    if count_doc:
        return count_doc.get('count', 1)
    else:
        return 1

# Firestore에서 GPU_LOG 컬렉션의 GPU 데이터를 가져오는 함수
def fetch_gpu_data(count):
    gpu_data = []
    gpu_logs_ref = db.collection("GPU_LOG").document("gpu_data_{}".format(count)).get()
    if gpu_logs_ref.exists:
        gpu_data = gpu_logs_ref.to_dict().get('gpu_data', [])
    return gpu_data

# 그래프를 그리는 Dash 앱 레이아웃
app.layout = html.Div([
    dcc.Graph(id='gpu-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # 1초마다 업데이트
        n_intervals=0
    )
])

# Dash 앱 콜백: 그래프 업데이트
@app.callback(
    dash.dependencies.Output('gpu-graph', 'figure'),
    dash.dependencies.Input('interval-component', 'n_intervals')
)
def update_graph(n):
    # Firestore에서 count 값을 가져옴
    count = fetch_count()
    # count 값을 기반으로 GPU 데이터를 가져옴
    gpu_data = fetch_gpu_data(count)
    # GPU 데이터를 DataFrame으로 변환하여 그래프 생성
    gpu_df = pd.DataFrame(gpu_data)
    fig = px.line(gpu_df, x=gpu_df.index, y=['GPU_CLOCK', 'GPU_LOAD', 'GPU_TEMP', 'MEMORY_CLOCK'],
                  title='GPU Data Over Time')
    return fig

# Dash 앱 실행
if __name__ == '__main__':
    app.run_server(debug=True)