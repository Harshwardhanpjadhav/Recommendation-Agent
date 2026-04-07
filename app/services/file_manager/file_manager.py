import os
from pathlib import Path

class FileManager:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()

    def write_file(self, file_path: str, content: str):
        """Writes content to a specific file path."""
        full_path = (self.base_path / file_path).resolve()
        
        # Security check: Ensure we stay inside the project folder
        if not str(full_path).startswith(str(self.base_path)):
            raise PermissionError("Attempted to write outside project directory")
            
        os.makedirs(full_path.parent, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"✅ File {file_path} written successfully."

    def read_file(self, file_path: str):
        """Reads content from a file."""
        full_path = self.base_path / file_path
        if full_path.exists():
            with open(full_path, "r") as f:
                return f.read()
        return None

    def list_files(self):
        """Lists all relevant files in the repository, ignoring .git, __pycache__, etc."""
        ignore_dirs = {".git", "__pycache__", "venv", ".pytest_cache", ".gemini", "node_modules"}
        ignore_files = {".DS_Store", "code_agent.db"}
        files_list = []
        for root, dirs, files in os.walk(self.base_path):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file in ignore_files:
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), self.base_path)
                files_list.append(rel_path)
        return files_list