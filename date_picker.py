import streamlit as st
from datetime import date

st.title("Date Range Calculator")

# Calendar widgets for selecting start and end dates
with st.form("travel_form"):
    start_date = st.date_input("Select Start Date", value=date.today())
    end_date = st.date_input("Select End Date", value=date.today())

    # Ensure end_date is not before start_date
    if start_date > end_date:
        st.error("End date must be after start date.")
    else:
        num_days = (end_date - start_date).days
        st.success(f"Start Date: {start_date}")
        st.success(f"End Date: {end_date}")
        st.info(f"Number of days: {num_days}")
        
    submit_button = st.form_submit_button("Submit")
