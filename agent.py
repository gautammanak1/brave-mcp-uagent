from uagents_adapter import MCPServerAdapter
from server import mcp

# Create an MCP adapter with your MCP server
mcp_adapter = MCPServerAdapter(
    mcp_server=mcp,                    
    asi1_api_key="", 
    model="asi1-mini"             
)

# Create a uAgent
agent = Agent()

# Include protocols from the adapter
for protocol in mcp_adapter.protocols:
    agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    # Run the MCP adapter with the agent
    mcp_adapter.run(agent)
