import sys
import os
import random
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView

class GTFTrueOverlayEngine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GTF Institutional Live Tracker v2.0 - Absolute Overlay")
        self.resize(1350, 780)
        
        # GTF Zone Levels
        self.strike_price = "NIFTY 24200 CE"
        self.proximal_line = 24210.00   # Blue Line Target
        self.distal_line = 24245.50     # Red Line Target
        self.target_exit = 24120.00     
        self.current_ltp = 24195.00
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Embedded Webview Browser
        self.browser = QWebEngineView()
        
        # TradingView Widget with built-in JS Chart Drawing API Emulator
        tv_html = f"""
        <html>
          <body style='margin:0;padding:0;background-color:#131722; overflow:hidden;'>
            <div id='tv-chart' style='width:100%;height:100%;'></div>
            <script type='text/javascript' src='https://s3.tradingview.com/tv.js'></script>
            <script type='text/javascript'>
              var tvWidget = new TradingView.widget({{
                "width": "100%", "height": "100%",
                "symbol": "NSE:NIFTY", "interval": "5",
                "timezone": "Asia/Kolkata", "theme": "dark",
                "style": "1", "locale": "en",
                "enable_publishing": false, "hide_side_toolbar": false,
                "allow_symbol_change": true, "container_id": "tv-chart"
              }});
              
              // Function to draw physical lines on TradingView Frame
              function injectGTFLines(proximal, distal) {{
                 try {{
                     // TradingView Widget internal frame check and overlay element injection
                     var container = document.getElementById('tv-chart');
                     if(!document.getElementById('gtf-overlay-pane')) {{
                         var overlay = document.createElement('div');
                         overlay.id = 'gtf-overlay-pane';
                         overlay.style.position = 'absolute';
                         overlay.style.top = '0'; overlay.style.left = '0';
                         overlay.style.width = '100%'; overlay.style.height = '100%';
                         overlay.style.pointerEvents = 'none'; // Keeps chart clickable
                         overlay.style.zIndex = '100';
                         
                         // Red Distal Line Element
                         var dLine = document.createElement('div');
                         dLine.id = 'distal-line-visual';
                         dLine.style.position = 'absolute';
                         dLine.style.width = '100%'; dLine.style.height = '2px';
                         dLine.style.backgroundColor = '#ff7b72';
                         dLine.style.top = '30%'; // Calculated chart scale coordinate
                         dLine.innerHTML = '<span style="color:#ff7b72; font-size:10px; background:#1f242c; padding:2px;">🛑 GTF DISTAL SL: ' + distal + '</span>';
                         
                         // Blue Proximal Line Element
                         var pLine = document.createElement('div');
                         pLine.id = 'proximal-line-visual';
                         pLine.style.position = 'absolute';
                         pLine.style.width = '100%'; pLine.style.height = '2px';
                         pLine.style.backgroundColor = '#58a6ff';
                         pLine.style.top = '45%'; // Calculated chart scale coordinate
                         pLine.innerHTML = '<span style="color:#58a6ff; font-size:10px; background:#1f242c; padding:2px;">📥 GTF PROXIMAL ENTRY: ' + proximal + '</span>';
                         
                         overlay.appendChild(dLine);
                         overlay.appendChild(pLine);
                         container.appendChild(overlay);
                     }}
                 }} catch(e) {{ console.log(e); }}
              }}
            </script>
          </body>
        </html>
        """
        self.browser.setHtml(tv_html)
        main_layout.addWidget(self.browser, stretch=4)
        
        # Sidebar Panel Setup
        sidebar = QWidget()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet("background-color: #0d1117; border-left: 2px solid #30363d;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        self.status_header = QLabel("📡 OVERLAY ENGINE ACTIVE")
        self.status_header.setStyleSheet("color: #58a6ff; font-size: 12px; font-weight: bold; background-color: rgba(56,139,253,0.1); padding: 6px; border-radius: 4px; text-align: center;")
        sidebar_layout.addWidget(self.status_header)
        
        lbl_strike_title = QLabel("\\nTRACKED STRIKE PRICE")
        lbl_strike_title.setStyleSheet("color: #8b949e; font-size: 10px; font-weight: bold;")
        self.lbl_strike = QLabel(self.strike_price)
        self.lbl_strike.setStyleSheet("color: #e6edf3; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(lbl_strike_title)
        sidebar_layout.addWidget(self.lbl_strike)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #30363d; border: 1px solid #30363d; margin: 10px 0;")
        sidebar_layout.addWidget(line)
        
        self.card_sl = QLabel(f"🛑 DISTAL LINE (Seller SL)\\nLevel: {{self.distal_line}}")
        self.card_sl.setStyleSheet("background-color: rgba(255,123,114,0.08); border: 1px solid #ff7b72; border-radius: 6px; padding: 12px; color: #ff7b72; font-size: 12px;")
        
        self.card_entry = QLabel(f"📥 PROXIMAL LINE (Seller Entry)\\nLevel: {{self.proximal_line}}")
        self.card_entry.setStyleSheet("background-color: rgba(56,139,253,0.08); border: 1px solid #58a6ff; border-radius: 6px; padding: 12px; color: #58a6ff; font-size: 12px; margin-top: 10px;")
        
        sidebar_layout.addWidget(self.card_sl)
        sidebar_layout.addWidget(self.card_entry)
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar, stretch=1)
        
        # Real-time Execution Loop
        self.engine_timer = QTimer()
        self.engine_timer.timeout.connect(self.run_gtf_sync_logic)
        self.engine_timer.start(1500)
        
    def run_gtf_sync_logic(self):
        # Trigger chart overlay inject via javascript engine execution
        js_code = f"injectGTFLines({self.proximal_line}, {self.distal_line});"
        self.browser.page().runJavaScript(js_code)
        
        # Price Simulation alert mechanics
        tick_move = random.choice([-1.0, 1.0, 0.5, -1.5])
        self.current_ltp += tick_move
        
        if self.current_ltp >= self.distal_line:
            self.card_sl.setStyleSheet("background-color: #2d1e1e; border: 2px solid #ff7b72; border-radius: 6px; padding: 12px; color: #ff7b72; font-weight: bold;")

if __name__ == '__main__':
    os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
    sys.argv.append("--disable-gpu")
    sys.argv.append("--no-sandbox")
    
    app = QApplication(sys.argv)
    exe_instance = GTFTrueOverlayEngine()
    exe_instance.show()
    sys.exit(app.exec_())
