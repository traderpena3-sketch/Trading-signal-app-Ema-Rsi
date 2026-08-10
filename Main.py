import requests
from datetime import datetime
from zoneinfo import ZoneInfo

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle


# =========================
# SETTINGS
# =========================

PAIRS = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "USD/CHF",
    "AUD/USD",
    "USD/CAD",
    "NZD/USD"
]

TIMEFRAMES = [
    "1min",
    "5min",
    "15min"
]

EMA_FAST = 2
EMA_SLOW = 5


# =========================
# INDICATORS
# =========================

def ema(values, period):
    if len(values) < period:
        return []

    multiplier = 2 / (period + 1)

    result = []
    previous = sum(values[:period]) / period
    result.append(previous)

    for price in values[period:]:
        current = (price - previous) * multiplier + previous
        result.append(current)
        previous = current

    return result


def rsi(values, period=14):
    if len(values) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, len(values)):
        change = values[i] - values[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    current_rsi = 100 - (100 / (1 + rs))

    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

        if avg_loss == 0:
            current_rsi = 100
        else:
            rs = avg_gain / avg_loss
            current_rsi = 100 - (100 / (1 + rs))

    return current_rsi


# =========================
# MAIN APP
# =========================

class SignalApp(App):

    def build(self):

        self.title = "Forex Signal Bot"

        root = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=10
        )

        # Background
        with root.canvas.before:
            Color(0.03, 0.05, 0.04, 1)
            self.bg = RoundedRectangle(
                pos=root.pos,
                size=root.size,
                radius=[20]
            )

        root.bind(
            pos=lambda obj, val: setattr(
                self.bg, "pos", val
            )
        )

        root.bind(
            size=lambda obj, val: setattr(
                self.bg, "size", val
            )
        )

        # =========================
        # TITLE
        # =========================

        title = Label(
            text="[b]AI FOREX SIGNAL BOT[/b]",
            markup=True,
            font_size="24sp",
            size_hint_y=None,
            height=55
        )

        root.add_widget(title)

        subtitle = Label(
            text="EMA 2 / EMA 5 + RSI confirmation",
            font_size="13sp",
            size_hint_y=None,
            height=30
        )

        root.add_widget(subtitle)

        # =========================
        # API KEY
        # =========================

        api_layout = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=8
        )

        self.api_input = TextInput(
            hint_text="Twelve Data API Key",
            password=True,
            multiline=False
        )

        api_layout.add_widget(self.api_input)

        root.add_widget(api_layout)

        # =========================
        # PAIR
        # =========================

        pair_layout = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=8
        )

        pair_label = Label(
            text="PAIR",
            size_hint_x=0.30
        )

        self.pair_spinner = Spinner(
            text="EUR/USD",
            values=PAIRS
        )

        pair_layout.add_widget(pair_label)
        pair_layout.add_widget(self.pair_spinner)

        root.add_widget(pair_layout)

        # =========================
        # TIMEFRAME
        # =========================

        tf_layout = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=8
        )

        tf_label = Label(
            text="TIMEFRAME",
            size_hint_x=0.30
        )

        self.tf_spinner = Spinner(
            text="5min",
            values=TIMEFRAMES
        )

        tf_layout.add_widget(tf_label)
        tf_layout.add_widget(self.tf_spinner)

        root.add_widget(tf_layout)

        # =========================
        # SCAN BUTTON
        # =========================

        self.scan_button = Button(
            text="SCAN MARKET",
            size_hint_y=None,
            height=55,
            font_size="18sp"
        )

        self.scan_button.bind(
            on_press=self.scan_market
        )

        root.add_widget(self.scan_button)

        # =========================
        # RESULT AREA
        # =========================

        scroll = ScrollView()

        self.result_box = GridLayout(
            cols=1,
            spacing=8,
            size_hint_y=None,
            padding=10
        )

        self.result_box.bind(
            minimum_height=self.result_box.setter(
                "height"
            )
        )

        scroll.add_widget(self.result_box)

        root.add_widget(scroll)

        self.set_result(
            "WAITING FOR MARKET SCAN..."
        )

        return root

    # =========================
    # RESULT DISPLAY
    # =========================

    def set_result(self, text):

        self.result_box.clear_widgets()

        label = Label(
            text=text,
            markup=True,
            font_size="17sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=300
        )

        label.bind(
            width=lambda obj, value: setattr(
                obj, "text_size", (value - 20, None)
            )
        )

        self.result_box.add_widget(label)

    # =========================
    # MARKET SCAN
    # =========================

    def scan_market(self, instance):

        api_key = self.api_input.text.strip()
        pair = self.pair_spinner.text
        interval = self.tf_spinner.text

        if not api_key:
            self.set_result(
                "[b]API KEY REQUIRED[/b]\n\n"
                "Enter your Twelve Data API key first."
            )
            return

        self.scan_button.disabled = True
        self.scan_button.text = "SCANNING..."

        self.set_result(
            "Connecting to market data...\n\n"
            "Please wait..."
        )

        # Run after UI updates
        Clock.schedule_once(
            lambda dt: self.get_market_data(
                api_key,
                pair,
                interval
            ),
            0.2
        )

    # =========================
    # GET DATA
    # =========================

    def get_market_data(
        self,
        api_key,
        pair,
        interval
    ):

        try:

            url = "https://api.twelvedata.com/time_series"

            params = {
                "symbol": pair,
                "interval": interval,
                "outputsize": 100,
                "apikey": api_key
            }

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            data = response.json()

            if "status" in data and data["status"] == "error":

                message = data.get(
                    "message",
                    "Unknown API error"
                )

                self.set_result(
                    "[b]API ERROR[/b]\n\n"
                    + str(message)
                )

                self.scan_button.disabled = False
                self.scan_button.text = "SCAN MARKET"
                return

            values = data.get("values")

            if not values:

                self.set_result(
                    "[b]NO MARKET DATA[/b]\n\n"
                    "Twelve Data did not return candle data."
                )

                self.scan_button.disabled = False
                self.scan_button.text = "SCAN MARKET"
                return

            # Twelve Data returns newest first.
            values = list(reversed(values))

            closes = []

            for candle in values:
                try:
                    closes.append(
                        float(candle["close"])
                    )
                except:
                    pass

            if len(closes) < 30:

                self.set_result(
                    "[b]NOT ENOUGH DATA[/b]\n\n"
                    "Waiting for more candles."
                )

                self.scan_button.disabled = False
                self.scan_button.text = "SCAN MARKET"
                return

            self.calculate_signal(
                pair,
                interval,
                values,
                closes
            )

        except requests.exceptions.Timeout:

            self.set_result(
                "[b]CONNECTION TIMEOUT[/b]\n\n"
                "Please try again."
            )

        except Exception as e:

            self.set_result(
                "[b]ERROR[/b]\n\n"
                + str(e)
            )

        finally:

            self.scan_button.disabled = False
            self.scan_button.text = "SCAN MARKET"

    # =========================
    # SIGNAL CALCULATION
    # =========================

    def calculate_signal(
        self,
        pair,
        interval,
        candles,
        closes
    ):

        fast = ema(closes, EMA_FAST)
        slow = ema(closes, EMA_SLOW)

        if not fast or not slow:

            self.set_result(
                "EMA calculation failed."
            )
            return

        # Align EMA arrays to common length
        length = min(
            len(fast),
            len(slow)
        )

        fast = fast[-length:]
        slow = slow[-length:]

        if len(fast) < 3:

            self.set_result(
                "Not enough EMA data."
            )
            return

        fast_previous = fast[-2]
        slow_previous = slow[-2]

        fast_current = fast[-1]
        slow_current = slow[-1]

        current_rsi = rsi(closes, 14)

        price = closes[-1]

        # =========================
        # CROSS DETECTION
        # =========================

        bullish_cross = (
            fast_previous <= slow_previous
            and
            fast_current > slow_current
        )

        bearish_cross = (
            fast_previous >= slow_previous
            and
            fast_current < slow_current
        )

        # =========================
        # SIGNAL FILTER
        # =========================

        signal = "WAIT"
        confidence = 50

        if current_rsi is None:
            current_rsi = 50

        # BUY:
        # EMA 2 crosses above EMA 5
        # RSI preferably above 50 but below overbought
        if bullish_cross:

            if 50 <= current_rsi < 70:
                signal = "BUY"
                confidence = 85

            elif current_rsi < 50:
                signal = "WAIT"
                confidence = 60

            else:
                signal = "WAIT"
                confidence = 55

        # SELL:
        # EMA 2 crosses below EMA 5
        # RSI preferably below 50 but above oversold
        elif bearish_cross:

            if 30 < current_rsi <= 50:
                signal = "SELL"
                confidence = 85

            elif current_rsi > 50:
                signal = "WAIT"
                confidence = 60

            else:
                signal = "WAIT"
                confidence = 55

        # No fresh cross
        else:

            signal = "WAIT"
            confidence = 50

        # =========================
        # ENTRY STATUS
        # =========================

        if signal == "BUY":
            entry = "CALL / BUY"
        elif signal == "SELL":
            entry = "PUT / SELL"
        else:
            entry = "NO ENTRY"

        # =========================
        # TIME
        # =========================

        try:
            bd_time = datetime.now(
                ZoneInfo("Asia/Dhaka")
            ).strftime(
                "%Y-%m-%d %I:%M:%S %p"
            )
        except:
            bd_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # =========================
        # DISPLAY
        # =========================

        result = (
            "[b]AI TRADING SIGNAL[/b]\n\n"
            f"PAIR: {pair}\n"
            f"TIMEFRAME: {interval}\n\n"
            f"PRICE: {price:.5f}\n\n"
            f"EMA {EMA_FAST}: {fast_current:.5f}\n"
            f"EMA {EMA_SLOW}: {slow_current:.5f}\n\n"
            f"RSI(14): {current_rsi:.2f}\n\n"
            f"[b]SIGNAL: {signal}[/b]\n"
            f"ENTRY: {entry}\n"
            f"CONFIDENCE: {confidence}%\n\n"
            f"Market Time: {bd_time}\n\n"
            "Strategy:\n"
            "EMA 2/5 crossover + RSI confirmation"
        )

        self.set_result(result)


# =========================
# START APP
# =========================

if __name__ == "__main__":
    SignalApp().run()
