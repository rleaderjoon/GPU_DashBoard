import dash
from dash import dcc, html, Input, Output
import dash_daq as daq
import random
import time

# Dash 애플리케이션 생성
app = dash.Dash(__name__)

# 레이아웃 설정
app.layout = html.Div([
    # Interval 컴포넌트를 사용하여 1초마다 값이 업데이트되도록 함
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # 1초마다 콜백 함수 호출
        n_intervals=0
    ),
    # Gauge 컴포넌트
    daq.Gauge(
        id='gauge',
        label='Temperature',
        value=20,  # 초기값 설정
        min=0,
        max=100,
        size=200  # 게이지 크기 설정
    ),
])

# 콜백 함수 정의
@app.callback(
    Output('gauge', 'value'),  # Gauge의 value 속성을 업데이트
    [Input('interval-component', 'n_intervals')]  # Interval 컴포넌트의 n_intervals를 입력으로 사용
)
def update_gauge(n):
    # 실제로는 여기에서 데이터를 수집하거나 계산하여 값을 업데이트할 것
    # 여기서는 임의의 값 생성
    new_value = random.randint(0, 100)
    return new_value

# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)