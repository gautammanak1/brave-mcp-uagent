# Brave Search Agent
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)


This agent provides access to Brave Search tools via a Model Context Protocol (MCP) server, integrated with Agentverse and ASI:One LLM. It supports:

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
