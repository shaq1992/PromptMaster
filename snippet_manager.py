import json
import os

FILE_NAME = "snippets.json"

class SnippetManager:
    def __init__(self):
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, "w") as f:
                json.dump({}, f)

    def load_snippets(self, section_tag):
        """Returns a list of dicts {'name':..., 'content':...} for the given tag"""
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
            # Return empty list if key doesn't exist
            return data.get(section_tag.upper(), [])
        except Exception:
            return []

    def save_snippet(self, section_tag, name, content):
        """Saves a new snippet under the section key"""
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
            
            key = section_tag.upper()
            if key not in data:
                data[key] = []
            
            # Add new snippet
            data[key].append({"name": name, "content": content})
            
            with open(FILE_NAME, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving snippet: {e}")
            return False