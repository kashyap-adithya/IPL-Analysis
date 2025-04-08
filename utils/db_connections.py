import psycopg2
import pandas as pd
import streamlit as st

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="ep-crimson-dream-a127ua7h-pooler.ap-southeast-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_xIoS7OUMlQV3",
        port=5432,
        sslmode="require",
    )