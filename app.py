import streamlit as st
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.serpapi import SerpApiTools
from agno.tools.yfinance import YFinanceTools
from datetime import datetime

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("## 🧠 Groq LLM Settings")
    api_key = st.text_input("🔑 Enter Your Groq API Key", type="password")
    model_choice = st.selectbox(
        "🧬 Choose a Groq Model",
        [
            "deepseek-r1-distill-llama-70b",
            "llama-3.3-70b-versatile",
            "llama3-70b-8192",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
            "qwen-2.5-32b",
            "allam-2-7b",
        ],
    )
    Serpi_api = st.text_input("🔍 Enter Your Serpi API Key", type="password")

    st.markdown(
        "[🗝️ Get Groq API key](https://console.groq.com/keys)", unsafe_allow_html=True
    )
    st.markdown(
        "[🔎 Get Serpi API key](https://serpapi.com/dashboard)", unsafe_allow_html=True
    )
    st.write("LLama knows Persian")

    st.markdown("---")
    st.button("🧹 Clear Chat", on_click=lambda: st.session_state.pop("messages", None))

# --- Header Section ---
st.title("💸 Arash+ Finance Assistant")
st.caption(
    "Created by **Arash Omranpour** | Combines AI Agents for Real-time Web & Finance Analysis"
)
st.markdown("---")

# Real-time Clock
today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"🕒 **Current Time:** `{today_date}`")

# --- Run App if API Keys Provided ---
if api_key and Serpi_api:
    selected_model = Groq(api_key=api_key, id=model_choice)

    # --- Agents Definition ---
    web_agent = Agent(
        name="Web Agent",
        role="Search the web for crypto, forex, and finance information",
        model=selected_model,
        tools=[SerpApiTools(api_key=Serpi_api)],
        instructions=f"Always include sources and provide up-to-date information as of {today_date}.",
        show_tool_calls=True,
        markdown=True,
    )

    finance_agent = Agent(
        name="Finance Agent",
        role="Get real-time financial data and charts for analysis",
        model=selected_model,
        tools=[
            YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                stock_fundamentals=True,
                company_info=True,
            )
        ],
        instructions=f"You are a top technical trader. Provide data in tables using information as of {today_date}. Always double-check results.",
        show_tool_calls=True,
        markdown=True,
    )

    manager_agent = Agent(
        name="Manager Agent",
        role="Manage user queries, coordinate agents, and provide final responses.",
        model=selected_model,
        instructions=(
            "You are Arash+, developed by Arash Omranpour. You are a strategic AI assistant in trading. "
            "Speak in a friendly tone, combine insights from Web Agent and Finance Agent, and greet users if needed. "
            "You speak fluent Persian and English."
        ),
        show_tool_calls=True,
        markdown=True,
    )

    agent_team = Agent(
        team=[manager_agent, web_agent, finance_agent],
        model=selected_model,
        instructions=[
            f"Use today's date: {today_date}",
            "Respond in markdown format",
            "Always include sources and structure information cleanly",
            "Use tables when appropriate",
            "You are Arash+, developed by Arash Omranpour",
        ],
        show_tool_calls=True,
        markdown=True,
    )

    # --- Session Chat State ---
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    tab1, tab2 = st.tabs(["💬 Chat", "📰 Market News & 📈 Financial Analysis"])

    # --- Tab 1: Chat Interface ---
    with tab1:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input(
            "💬 Ask a question about crypto, forex, or stocks..."
        )

        if user_input:
            st.session_state["messages"].append({"role": "user", "content": user_input})
            with st.chat_message("assistant"):
                with st.spinner("🤖 Arash+ is thinking..."):
                    try:
                        result = agent_team.run(user_input).content
                    except Exception as e:
                        result = (
                            f"⚠️ Error: {e}. Check your API key and internet connection."
                        )
                    st.markdown(result)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": result}
                    )

    # --- Tab 2: Market News & Financial Analysis ---
    with tab2:
        st.subheader("📰 Latest Market News")
        try:
            with st.spinner("🌐 Web Agent is searching..."):
                news_response = web_agent.run(
                    "Give me the latest market news today"
                ).content
                st.markdown(news_response)
        except Exception as e:
            st.warning(f"Could not fetch market news: {e}")

        st.subheader("📊 Financial Analysis")
        try:
            with st.spinner("📈 Finance Agent is analyzing..."):
                finance_response = finance_agent.run(
                    "Analyze current financial trends for Bitcoin, Tesla, and Nvidia"
                ).content
                st.markdown(finance_response)
        except Exception as e:
            st.warning(f"Could not fetch financial data: {e}")
else:
    st.warning("🔐 Please enter your Groq & Serpi API keys in the sidebar to start.")
