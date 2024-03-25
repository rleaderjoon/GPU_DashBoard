import subprocess
import time
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import time
import plotly.graph_objs as go
import random
import datetime
import threading

subprocess.Popen("GPU-Z.exe")

# Dash 애플리케이션 설정
app = dash.Dash("IGPU Test")
# GPU clock 데이터를 저장할 리스트
gpu_clock_data = []

app.layout = html.Div([
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # 1초마다 업데이트
        n_intervals=0
    )
])

def update_gpu_clock(file):
    global gpu_clock_data
    # 항상 파일 핸들러를 처음으로 위치시킴
    file.seek(0)
    lines = file.readlines()

    if len(lines) > 0:
        last_line = lines[-1]
        gpu_clock = last_line.split()[3]
        gpu_clock_data.append(gpu_clock)
        
    if len(lines) >= 100 :
        file.seek(0)
        file.truncate()
        file.write(lines[-99])
    # 데이터를 최근 60개까지 유지
    gpu_clock_data = gpu_clock_data[-60:]
    print("Updating GPU clock...")

with open('GPU-Z Sensor Log.txt', 'a+') as file:
    update_gpu_clock(file)

def repeat_update(interval):
    update_gpu_clock()
    threading.Timer(interval, repeat_update, args=[interval]).start()

# 처음 한 번은 바로 실행하고, 그 후에는 1초마다 호출
repeat_update(1)

@app.callback(
    Output('live-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)

def update_graph(n):
    # 그래프 업데이트
    trace = go.Scatter(
        y=gpu_clock_data,
        mode='lines+markers'
    )
    layout = go.Layout(title='GPU Clock Data')
    return {'data': [trace], 'layout': layout}

thread = threading.Thread(target=update_gpu_clock)
thread.daemon = True
thread.start()

app.run_server(debug=True)
