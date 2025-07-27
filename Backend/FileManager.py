# Advanced File Management System
# Provides comprehensive file operations, organization, and analysis

import os
import shutil
import json
import datetime
import hashlib
import zipfile
import tarfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import mimetypes
from dataclasses import dataclass, asdict
import threading
import time
from Backend.security import SecuritySystem

@dataclass
class FileInfo:
    path: str
    name: str
    size: int
    type: str
    modified: str
    created: str
    permissions: str
    is_directory: bool
    extension: str = ""
    mime_type: str = ""
    hash: str = ""

class FileManager:
    def __init__(self):
        self.security = SecuritySystem()
        self.data_dir = "Data/FileManager"
        self.favorites_file = f"{self.data_dir}/favorites.json"
        self.history_file = f"{self.data_dir}/history.json"
        self.bookmarks_file = f"{self.data_dir}/bookmarks.json"
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load data
        self.favorites = self._load_favorites()
        self.history = self._load_history()
        self.bookmarks = self._load_bookmarks()
        
        # File organization rules
        self.organization_rules = {
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
            "presentations": [".ppt", ".pptx", ".odp"],
            "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php"]
        }
    
    def get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """Get detailed information about a file or directory"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            
            file_info = FileInfo(
                path=str(path.absolute()),
                name=path.name,
                size=stat.st_size if path.is_file() else 0,
                type="Directory" if path.is_dir() else "File",
                modified=datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                created=datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                permissions=oct(stat.st_mode)[-3:],
                is_directory=path.is_dir(),
                extension=path.suffix.lower() if path.is_file() else "",
                mime_type=mimetypes.guess_type(str(path))[0] or "unknown"
            )
            
            # Calculate file hash for regular files
            if path.is_file() and stat.st_size < 100 * 1024 * 1024:  # Only for files < 100MB
                file_info.hash = self._calculate_file_hash(str(path))
            
            return file_info
            
        except Exception as e:
            print(f"❌ Error getting file info: {e}")
            return None
    
    def list_directory(self, directory_path: str, include_hidden: bool = False, 
                      sort_by: str = "name") -> List[FileInfo]:
        """List contents of a directory with detailed information"""
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                print(f"❌ Directory not found: {directory_path}")
                return []
            
            files = []
            for item in path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                file_info = self.get_file_info(str(item))
                if file_info:
                    files.append(file_info)
            
            # Sort files
            if sort_by == "size":
                files.sort(key=lambda x: x.size, reverse=True)
            elif sort_by == "modified":
                files.sort(key=lambda x: x.modified, reverse=True)
            elif sort_by == "type":
                files.sort(key=lambda x: (x.is_directory, x.extension))
            else:  # default: name
                files.sort(key=lambda x: x.name.lower())
            
            self._add_to_history("list_directory", directory_path)
            return files
            
        except Exception as e:
            print(f"❌ Error listing directory: {e}")
            return []
    
    def search_files(self, directory: str, pattern: str, search_content: bool = False,
                    file_types: List[str] = None, max_size: int = None) -> List[FileInfo]:
        """Search for files based on various criteria"""
        results = []
        pattern = pattern.lower()
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_info = self.get_file_info(file_path)
                    
                    if not file_info:
                        continue
                    
                    # Apply filters
                    if file_types and file_info.extension not in file_types:
                        continue
                    
                    if max_size and file_info.size > max_size:
                        continue
                    
                    # Check if file matches pattern
                    matches = False
                    
                    # Search in filename
                    if pattern in file_info.name.lower():
                        matches = True
                    
                    # Search in file content (for text files)
                    if search_content and not matches and file_info.size < 10 * 1024 * 1024:  # < 10MB
                        if self._search_in_file_content(file_path, pattern):
                            matches = True
                    
                    if matches:
                        results.append(file_info)
            
            self._add_to_history("search_files", f"{directory} - {pattern}")
            return results
            
        except Exception as e:
            print(f"❌ Error searching files: {e}")
            return []
    
    def create_directory(self, directory_path: str, parents: bool = True) -> bool:
        """Create a new directory"""
        try:
            path = Path(directory_path)
            if path.exists():
                print(f"❌ Directory already exists: {directory_path}")
                return False
            
            if parents:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.mkdir()
            
            self._add_to_history("create_directory", directory_path)
            print(f"📁 Directory created: {directory_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating directory: {e}")
            return False
    
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """Copy a file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                print(f"❌ Source not found: {source}")
                return False
            
            if dest_path.exists() and not overwrite:
                print(f"❌ Destination already exists: {destination}")
                return False
            
            if source_path.is_file():
                shutil.copy2(source, destination)
            else:
                shutil.copytree(source, destination, dirs_exist_ok=overwrite)
            
            self._add_to_history("copy", f"{source} -> {destination}")
            print(f"📋 Copied: {source} -> {destination}")
            return True
            
        except Exception as e:
            print(f"❌ Error copying: {e}")
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move a file or directory"""
        try:
            source_path = Path(source)
            if not source_path.exists():
                print(f"❌ Source not found: {source}")
                return False
            
            shutil.move(source, destination)
            
            self._add_to_history("move", f"{source} -> {destination}")
            print(f"🚚 Moved: {source} -> {destination}")
            return True
            
        except Exception as e:
            print(f"❌ Error moving: {e}")
            return False
    
    def delete_file(self, file_path: str, secure_delete: bool = False) -> bool:
        """Delete a file or directory"""
        if self.security.requires_auth("file_delete") and not self.security.authenticate():
            print("🔒 Delete operation blocked")
            return False
        
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return False
            
            if secure_delete and path.is_file():
                self._secure_delete_file(str(path))
            elif path.is_file():
                path.unlink()
            else:
                shutil.rmtree(str(path))
            
            self.security.log_action(f"File deleted: {file_path}")
            self._add_to_history("delete", file_path)
            print(f"🗑️ Deleted: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting: {e}")
            return False
    
    def compress_files(self, files: List[str], archive_path: str, 
                      compression_type: str = "zip") -> bool:
        """Compress files into an archive"""
        try:
            if compression_type.lower() == "zip":
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files:
                        path = Path(file_path)
                        if path.exists():
                            if path.is_file():
                                zipf.write(file_path, path.name)
                            else:
                                for root, dirs, files_in_dir in os.walk(file_path):
                                    for file in files_in_dir:
                                        file_full_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_full_path, file_path)
                                        zipf.write(file_full_path, arcname)
            
            elif compression_type.lower() in ["tar", "tar.gz"]:
                mode = "w:gz" if compression_type.lower() == "tar.gz" else "w"
                with tarfile.open(archive_path, mode) as tarf:
                    for file_path in files:
                        path = Path(file_path)
                        if path.exists():
                            tarf.add(file_path, path.name)
            
            self._add_to_history("compress", f"{len(files)} files -> {archive_path}")
            print(f"📦 Archive created: {archive_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error compressing files: {e}")
            return False
    
    def extract_archive(self, archive_path: str, destination: str = None) -> bool:
        """Extract an archive"""
        try:
            archive = Path(archive_path)
            if not archive.exists():
                print(f"❌ Archive not found: {archive_path}")
                return False
            
            if destination is None:
                destination = str(archive.parent / archive.stem)
            
            if archive.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(destination)
            elif archive.suffix.lower() in [".tar", ".gz", ".bz2"]:
                with tarfile.open(archive_path, 'r:*') as tarf:
                    tarf.extractall(destination)
            
            self._add_to_history("extract", f"{archive_path} -> {destination}")
            print(f"📂 Archive extracted: {archive_path} -> {destination}")
            return True
            
        except Exception as e:
            print(f"❌ Error extracting archive: {e}")
            return False
    
    def organize_files(self, directory: str, create_folders: bool = True) -> Dict[str, int]:
        """Organize files in a directory by type"""
        try:
            organized_count = {}
            
            for file_info in self.list_directory(directory):
                if file_info.is_directory:
                    continue
                
                # Determine file category
                category = self._get_file_category(file_info.extension)
                
                if create_folders:
                    category_dir = os.path.join(directory, category.title())
                    os.makedirs(category_dir, exist_ok=True)
                    
                    new_path = os.path.join(category_dir, file_info.name)
                    
                    if not os.path.exists(new_path):
                        self.move_file(file_info.path, new_path)
                        organized_count[category] = organized_count.get(category, 0) + 1
            
            self._add_to_history("organize", directory)
            print(f"🗂️ Organized {sum(organized_count.values())} files")
            return organized_count
            
        except Exception as e:
            print(f"❌ Error organizing files: {e}")
            return {}
    
    def find_duplicates(self, directory: str) -> Dict[str, List[str]]:
        """Find duplicate files based on content hash"""
        duplicates = {}
        file_hashes = {}
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_info = self.get_file_info(file_path)
                    
                    if file_info and file_info.hash:
                        if file_info.hash in file_hashes:
                            if file_info.hash not in duplicates:
                                duplicates[file_info.hash] = [file_hashes[file_info.hash]]
                            duplicates[file_info.hash].append(file_path)
                        else:
                            file_hashes[file_info.hash] = file_path
            
            return duplicates
            
        except Exception as e:
            print(f"❌ Error finding duplicates: {e}")
            return {}
    
    def get_directory_size(self, directory: str) -> Tuple[int, int]:
        """Get total size and file count of a directory"""
        total_size = 0
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        continue
            
            return total_size, file_count
            
        except Exception as e:
            print(f"❌ Error calculating directory size: {e}")
            return 0, 0
    
    def add_bookmark(self, name: str, path: str):
        """Add a directory bookmark"""
        self.bookmarks[name] = {
            "path": path,
            "created_at": datetime.datetime.now().isoformat()
        }
        self._save_bookmarks()
        print(f"🔖 Bookmark added: {name} -> {path}")
    
    def get_bookmarks(self) -> Dict:
        """Get all bookmarks"""
        return self.bookmarks
    
    def add_to_favorites(self, file_path: str):
        """Add a file to favorites"""
        file_info = self.get_file_info(file_path)
        if file_info:
            self.favorites[file_path] = {
                "name": file_info.name,
                "added_at": datetime.datetime.now().isoformat()
            }
            self._save_favorites()
            print(f"⭐ Added to favorites: {file_info.name}")
    
    def get_favorites(self) -> Dict:
        """Get all favorite files"""
        return self.favorites
    
    def get_file_history(self, limit: int = 50) -> List[Dict]:
        """Get recent file operations history"""
        return self.history[-limit:] if len(self.history) > limit else self.history
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _secure_delete_file(self, file_path: str):
        """Securely delete a file by overwriting it"""
        try:
            file_size = os.path.getsize(file_path)
            
            with open(file_path, "r+b") as f:
                # Overwrite with random data multiple times
                for _ in range(3):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            os.remove(file_path)
            
        except Exception as e:
            print(f"❌ Error in secure delete: {e}")
            # Fallback to regular delete
            os.remove(file_path)
    
    def _search_in_file_content(self, file_path: str, pattern: str) -> bool:
        """Search for pattern in file content (text files only)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return pattern.lower() in content.lower()
        except Exception:
            return False
    
    def _get_file_category(self, extension: str) -> str:
        """Get file category based on extension"""
        extension = extension.lower()
        for category, extensions in self.organization_rules.items():
            if extension in extensions:
                return category
        return "others"
    
    def _add_to_history(self, operation: str, details: str):
        """Add operation to history"""
        self.history.append({
            "operation": operation,
            "details": details,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Keep only last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self._save_history()
    
    def _load_favorites(self) -> Dict:
        """Load favorites from file"""
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_favorites(self):
        """Save favorites to file"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=4)
    
    def _load_history(self) -> List:
        """Load history from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save history to file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4)
    
    def _load_bookmarks(self) -> Dict:
        """Load bookmarks from file"""
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_bookmarks(self):
        """Save bookmarks to file"""
        with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, indent=4)

# Global file manager instance
file_manager = FileManager()

# Voice command functions for file management
def list_files_voice(command: str):
    """List files from voice command"""
    # Parse command like "list files in downloads" or "show files in documents"
    if "downloads" in command.lower():
        directory = os.path.expanduser("~/Downloads")
    elif "documents" in command.lower():
        directory = os.path.expanduser("~/Documents")
    elif "desktop" in command.lower():
        directory = os.path.expanduser("~/Desktop")
    else:
        directory = os.getcwd()
    
    files = file_manager.list_directory(directory)
    
    if not files:
        return f"No files found in {directory}"
    
    result = f"Files in {directory}:\n"
    for i, file_info in enumerate(files[:10], 1):  # Limit to 10 for voice
        file_type = "📁" if file_info.is_directory else "📄"
        result += f"{i}. {file_type} {file_info.name}\n"
    
    if len(files) > 10:
        result += f"... and {len(files) - 10} more files"
    
    return result

def search_files_voice(command: str):
    """Search files from voice command"""
    # Parse command like "search for budget files" or "find document about meeting"
    query_parts = command.lower().split()
    
    # Extract search terms
    search_terms = []
    for word in query_parts:
        if word not in ["search", "for", "find", "files", "file", "document", "documents"]:
            search_terms.append(word)
    
    if not search_terms:
        return "Please specify what to search for"
    
    pattern = " ".join(search_terms)
    search_directory = os.path.expanduser("~")  # Search in home directory
    
    results = file_manager.search_files(search_directory, pattern, search_content=False)
    
    if not results:
        return f"No files found matching '{pattern}'"
    
    result = f"Found {len(results)} files matching '{pattern}':\n"
    for i, file_info in enumerate(results[:5], 1):  # Limit to 5 for voice
        result += f"{i}. {file_info.name} in {os.path.dirname(file_info.path)}\n"
    
    return result

def organize_files_voice(command: str):
    """Organize files from voice command"""
    # Parse command like "organize downloads folder" or "organize my files"
    if "downloads" in command.lower():
        directory = os.path.expanduser("~/Downloads")
    elif "documents" in command.lower():
        directory = os.path.expanduser("~/Documents")
    elif "desktop" in command.lower():
        directory = os.path.expanduser("~/Desktop")
    else:
        return "Please specify which folder to organize (downloads, documents, or desktop)"
    
    organized = file_manager.organize_files(directory)
    
    if not organized:
        return f"No files to organize in {directory}"
    
    result = f"Organized files in {directory}:\n"
    for category, count in organized.items():
        result += f"- {count} {category} files\n"
    
    return result

def get_file_info_voice(command: str):
    """Get file information from voice command"""
    # This would typically need more sophisticated parsing
    return "Please specify the file path to get information about"