from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from modules import generate_itinerary
from modules import recommend_activities
from modules import fetch_useful_links
from modules import weather_forecaster
from modules import packing_list_generator
from modules import food_culture_recommender
from modules import chat_agent
from utils_export import export_to_pdf


# Define state
class GraphState(TypedDict):
    preferences_text: str
    preferences: dict
    itinerary: str
    activity_suggestions: str
    useful_links: list[dict]
    weather_forecast: str
    packing_list: str
    food_culture_info: str
    chat_history: Annotated[list[dict], "List of question-response pairs"]
    user_question: str
    chat_response: str
 
def create_graph():   
    workflow = StateGraph(GraphState)
    workflow.add_node("generate_itinerary", generate_itinerary.generate_itinerary)
    workflow.add_node("recommend_activities", recommend_activities.recommend_activities)
    workflow.add_node("fetch_useful_links", fetch_useful_links.fetch_useful_links)
    workflow.add_node("weather_forecaster", weather_forecaster.weather_forecaster)
    workflow.add_node("packing_list_generator", packing_list_generator.packing_list_generator)
    workflow.add_node("food_culture_recommender", food_culture_recommender.food_culture_recommender)
    workflow.add_node("chat", chat_agent.chat_node)
    workflow.set_entry_point("generate_itinerary")
    workflow.add_edge("generate_itinerary", END)
    workflow.add_edge("recommend_activities", END)
    workflow.add_edge("fetch_useful_links", END)
    workflow.add_edge("weather_forecaster", END)
    workflow.add_edge("packing_list_generator", END)
    workflow.add_edge("food_culture_recommender", END)
    workflow.add_edge("chat", END)
    graph = workflow.compile()
    return graph
