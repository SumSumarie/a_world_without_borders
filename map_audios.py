import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from pydub import AudioSegment
import random
from colorama import Fore, Style
import hashlib

from io import BytesIO


def get_audio_bytes(file_path):
    audio = AudioSegment.from_file(file_path)
    buffer = BytesIO()
    audio.export(buffer, format="mp3")
    return buffer.getvalue()


# Load Data
general_info = pd.read_csv(
    "data/border - general_info.csv")  # CSV should have 'latitude', 'longitude', 'location', and 'audio' columns
coordinates_data = pd.read_csv(
    "data/border - coordinates.csv")  # CSV should have 'latitude', 'longitude', 'location', and 'audio' columns
merged_data = pd.merge(general_info, coordinates_data, on=["id", "Address"], how="outer")
merged_data.to_csv("data/a_world_without_border.csv", index=False)

AudioSegment.converter = "/path/to/ffmpeg"  # Adjust this path as needed

# Initialize Streamlit App
st.title("A World without Borders")
st.write("Explore sounds from various locations on this map.")

# List of available Folium colors
colors = ["blue", "green", "purple", "orange", "lightred", "beige", "darkblue",
          "darkgreen", "cadetblue", "darkpurple", "white", "pink", "lightblue", "lightgreen",
          "gray", "black", "lightgray",
          "#FF5733", "#33FF57", "#3357FF", "#FF33A8", "#A833FF", "#33FFF6", "#FF9633", "#FF3333",
          "#85FF33", "#3385FF", "#FF8C33", "#33FF99"]


# Function to generate a fixed color for each location based on its coordinates
def get_fixed_color(lat, lon):
    # Create a unique hash for each (latitude, longitude) pair
    location_str = f"{lat},{lon}"
    # Convert hash to a number
    hash_value = int(hashlib.md5(location_str.encode()).hexdigest(), 16)
    # Use the hash to select a color from the list
    return colors[hash_value % 16]


# Initialize Folium Map centered on the mean location
m = folium.Map(tiles="Cartodb Positron", zoom_start=10)

# Add fullscreen functionality
folium.plugins.Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(m)

for id, row in merged_data.iterrows():
    # Create a relative path to the audio file
    audio_file_path1 = {row['Audio1']}
    audio_file_path2 = {row['Audio2']}
    print(audio_file_path2)
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: green; background-color: lightgreen; padding: 20px; border-radius: 10px;">
        <b>Location:</br> 
        </b>{row['Address']}</br>
        <b>Description:</br> 
        </b> {row['Description']}<br>
        <b>Mother tongue language:</br> 
        </b>{row['Language']}</br>
        <b>{'How to greet in'} {row['Language']}{'?'}</br> 
        </b>{row['Greet']}<br>     
        <b>Bordering countries:</br> 
        </b>{row['Bordering_countries']}</br>

        <b>Audio Language:</br> 
        </b> {'English'}</br>
        <audio controls>
            <source src="{audio_file_path1}" type="audio/mp3">
        </audio>
        </b> {row['Language']}</br>
        <audio controls>
            <source src="{audio_file_path2}" type="audio/mp3">
        </audio>
        """
    # Get a fixed color for each location
    marker_color = get_fixed_color(row['Latitude'], row['Longitude'])
    folium.Marker(

        # https://stackoverflow.com/questions/53721079/python-folium-icon-list
        # the list of icon :https://fontawesome.com/icons?d=gallery
        icon=folium.Icon(color=marker_color, icon='star', prefix='fa'),
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip="Click to hear sound"
    ).add_to(m)

# Display the map in Streamlit
map_component = st_folium(m, width=1000, height=500)