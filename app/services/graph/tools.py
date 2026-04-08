import docker
import base64
from langchain_core.tools import tool

client = docker.from_env()

def get_agent_tools(container_name: str):
    """
    Factory function to generate tools locked to a specific live container.
    """
    
    @tool
    def execute_shell(command: str) -> str:
        """
        Executes a raw bash command in the workspace. 
        Use this for exploring (ls, pwd), installing packages (pip install), or running tests (pytest).
        Do NOT use this for writing complex code files.
        """
        print(f"🤖 [TOOL] Shell: {command}")
        try:
            container = client.containers.get(container_name)
            exit_code, output = container.exec_run(
                cmd=["sh", "-c", command],
                workdir="/workspace"
            )
            result = output.decode("utf-8").strip()
            return f"✅ SUCCESS:\n{result}" if exit_code == 0 else f"❌ FAILED (Code {exit_code}):\n{result}"
        except Exception as e:
            return f"System Error: {str(e)}"

    @tool
    def read_file_with_lines(filepath: str) -> str:
        """
        Reads a file from the workspace and prints it with line numbers.
        Always use this before editing a file so you know exactly what to replace.
        """
        print(f"🤖 [TOOL] Reading: {filepath}")
        try:
            container = client.containers.get(container_name)
            # 'cat -n' automatically adds line numbers to the output
            exit_code, output = container.exec_run(
                cmd=["sh", "-c", f"cat -n {filepath}"],
                workdir="/workspace"
            )
            result = output.decode("utf-8")
            if exit_code != 0:
                return f"❌ FAILED to read {filepath}: {result}"
            return f"📄 File: {filepath}\n{result}"
        except Exception as e:
            return f"System Error: {str(e)}"

    @tool
    def str_replace_editor(filepath: str, old_str: str, new_str: str) -> str:
        """
        Surgically edits an existing file by replacing `old_str` with `new_str`.
        The `old_str` must match the file content EXACTLY, including spaces and indentation.
        """
        print(f"🤖 [TOOL] Editing: {filepath}")
        try:
            container = client.containers.get(container_name)
            
            # 1. Read the current content directly
            exit_code, output = container.exec_run(["cat", filepath], workdir="/workspace")
            if exit_code != 0:
                return f"❌ FAILED: File {filepath} does not exist. Create it first."
                
            current_content = output.decode("utf-8")
            
            # 2. Check if the old string actually exists
            if old_str not in current_content:
                return "❌ FAILED: `old_str` not found in file. Use read_file_with_lines to check exact spacing/indentation."
                
            # 3. Perform the replacement in Python (Safe from hallucination)
            new_content = current_content.replace(old_str, new_str, 1) # Replace first occurrence
            
            # 4. The Base64 Trick: Safely write it back to the container
            encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
            write_cmd = f"echo '{encoded_content}' | base64 -d > {filepath}"
            
            container.exec_run(["sh", "-c", write_cmd], workdir="/workspace")
            return f"✅ SUCCESS: Updated {filepath}."
            
        except Exception as e:
            return f"System Error: {str(e)}"

    @tool
    def write_new_file(filepath: str, content: str) -> str:
        """
        Creates a brand new file with the provided content. 
        Will overwrite the file if it already exists.
        """
        print(f"🤖 [TOOL] Writing new file: {filepath}")
        try:
            container = client.containers.get(container_name)
            
            # Ensure the directory exists
            dir_cmd = f"mkdir -p $(dirname {filepath})"
            container.exec_run(["sh", "-c", dir_cmd], workdir="/workspace")
            
            # The Base64 Trick again! No more quote escaping errors.
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            write_cmd = f"echo '{encoded_content}' | base64 -d > {filepath}"
            
            container.exec_run(["sh", "-c", write_cmd], workdir="/workspace")
            return f"✅ SUCCESS: Created {filepath}."
        except Exception as e:
            return f"System Error: {str(e)}"

    # Return the suite of tools bound to this specific session
    return [execute_shell, read_file_with_lines, str_replace_editor, write_new_file]