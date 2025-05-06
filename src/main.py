from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal, Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.theme import Theme
from rich import print as rprint
import tweepy

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
    "heading": "bold blue"
})

console = Console(theme=custom_theme)

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

class State(TypedDict):
    user_message: str
    is_publish: bool
    ai_response: str
    feedback: Optional[str]

def generate_post(state: State):
    messages = [
        ("system", """You are an expert Twitter post creator. Create engaging, concise posts based on the user's input.
           Guidelines:
           - Create only ONE post
           - Maximum 280 characters 
           - Be engaging, clear, and relevant
           - Include relevant hashtags if appropriate
           - Format for readability
           - If user input is inappropriate, respond with a polite refusal"""),
        ("human", state["user_message"]),
    ]
    res = llm.invoke(messages)
    
    console.print()
    console.print(Panel.fit(
        Text("Generated Post", style="heading"),
        border_style="blue",
        title="Twitter AI Agent"
    ))
    console.print(Panel.fit(
        res.content,
        border_style="cyan",
        padding=(1, 2)
    ))
    
    state["ai_response"] = res.content
    return state

def validate_post(state: State):
    console.print()
    console.print(Panel(
        "Should we publish this post?",
        border_style="yellow",
        title="Decision Required"
    ))
    
    user_input = Prompt.ask(
        "[yellow]Enter[/yellow]", 
        choices=["yes", "y", "no", "n"], 
        default="no",
        show_choices=True
    ).strip().lower()
    
    if user_input in ["yes", "y"]:
        state["is_publish"] = True
        return state
    elif user_input in ["no", "n"]:
        state["is_publish"] = False
        return state
    
    messages = [
        ("system", """You are validating if a user wants to publish a post or not.
           Based on their response, determine their intent and respond with a JSON object:
           {"publish": true} if they want to publish
           {"publish": false} if they don't want to publish
           Only respond with the JSON object, nothing else."""),
        ("human", user_input),
    ]
    res = llm.invoke(messages)
    try:
        json_str = res.content.strip()
        if json_str.startswith("```json"):
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif json_str.startswith("```"):
            json_str = json_str.split("```")[1].split("```")[0].strip()
        
        result = json.loads(json_str)
        state["is_publish"] = bool(result.get("publish", False))
    except (json.JSONDecodeError, AttributeError) as e:
        console.print(f"[danger]Error parsing response: {e}[/danger]")
        state["is_publish"] = False
    
    decision = "Publishing" if state["is_publish"] else "Not publishing"
    console.print(f"[info]Decision: {decision} the post[/info]")
    return state

def route_edge(state: State) -> Literal["create_post", "feedback_on_post"]:
    if state["is_publish"] is True:
        return "create_post"
    else:
        return "feedback_on_post"

def create_post(state: State):
    tweet_content = state["ai_response"]

    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )

        response = client.create_tweet(text=tweet_content)

        console.print()
        console.print(Panel(
            Text("✅ POST PUBLISHED SUCCESSFULLY TO TWITTER (v2 API)! ✅", style="success"),
            border_style="green",
            title="Tweet Sent"
        ))
        console.print(Panel.fit(
            tweet_content,
            border_style="green",
            padding=(1, 2)
        ))

    except Exception as e:
        console.print(Panel(
            f"[danger]Failed to publish tweet: {e}[/danger]",
            border_style="red",
            title="Error"
        ))

    return state

def feedback_on_post(state: State):
    console.print()
    console.print(Panel(
        "Please provide feedback to improve the post:",
        border_style="yellow",
        title="Feedback Required"
    ))
    
    user_input = Prompt.ask("[yellow]Enter your feedback[/yellow]")
    state["feedback"] = user_input
    
    messages = [
        ("system", """You are an expert Twitter post creator. Revise the previous post based on the user's feedback.
          Guidelines:
          - Create only ONE revised post
          - Maximum 280 characters 
          - Incorporate all the feedback provided
          - Be engaging, clear, and relevant
          - Include relevant hashtags if appropriate
          - Format for readability"""),
        ("human", f"Original post: {state['ai_response']}\n\nFeedback: {user_input}\n\nPlease revise the post based on this feedback."),
    ]
    res = llm.invoke(messages)
    
    console.print()
    console.print(Panel.fit(
        Text("Revised Post", style="heading"),
        border_style="blue",
        title="Twitter AI Agent"
    ))
    console.print(Panel.fit(
        res.content,
        border_style="cyan",
        padding=(1, 2)
    ))
    
    state["ai_response"] = res.content
    return state

def create_twitter_graph() -> StateGraph:
    graph_builder = StateGraph(State)

    # define the nodes
    graph_builder.add_node("create_post", create_post)
    graph_builder.add_node("generate_post", generate_post)
    graph_builder.add_node("validate_post", validate_post)
    graph_builder.add_node("feedback_on_post", feedback_on_post)

    # define the edges
    graph_builder.add_edge(START, "generate_post")
    graph_builder.add_edge("generate_post", "validate_post")
    graph_builder.add_conditional_edges("validate_post", route_edge)
    graph_builder.add_edge("feedback_on_post", "validate_post")
    graph_builder.add_edge("create_post", END)

    return graph_builder.compile()

graph = create_twitter_graph()

def main(user_mess: str):
    state = {
        "user_message": user_mess,
        "is_publish": False,
        "ai_response": "",
        "feedback": None
    }
    
    result = graph.invoke(state)
    return result

if __name__ == "__main__":
    console.print(Panel.fit(
        Text("Twitter AI Agent", style="bold cyan"),
        border_style="blue",
        subtitle="Create engaging Twitter posts with AI"
    ))
    
    while True:
        console.rule("[bold blue]New Post", style="blue")
        user_mess = Prompt.ask("\n[bold cyan]What post do you want to create?[/bold cyan]")
        if user_mess.lower() in ["exit", "quit", "q"]:
            console.print(Panel(
                "Exiting Twitter AI Agent. Goodbye!",
                border_style="yellow",
                title="Goodbye"
            ))
            break
        main(user_mess)