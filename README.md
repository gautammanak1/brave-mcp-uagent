
# Brave Search Agent
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
[![tech:python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![tech:uagents](https://img.shields.io/badge/uAgents-000000?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDBDNS4zNzMgMCAwIDUuMzczIDAgMTJDNy4xNTMgMTIgMTIgNy4xNTMgMTIgMFoiIGZpbGw9IndoaXRlIi8+CjxwYXRoIGQ9Ik0xMiAyNEMxOC42MjcgMjQgMjQgMTguNjI3IDI0IDEyQzE2Ljg0NyAxMiAxMiAxNi4xNTMgMTIgMjRaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://fetch.ai/uagents)


**Overview**

The uAgent, built with the uAgents framework, serves as an autonomous client that interacts with an MCP server to perform web and local searches using the Brave Search API. It handles communication, protocol inclusion, and result delivery.

- **Web Search**: Search for general queries, news, articles, and videos with pagination, result type filtering (web, news, videos, all), safety levels (strict, moderate, off), and content freshness (past day, week, month, year, all).
- **Local Search**: Find local businesses and places (e.g., restaurants, stores) with detailed information like addresses, ratings, and hours. Falls back to web search if no local results are found.

## Usage
- Query for web content: "Search for recent AI news" or "Find AI videos from the past month with strict safety".
- Query for local businesses: "Find pizza restaurants near Central Park".
- Use the agent's address to target it specifically in ASI:One, e.g., "Please ask [agent_address] for recent AI news".

## Tools
- `brave_web_search`: Performs web searches with customizable parameters.
- `brave_local_search`: Searches for local businesses with automatic web search fallback.

Built with Fetch.ai's Agentverse and powered by ASI:One LLM for intelligent tool selection.
**Input Data Model**
```
class QueryMessage(Model):
    query : str
```
**Output Data Model**
```
class ResponseMessage(Model):
    response : str
```


[Check out the Agent Profile on Agentverse](https://agentverse.ai/agents/details/agent1qgfnnx5nwxspd55e3zjwtra2gegdt77edf254k47tkcl0nc9dv2zvj6jjhj/profile)

