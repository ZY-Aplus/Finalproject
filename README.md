

# 互動式訊號產生器與頻譜分析實驗台 (Interactive Signal Processing Workbench)

## (1) 程式的原理與功能 (Principles & Functions)
本專案旨在建立一個結合「數學模擬」與「工程應用」的訊號處理虛擬實驗室，透過圖形化介面直觀地展示時域與頻域的轉換關係。

### 核心功能
- 訊號模擬 (Signal Simulation)： 可生成指定頻率的正弦波，並模擬真實環境疊加高斯白雜訊 (Gaussian White Noise)  
- 頻譜視覺化 (FFT Analysis)： 利用快速傅立葉變換將時域波形轉為頻域，視覺化展示訊號的頻率分佈  
- 數位濾波 (Digital Filtering)： 實作理想低通濾波器 (Low-pass Filter)，使用者可透過滑桿設定截止頻率，即時觀察濾波與還原效果  
- 真實音訊處理 (Real-world Audio)： 支援載入 `.wav` 音訊檔案，自動進行聲道合併與正規化，實現對真實錄音的降噪測試  

### 數學與物理原理
本程式核心基於數位訊號處理 (DSP) 理論：

1. 訊號合成原理：模擬訊號由主頻率正弦波與隨機雜訊組成：  
   ![公式](https://latex.codecogs.com/png.latex?x(t)=A\sin(2\pi ft)+N(\mu,\sigma))  
   其中 N(μ,σ) 代表平均值為 μ、標準差為 σ 的常態分佈雜訊 (Gaussian Noise)。  

2. 快速傅立葉變換 (FFT)：為了分析頻率成分，我們將離散時域訊號 x[n] 轉換為頻域訊號 X[k]：  
   ![公式](https://latex.codecogs.com/png.latex?X[k]=\sum_{n=0}^{N-1}x[n]e^{-j\frac{2\pi}{N}kn})  
   這讓我們能從雜亂的時域波形中，分離出特定頻率的訊號與寬頻雜訊。  

3. 頻域濾波 (Frequency Domain Filtering)：低通濾波器的運作原理是對頻譜套用一個遮罩 (Mask) H[k]：  
   ![公式](https://latex.codecogs.com/png.latex?Y[k]=X[k]\cdot H[k])  
   其中截止頻率 (Cutoff Frequency) fc 定義了遮罩範圍：  
   ![公式](https://latex.codecogs.com/png.latex?H[k]=\begin{cases}1,&|f|\leq f_c\text{(保留低頻)}\\0,&|f|>f_c\text{(濾除高頻)}\end{cases})  
   最後透過逆傅立葉變換 (IFFT) 將 Y[k] 還原為過濾後的時域訊號。   

---

## (2) 使用方式 (Usage)
環境建置請確保已安裝以下 Python 套件：

`pip install numpy matplotlib scipy`

---

## (3) 程式的架構 (Architecture)
本程式採用 MVC (Model-View-Controller) 變體架構，確保邏輯清晰並對應上述數學原理：

1. Model (運算核心層) - 對應數學原理：  
   - generate_simulation: 負責訊號合成公式  
   - compute_fft: 負責執行 FFT 運算  
   - apply_filter_and_restore: 負責套用濾波遮罩與 IFFT 還原  
   - load_wav_file: 負責真實音訊的讀取、轉單聲道與正規化  

2. View (視覺層) - 負責呈現：  
   - 使用 matplotlib.pyplot 建立三個子圖：  
     - Top: Input Signal (時域輸入)  
     - Mid: Frequency Spectrum (頻域分析 + Cutoff 線)  
     - Bottom: Restored Signal (濾波後時域輸出)  
   - 使用 set_ydata 進行局部渲染，實現流暢動畫  

3. Controller (互動控制層) - 負責邏輯分流：  
   - update_source: 監聽 Freq/Noise 滑桿，觸發訊號重算  
   - update_filter: 監聽 Cutoff 滑桿，僅觸發濾波計算，不重算訊號源 (詳見開發過程)  

---

## (4) 開發過程 (Development Process)
### 題目發想
起初希望能製作即時麥克風頻譜儀，但考量硬體延遲與緩衝區處理過於複雜，且難以量化教學效果。因此轉向開發「虛擬實驗台」，結合數學模擬與檔案處理，讓使用者能更可控地實驗訊號處理原理。  

### 遭遇困難與解決方案
- 困難點：隨機雜訊的視覺跳動 (The Flicker Issue)  
- 現象：在開發中期發現，當我調整濾波器 (Cutoff) 時，畫面上方的「原始雜訊波形」也會跟著劇烈跳動  
- 原因：原始程式邏輯在 update 迴圈中，每次滑桿變動都重新呼叫 np.random.normal，導致雜訊被重新生成 (Resampling)  
- 解決：重構程式架構，將更新邏輯拆分為 update_source 與 update_filter  
  - 動 Freq/Noise 時 -> 呼叫 update_source (重骰亂數)  
  - 動 Cutoff 時 -> 呼叫 update_filter (鎖定亂數種子，只重算 FFT Mask)  
  - 此修改成功模擬了真實示波器的行為  

---

## (5) 參考資料來源 (References)
- NumPy Documentation: 查閱 numpy.fft.fft 與 numpy.fft.fftfreq 的實作細節  
- Matplotlib Gallery: 參考 Slider 與 Button 的 Event Handling 寫法  
- SciPy Documentation: 查閱 scipy.io.wavfile.read 用於音訊讀取  

### LLM 協作說明 (ChatGPT/Gemini)
本專案在開發過程中使用 LLM 作為技術顧問，具體協作內容如下：  
- 效能優化：詢問 LLM 如何解決 Matplotlib 動畫卡頓問題。LLM 建議使用 line.set_ydata() 取代 plt.plot() 重繪，並使用 fig.canvas.draw_idle()，大幅提升了 FPS  
- 雙聲道處理：詢問如何處理立體聲 WAV 檔。LLM 提供了 data.mean(axis=1) 的 NumPy 矩陣運算建議，將雙聲道轉為單聲道以利 FFT 分析  
> (註：核心程式架構、邏輯拆分為自行開發)  

---

## (6) 程式修改或增強的內容 (Modifications & Enhancements)
相較於網路上基礎的 FFT 範例程式，本專案在實用性與架構上做了以下大幅度的增強（我的貢獻）：  

1. **邏輯分離架構 (Logic Separation for Physics Accuracy)**  
   網路上的範例通常只有單一 update 函式。我自行設計了分離式的更新機制（Source vs Filter），解決了蒙地卡羅模擬中常見的「雜訊重骰」問題。這讓使用者在調整濾波器時，能觀察到「同一個含噪訊號」的變化，這是非常關鍵的改進。  

2. **真實音訊整合 (Real-world Integration)**  
   將原本僅能跑數學模擬的程式，擴充為支援 `.wav` 檔案。實作了 WAV 檔解析器，包含立體聲轉單聲道 (Stereo-to-Mono) 與振幅正規化 (Normalization) 演算法，確保能處理各種來源的音訊檔，提升了專案的工程實用價值。  

3. **自適應視覺化 (Adaptive Visualization)**  
   實作了座標軸動態縮放 (Auto-scaling) 功能。  
   當處理模擬訊號 (低頻 50Hz) 時，與處理真實音訊 (高頻 20kHz) 時，程式會自動判斷並調整頻譜圖的 X 軸與 Cutoff 滑桿範圍，提供最佳的使用者體驗 (UX)。  