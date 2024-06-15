# python에서 nvidia-smi를 통해서 코드의 전체 실행 기간동안 기록을 함
# 1. GPU LOAD
# 2. MEMORY LOAD
# 3. POWER CONSUMPTION
# MEMORY의 최대 사용량은 RTX3070기준으로 8196MB
# POWER CONSUMPTION의 최대는 nvidia-smi의 power-limit을 불러와서 기준을 잡음
# 1,2,3를 모두 %로 기록을 함

# 0.01초마다 기록을 함
# 10초마다 지금까지 기록한 데이터에 대하여 3가지 각각의 그래프에 대해서 FFT를 진행함
# FFT를 진행한 3가지 그래프를 모두 합침
# 합친 그래프에서 FFT의 주기를 찾아냄

import subprocess
import numpy as np
import os
import seaborn as sn; sn.set(font_scale=1.4)
import matplotlib.pyplot as plt             
import cv2                                 
import tensorflow as tf                
from tqdm import tqdm
from sklearn.metrics import confusion_matrix
from sklearn.utils import shuffle   
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import time
import threading

# 최대 메모리 사용량과 전력 소비량 설정 (RTX 3070 기준)
MAX_MEMORY_USAGE = 8196  # MB
POWER_LIMIT_CMD = "nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits"
power_limit = float(subprocess.getoutput(POWER_LIMIT_CMD))

# 데이터 저장 리스트
gpu_loads = []
memory_loads = []
power_usages = []

def get_gpu_stats():
    smi_output = subprocess.getoutput("nvidia-smi --query-gpu=utilization.gpu,utilization.memory,power.draw --format=csv,noheader,nounits")
    gpu_load, memory_load, power_usage = map(float, smi_output.split(', '))
    gpu_load_percentage = gpu_load
    memory_load_percentage = (memory_load / MAX_MEMORY_USAGE) * 100
    power_usage_percentage = (power_usage / power_limit) * 100
    return gpu_load_percentage, memory_load_percentage, power_usage_percentage

def perform_fft(data):
    n = len(data)
    T = 0.01  # Sampling interval
    yf = fft(data)
    xf = np.fft.fftfreq(n, T)[:n//2]
    return xf, 2.0/n * np.abs(yf[:n//2])

def find_peak_frequency(xf, yf):
    peaks, _ = find_peaks(yf)
    if peaks.size > 0:
        main_peak = xf[peaks[np.argmax(yf[peaks])]]
    else:
        main_peak = None
    return main_peak

def collect_and_analyze_gpu_data():
    try:
        start_time = time.time()
        while True:
            # 데이터 수집
            gpu_load, memory_load, power_usage = get_gpu_stats()
            gpu_loads.append(gpu_load)
            memory_loads.append(memory_load)
            power_usages.append(power_usage)
            
            time.sleep(0.01)
            
            # 10초마다 FFT 수행
            if (time.time() - start_time) >= 10:
                start_time = time.time()

                # GPU Load FFT
                xf, yf = perform_fft(gpu_loads)
                gpu_peak = find_peak_frequency(xf, yf)

                # Memory Load FFT
                xf, yf = perform_fft(memory_loads)
                memory_peak = find_peak_frequency(xf, yf)

                # Power Usage FFT
                xf, yf = perform_fft(power_usages)
                power_peak = find_peak_frequency(xf, yf)

                print(f"GPU Load Peak Frequency: {gpu_peak} Hz")
                print(f"Memory Load Peak Frequency: {memory_peak} Hz")
                print(f"Power Usage Peak Frequency: {power_peak} Hz")

    except KeyboardInterrupt:
        print("Data collection stopped.")

# 백그라운드에서 GPU 데이터 수집 시작
gpu_thread = threading.Thread(target=collect_and_analyze_gpu_data)
gpu_thread.start()

"""
------------------------------
아래는 이미지 분류 Deep Learning
------------------------------
"""
class_names = ['mountain', 'street', 'glacier', 'buildings', 'sea', 'forest']
class_names_label = {class_name:i for i, class_name in enumerate(class_names)}

nb_classes = len(class_names)

IMAGE_SIZE = (150, 150)

def load_data():
    """
        Load the data:
            - 14,034 images to train the network.
            - 3,000 images to evaluate how accurately the network learned to classify images.
    """
    
    datasets = [r'C:\Users\win\Desktop\GPU_TEST\seg_test', r'C:\Users\win\Desktop\GPU_TEST\seg_test']
    output = []
    
    # Iterate through training and test sets
    for dataset in datasets:
        
        images = []
        labels = []
        
        print("Loading {}".format(dataset))
        
        # Iterate through each folder corresponding to a category
        for folder in os.listdir(dataset):
            label = class_names_label[folder]
            
            # Iterate through each image in our folder
            for file in tqdm(os.listdir(os.path.join(dataset, folder))):
                
                # Get the path name of the image
                img_path = os.path.join(os.path.join(dataset, folder), file)
                
                # Open and resize the img
                image = cv2.imread(img_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, IMAGE_SIZE) 
                
                # Append the image and its corresponding label to the output
                images.append(image)
                labels.append(label)
                
        images = np.array(images, dtype = 'float32')
        labels = np.array(labels, dtype = 'int32')   
        
        output.append((images, labels))

    return output

(train_images, train_labels), (test_images, test_labels) = load_data()

train_images, train_labels = shuffle(train_images, train_labels, random_state=25)

train_images = train_images / 255.0 
test_images = test_images / 255.0

model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation = 'relu', input_shape = (150, 150, 3)), 
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(32, (3, 3), activation = 'relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation=tf.nn.relu),
    tf.keras.layers.Dense(6, activation=tf.nn.softmax)
])

model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics=['accuracy'])

history = model.fit(train_images, train_labels, batch_size=128, epochs=100, validation_split = 0.2)