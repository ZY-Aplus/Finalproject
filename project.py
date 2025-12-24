import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import wavfile
import sounddevice as sd

class SignalWorkbench:
    def __init__(self, root):
        self.root = root
        self.root.title("互動式訊號產生器與頻譜分析實驗台 (Interactive Signal Workbench)")
        self.root.geometry("1000x800")

        # --- 系統參數初始設定 ---
        self.sample_rate = 44100  # 預設採樣率 (Hz)
        self.duration = 2.0       # 模擬訊號長度 (秒)
        self.is_file_mode = False # 模式旗標
        
        # 資料容器
        self.t = None             # 時間軸
        self.input_signal = None  # 原始訊號 (含噪)
        self.fft_freq = None      # 頻率軸
        self.fft_magnitude = None # 頻譜大小
        self.fft_complex = None   # FFT 複數結果 (用於還原)
        self.filtered_signal = None # 濾波後訊號

        # --- 建立 GUI ---
        self.setup_ui()
        
        # --- 初始化訊號 ---
        self.on_source_change()

    def setup_ui(self):
        """建立圖形介面佈局"""
        # 1. 繪圖區域 (Matplotlib Canvas)
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 6), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 2. 控制面板 (Control Panel)
        control_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # 左側：滑桿區
        sliders_frame = tk.Frame(control_frame)
        sliders_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # 頻率滑桿 (模擬用)
        tk.Label(sliders_frame, text="Sim Freq (Hz):").grid(row=0, column=0, sticky="w")
        self.slider_freq = tk.Scale(sliders_frame, from_=1, to=1000, orient=tk.HORIZONTAL, length=300, command=self.on_source_change)
        self.slider_freq.set(440) # 預設 A4 音
        self.slider_freq.grid(row=0, column=1)

        # 雜訊滑桿 (模擬用)
        tk.Label(sliders_frame, text="Add Noise:").grid(row=1, column=0, sticky="w")
        self.slider_noise = tk.Scale(sliders_frame, from_=0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, length=300, command=self.on_source_change)
        self.slider_noise.set(0.2)
        self.slider_noise.grid(row=1, column=1)

        # 截止頻率滑桿 (濾波器用)
        tk.Label(sliders_frame, text="Cutoff (Hz):").grid(row=2, column=0, sticky="w")
        self.slider_cutoff = tk.Scale(sliders_frame, from_=1, to=20000, orient=tk.HORIZONTAL, length=300, command=self.on_filter_change)
        self.slider_cutoff.set(1000)
        self.slider_cutoff.grid(row=2, column=1)

        # 右側：按鈕區
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT, padx=20)

        # 載入檔案按鈕
        self.btn_load = tk.Button(btn_frame, text="📂 Load .wav", font=("Arial", 10, "bold"), command=self.load_wav)
        self.btn_load.pack(side=tk.TOP, pady=5, fill=tk.X)

        # 播放按鈕
        self.btn_play = tk.Button(btn_frame, text="▶ Play Filtered", font=("Arial", 10, "bold"), bg="#d9ffcc", command=self.play_audio)
        self.btn_play.pack(side=tk.TOP, pady=5, fill=tk.X)

        # 停止按鈕
        self.btn_stop = tk.Button(btn_frame, text="⏹ Stop Audio", font=("Arial", 10), bg="#ffcccc", command=lambda: sd.stop())
        self.btn_stop.pack(side=tk.TOP, pady=5, fill=tk.X)

    # ==========================
    #   核心邏輯 (Model)
    # ==========================

    def generate_simulation(self):
        """生成模擬訊號：正弦波 + 高斯雜訊"""
        self.sample_rate = 44100
        N = int(self.sample_rate * self.duration)
        self.t = np.linspace(0, self.duration, N, endpoint=False)
        
        freq = self.slider_freq.get()
        noise_level = self.slider_noise.get()

        # 訊號合成原理 x(t) = A*sin(2pi*f*t) + Noise
        clean_signal = np.sin(2 * np.pi * freq * self.t)
        noise = np.random.normal(0, 1, N) * noise_level
        self.input_signal = clean_signal + noise

    def compute_fft(self):
        """執行快速傅立葉變換 (FFT)"""
        if self.input_signal is None: return
        
        N = len(self.input_signal)
        # FFT 運算
        self.fft_complex = np.fft.fft(self.input_signal)
        self.fft_freq = np.fft.fftfreq(N, d=1/self.sample_rate)
        
        # 取絕對值獲得振幅頻譜
        self.fft_magnitude = np.abs(self.fft_complex) / N

    def apply_filter_and_restore(self):
        """套用頻域遮罩並進行 IFFT 還原"""
        if self.fft_complex is None: return

        cutoff = self.slider_cutoff.get()
        
        # 製作理想低通濾波器遮罩 (Ideal Low-pass Mask)
        # H[k] = 1 if |f| <= fc else 0
        mask = np.abs(self.fft_freq) <= cutoff
        
        # 頻域濾波 Y[k] = X[k] * H[k]
        filtered_fft = self.fft_complex * mask
        
        # 逆傅立葉變換 (IFFT) 還原為時域
        self.filtered_signal = np.fft.ifft(filtered_fft).real

    # ==========================
    #   事件處理 (Controller)
    # ==========================

    def on_source_change(self, event=None):
        """當頻率或雜訊滑桿變動時觸發 -> 重算源頭"""
        if self.is_file_mode:
            return # 檔案模式下不重新生成模擬訊號
        
        self.generate_simulation()
        self.compute_fft()
        self.on_filter_change() # 源頭變了，濾波也要重做

    def on_filter_change(self, event=None):
        """當 Cutoff 滑桿變動時觸發 -> 只重算濾波 (不重骰雜訊)"""
        # 確保有資料
        if self.fft_complex is None: return

        self.apply_filter_and_restore()
        self.update_plots()

    def update_plots(self):
        """更新所有圖表 (View)"""
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # --- 設定顯示範圍 (Zoom Logic) ---
        display_limit = 1000 # 畫 1000 個點
        
        # 預設從頭開始 (模擬模式)
        start_idx = 0
        end_idx = display_limit

        if self.input_signal is not None:
            total_len = len(self.input_signal)
            
            # ★★★ 關鍵修正：如果是讀檔模式，我們抓正中間的數據，避開開頭靜音 ★★★
            if self.is_file_mode and total_len > display_limit:
                start_idx = total_len // 2  # 從中間開始
                end_idx = start_idx + display_limit
            
            # 邊界檢查
            if end_idx > total_len:
                start_idx = 0
                end_idx = min(display_limit, total_len)

            # 1. 原始訊號 (上圖)
            self.ax1.plot(self.t[start_idx:end_idx], self.input_signal[start_idx:end_idx], 
                          color='gray', alpha=0.7, label='Input Signal (Zoomed)')
            self.ax1.set_title("Input Time Domain Signal (Waveform)")
            self.ax1.set_ylabel("Amplitude")
            self.ax1.legend(loc="upper right")
            self.ax1.grid(True, alpha=0.3)

            # 3. 濾波後訊號 (下圖) - 必須跟上圖同一段時間，才能比較
            if self.filtered_signal is not None:
                self.ax3.plot(self.t[start_idx:end_idx], self.filtered_signal[start_idx:end_idx], 
                              color='green', linewidth=2, label='Restored Signal')
            
            self.ax3.set_title("Restored Time Domain Signal (After IFFT)")
            self.ax3.set_xlabel("Time (s)")
            self.ax3.legend(loc="upper right")
            self.ax3.grid(True, alpha=0.3)

        # 2. 頻譜圖 (中圖) - 頻譜是看整體的，不需要切片
        if self.fft_freq is not None:
            half_N = len(self.fft_freq) // 2
            pos_freqs = self.fft_freq[:half_N]
            pos_mags = self.fft_magnitude[:half_N]
            
            self.ax2.plot(pos_freqs, pos_mags, color='purple')
            self.ax2.set_title("Frequency Spectrum (FFT)")
            self.ax2.set_ylabel("Magnitude")
            self.ax2.grid(True, alpha=0.3)
            
            # 畫出 Cutoff 線
            cutoff = self.slider_cutoff.get()
            self.ax2.axvline(x=cutoff, color='blue', linestyle='--', label=f'Cutoff: {cutoff} Hz')
            self.ax2.legend()

            # 自適應 X 軸縮放
            if self.is_file_mode:
                self.ax2.set_xlim(0, 5000) # 真實音樂看 5kHz
            else:
                self.ax2.set_xlim(0, 2000) # 模擬訊號看 2kHz

        self.canvas.draw()

    # ==========================
    #   檔案與音訊功能
    # ==========================

    def load_wav(self):
        """讀取 WAV 檔案"""
        filename = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if not filename: return

        try:
            rate, data = wavfile.read(filename)
            self.sample_rate = rate
            
            # 處理雙聲道 -> 轉單聲道
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            # 正規化 (Normalize) 到 -1~1 之間
            data = data.astype(np.float32)
            max_val = np.max(np.abs(data))
            if max_val > 0:
                data = data / max_val
            
            self.input_signal = data
            self.t = np.arange(len(data)) / self.sample_rate
            self.is_file_mode = True
            
            # 調整 GUI
            self.root.title(f"目前檔案: {filename.split('/')[-1]}")
            
            # 執行運算
            self.compute_fft()
            self.on_filter_change()

        except Exception as e:
            messagebox.showerror("Error", f"無法讀取檔案: {e}")

    def play_audio(self):
        """播放濾波後的音訊"""
        if self.filtered_signal is None:
            return

        # 安全防護：音量正規化
        data_to_play = self.filtered_signal.copy()
        max_val = np.max(np.abs(data_to_play))
        if max_val > 0:
            data_to_play = data_to_play / max_val * 0.8 # 留一點 headroom

        # 非阻塞播放
        print(f"Playing audio at {self.sample_rate} Hz")
        sd.play(data_to_play, self.sample_rate, blocking=False)

# --- 程式進入點 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SignalWorkbench(root)
    root.mainloop()