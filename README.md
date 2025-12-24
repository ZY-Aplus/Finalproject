

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

1. **訊號合成原理**：模擬訊號由主頻率正弦波與隨機雜訊組成：

   $$x(t) = A \sin(2\pi f t) + N(\mu, \sigma)$$

   其中 $N(\mu, \sigma)$ 代表平均值為 $\mu$、標準差為 $\sigma$ 的常態分佈雜訊。

2. **快速傅立葉變換 (FFT)**：為了分析頻率成分，我們將離散時域訊號 $x[n]$ 轉換為頻域訊號 $X[k]$：

   $$X[k] = \sum_{n=0}^{N-1} x[n] e^{-j \frac{2\pi}{N} k n}$$

   這讓我們能從雜亂的時域波形中，分離出特定頻率的訊號與寬頻雜訊。

3. **頻域濾波**：低通濾波器的運作原理是對頻譜套用一個遮罩 $H[k]$：

$$Y[k] = X[k] \cdot H[k]$$

其中截止頻率 $f_c$ 定義了遮罩範圍（小於截止頻率為 1，大於則為 0）：

$$H[k] = 1 \quad (\text{if } |f| \le f_c), \quad H[k] = 0 \quad (\text{if } |f| > f_c)$$

最後透過逆傅立葉變換 (IFFT) 將 $Y[k]$ 還原為過濾後的時域訊號。
---

## (2) 使用方式 (Usage)
環境建置請確保已安裝以下 Python 套件：

`pip install numpy matplotlib scipy`
`pip install numpy matplotlib scipy sounddevice`
程式啟動後，您將看到包含三個圖表與控制面板的主視窗。操作模式分為「模擬訊號」與「真實音訊」兩種：

### 🅰 模式一：模擬訊號實驗 (Simulation Mode)
這是程式預設的模式，用於理解基本的訊號與雜訊原理。

1.  **設定訊號源**：
    * 調整 **Sim Freq (Hz)** 滑桿：設定正弦波的主頻率 (例如 440Hz)。
    * 調整 **Add Noise** 滑桿：注入高斯白雜訊。你會觀察到上圖 (Input) 的波形變得粗糙雜亂。
2.  **操作濾波器**：
    * 調整 **Cutoff (Hz)** 滑桿：移動藍色虛線。
    * **觀察重點**：當截止頻率低於主頻率時，訊號會被濾除；當截止頻率位於訊號與雜訊之間時，下圖 (Restored) 將顯示變乾淨的波形。
    * *Note：本程式採用邏輯分離設計，調整 Filter 時，上方的原始雜訊波形會保持鎖定 (Locked)，不會重新隨機生成，方便比較濾波前後差異。*

### 🅱 模式二：真實音訊分析 (Real Audio Mode)
用於分析樂器泛音、改變音色或去除錄音雜訊。

1.  **載入檔案**：
    * 點擊 **📂 Load .wav** 按鈕，選擇電腦中的 `.wav` 檔案 (例如鋼琴錄音)。
    * **程式會自動執行以下優化**：
        * **立體聲轉單聲道**：自動平均雙聲道數據。
        * **自適應縮放 (Auto-Zoom)**：自動抓取波形的「正中心切片 (Center Slice)」進行繪圖，避開錄音開頭的靜音區，確保波形清晰可見。
2.  **頻譜分析 (泛音觀察)**：
    * 觀察中間的 **Frequency Spectrum** 圖表。
    * 若是鋼琴等樂器聲音，你將看到明顯的**基頻 (Fundamental)** (最左側最高峰) 與右側排列整齊的**泛音列 (Harmonics)**。
3.  **濾波與聽覺驗證**：
    * 將 **Cutoff** 滑桿向左拉，切除右側的高頻泛音。
    * 點擊 **▶ Play Filtered** 按鈕。
    * **結果**：你將聽到聲音變「悶 (Muffled)」，證明濾波器成功濾除了構成音色的高頻細節。
    * 若需停止播放，請點擊 **⏹ Stop Audio**。

### 📊 圖表介面說明

* **上圖 (Input Time Domain)**：
    * 顯示原始輸入訊號 (含雜訊或原始錄音)。
    * 在讀檔模式下，自動顯示訊號中間段的波形細節。
* **中圖 (Frequency Spectrum FFT)**：
    * 顯示訊號的頻率分佈 (紫色線)。
    * **藍色虛線**代表濾波器的截止頻率 ($f_c$)，左邊保留，右邊濾除。
* **下圖 (Restored Time Domain)**：
    * 顯示經過 IFFT 還原後的時域波形 (濾波結果)。

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

## (6) 程式修改或增強 (Program Modifications & Enhancements)

相較於基礎範例，本專案針對「使用者體驗」、「程式架構」與「物理真實性」進行了大幅度的優化與功能擴充：

### 1. 架構優化：邏輯分離 (Logic Separation)
* **問題**：傳統寫法常將「訊號生成」與「濾波運算」寫在同一個迴圈中。這導致每當調整 Cutoff 頻率時，隨機雜訊 (Noise) 就會重新生成，導致波形不斷跳動，無法觀察「同一個雜訊樣本」在不同濾波參數下的變化。
* **修改**：導入類似 **MVC (Model-View-Controller)** 的概念，將事件處理拆分為：
    * `on_source_change`：只在改變頻率或雜訊量時，才重新生成訊號源。
    * `on_filter_change`：調整濾波器時，鎖定原始訊號源，僅重新計算 FFT 遮罩與 IFFT 還原。
* **效益**：實現了如真實示波器般的穩定操作體驗，讓使用者能清楚比較濾波前後的差異。

### 2. 功能增強：即時音訊回放 (Real-time Audio Playback)
* **新增功能**：整合 `sounddevice` 套件，實作 **非阻塞 (Non-blocking)** 音訊播放功能。
* **技術細節**：
    * **防爆音保護 (Normalization)**：在播放前自動偵測訊號最大振幅，並將其正規化至 `-1.0 ~ 1.0` 區間 (留有 0.8 的 Headroom)，保護使用者聽力與設備。
    * **播放控制**：新增 Play/Stop 按鈕，讓使用者能透過「聽覺」驗證濾波器是否成功去除了高頻泛音或雜訊。

### 3. 視覺優化：WAV 檔案自適應處理 (Adaptive Visualization)
* **問題**：真實樂器錄音 (如鋼琴) 在按下琴鍵前通常有 0.1~0.5 秒的「前置靜音 (Pre-roll)」。若直接繪製前 1000 個採樣點，圖表只會顯示一條死板的直線。
* **修改**：實作**自適應縮放演算法 (Auto-Zoom)**。
    * 程式會自動判斷目前模式。若為讀檔模式，自動計算訊號總長度的中點 (`len // 2`)，並抓取該處的「中心切片 (Center Slice)」進行繪圖。
* **效益**：確保使用者載入任何錄音檔時，都能立刻看到波形最豐富、振幅最大的部分，無需手動調整。

### 4. 訊號處理強健性 (Robustness)
* **立體聲轉單聲道**：使用 `numpy.mean(axis=1)` 自動將雙聲道錄音檔轉為單聲道訊號，以利 FFT 頻譜分析。
* **採樣率解析**：不再假設所有檔案都是 44100Hz，而是從 WAV檔頭 (Header) 動態讀取真實 Sample Rate，確保頻率軸與播放速度正確。
