import streamlit as st
import base64

st.set_page_config(
    page_title="IPL Tournament Dashboard",
    page_icon="🏏",
    layout="wide",
)

def set_bg_from_local(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
             background-size: 1500px 1500px;
            background-position: right;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function
set_bg_from_local("utils/random_ipl_image_2.png")


st.title("🏆 IPL Tournament Dashboard")

st.markdown("""
Welcome to the IPL Tournament Dashboard!  
This dashboard provides detailed analysis of the tournament, teams, and players using ball-by-ball data.

Use the sidebar to navigate across different pages:
- Tournament Overview  
- Team Analysis  
- Player Analysis  
- Venue Analysis  

Built with ❤️ using Streamlit and PostgreSQL and Airflow.
""")

# st.image("https://resources.pulse.icc-cricket.com/ICC/photo/2023/03/31/711kz1WI-Fans.jpg", use_column_width=True)

st.markdown("---")
