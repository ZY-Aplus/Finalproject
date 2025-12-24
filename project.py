import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.io import wavfile
import tkinter as tk
from tkinter import filedialog

# 隱藏 tkinter 主視窗 (只用來跳出檔案選擇框)
root = tk.Tk()
root.withdraw()

# --- 1. 參數設定 ---
# 預設模擬參數
default_fs = 1000
duration = 1.0 # 為了效能，預設只取前 1 秒 (若讀取檔案)

# 全域變數 (用來儲存當前的訊號狀態)
current_fs = default_fs
current_clean = None
current_noisy = None
current_yf_complex = None
current_xf = None
is_file_mode = False # 標記目前是否為檔案模式

# --- 2. 運算函式 ---
def generate_simulation(f, n_level):
    """[模式 A] 生成模擬訊號"""
    global current_fs
    current_fs = default_fs
    t = np.linspace(0, duration, int(current_fs * duration), endpoint=False)
    clean = np.sin(2 * np.pi * f * t)
    noise = np.random.normal(0, n_level, clean.shape)
    return t, clean, clean + noise

def load_wav_file(filepath):
    """[模式 B] 讀取真實 WAV 檔案"""
    global current_fs
    
    # 讀取檔案
    fs, data = wavfile.read(filepath)
    current_fs = fs
    
    # 正規化 (Normalize) 到 -1~1 之間，方便繪圖
    if data.dtype == np.int16:
        data = data / 32768.0
    elif data.dtype == np.int32:
        data = data / 2147483648.0
        
    # 如果是雙聲道 (Stereo)，轉為單聲道 (Mono)
    if len(data.shape) > 1:
        data = data.mean(axis=1)
        
    # 裁切長度 (避免檔案太長跑不動，這裡限制最多跑 2 秒)
    limit_samples = int(current_fs * 2.0) 
    if len(data) > limit_samples:
        data = data[:limit_samples]
        
    t = np.arange(len(data)) / current_fs
    
    # 真實檔案通常自帶雜訊，這裡我們把「讀進來的」當作 clean (或是 base)
    # 為了讓 Noise 滑桿還能用，我們允許使用者疊加額外雜訊測試
    return t, data

def compute_fft(signal):
    n = len(signal)
    yf = np.fft.fft(signal)
    xf = np.fft.fftfreq(n, 1/current_fs)
    half_n = n // 2
    # 回傳: 頻率軸, 振幅, 複數頻譜
    return xf[:half_n], np.abs(yf)[:half_n] / half_n, yf

def apply_filter_and_restore(yf_complex, cutoff):
    n = len(yf_complex)
    xf = np.fft.fftfreq(n, 1/current_fs)
    
    yf_filtered = yf_complex.copy()
    # 低通濾波
    yf_filtered[np.abs(xf) > cutoff] = 0
    
    restored = np.real(np.fft.ifft(yf_filtered))
    return restored

# --- 3. 建立繪圖 ---
fig, (ax_time_input, ax_freq, ax_time_output) = plt.subplots(3, 1, figsize=(10, 10))
plt.subplots_adjust(left=0.1, bottom=0.30, hspace=0.4) # 底部留更多空間給按鈕

# 預設先執行一次模擬
t, current_clean, current_noisy = generate_simulation(5.0, 0.5)
current_xf, yf_amp, current_yf_complex = compute_fft(current_noisy)
restored_sig = apply_filter_and_restore(current_yf_complex, 10.0)

# 繪圖物件
l_noisy, = ax_time_input.plot(t, current_noisy, color='red', alpha=0.5, label='Input (Noisy)')
l_clean, = ax_time_input.plot(t, current_clean, 'g--', label='Base / Original', lw=1.5, alpha=0.7)
ax_time_input.set_title("1. Time Domain: Input Signal")
ax_time_input.legend(loc='upper right', fontsize='small')

l_fft, = ax_freq.plot(current_xf, yf_amp, color='purple', label='Spectrum')
l_cutoff_line = ax_freq.axvline(x=10.0, color='blue', linestyle='--', lw=2, label='Cutoff')
ax_freq.set_title("2. Frequency Domain")
ax_freq.set_xlabel("Frequency (Hz)")
ax_freq.legend(loc='upper right', fontsize='small')

l_restored, = ax_time_output.plot(t, restored_sig, color='blue', label='Filtered Result')
ax_time_output.set_title("3. Time Domain: Restored Result")
ax_time_output.legend(loc='upper right', fontsize='small')

# --- 4. 介面元件 (滑桿 + 按鈕) ---
ax_color = 'lightgoldenrodyellow'
# 滑桿位置
ax_freq_s   = plt.axes([0.15, 0.18, 0.65, 0.03], facecolor=ax_color)
ax_noise_s  = plt.axes([0.15, 0.13, 0.65, 0.03], facecolor=ax_color)
ax_cutoff_s = plt.axes([0.15, 0.08, 0.65, 0.03], facecolor=ax_color)
# 按鈕位置
ax_load_btn = plt.axes([0.8, 0.025, 0.1, 0.04]) # 右下角

s_freq   = Slider(ax_freq_s, 'Sim Freq', 1.0, 50.0, valinit=5.0)
s_noise  = Slider(ax_noise_s, 'Add Noise', 0.0, 1.0, valinit=0.5)
s_cutoff = Slider(ax_cutoff_s, 'Cutoff Hz', 1.0, 2000.0, valinit=10.0) # 範圍加大以適應真實音訊
btn_load = Button(ax_load_btn, 'Load .wav', hovercolor='0.975')

# --- 5. 更新邏輯 ---

def update_plots(new_t, new_clean, new_noisy):
    """通用繪圖更新函式"""
    global current_xf, current_yf_complex
    
    # 1. 計算 FFT
    current_xf, yf_amp, current_yf_complex = compute_fft(new_noisy)
    
    # 2. 應用濾波
    cut = s_cutoff.val
    restored = apply_filter_and_restore(current_yf_complex, cut)
    
    # 3. 更新圖表數據
    # X 軸可能變了 (因為不同檔案長度不同)，所以要重設 xdata
    l_clean.set_data(new_t, new_clean)
    l_noisy.set_data(new_t, new_noisy)
    
    ax_time_input.set_xlim(0, new_t[-1]) # 自動調整 X 軸範圍
    ax_time_input.set_ylim(min(new_noisy)*1.2, max(new_noisy)*1.2)
    
    l_fft.set_data(current_xf, yf_amp)
    ax_freq.set_xlim(0, cut * 2 if cut > 50 else 100) # 頻譜顯示範圍隨 Cutoff 動態調整
    ax_freq.set_ylim(0, max(yf_amp)*1.1)
    l_cutoff_line.set_xdata([cut, cut])
    
    l_restored.set_data(new_t, restored)
    ax_time_output.set_xlim(0, new_t[-1])
    ax_time_output.set_ylim(min(restored)*1.2, max(restored)*1.2)
    
    fig.canvas.draw_idle()

def update_source(val):
    """滑桿變動時觸發"""
    global current_clean, current_noisy
    
    n_lvl = s_noise.val
    
    if is_file_mode:
        # 檔案模式：基礎訊號是檔案本身，疊加雜訊
        # 注意：這裡不重新讀檔，只加雜訊
        t = np.arange(len(current_clean)) / current_fs
        noise = np.random.normal(0, n_lvl, current_clean.shape)
        current_noisy = current_clean + noise
        update_plots(t, current_clean, current_noisy)
    else:
        # 模擬模式：使用 Freq 滑桿
        f = s_freq.val
        t, current_clean, current_noisy = generate_simulation(f, n_lvl)
        update_plots(t, current_clean, current_noisy)

def update_filter(val):
    """Cutoff 變動時觸發"""
    cut = s_cutoff.val
    # 只更新 Cutoff 線和還原結果
    restored = apply_filter_and_restore(current_yf_complex, cut)
    
    l_cutoff_line.set_xdata([cut, cut])
    l_restored.set_ydata(restored)
    
    # 動態調整頻譜 X 軸，避免真實音訊頻率太高看不到
    ax_freq.set_xlim(0, max(100, cut * 2)) 
    
    fig.canvas.draw_idle()

def on_load_click(event):
    """按下載入按鈕"""
    global is_file_mode, current_clean, current_noisy, current_fs
    
    filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if filename:
        is_file_mode = True
        print(f"Loading: {filename}")
        
        # 讀取檔案
        t, data = load_wav_file(filename)
        current_clean = data # 將讀入的檔案視為乾淨/基礎訊號
        
        # 加上目前的雜訊設定
        n_lvl = s_noise.val
        noise = np.random.normal(0, n_lvl, current_clean.shape)
        current_noisy = current_clean + noise
        
        # 更新圖表
        update_plots(t, current_clean, current_noisy)
        ax_time_input.set_title(f"Input Signal: {filename.split('/')[-1]}")

# 綁定事件
s_freq.on_changed(update_source)
s_noise.on_changed(update_source)
s_cutoff.on_changed(update_filter)
btn_load.on_clicked(on_load_click)

plt.show()