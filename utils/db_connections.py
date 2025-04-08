import psycopg2
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

db = st.secrets["database"]

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=db["host"],
        database=db["name"],
        user=db["user"],
        password=db["password"],
        port=db["port"],
        sslmode=db["sslmode"],
    )
