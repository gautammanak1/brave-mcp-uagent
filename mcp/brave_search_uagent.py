import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from uagents_adapter import LangchainRegisterTool, cleanup_uagent
from uagents_adapter.langchain import AgentManager

# Load environment variables
load_dotenv()

# Set API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
if not AGENTVERSE_API_KEY:
    raise ValueError("AGENTVERSE_API_KEY environment variable is required")

# Initialize the model
model = ChatOpenAI(model="gpt-4o")

# Store the graph globally
_global_graph = None
graph_ready = asyncio.Event()

async def setup_brave_search_agent():
    global _global_graph
    print("Setting up Brave Search agent...")
    try:
        # Configure Brave Search MCP server
        client = MultiServerMCPClient(
            {
                "brave_search": {
                    "command": "python",
                    "args": ["brave_search_mcp.py"],
                    "transport": "stdio",
                    "timeout": 5,
                }
            }
        )

        # Get tools
        tools = await client.get_tools()
        print(f"Successfully loaded {len(tools)} tools")

        # Define call_model function
        def call_model(state: MessagesState):
            response = model.bind_tools(tools).invoke(state["messages"])
            return {"messages": response}

        # Build the graph
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "call_model")
        builder.add_conditional_edges("call_model", tools_condition)
        builder.add_edge("tools", "call_model")
        _global_graph = builder.compile()
        print("Graph successfully compiled")

        graph_ready.set()
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error setting up graph: {e}")
        graph_ready.set()

def main():
    print("Initializing Brave Search agent...")
    manager = AgentManager()

    async def graph_func(x):
        await graph_ready.wait()
        if _global_graph is None:
            error_msg = "Error: Graph not initialized properly. Please try again later."
            print(f"Response: {error_msg}")
            return error_msg
        try:
            print(f"\nReceived query: {x}")
            response = await _global_graph.ainvoke({"messages": x})
            result = response["messages"][-1].content
            print(f"\n✅ Response: {result}\n")
            return result
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            print(f"\n❌ {error_msg}\n")
            return error_msg

    agent_wrapper = manager.create_agent_wrapper(graph_func)
    manager.start_agent(setup_brave_search_agent)

    print("Registering Brave Search Agent...")
    tool = LangchainRegisterTool()
    try:
        agent_info = tool.invoke(
            {
                "agent_obj": agent_wrapper,
                "name": "Brave_search_agent",
                "port": 8080,
                "description": "This agent provides access to Brave Search tools via a Model Context Protocol (MCP) server, integrated with Agentverse and ASI:One LLM. It supports: web search, news search, video search, and image search.",
                "api_token": AGENTVERSE_API_KEY,
                "mailbox": True,
            }
        )
        print(f"✅ Registered Brave Search agent: {agent_info}")
    except Exception as e:
        print(f"⚠️ Error registering agent: {e}")
        print("Continuing with local agent only...")
    try:
        manager.run_forever()
    except KeyboardInterrupt:
        print("Shutting down agent...")
        cleanup_uagent("Brave_search_agent")
        print(" Brave agent stopped.")

if __name__ == "__main__":
    main()