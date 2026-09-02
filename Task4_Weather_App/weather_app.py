import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.parse
import json
from datetime import datetime


APP_TITLE = "Advanced Weather App"


# ============================================================
# WEATHER DATA
# ============================================================

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


# ============================================================
# API FUNCTIONS
# ============================================================

def fetch_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AdvancedWeatherApp/1.0"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=15
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def get_coordinates(city):
    encoded_city = urllib.parse.quote(city)

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={encoded_city}"
        "&count=1"
        "&language=en"
        "&format=json"
    )

    data = fetch_json(url)

    results = data.get("results", [])

    if not results:
        raise ValueError(
            "City not found. Please check the city name."
        )

    result = results[0]

    return {
        "name": result.get("name", city),
        "country": result.get("country", ""),
        "admin1": result.get("admin1", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "timezone": result.get("timezone", "auto")
    }


def get_weather(latitude, longitude):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "is_day,"
        "precipitation,"
        "rain,"
        "weather_code,"
        "cloud_cover,"
        "pressure_msl,"
        "surface_pressure,"
        "wind_speed_10m,"
        "wind_direction_10m,"
        "wind_gusts_10m"
        "&hourly="
        "temperature_2m,"
        "precipitation_probability,"
        "weather_code"
        "&daily="
        "weather_code,"
        "temperature_2m_max,"
        "temperature_2m_min,"
        "sunrise,"
        "sunset,"
        "precipitation_sum,"
        "rain_sum,"
        "precipitation_probability_max,"
        "wind_speed_10m_max"
        "&timezone=auto"
        "&forecast_days=7"
    )

    return fetch_json(url)


# ============================================================
# APPLICATION
# ============================================================

class WeatherApp:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_TITLE)

        self.root.geometry(
            "1200x800"
        )

        self.root.minsize(
            950,
            650
        )

        self.dark_mode = False

        self.location = None
        self.weather = None

        # ----------------------------------------------------
        # Variables
        # ----------------------------------------------------

        self.city_var = tk.StringVar()

        self.location_var = tk.StringVar(
            value="Search for a city"
        )

        self.temperature_var = tk.StringVar(
            value="--°C"
        )

        self.condition_var = tk.StringVar(
            value="No weather data"
        )

        self.feels_var = tk.StringVar(
            value="Feels like: --"
        )

        self.humidity_var = tk.StringVar(
            value="-- %"
        )

        self.wind_var = tk.StringVar(
            value="-- km/h"
        )

        self.pressure_var = tk.StringVar(
            value="-- hPa"
        )

        self.cloud_var = tk.StringVar(
            value="-- %"
        )

        self.precipitation_var = tk.StringVar(
            value="-- mm"
        )

        self.sunrise_var = tk.StringVar(
            value="--"
        )

        self.sunset_var = tk.StringVar(
            value="--"
        )

        self.updated_var = tk.StringVar(
            value="Last updated: --"
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        self.build_ui()

    # ========================================================
    # THEME
    # ========================================================

    def setup_theme(self):

        if self.dark_mode:

            self.bg = "#111827"
            self.card = "#1F2937"
            self.fg = "#F9FAFB"
            self.muted = "#CBD5E1"
            self.entry_bg = "#374151"
            self.accent = "#38BDF8"

        else:

            self.bg = "#F1F5F9"
            self.card = "#FFFFFF"
            self.fg = "#111827"
            self.muted = "#475569"
            self.entry_bg = "#FFFFFF"
            self.accent = "#2563EB"

        self.root.configure(
            bg=self.bg
        )

        self.style = ttk.Style()

        try:
            self.style.theme_use(
                "clam"
            )
        except tk.TclError:
            pass

        self.style.configure(
            "TFrame",
            background=self.bg
        )

        self.style.configure(
            "Card.TFrame",
            background=self.card
        )

        self.style.configure(
            "TLabel",
            background=self.bg,
            foreground=self.fg,
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "Title.TLabel",
            background=self.bg,
            foreground=self.fg,
            font=("Segoe UI", 26, "bold")
        )

        self.style.configure(
            "Subtitle.TLabel",
            background=self.bg,
            foreground=self.muted,
            font=("Segoe UI", 11)
        )

        self.style.configure(
            "CardTitle.TLabel",
            background=self.card,
            foreground=self.fg,
            font=("Segoe UI", 12, "bold")
        )

        self.style.configure(
            "CardValue.TLabel",
            background=self.card,
            foreground=self.fg,
            font=("Segoe UI", 16, "bold")
        )

        self.style.configure(
            "WeatherTemp.TLabel",
            background=self.card,
            foreground=self.fg,
            font=("Segoe UI", 48, "bold")
        )

        self.style.configure(
            "WeatherCondition.TLabel",
            background=self.card,
            foreground=self.muted,
            font=("Segoe UI", 14)
        )

        self.style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8)
        )

        self.style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 9)
        )

        self.style.configure(
            "Treeview",
            rowheight=34,
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        self.setup_theme()

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = ttk.Frame(
            self.root
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        title_frame = ttk.Frame(
            header
        )

        title_frame.pack(
            side="left"
        )

        ttk.Label(
            title_frame,
            text="🌦️ Advanced Weather App",
            style="Title.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            title_frame,
            text=(
                "Live weather information and "
                "7-day forecast"
            ),
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        ttk.Button(
            header,
            text="☀ / ☾ Theme",
            command=self.toggle_theme
        ).pack(
            side="right"
        )

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search_frame = ttk.Frame(
            self.root
        )

        search_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.city_entry = tk.Entry(
            search_frame,
            textvariable=self.city_var,
            font=("Segoe UI", 12),
            bg=self.entry_bg,
            fg=self.fg,
            insertbackground=self.fg,
            relief="solid",
            bd=1
        )

        self.city_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9
        )

        self.city_entry.bind(
            "<Return>",
            lambda event: self.search_weather()
        )

        ttk.Button(
            search_frame,
            text="🔍 Search",
            style="Accent.TButton",
            command=self.search_weather
        ).pack(
            side="left",
            padx=8
        )

        ttk.Button(
            search_frame,
            text="🔄 Refresh",
            command=self.refresh_weather
        ).pack(
            side="left"
        )

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        ttk.Label(
            self.root,
            textvariable=self.location_var,
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(5, 5)
        )

        # ----------------------------------------------------
        # Notebook
        # ----------------------------------------------------

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        self.current_tab = ttk.Frame(
            self.notebook
        )

        self.forecast_tab = ttk.Frame(
            self.notebook
        )

        self.info_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.current_tab,
            text="  Current Weather  "
        )

        self.notebook.add(
            self.forecast_tab,
            text="  7-Day Forecast  "
        )

        self.notebook.add(
            self.info_tab,
            text="  About  "
        )

        self.build_current_tab()
        self.build_forecast_tab()
        self.build_info_tab()

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status = ttk.Frame(
            self.root
        )

        status.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        ttk.Label(
            status,
            textvariable=self.status_var
        ).pack(
            side="left"
        )

        ttk.Label(
            status,
            textvariable=self.updated_var
        ).pack(
            side="right"
        )

    # ========================================================
    # CURRENT WEATHER TAB
    # ========================================================

    def build_current_tab(self):

        main = ttk.Frame(
            self.current_tab
        )

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # ----------------------------------------------------
        # Main Weather Card
        # ----------------------------------------------------

        weather_card = ttk.Frame(
            main,
            style="Card.TFrame"
        )

        weather_card.pack(
            fill="x",
            pady=(0, 15)
        )

        ttk.Label(
            weather_card,
            text="Current Conditions",
            style="CardTitle.TLabel"
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 5)
        )

        ttk.Label(
            weather_card,
            textvariable=self.temperature_var,
            style="WeatherTemp.TLabel"
        ).pack(
            pady=(5, 0)
        )

        ttk.Label(
            weather_card,
            textvariable=self.condition_var,
            style="WeatherCondition.TLabel"
        ).pack(
            pady=5
        )

        ttk.Label(
            weather_card,
            textvariable=self.feels_var,
            style="WeatherCondition.TLabel"
        ).pack(
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        stats = ttk.Frame(
            main
        )

        stats.pack(
            fill="both",
            expand=True
        )

        self.create_stat_card(
            stats,
            "💧 Humidity",
            self.humidity_var,
            0,
            0
        )

        self.create_stat_card(
            stats,
            "💨 Wind Speed",
            self.wind_var,
            0,
            1
        )

        self.create_stat_card(
            stats,
            "🌡️ Pressure",
            self.pressure_var,
            0,
            2
        )

        self.create_stat_card(
            stats,
            "☁️ Cloud Cover",
            self.cloud_var,
            1,
            0
        )

        self.create_stat_card(
            stats,
            "🌧️ Precipitation",
            self.precipitation_var,
            1,
            1
        )

        self.create_stat_card(
            stats,
            "🌅 Sunrise",
            self.sunrise_var,
            1,
            2
        )

        self.create_stat_card(
            stats,
            "🌇 Sunset",
            self.sunset_var,
            2,
            1
        )

    def create_stat_card(
        self,
        parent,
        title,
        variable,
        row,
        column
    ):

        card = ttk.Frame(
            parent,
            style="Card.TFrame"
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6
        )

        parent.grid_rowconfigure(
            row,
            weight=1
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        ttk.Label(
            card,
            text=title,
            style="CardTitle.TLabel"
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 5)
        )

        ttk.Label(
            card,
            textvariable=variable,
            style="CardValue.TLabel"
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 15)
        )

    # ========================================================
    # FORECAST TAB
    # ========================================================

    def build_forecast_tab(self):

        frame = ttk.Frame(
            self.forecast_tab
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        ttk.Label(
            frame,
            text="7-Day Weather Forecast",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        columns = (
            "date",
            "condition",
            "min",
            "max",
            "rain",
            "wind"
        )

        self.forecast_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "date": "Date",
            "condition": "Condition",
            "min": "Min °C",
            "max": "Max °C",
            "rain": "Rain %",
            "wind": "Max Wind"
        }

        for column, heading in headings.items():

            self.forecast_tree.heading(
                column,
                text=heading
            )

        self.forecast_tree.column(
            "date",
            width=150
        )

        self.forecast_tree.column(
            "condition",
            width=260
        )

        self.forecast_tree.column(
            "min",
            width=100,
            anchor="center"
        )

        self.forecast_tree.column(
            "max",
            width=100,
            anchor="center"
        )

        self.forecast_tree.column(
            "rain",
            width=100,
            anchor="center"
        )

        self.forecast_tree.column(
            "wind",
            width=130,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.forecast_tree.yview
        )

        self.forecast_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.forecast_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # ========================================================
    # ABOUT TAB
    # ========================================================

    def build_info_tab(self):

        frame = ttk.Frame(
            self.info_tab
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        ttk.Label(
            frame,
            text="About This Application",
            style="Title.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        information = (
            "ADVANCED WEATHER APPLICATION\n\n"

            "This application retrieves live weather "
            "information using Open-Meteo APIs.\n\n"

            "FEATURES\n\n"

            "• City search\n"
            "• Current temperature\n"
            "• Feels-like temperature\n"
            "• Weather condition\n"
            "• Humidity\n"
            "• Wind speed and direction\n"
            "• Atmospheric pressure\n"
            "• Cloud cover\n"
            "• Precipitation\n"
            "• Sunrise and sunset\n"
            "• Seven-day forecast\n"
            "• Rain probability\n"
            "• Maximum wind speed\n"
            "• Refresh weather data\n"
            "• Light / Dark theme\n"
            "• Network error handling\n\n"

            "DATA SOURCE\n\n"

            "Weather data is provided by Open-Meteo.\n\n"

            "TECHNOLOGIES\n\n"

            "Python • Tkinter • REST API • JSON\n"
            "urllib • Object-Oriented Programming\n\n"

            "INTERNSHIP\n\n"

            "Oasis Infobyte Python Programming Internship\n"
            "Task 4 — Basic Weather App"
        )

        text = tk.Text(
            frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg=self.entry_bg,
            fg=self.fg,
            insertbackground=self.fg,
            relief="solid",
            bd=1
        )

        text.insert(
            "1.0",
            information
        )

        text.configure(
            state="disabled"
        )

        text.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # WEATHER SEARCH
    # ========================================================

    def search_weather(self):

        city = self.city_var.get().strip()

        if not city:

            messagebox.showwarning(
                "City Required",
                "Please enter a city name."
            )

            return

        self.status_var.set(
            "Searching for weather..."
        )

        self.root.update_idletasks()

        try:

            self.location = get_coordinates(
                city
            )

            self.weather = get_weather(
                self.location["latitude"],
                self.location["longitude"]
            )

            self.display_weather()

            self.status_var.set(
                "Weather data loaded successfully."
            )

        except Exception as error:

            self.status_var.set(
                "Unable to load weather data."
            )

            messagebox.showerror(
                "Weather Error",
                f"Could not retrieve weather data.\n\n{error}"
            )

    def refresh_weather(self):

        if not self.location:

            messagebox.showinfo(
                "Refresh Weather",
                "Search for a city first."
            )

            return

        try:

            self.status_var.set(
                "Refreshing weather..."
            )

            self.root.update_idletasks()

            self.weather = get_weather(
                self.location["latitude"],
                self.location["longitude"]
            )

            self.display_weather()

            self.status_var.set(
                "Weather refreshed successfully."
            )

        except Exception as error:

            messagebox.showerror(
                "Refresh Error",
                str(error)
            )

    # ========================================================
    # DISPLAY WEATHER
    # ========================================================

    def display_weather(self):

        current = self.weather.get(
            "current",
            {}
        )

        daily = self.weather.get(
            "daily",
            {}
        )

        location_name = self.location[
            "name"
        ]

        country = self.location.get(
            "country",
            ""
        )

        region = self.location.get(
            "admin1",
            ""
        )

        location_parts = [
            location_name
        ]

        if region:
            location_parts.append(
                region
            )

        if country:
            location_parts.append(
                country
            )

        self.location_var.set(
            "📍 " + ", ".join(
                location_parts
            )
        )

        temperature = current.get(
            "temperature_2m"
        )

        feels_like = current.get(
            "apparent_temperature"
        )

        humidity = current.get(
            "relative_humidity_2m"
        )

        wind = current.get(
            "wind_speed_10m"
        )

        pressure = current.get(
            "pressure_msl"
        )

        cloud = current.get(
            "cloud_cover"
        )

        precipitation = current.get(
            "precipitation"
        )

        weather_code = current.get(
            "weather_code"
        )

        description, emoji = WEATHER_CODES.get(
            weather_code,
            ("Unknown", "🌡️")
        )

        self.temperature_var.set(
            f"{temperature:.1f}°C"
            if temperature is not None
            else "--°C"
        )

        self.condition_var.set(
            f"{emoji} {description}"
        )

        self.feels_var.set(
            f"Feels like: "
            f"{feels_like:.1f}°C"
            if feels_like is not None
            else "Feels like: --"
        )

        self.humidity_var.set(
            f"{humidity}%"
            if humidity is not None
            else "-- %"
        )

        self.wind_var.set(
            f"{wind:.1f} km/h"
            if wind is not None
            else "-- km/h"
        )

        self.pressure_var.set(
            f"{pressure:.0f} hPa"
            if pressure is not None
            else "-- hPa"
        )

        self.cloud_var.set(
            f"{cloud}%"
            if cloud is not None
            else "-- %"
        )

        self.precipitation_var.set(
            f"{precipitation:.1f} mm"
            if precipitation is not None
            else "-- mm"
        )

        sunrise = daily.get(
            "sunrise",
            ["--"]
        )[0]

        sunset = daily.get(
            "sunset",
            ["--"]
        )[0]

        self.sunrise_var.set(
            self.format_time(sunrise)
        )

        self.sunset_var.set(
            self.format_time(sunset)
        )

        updated = datetime.now().strftime(
            "%d %b %Y, %I:%M:%S %p"
        )

        self.updated_var.set(
            f"Last updated: {updated}"
        )

        self.update_forecast()

    # ========================================================
    # FORECAST
    # ========================================================

    def update_forecast(self):

        for item in self.forecast_tree.get_children():

            self.forecast_tree.delete(
                item
            )

        daily = self.weather.get(
            "daily",
            {}
        )

        dates = daily.get(
            "time",
            []
        )

        codes = daily.get(
            "weather_code",
            []
        )

        min_temp = daily.get(
            "temperature_2m_min",
            []
        )

        max_temp = daily.get(
            "temperature_2m_max",
            []
        )

        rain_probability = daily.get(
            "precipitation_probability_max",
            []
        )

        wind_speed = daily.get(
            "wind_speed_10m_max",
            []
        )

        for i in range(
            len(dates)
        ):

            code = codes[i]

            description, emoji = WEATHER_CODES.get(
                code,
                ("Unknown", "🌡️")
            )

            date_text = self.format_date(
                dates[i]
            )

            rain = (
                f"{rain_probability[i]}%"
                if i < len(rain_probability)
                else "--"
            )

            wind = (
                f"{wind_speed[i]:.1f} km/h"
                if i < len(wind_speed)
                else "--"
            )

            self.forecast_tree.insert(
                "",
                "end",
                values=(
                    date_text,
                    f"{emoji} {description}",
                    f"{min_temp[i]:.1f}",
                    f"{max_temp[i]:.1f}",
                    rain,
                    wind
                )
            )

    # ========================================================
    # DATE / TIME
    # ========================================================

    @staticmethod
    def format_time(value):

        if not value or value == "--":

            return "--"

        try:

            dt = datetime.fromisoformat(
                value
            )

            return dt.strftime(
                "%I:%M %p"
            )

        except ValueError:

            return value

    @staticmethod
    def format_date(value):

        try:

            dt = datetime.fromisoformat(
                value
            )

            return dt.strftime(
                "%A, %d %b"
            )

        except ValueError:

            return value

    # ========================================================
    # THEME
    # ========================================================

    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        # Save current data
        current_location = self.location
        current_weather = self.weather

        for widget in self.root.winfo_children():

            widget.destroy()

        self.build_ui()

        self.location = current_location
        self.weather = current_weather

        if self.weather:

            self.display_weather()

        self.status_var.set(
            "Theme changed."
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = WeatherApp(
        root
    )

    root.mainloop()
