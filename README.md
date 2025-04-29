# test-tableau-mcp
This project is a quick prototype to expose Tableau VDS endpoints through an MCP server and integrate them with Claude Desktop client.

To run this MCP Server and connect it Claude Desktop follow these steps. These instructions were adapted from the [MCP how-to guide](https://modelcontextprotocol.io/quickstart/server). These instructions assume you are using MacOS/Linux. If you're running Windows, refer to the how-to guide linked above.

## System requirements
Python 3.10 or higher installed.
You must use the Python MCP SDK 1.2.0 or higher.

## Set up your environment
Install UV if you haven't already.
```python
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Make sure to restart your terminal afterwards to ensure that the uv command gets picked up.

Now, create and set up your virtual environment:
```python
# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx
```
## Hardcode required environment variables
This simple prototype requires that you harcode 4 variables in vds.py file:
1. your server url in `VIZQL_API_BASE`
2. your server url in `METADATA_GRAPHQL`
3. the datasource LUID for the data source you want to query in `DS_LUID`
4. A valid session token in `AUTH_TOKEN`

## Running the server
`uv --directory <ABSOLUTE PATH TO PROJECT> run vds.py`

## Testing your server with Claude for Desktop
First, make sure you have Claude for Desktop installed. You can install the [latest version here](https://claude.ai/download). If you already have Claude for Desktop, make sure it’s updated to the latest version.

We’ll need to configure Claude for Desktop for whichever MCP servers you want to use. To do this, open your Claude for Desktop App configuration at `~/Library/Application Support/Claude/claude_desktop_config.json` in a text editor. Make sure to create the file if it doesn’t exist.

For example, if you have VS Code installed:
`code ~/Library/Application\ Support/Claude/claude_desktop_config.json`

You’ll then add your servers in the mcpServers key. The MCP UI elements will only show up in Claude for Desktop if at least one server is properly configured.

In this case, we’ll add our single vds server like so:
```python
{
    "mcpServers": {
        "vds": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/test-tableau-mcp/",
                "run",
                "vds.py"
            ]
        }
    }
}
```
You may need to put the full path to the uv executable in the command field. You can get this by running `which uv` on MacOS/Linux or `where uv` on Windows.

This tells Claude for Desktop:

There’s an MCP server named “vds.” Launch it by running `uv --directory /ABSOLUTE/PATH/TO/PARENT/FOLDER/ run vds.py`. Save the file, and restart Claude for Desktop.

## Running queries in Claude to trigger the tool
The VDS API syntax is not explicitly passed in MCP tools, so start your session by passing a few in context samples that show Claude how to properly format `Query` objects. You can copy the array of dictionaries in the samples.py. Send an inital message to Claude like so:
make sure you generate payloads according to this syntax:
```
in_context_samples = [
  {
    "fields": [
      { "fieldCaption": "Segment" },
      { "fieldCaption": "Sales", "function": "SUM" }
    ]
  },
  {
    "fields": [
      { "fieldCaption": "Category" },
      { "fieldCaption": "Profit", "function": "SUM", "sortDirection": "DESC" }
    ]
  },
  {
    "fields": [
      { "fieldCaption": "State/Province" },
      { "fieldCaption": "Sales", "function": "SUM", "sortDirection": "DESC" }
    ],
    "filters": [
      {
        "field": { "fieldCaption": "Segment" },
        "filterType": "SET",
        "values": ["Consumer"],
        "exclude": false
      },
      {
        "field": { "fieldCaption": "Order Date" },
        "filterType": "RANGE",
        "min": "2021-01-01",
        "max": "2021-12-31"
      }
    ],
    "limit": 5
  }
]

do the states with the most sales also have the most profit?
```
