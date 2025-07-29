import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast")
        self.root.geometry("800x900")
        self.api_key = 'e3cabd10791fe27bab209ae34d1207b0'
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cities entry frame
        self.cities_frame = ttk.LabelFrame(self.main_frame, text="Enter Cities", padding="10")
        self.cities_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # City entry
        ttk.Label(self.cities_frame, text="City:").grid(row=0, column=0, padx=5, pady=5)
        self.city_entry = ttk.Entry(self.cities_frame, width=30)
        self.city_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Add, Search and Compare buttons
        ttk.Button(self.cities_frame, text="Add City", command=self.add_city).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.cities_frame, text="Search All", command=self.update_all_weather).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self.cities_frame, text="Compare Cities", command=self.compare_cities).grid(row=0, column=4, padx=5, pady=5)
        
        # Cities list and frames
        self.cities_list = []
        self.weather_frames = []
        
        # Scrollable frame for weather info
        self.setup_scrollable_frame()
        
        # Comparison frame
        self.setup_comparison_frame()

    def setup_scrollable_frame(self):
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def setup_comparison_frame(self):
        self.comparison_frame = ttk.LabelFrame(self.main_frame, text="Cities Comparison", padding="10")
        self.comparison_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.comparison_text = tk.Text(self.comparison_frame, height=10, width=70)
        self.comparison_text.grid(row=0, column=0, padx=5, pady=5)

    def add_city(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
            
        if city not in self.cities_list:
            self.cities_list.append(city)
            self.create_city_frame(city)
            self.city_entry.delete(0, tk.END)
            self.update_weather_for_city(city, len(self.weather_frames) - 1)

    def create_city_frame(self, city):
        frame = ttk.LabelFrame(self.scrollable_frame, text=city, padding="10")
        frame.grid(row=len(self.weather_frames), column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        temp_label = ttk.Label(frame, text="")
        temp_label.grid(row=0, column=0, sticky=tk.W)
        
        desc_label = ttk.Label(frame, text="")
        desc_label.grid(row=1, column=0, sticky=tk.W)
        
        humidity_label = ttk.Label(frame, text="")
        humidity_label.grid(row=2, column=0, sticky=tk.W)
        
        wind_label = ttk.Label(frame, text="")
        wind_label.grid(row=3, column=0, sticky=tk.W)
        
        remove_btn = ttk.Button(frame, text="Remove", 
                              command=lambda c=city, f=frame: self.remove_city(c, f))
        remove_btn.grid(row=4, column=0, pady=5)
        
        self.weather_frames.append({
            'frame': frame,
            'temp': temp_label,
            'desc': desc_label,
            'humidity': humidity_label,
            'wind': wind_label
        })

    def remove_city(self, city, frame):
        if city in self.cities_list:
            idx = self.cities_list.index(city)
            self.cities_list.remove(city)
            self.weather_frames.pop(idx)
            frame.destroy()

    def update_weather_for_city(self, city, idx):
        try:
            weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric'
            response = requests.get(weather_url)
            
            if response.status_code == 200:
                data = response.json()
                frame_data = self.weather_frames[idx]
                frame_data['temp'].config(text=f"Temperature: {data['main']['temp']}°C")
                frame_data['desc'].config(text=f"Description: {data['weather'][0]['description']}")
                frame_data['humidity'].config(text=f"Humidity: {data['main']['humidity']}%")
                frame_data['wind'].config(text=f"Wind Speed: {data['wind']['speed']} m/s")
            else:
                messagebox.showerror("Error", f"Failed to get weather for {city}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred for {city}: {str(e)}")

    def update_all_weather(self):
        for idx, city in enumerate(self.cities_list):
            self.update_weather_for_city(city, idx)

    def compare_cities(self):
        if len(self.cities_list) < 2:
            messagebox.showwarning("Warning", "Please add at least 2 cities to compare")
            return

        try:
            comparison_data = []
            for city in self.cities_list:
                weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric'
                response = requests.get(weather_url)
                
                if response.status_code == 200:
                    data = response.json()
                    comparison_data.append({
                        'city': city,
                        'temp': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'humidity': data['main']['humidity'],
                        'wind': data['wind']['speed'],
                        'desc': data['weather'][0]['description'],
                        'pressure': data['main']['pressure']
                    })

            # Clear previous comparison
            self.comparison_text.delete(1.0, tk.END)
            
            # Add comparison header
            self.comparison_text.insert(tk.END, "Weather Comparison Analysis:\n\n")
            
            # Find extreme values
            temps = [d['temp'] for d in comparison_data]
            humidities = [d['humidity'] for d in comparison_data]
            winds = [d['wind'] for d in comparison_data]
            
            hottest = max(temps)
            coldest = min(temps)
            most_humid = max(humidities)
            windiest = max(winds)
            
            # Display comparison with detailed analysis
            for data in comparison_data:
                temp = data['temp']
                temp_status = []
                if temp == hottest:
                    temp_status.append("HOTTEST")
                if temp == coldest:
                    temp_status.append("COLDEST")
                
                status_str = f" ({', '.join(temp_status)})" if temp_status else ""
                
                self.comparison_text.insert(tk.END, f"\n{data['city'].upper()}:\n")
                self.comparison_text.insert(tk.END, f"{'='*30}\n")
                self.comparison_text.insert(tk.END, 
                    f"  Temperature: {temp}°C{status_str}\n"
                    f"  Feels Like: {data['feels_like']}°C\n"
                    f"  Humidity: {data['humidity']}%{' (HIGHEST)' if data['humidity'] == most_humid else ''}\n"
                    f"  Wind Speed: {data['wind']} m/s{' (STRONGEST)' if data['wind'] == windiest else ''}\n"
                    f"  Pressure: {data['pressure']} hPa\n"
                    f"  Conditions: {data['desc'].title()}\n")
                
                # Add temperature difference from average
                avg_temp = sum(temps) / len(temps)
                diff = temp - avg_temp
                self.comparison_text.insert(tk.END, 
                    f"  Difference from average: {diff:+.1f}°C\n\n")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during comparison: {str(e)}")

def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()

    