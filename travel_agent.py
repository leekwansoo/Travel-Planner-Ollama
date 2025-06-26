import streamlit as st
from datetime import date
import json

from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import os
from modules import generate_itinerary
from modules import recommend_activities
from modules import fetch_useful_links
from modules import weather_forecaster
from modules import packing_list_generator
from modules import food_culture_recommender
from modules import chat_agent
from modules.generate_graph import create_graph
from utils_export import export_to_pdf

# Load environment variables
load_dotenv()

# Initialize LLM
st.set_page_config(page_title="AI Travel Planner", layout="wide")
try:
    llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")
    #llm = ChatOpenAI(model="gpt-4o")
except Exception as e:
    st.error(f"LLM initialization failed: {str(e)}")
    st.stop()

# Initialize GoogleSerperAPIWrapper
try:
    search = GoogleSerperAPIWrapper()
except Exception as e:
    st.error(f"Serper API initialization failed: {str(e)}")
    st.stop()

# --- LangGraph from generate_graph.py-------------------

graph = create_graph()

# ------------------- UI -------------------

st.markdown("# AI-Powered Travel Planner")

if "state" not in st.session_state:
    st.session_state.state = {
        "preferences_text": "",
        "preferences": {},
        "itinerary": "",
        "activity_suggestions": "",
        "useful_links": [],
        "weather_forecast": "",
        "packing_list": "",
        "food_culture_info": "",
        "chat_history": [],
        "user_question": "",
        "chat_response": ""
    }


col1, col2 = st.columns(2)
with col1:
    destination = st.text_input("Destination (Ex: Paris, Tokyo ...)", placeholder="City or Country for Traveling...")
    origin = st.text_input("Origin", value="Inchon, Korea")
    # Calendar widgets for selecting start and end dates
    start_date = st.date_input("Select Start Date", value=date.today())
    end_date = st.date_input("Select End Date", value=date.today())
    # Ensure end_date is not before start_date
    if start_date > end_date:
        st.error("End date must be after start date.")
    else:
        duration = (end_date - start_date).days
        month = start_date.strftime("%B")
        st.info(f"Number of Days: {duration} days")

    num_people = st.number_input("Number of People", min_value=1, max_value=10, value=2, step=1)
with col2:
    holiday_type = st.selectbox("Holiday Type", ["Family", "City Tour", "Backpacking","Cruise"])
    budget_type = st.selectbox("Budget", [ "Mid-Range", "Economy", "Family"])
    air_class = st.selectbox("Air Flight Cabin", ["Economy", "Business"])
    daily_hotel_cost = st.number_input("Daily Accommodations (USD)", min_value=0, value=200, step=50 )
    example ="""please recommend proper accommodations good  restaurants for dinning in downtown.
                provide me approximate total budgets"""
    comments = st.text_area("Additional Request", placeholder=f"Additional Information or request for this travel ...{example}")
submit_btn = st.button("Generate Itinerary")

if submit_btn:
    preferences_text = f"Destination: {destination}\nOrigin: {origin}\nMonth: {month}\nDuration: {duration} days\nPeople: {num_people}\nType: {holiday_type}\nBudget: {budget_type}\nAir_class: {air_class}\nDaily_hotel_cost: {daily_hotel_cost}\nComments: {comments}"
    preferences = {
        "destination": destination,
        "origin": origin,
        "month": month,
        "duration": duration,
        "num_people": num_people,
        "holiday_type": holiday_type,
        "air_class": air_class,
        "daily_hotel_cost": daily_hotel_cost,
        "budget_type": budget_type,
        "comments": comments
    }
    st.session_state.state.update({
        "preferences_text": preferences_text,
        "preferences": preferences,
        "chat_history": [],
        "user_question": "",
        "chat_response": "",
        "activity_suggestions": "",
        "useful_links": [],
        "weather_forecast": "",
        "packing_list": "",
        "food_culture_info": ""
    })
    with st.spinner("Generating itinerary..."):
        result = graph.invoke(st.session_state.state)
        st.session_state.state.update(result)
        if result.get("itinerary"):
            st.success("Itinerary Created")
        else:
            st.error("Failed to generate itinerary.")

# Layout
if st.session_state.state.get("itinerary"):
    col_itin, col_chat = st.columns([3, 2])

    with col_itin:
        st.markdown("### Travel Itinerary")
        st.markdown(st.session_state.state["itinerary"])

        # All agent buttons in one row
        col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
        with col_btn1:
            if st.button("Get Activity Suggestions"):
                with st.spinner("Fetching activity suggestions..."):
                    result = recommend_activities.recommend_activities(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn2:
            if st.button("Get Useful Links"):
                with st.spinner("Fetching useful links..."):
                    result = fetch_useful_links.fetch_useful_links(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn3:
            if st.button("Get Weather Forecast"):
                with st.spinner("Fetching weather forecast..."):
                    result = weather_forecaster.weather_forecaster(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn4:
            if st.button("Get Packing List"):
                with st.spinner("Generating packing list..."):
                    result = packing_list_generator.packing_list_generator(st.session_state.state)
                    st.session_state.state.update(result)
        with col_btn5:
            if st.button("Get Food & Culture Info"):
                with st.spinner("Fetching food and culture info..."):
                    result = food_culture_recommender.food_culture_recommender(st.session_state.state)
                    st.session_state.state.update(result)

        # Display all agent outputs in expanders
        if st.session_state.state.get("activity_suggestions"):
            with st.expander("🎯 Activity Suggestions", expanded=False):
                st.markdown(st.session_state.state["activity_suggestions"])

        if st.session_state.state.get("useful_links"):
            with st.expander("🔗 Useful Links", expanded=False):
                for link in st.session_state.state["useful_links"]:
                    st.markdown(f"- [{link['title']}]({link['link']})")

        if st.session_state.state.get("weather_forecast"):
            with st.expander("🌤️ Weather Forecast", expanded=False):
                st.markdown(st.session_state.state["weather_forecast"])

        if st.session_state.state.get("packing_list"):
            with st.expander("🎒 Packing List", expanded=False):
                st.markdown(st.session_state.state["packing_list"])

        if st.session_state.state.get("food_culture_info"):
            with st.expander("🍽️ Food & Culture Info", expanded=False):
                st.markdown(st.session_state.state["food_culture_info"])

        # Export PDF button
        if st.button("Export as PDF"):
            pdf_path = export_to_pdf(st.session_state.state["itinerary"])
            if pdf_path:
                with open(pdf_path, "rb") as f:
                    st.download_button("Download Itinerary PDF", f, file_name="itinerary.pdf")

    with col_chat:
        st.markdown("### Chat About Your Itinerary")
        for chat in st.session_state.state["chat_history"]:
            with st.chat_message("user"):
                st.markdown(chat["question"])
            with st.chat_message("assistant"):
                st.markdown(chat["response"])

        if user_input := st.chat_input("Ask something about your itinerary"):
            st.session_state.state["user_question"] = user_input
            with st.spinner("Generating response..."):
                result = chat_agent.chat_node(st.session_state.state)
                st.session_state.state.update(result)
                st.rerun()
else:
    st.info("Fill the form and generate an itinerary to begin.")
