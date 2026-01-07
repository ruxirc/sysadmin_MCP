import os
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

OLLAMA_MODEL = "llama3.2:3b"
MCP_SERVER_URL = "http://mcp_server:8000/mcp"

AGENT_DESCRIPTION = (
    "Agent AI administrator de sistem, executa operatii pe sistemul de fisiere si pe procese cu ajutorul instrumentelor externe de pe serverul MCP."
)

AGENT_INSTRUCTION = (
    "Esti un administrator de sistem Linux. Sarcina ta este sa raspunzi la FIECARE cerere a utilizatorului. "
    "Pentru a raspunde, trebuie sa folosesti EXCLUSIV UN SINGUR instrument din McpToolset (get_file_content, list_directory, get_file_metadata, get_memory_status, list_processes). "
    "DACA intrebarea nu poate fi rezolvata cu un tool, raspunde politicos ca nu poti ajuta si ATAT. NU inventa raspunsuri sau tool calls. "
    
    "LOGICA TA DE RASPUNS ESTE: "
    "1. Genereaza Tool Call-ul. "
    # "2. Odata ce ai primit rezultatul de la tool, NU MAI GENERA ALTE TOOL CALL-uri. Te OPRESTI."
    "2. Afiseaza continutul rezultatului (textul brut) intr-un singur bloc de cod Markdown (```text...```). "
    "3. NU adauga text, comentarii, explicatii, acolade sau paranteze in afara blocului de cod. Doar blocul de cod."
)

root_agent = Agent(
    model=LiteLlm(model=f'ollama_chat/{OLLAMA_MODEL}', temperature=0.0, api_base = os.environ.get("OLLAMA_HOST", "http://ollama_server:11434")),
    name="system_administration",
    
    description=(
        AGENT_DESCRIPTION
    ),
    
    instruction=AGENT_INSTRUCTION,
    
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams( 
                url=MCP_SERVER_URL
            )
        )
    ],
)
