# workspace_manager.py
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

class WorkspaceManager:
    """
    Manages user research workspaces with save/load functionality.
    Uses local file storage for persistence.
    """
    
    def __init__(self, workspace_dir="workspaces"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def save_workspace(self, workspace_name: str, data: Dict[str, Any]) -> bool:
        """
        Save a research workspace to a JSON file.
        
        Args:
            workspace_name: Name of the workspace
            data: Dictionary containing workspace data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add metadata
            workspace_data = {
                "name": workspace_name,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "data": data
            }
            
            # Sanitize filename
            safe_name = "".join(c for c in workspace_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.workspace_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workspace_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            st.error(f"Error saving workspace: {str(e)}")
            return False
    
    def load_workspace(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load a research workspace from a JSON file.
        
        Args:
            filename: Name of the workspace file
            
        Returns:
            Dictionary containing workspace data or None if failed
        """
        try:
            filepath = os.path.join(self.workspace_dir, filename)
            
            if not os.path.exists(filepath):
                st.error(f"Workspace file not found: {filename}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                workspace_data = json.load(f)
            
            return workspace_data.get('data', {})
        except Exception as e:
            st.error(f"Error loading workspace: {str(e)}")
            return None
    
    def list_workspaces(self) -> List[Dict[str, str]]:
        """
        List all available workspaces.
        
        Returns:
            List of workspace metadata dictionaries
        """
        workspaces = []
        
        try:
            for filename in os.listdir(self.workspace_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.workspace_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        workspaces.append({
                            'filename': filename,
                            'name': data.get('name', 'Unnamed'),
                            'created_at': data.get('created_at', 'Unknown'),
                            'size': os.path.getsize(filepath)
                        })
                    except:
                        continue
        except Exception as e:
            st.error(f"Error listing workspaces: {str(e)}")
        
        # Sort by creation date, newest first
        workspaces.sort(key=lambda x: x['created_at'], reverse=True)
        return workspaces
    
    def delete_workspace(self, filename: str) -> bool:
        """
        Delete a workspace file.
        
        Args:
            filename: Name of the workspace file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.workspace_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting workspace: {str(e)}")
            return False
    
    def clear_all_workspaces(self) -> bool:
        """
        Delete all workspace files.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            count = 0
            for filename in os.listdir(self.workspace_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.workspace_dir, filename)
                    os.remove(filepath)
                    count += 1
            return True
        except Exception as e:
            st.error(f"Error clearing workspaces: {str(e)}")
            return False
    
    def export_workspace(self, filename: str) -> Optional[bytes]:
        """
        Export workspace as downloadable JSON bytes.
        
        Args:
            filename: Name of the workspace file
            
        Returns:
            Bytes of the JSON file or None if failed
        """
        try:
            filepath = os.path.join(self.workspace_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            st.error(f"Error exporting workspace: {str(e)}")
            return None
    
    def import_workspace(self, uploaded_file) -> bool:
        """
        Import workspace from uploaded JSON file.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read and validate JSON
            content = uploaded_file.read()
            data = json.loads(content)
            
            # Save to workspace directory
            filename = uploaded_file.name
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = os.path.join(self.workspace_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(content)
            
            return True
        except Exception as e:
            st.error(f"Error importing workspace: {str(e)}")
            return False


def collect_current_session_data() -> Dict[str, Any]:
    """
    Collect all current session data for saving.
    
    Returns:
        Dictionary containing all session data
    """
    session_data = {
        # Papers and files
        "uploaded_papers": st.session_state.get("last_uploaded", []),
        
        # Questions and answers
        "suggested_questions": st.session_state.get("suggested_questions", []),
        "query_input": st.session_state.get("query_input", ""),
        
        # Store any custom results (we'll add these dynamically)
        "qa_history": st.session_state.get("qa_history", []),
        "comparison_results": st.session_state.get("comparison_results", []),
        "literature_reviews": st.session_state.get("literature_reviews", []),
        "dataset_extractions": st.session_state.get("dataset_extractions", []),
        
        # Metadata
        "saved_at": datetime.now().isoformat(),
    }
    
    return session_data


def restore_session_data(data: Dict[str, Any]):
    """
    Restore session data from loaded workspace.
    
    Args:
        data: Dictionary containing session data
    """
    # Restore session state
    if "suggested_questions" in data:
        st.session_state["suggested_questions"] = data["suggested_questions"]
    
    if "query_input" in data:
        st.session_state["query_input"] = data["query_input"]
    
    if "last_uploaded" in data:
        st.session_state["last_uploaded"] = data["last_uploaded"]
    
    # Restore history
    if "qa_history" in data:
        st.session_state["qa_history"] = data["qa_history"]
    
    if "comparison_results" in data:
        st.session_state["comparison_results"] = data["comparison_results"]
    
    if "literature_reviews" in data:
        st.session_state["literature_reviews"] = data["literature_reviews"]
    
    if "dataset_extractions" in data:
        st.session_state["dataset_extractions"] = data["dataset_extractions"]
