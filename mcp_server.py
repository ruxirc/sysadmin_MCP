import datetime
import os
import subprocess
from fastmcp import FastMCP

MCP_SERVER_NAME = "Server sys admin smecher"  
HOME_DIR = "/ruxi"  
MCP_HOST = "0.0.0.0" 
MCP_PORT = 8000

async def get_file_content(file_path: str) -> str:
    if not is_path_allowed(file_path):
        return f"Eroare de Securitate: Accesul la calea '{file_path}' este interzis."

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Eroare: Fisierul '{file_path}' nu a fost gasit."
    except Exception as e:
        return f"Eroare: {e}"

async def list_directory(dir_path: str) -> list[str]:
    if not is_path_allowed(dir_path):
        return [f"Eroare de Securitate: Accesul la calea '{dir_path}' este interzis."]

    if not os.path.isdir(dir_path):
        return [f"Eroare: Directorul '{dir_path}' nu exista sau e invalid."]
    return os.listdir(dir_path)

async def get_file_metadata(file_path: str) -> dict[str, str]:
    if not is_path_allowed(file_path):
        return f"Eroare de Securitate: Accesul la calea '{file_path}' este interzis."

    try:
        stat_info = os.stat(file_path)

        # tipul obiectului
        if os.path.isfile(file_path):
            object_type = "file"
        elif os.path.isdir(file_path):
            object_type = "directory"
        else:
            object_type = "other"
        
        modified_time = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        created_time = datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        permissions = oct(stat_info.st_mode)[-4:]

        return {
            "path": file_path,
            "type": object_type,
            "size_bytes": str(stat_info.st_size),
            "last_modified": modified_time,
            "created_time": created_time,
            "permissions_octal": permissions
        }
    except FileNotFoundError:
        return {"error": f"Eroare: Calea nu a fost găsita: {file_path}"}
    except Exception as e:
        return {"error": f"Eroare: {e}"}

async def get_memory_status() -> dict[str, any]:
    try:
        result = subprocess.run(
            ['free', '-m'],
            capture_output=True, 
            text=True,           
            check=True           
        )
        
        lines = result.stdout.strip().split('\n')
        
        if len(lines) < 2:
            return {"error": "Nu s-au putut extrage datele din 'free -m'."}

        # datele sunt in a 2-a linie
        mem_line = lines[1].split()
        
        # [1]=total, [2]=used, [6]=available
        total_mb = int(mem_line[1])
        used_mb = int(mem_line[2])
        available_mb = int(mem_line[6]) 
        
        # calcul procent utilizat
        used_percent = f"{ (used_mb / total_mb) * 100:.1f}%" if total_mb else "0%"
        
        return {
            "status": "OK",
            "total_ram": f"{total_mb} MB",
            "available_ram": f"{available_mb} MB",
            "used_ram": f"{used_mb} MB",
            "used_percent": used_percent
        }
    except FileNotFoundError:
        return {"error": "Comanda 'free' nu a fost găsita"}
    except Exception as e:
        return {"error": f"Eroare: {e}"}

def is_path_allowed(file_path: str) -> bool:
    """
    Verifica daca path-ul:
    1. Nu contine explicit secventa '..'
    2. Incepe cu calea de baza (/ruxi).
    Argumente:
        file_path: Calea catre fisier/director de verificat.
    Returneaza:
        True daca este permisa calea, altfel False.
    """
    
    if '..' in file_path:
        return False
        
    try:
        if file_path == HOME_DIR:
            return True
            
        return file_path.startswith(HOME_DIR + os.sep)
    except Exception as e:
        return {"error": f"Eroare: {e}"}

async def list_processes() -> str:
    try:
        command = ['ps aux | head -n 16'] 
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True,           
            check=True, 
            shell=True
        )
        
        return result.stdout.strip()

    except FileNotFoundError:
        return "Eroare: Comanda nu a fost gasita."
    except subprocess.CalledProcessError as e:
        return f"Eroare la executarea comenzii: {e.stderr.strip()}"
    except Exception as e:
        return f"Eroare: {e}"



mcp = FastMCP(MCP_SERVER_NAME)

@mcp.tool("get_file_content")
async def get_file_content_tool(file_path: str) -> str:
    """
    Citeste si returneaza continutul complet al unui fisier specificat.
    
    Argumente:
        file_path: Calea absoluta catre fisierul care trebuie citit.
    """
    return await get_file_content(file_path)

@mcp.tool("list_directory")
async def list_directory_tool(dir_path: str) -> str:
    """
    Citeste si returneaza toate fisierele si sub-directoarele dintr-un director specificat.
    
    Argumente:
        dir_path: Calea absoluta catre directorul care trebuie afisat.
    """
    result_list: list[str] = await list_directory(dir_path)
    
    if result_list and result_list[0].startswith("Eroare:"):
        return result_list[0]
        
    return "\n".join(result_list)

@mcp.tool("get_file_metadata")
async def get_file_metadata_tool(file_path: str) -> str:
    """
    Extrage si returneaza metadatele (dimensiune, data modificarii, permisiuni) pentru un fisier/director specificat.
    
    Argumente:
        file_path: Calea către fisierul/directorul ce trebuie inspectat.
    """
    result = await get_file_metadata(file_path) 
    return str(result)

@mcp.tool("get_memory_status")
async def get_memory_status_tool() -> str:
    """
    Returneaza starea curenta a memoriei RAM (Total, Utilizat, Disponibil) in Megabytes si procentul de utilizare.
    Se foloseste subprocess.run()
    """
    result = await get_memory_status()
    
    if "error" in result:
        return result["error"]
        
    formatted_output = (
        f"Memorie RAM Status: {result['status']}\n"
        f"  Total RAM: {result['total_ram']}\n"
        f"  RAM Disponibila: {result['available_ram']}\n"
        f"  RAM Utilizata: {result['used_ram']} ({result['used_percent']})"
    )
    return formatted_output

@mcp.tool("list_processes")
async def list_processes_tool() -> str:
    """
    Listează primele 15 procese care ruleaza pe sistem (User, PID, CPU, Memorie).
    Returneaza output-ul brut al comenzii 'ps aux'.
    """
    return await list_processes()

if __name__ == "__main__":
    try:
        mcp.run(transport="http", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\nServer MCP inchis.")