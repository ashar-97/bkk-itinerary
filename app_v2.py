import streamlit as st
import pandas as pd
import pydeck as pdk
import base64
import os

# --- Load Google Sheet ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSk6XqiZs97uihKKu7p0rdNYQ0_2PliPlyL07IQs-yKEIURGYgWZ7sMMJPpknKK0REmmzRb05qmGIaN/pub?gid=0&single=true&output=csv"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()

# --- Sidebar filters ---
st.sidebar.markdown("🔍 **Filter your trip**")

with st.sidebar.expander("Filter by Tag", expanded=False):
    selected_tags = st.multiselect(
        "Select Tags",
        df["Tag"].unique(),
        default=df["Tag"].unique(),
        label_visibility="collapsed"
    )

with st.sidebar.expander("Filter by District", expanded=False):
    selected_districts = st.multiselect(
        "Select Districts",
        df["District"].unique(),
        default=df["District"].unique(),
        label_visibility="collapsed"
    )

# Optional: Reset Filters button
if st.sidebar.button("🔄 Reset Filters"):
    selected_tags = df["Tag"].unique()
    selected_districts = df["District"].unique()

# Toggle for showing names
show_labels = st.sidebar.checkbox("🪧 Show Place Names", value=True)

# Reset view button
reset_view = st.sidebar.button("📍 Reset Map View")

# --- Filter the dataframe ---
filtered_df = df[df["Tag"].isin(selected_tags) & df["District"].isin(selected_districts)].copy()
filtered_df["Latitude"] = pd.to_numeric(filtered_df["Latitude"], errors="coerce")
filtered_df["Longitude"] = pd.to_numeric(filtered_df["Longitude"], errors="coerce")
filtered_df = filtered_df.dropna(subset=["Latitude", "Longitude"])

# --- Encode icon images ---
tag_to_icon_path = {
    "Market": "icons/market.png",
    "Cafe": "icons/cafe.png",
    "Cool Streets": "icons/cool_street.png",
    "Nature": "icons/nature.png",
    "Gallery": "icons/gallery.png",
    "Museum": "icons/museum.png",
    "Shopping": "icons/shopping.png",
    "Self Care": "icons/self_care.png",
    "Landmark": "icons/landmark.png",
    "Islam": "icons/islam.png",
    "Hotel": "icons/hotel.png",
    "Viewpoint": "icons/viewpoint.png",
    "Village": "icons/village.png",
    "Historic District": "icons/historic_district.png",
    "Neighbourhood": "icons/neighbourhood.png",
    "Beach": "icons/beach.png",
    "Activity": "icons/activity.png",
    "Night Market": "icons/night_market.png"
}

def encode_icon(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return None

filtered_df["icon_data"] = filtered_df["Tag"].map(lambda tag: {
    "url": encode_icon(tag_to_icon_path.get(tag, "icons/market.png")),
    "width": 128,
    "height": 128,
    "anchorY": 128
})

# --- Layers ---
icon_layer = pdk.Layer(
    "IconLayer",
    data=filtered_df,
    get_icon="icon_data",
    get_position='[Longitude, Latitude]',
    size_scale=15,
    pickable=True
)

text_layer = pdk.Layer(
    "TextLayer",
    data=filtered_df,
    get_position='[Longitude, Latitude]',
    get_text="Item",
    get_color=[0, 0, 0],
    get_size=12,
    size_units='meters',
    size_scale=1,
    size_min_pixels=10,
    size_max_pixels=30,
    pickable=False,
    get_alignment_baseline="'bottom'"
)

# --- View state ---
initial_view_state = pdk.ViewState(
    latitude=13.7563,
    longitude=100.5018,
    zoom=11,
    pitch=0
)

# Reset view logic
view_state = initial_view_state if reset_view else pdk.ViewState(
    latitude=filtered_df["Latitude"].mean() if not filtered_df.empty else 13.7563,
    longitude=filtered_df["Longitude"].mean() if not filtered_df.empty else 100.5018,
    zoom=11,
    pitch=0
)

# --- Tooltip ---
tooltip = {
    "html": "<b>{Item}</b><br/>✨ {Vibes}<br/><i>{Description}</i>",
    "style": {"backgroundColor": "#1e1e1e", "color": "white"}
}

# --- Render Map ---
st.markdown("🌴 # Bangkok Travel Planner")

if not filtered_df.empty:
    layers = [icon_layer]
    if show_labels:
        layers.append(text_layer)

    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=view_state,
        layers=layers,
        tooltip=tooltip
    ))
else:
    st.warning("No locations to display with selected filters.")