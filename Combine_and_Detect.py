import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# 주파수 정보 (예시 데이터)
gpu_load_peak_freq = 9.242957746478874
memory_load_peak_freq = 9.242957746478874
power_usage_peak_freq = 1.760563380281690

# 샘플 데이터 생성 (여기서는 임의의 데이터를 생성합니다)
t = np.linspace(0, 100, 1000)
gpu_load_data = np.sin(2 * np.pi * gpu_load_peak_freq * t)
memory_load_data = np.sin(2 * np.pi * memory_load_peak_freq * t)
power_usage_data = np.sin(2 * np.pi * power_usage_peak_freq * t)

# 데이터 그리기
plt.figure(figsize=(12, 6))
plt.plot(t, gpu_load_data, label='GPU Load')
plt.plot(t, memory_load_data, label='Memory Load')
plt.plot(t, power_usage_data, label='Power Usage')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.title('GPU Metrics Over Time')
plt.show()

# FFT 수행
def perform_fft(data):
    n = len(data)
    T = t[1] - t[0]  # Sampling interval
    yf = fft(data)
    xf = fftfreq(n, T)[:n//2]
    return xf, 2.0/n * np.abs(yf[:n//2])

xf_gpu, yf_gpu = perform_fft(gpu_load_data)
xf_memory, yf_memory = perform_fft(memory_load_data)
xf_power, yf_power = perform_fft(power_usage_data)

# FFT 결과 그리기
plt.figure(figsize=(12, 6))
plt.plot(xf_gpu, yf_gpu, label='GPU Load FFT')
plt.plot(xf_memory, yf_memory, label='Memory Load FFT')
plt.plot(xf_power, yf_power, label='Power Usage FFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.legend()
plt.title('FFT of GPU Metrics')
plt.show()

# FFT 결과 합치기
yf_combined = yf_gpu + yf_memory + yf_power

# 합친 FFT 결과 그리기
plt.figure(figsize=(12, 6))
plt.plot(xf_gpu, yf_combined, label='Combined FFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.legend()
plt.title('Combined FFT of GPU Metrics')
plt.show()

# 주기 계산 및 표시
peak_freq = xf_gpu[np.argmax(yf_combined)]
period = 1 / peak_freq

print(f'Peak Frequency: {peak_freq} Hz')
print(f'Corresponding Period: {period} seconds')
