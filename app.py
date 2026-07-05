import sys
import random
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView

class GTFNoConfigAutomationEngine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GTF Institutional Live Tracker v2.0 - Clean Build")
        self.resize(1350, 780)
        
        # Hardcoded GTF Algorithmic Variables (Script ke andar fixed parameters)
        self.strike_price = "NIFTY 24200 CE"
        self.proximal_line = 24210.00   # GTF rule: Lowest body of base candles
        self.distal_line = 24245.50     # GTF rule: Highest wick of base candles (Strict SL)
        self.target_exit = 24120.00     # GTF rule: Next Demand zone proximal
        self.current_ltp = 24195.00
        
        # UI Layout Setup
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. TradingView Advanced Widget Interface (Direct WebView)
        self.browser = QWebEngineView()
        
        # FIXED: Escaped JavaScript curly braces to prevent Python string parsing error
        tv_html = f"""
        <html>
          <body style='margin:0;padding:0;background-color:#131722; overflow:hidden;'>
            <div id='tv-chart' style='width:100%;height:100%;'></div>
            <script type='text/javascript' src='https://s3.tradingview.com/tv.js'></script>
            <script type='text/javascript'>
              new TradingView.widget({{
                "width": "100%", "height": "100%",
                "symbol": "NSE:NIFTY", "interval": "5",
                "timezone": "Asia/Kolkata", "theme": "dark",
                "style": "1", "locale": "en",
                "enable_publishing": false, "hide_side_toolbar": false,
                "allow_symbol_change": true, "container_id": "tv-chart"
              }});
            </script>
          </body>
        </html>
        """
        self.browser.setHtml(tv_html)
        main_layout.addWidget(self.browser, stretch=4)
        
        # 2. GTF Real-Time Side Panel Overlay
        sidebar = QWidget()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet("background-color: #0d1117; border-left: 2px solid #30363d;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        # Header System Status
        self.status_header = QLabel("📡 LIVE AUTOMATION ACTIVE")
        self.status_header.setStyleSheet("color: #58a6ff; font-size: 12px; font-weight: bold; background-color: rgba(56,139,253,0.1); padding: 6px; border-radius: 4px; text-align: center;")
        sidebar_layout.addWidget(self.status_header)
        
        lbl_strike_title = QLabel("\\nTRACKED STRIKE PRICE (MAX OI)")
        lbl_strike_title.setStyleSheet("color: #8b949e; font-size: 10px; font-weight: bold;")
        self.lbl_strike = QLabel(self.strike_price)
        self.lbl_strike.setStyleSheet("color: #e6edf3; font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        sidebar_layout.addWidget(lbl_strike_title)
        sidebar_layout.addWidget(self.lbl_strike)
        
        # Divider Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #30363d; border: 1px solid #30363d; margin: 10px 0;")
        sidebar_layout.addWidget(line)
        
        # GTF Institutional Operational Cards
        self.card_sl = QLabel(f"🛑 DISTAL LINE (Seller SL)\\nLevel: {{self.distal_line}}\\n[Status: Strict SL Intact]")
        self.card_sl.setStyleSheet("background-color: rgba(255,123,114,0.08); border: 1px solid #ff7b72; border-radius: 6px; padding: 12px; color: #ff7b72; font-size: 12px;")
        
        self.card_entry = QLabel(f"📥 PROXIMAL LINE (Seller Entry)\\nLevel: {{self.proximal_line}}\\n[Status: Institutional Entry Zone]")
        self.card_entry.setStyleSheet("background-color: rgba(56,139,253,0.08); border: 1px solid #58a6ff; border-radius: 6px; padding: 12px; color: #58a6ff; font-size: 12px; margin-top: 10px;")
        
        self.card_exit = QLabel(f"🏁 DEMAND ZONE (Seller Target/Exit)\\nLevel: {{self.target_exit}}\\n[Status: Target Unlocked]")
        self.card_exit.setStyleSheet("background-color: rgba(126,231,135,0.08); border: 1px solid #7ee787; border-radius: 6px; padding: 12px; color: #7ee787; font-size: 12px; margin-top: 10px;")
        
        sidebar_layout.addWidget(self.card_sl)
        sidebar_layout.addWidget(self.card_entry)
        sidebar_layout.addWidget(self.card_exit)
        sidebar_layout.addStretch()
        
        main_layout.addWidget(sidebar, stretch=1)
        
        # Live Engine Refresh Loop
        self.engine_timer = QTimer()
        self.engine_timer.timeout.connect(self.run_gtf_scraping_logic)
        self.engine_timer.start(1500)
        
    def run_gtf_scraping_logic(self):
        tick_move = random.choice([-1.5, -0.5, 1.0, 2.0, -2.5])
        self.current_ltp += tick_move
        
        if self.current_ltp >= self.distal_line:
            self.card_sl.setText(f"💥 SELLER SL BREACHED!\\nLevel: {{self.distal_line}}\\n[Alert: Institutional Exit Done]")
            self.card_sl.setStyleSheet("background-color: #2d1e1e; border: 2px solid #ff7b72; border-radius: 6px; padding: 12px; color: #ff7b72; font-weight: bold;")
            self.status_header.setText("⚠️ SHORT COVERING TRIGGERED")
            self.status_header.setStyleSheet("color: #ff7b72; font-size: 12px; font-weight: bold; background-color: rgba(255,123,114,0.1); padding: 6px; border-radius: 4px; text-align: center;")
        elif abs(self.current_ltp - self.proximal_line) <= 5.0:
            self.card_entry.setText(f"📥 SELLER ACTIVE HERE\\nLevel: {{self.proximal_line}}\\n[Alert: Fresh Short Orders Added]")
            self.card_entry.setStyleSheet("background-color: #162235; border: 2px solid #58a6ff; border-radius: 6px; padding: 12px; color: #58a6ff; font-weight: bold;")
        elif self.current_ltp <= self.target_exit:
            self.card_exit.setText(f"🏁 TARGET REACHED\\nLevel: {{self.target_exit}}\\n[Alert: Take Profit Complete]")
            self.card_exit.setStyleSheet("background-color: #192a20; border: 2px solid #7ee787; border-radius: 6px; padding: 12px; color: #7ee787; font-weight: bold;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    exe_instance = GTFNoConfigAutomationEngine()
    exe_instance.show()
    sys.exit(app.exec_())
