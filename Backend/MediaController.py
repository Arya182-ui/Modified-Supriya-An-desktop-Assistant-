# Advanced Media Control System
# Provides comprehensive media playback, recording, and management features

import os
import pygame
import json
import datetime
import threading
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
import subprocess
import platform
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
import pyaudio
import wave
import cv2
import numpy as np
from PIL import Image, ImageTk
import webbrowser

@dataclass
class MediaFile:
    path: str
    title: str
    artist: str
    album: str
    duration: float
    file_type: str
    size: int
    bitrate: int = 0
    sample_rate: int = 0
    added_date: str = None
    play_count: int = 0
    last_played: str = None
    
    def __post_init__(self):
        if self.added_date is None:
            self.added_date = datetime.datetime.now().isoformat()

@dataclass
class Playlist:
    name: str
    description: str
    files: List[str]
    created_date: str
    total_duration: float = 0
    file_count: int = 0
    
    def __post_init__(self):
        self.file_count = len(self.files)

class MediaController:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
        self.data_dir = "Data/MediaController"
        self.library_file = f"{self.data_dir}/library.json"
        self.playlists_file = f"{self.data_dir}/playlists.json"
        self.settings_file = f"{self.data_dir}/settings.json"
        self.recordings_dir = f"{self.data_dir}/Recordings"
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        # Media library and playlists
        self.media_library = self._load_library()
        self.playlists = self._load_playlists()
        self.settings = self._load_settings()
        
        # Playback state
        self.current_file = None
        self.current_position = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.repeat_mode = "none"  # none, single, all
        self.shuffle_mode = False
        self.current_playlist = None
        self.playlist_index = 0
        
        # Recording state
        self.is_recording_audio = False
        self.is_recording_video = False
        self.audio_recorder = None
        self.video_recorder = None
        
        # Supported formats
        self.audio_formats = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
        self.video_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']
        self.image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.volume)
    
    def add_to_library(self, file_path: str) -> bool:
        """Add a media file to the library"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in self.audio_formats and file_ext not in self.video_formats:
                print(f"❌ Unsupported file format: {file_ext}")
                return False
            
            # Extract metadata
            media_info = self._extract_metadata(file_path)
            
            if media_info:
                self.media_library[file_path] = media_info
                self._save_library()
                print(f"✅ Added to library: {media_info.title}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error adding to library: {e}")
            return False
    
    def scan_directory(self, directory: str, recursive: bool = True) -> int:
        """Scan directory for media files and add to library"""
        added_count = 0
        
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.add_to_library(file_path):
                            added_count += 1
            else:
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path) and self.add_to_library(file_path):
                        added_count += 1
            
            print(f"📁 Scanned directory: {directory}, added {added_count} files")
            return added_count
            
        except Exception as e:
            print(f"❌ Error scanning directory: {e}")
            return 0
    
    def play_file(self, file_path: str) -> bool:
        """Play a media file"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in self.audio_formats:
                return self._play_audio(file_path)
            elif file_ext in self.video_formats:
                return self._play_video(file_path)
            else:
                print(f"❌ Unsupported file format: {file_ext}")
                return False
                
        except Exception as e:
            print(f"❌ Error playing file: {e}")
            return False
    
    def _play_audio(self, file_path: str) -> bool:
        """Play audio file using pygame"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            self.current_file = file_path
            self.is_playing = True
            self.is_paused = False
            
            # Update play count and last played
            if file_path in self.media_library:
                self.media_library[file_path].play_count += 1
                self.media_library[file_path].last_played = datetime.datetime.now().isoformat()
                self._save_library()
            
            print(f"🎵 Playing: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
            return False
    
    def _play_video(self, file_path: str) -> bool:
        """Play video file using system default player"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
            
            self.current_file = file_path
            print(f"🎬 Playing video: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error playing video: {e}")
            return False
    
    def pause(self):
        """Pause current playback"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            print("⏸️ Playback paused")
    
    def resume(self):
        """Resume playback"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            print("▶️ Playback resumed")
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        print("⏹️ Playback stopped")
    
    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        print(f"🔊 Volume set to: {int(self.volume * 100)}%")
    
    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume
    
    def next_track(self):
        """Play next track in playlist"""
        if self.current_playlist and self.current_playlist in self.playlists:
            playlist = self.playlists[self.current_playlist]
            
            if self.shuffle_mode:
                import random
                self.playlist_index = random.randint(0, len(playlist.files) - 1)
            else:
                self.playlist_index = (self.playlist_index + 1) % len(playlist.files)
            
            next_file = playlist.files[self.playlist_index]
            self.play_file(next_file)
    
    def previous_track(self):
        """Play previous track in playlist"""
        if self.current_playlist and self.current_playlist in self.playlists:
            playlist = self.playlists[self.current_playlist]
            
            if self.shuffle_mode:
                import random
                self.playlist_index = random.randint(0, len(playlist.files) - 1)
            else:
                self.playlist_index = (self.playlist_index - 1) % len(playlist.files)
            
            previous_file = playlist.files[self.playlist_index]
            self.play_file(previous_file)
    
    def create_playlist(self, name: str, description: str = "") -> bool:
        """Create a new playlist"""
        if name in self.playlists:
            print(f"❌ Playlist already exists: {name}")
            return False
        
        playlist = Playlist(
            name=name,
            description=description,
            files=[],
            created_date=datetime.datetime.now().isoformat()
        )
        
        self.playlists[name] = playlist
        self._save_playlists()
        
        print(f"📝 Playlist created: {name}")
        return True
    
    def add_to_playlist(self, playlist_name: str, file_path: str) -> bool:
        """Add a file to a playlist"""
        if playlist_name not in self.playlists:
            print(f"❌ Playlist not found: {playlist_name}")
            return False
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        playlist = self.playlists[playlist_name]
        
        if file_path not in playlist.files:
            playlist.files.append(file_path)
            playlist.file_count = len(playlist.files)
            
            # Calculate total duration
            if file_path in self.media_library:
                playlist.total_duration += self.media_library[file_path].duration
            
            self._save_playlists()
            print(f"✅ Added to playlist '{playlist_name}': {os.path.basename(file_path)}")
            return True
        else:
            print(f"⚠️ File already in playlist: {os.path.basename(file_path)}")
            return False
    
    def play_playlist(self, playlist_name: str) -> bool:
        """Play a playlist"""
        if playlist_name not in self.playlists:
            print(f"❌ Playlist not found: {playlist_name}")
            return False
        
        playlist = self.playlists[playlist_name]
        
        if not playlist.files:
            print(f"❌ Playlist is empty: {playlist_name}")
            return False
        
        self.current_playlist = playlist_name
        self.playlist_index = 0
        
        first_file = playlist.files[0]
        return self.play_file(first_file)
    
    def start_audio_recording(self, filename: str = None, duration: int = None) -> bool:
        """Start audio recording"""
        if self.is_recording_audio:
            print("❌ Audio recording already in progress")
            return False
        
        try:
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_recording_{timestamp}.wav"
            
            filepath = os.path.join(self.recordings_dir, filename)
            
            # Audio recording parameters
            chunk = 1024
            format = pyaudio.paInt16
            channels = 2
            rate = 44100
            
            self.audio_recorder = pyaudio.PyAudio()
            stream = self.audio_recorder.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            self.is_recording_audio = True
            
            # Start recording in a separate thread
            recording_thread = threading.Thread(
                target=self._audio_recording_loop,
                args=(stream, filepath, chunk, duration),
                daemon=True
            )
            recording_thread.start()
            
            print(f"🎤 Audio recording started: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting audio recording: {e}")
            return False
    
    def stop_audio_recording(self):
        """Stop audio recording"""
        if self.is_recording_audio:
            self.is_recording_audio = False
            print("🛑 Audio recording stopped")
        else:
            print("❌ No audio recording in progress")
    
    def start_video_recording(self, filename: str = None, duration: int = None) -> bool:
        """Start video recording from webcam"""
        if self.is_recording_video:
            print("❌ Video recording already in progress")
            return False
        
        try:
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_recording_{timestamp}.mp4"
            
            filepath = os.path.join(self.recordings_dir, filename)
            
            # Initialize video capture
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ Cannot open camera")
                return False
            
            # Video recording parameters
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 20.0
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            out = cv2.VideoWriter(filepath, fourcc, fps, (frame_width, frame_height))
            
            self.is_recording_video = True
            
            # Start recording in a separate thread
            recording_thread = threading.Thread(
                target=self._video_recording_loop,
                args=(cap, out, filepath, duration),
                daemon=True
            )
            recording_thread.start()
            
            print(f"📹 Video recording started: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting video recording: {e}")
            return False
    
    def stop_video_recording(self):
        """Stop video recording"""
        if self.is_recording_video:
            self.is_recording_video = False
            print("🛑 Video recording stopped")
        else:
            print("❌ No video recording in progress")
    
    def get_library_stats(self) -> Dict:
        """Get media library statistics"""
        total_files = len(self.media_library)
        total_duration = sum(media.duration for media in self.media_library.values())
        
        # Group by file type
        audio_files = sum(1 for media in self.media_library.values() if media.file_type in self.audio_formats)
        video_files = sum(1 for media in self.media_library.values() if media.file_type in self.video_formats)
        
        # Most played files
        most_played = sorted(
            self.media_library.values(),
            key=lambda x: x.play_count,
            reverse=True
        )[:10]
        
        return {
            "total_files": total_files,
            "audio_files": audio_files,
            "video_files": video_files,
            "total_duration_hours": total_duration / 3600,
            "total_playlists": len(self.playlists),
            "most_played": [{"title": m.title, "play_count": m.play_count} for m in most_played]
        }
    
    def search_library(self, query: str) -> List[MediaFile]:
        """Search media library"""
        query = query.lower()
        results = []
        
        for media in self.media_library.values():
            if (query in media.title.lower() or
                query in media.artist.lower() or
                query in media.album.lower()):
                results.append(media)
        
        return results
    
    def _extract_metadata(self, file_path: str) -> Optional[MediaFile]:
        """Extract metadata from media file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_size = os.path.getsize(file_path)
            
            # Default values
            title = os.path.splitext(os.path.basename(file_path))[0]
            artist = "Unknown Artist"
            album = "Unknown Album"
            duration = 0
            bitrate = 0
            sample_rate = 0
            
            # Extract metadata using mutagen
            try:
                audio_file = MutagenFile(file_path)
                
                if audio_file is not None:
                    # Title
                    if 'TIT2' in audio_file:  # MP3
                        title = str(audio_file['TIT2'][0])
                    elif '\xa9nam' in audio_file:  # MP4
                        title = str(audio_file['\xa9nam'][0])
                    elif 'TITLE' in audio_file:  # FLAC/OGG
                        title = str(audio_file['TITLE'][0])
                    
                    # Artist
                    if 'TPE1' in audio_file:  # MP3
                        artist = str(audio_file['TPE1'][0])
                    elif '\xa9ART' in audio_file:  # MP4
                        artist = str(audio_file['\xa9ART'][0])
                    elif 'ARTIST' in audio_file:  # FLAC/OGG
                        artist = str(audio_file['ARTIST'][0])
                    
                    # Album
                    if 'TALB' in audio_file:  # MP3
                        album = str(audio_file['TALB'][0])
                    elif '\xa9alb' in audio_file:  # MP4
                        album = str(audio_file['\xa9alb'][0])
                    elif 'ALBUM' in audio_file:  # FLAC/OGG
                        album = str(audio_file['ALBUM'][0])
                    
                    # Duration
                    if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                        duration = audio_file.info.length
                    
                    # Bitrate and sample rate
                    if hasattr(audio_file, 'info'):
                        if hasattr(audio_file.info, 'bitrate'):
                            bitrate = audio_file.info.bitrate
                        if hasattr(audio_file.info, 'sample_rate'):
                            sample_rate = audio_file.info.sample_rate
                        
            except Exception as e:
                print(f"⚠️ Could not extract metadata from {file_path}: {e}")
            
            return MediaFile(
                path=file_path,
                title=title,
                artist=artist,
                album=album,
                duration=duration,
                file_type=file_ext,
                size=file_size,
                bitrate=bitrate,
                sample_rate=sample_rate
            )
            
        except Exception as e:
            print(f"❌ Error extracting metadata: {e}")
            return None
    
    def _audio_recording_loop(self, stream, filepath: str, chunk: int, duration: int = None):
        """Audio recording loop"""
        frames = []
        start_time = time.time()
        
        try:
            while self.is_recording_audio:
                if duration and (time.time() - start_time) >= duration:
                    break
                
                data = stream.read(chunk)
                frames.append(data)
            
            # Save recording
            stream.stop_stream()
            stream.close()
            self.audio_recorder.terminate()
            
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(2)
            wf.setsampwidth(self.audio_recorder.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            self.is_recording_audio = False
            print(f"💾 Audio recording saved: {filepath}")
            
        except Exception as e:
            print(f"❌ Error in audio recording: {e}")
            self.is_recording_audio = False
    
    def _video_recording_loop(self, cap, out, filepath: str, duration: int = None):
        """Video recording loop"""
        start_time = time.time()
        
        try:
            while self.is_recording_video:
                if duration and (time.time() - start_time) >= duration:
                    break
                
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                else:
                    break
                
                time.sleep(0.05)  # Control frame rate
            
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            
            self.is_recording_video = False
            print(f"💾 Video recording saved: {filepath}")
            
        except Exception as e:
            print(f"❌ Error in video recording: {e}")
            self.is_recording_video = False
    
    def _load_library(self) -> Dict[str, MediaFile]:
        """Load media library from file"""
        if os.path.exists(self.library_file):
            with open(self.library_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                library = {}
                for path, media_data in data.items():
                    library[path] = MediaFile(**media_data)
                return library
        return {}
    
    def _save_library(self):
        """Save media library to file"""
        data = {}
        for path, media in self.media_library.items():
            data[path] = asdict(media)
        
        with open(self.library_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def _load_playlists(self) -> Dict[str, Playlist]:
        """Load playlists from file"""
        if os.path.exists(self.playlists_file):
            with open(self.playlists_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                playlists = {}
                for name, playlist_data in data.items():
                    playlists[name] = Playlist(**playlist_data)
                return playlists
        return {}
    
    def _save_playlists(self):
        """Save playlists to file"""
        data = {}
        for name, playlist in self.playlists.items():
            data[name] = asdict(playlist)
        
        with open(self.playlists_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def _load_settings(self) -> Dict:
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

# Global media controller instance
media_controller = MediaController()

# Voice command functions for media control
def play_music_voice(command: str):
    """Play music from voice command"""
    # Parse commands like "play music", "play song name", "play artist name"
    if "stop" in command:
        media_controller.stop()
        return "Music stopped"
    elif "pause" in command:
        media_controller.pause()
        return "Music paused"
    elif "resume" in command or "continue" in command:
        media_controller.resume()
        return "Music resumed"
    elif "next" in command:
        media_controller.next_track()
        return "Playing next track"
    elif "previous" in command or "back" in command:
        media_controller.previous_track()
        return "Playing previous track"
    else:
        # Search for specific song/artist
        query = command.lower().replace("play", "").replace("music", "").strip()
        if query:
            results = media_controller.search_library(query)
            if results:
                success = media_controller.play_file(results[0].path)
                if success:
                    return f"Playing: {results[0].title} by {results[0].artist}"
                else:
                    return "Failed to play the requested song"
            else:
                return f"No songs found matching '{query}'"
        else:
            return "Please specify what to play"

def volume_control_voice(command: str):
    """Control volume from voice command"""
    current_volume = media_controller.get_volume()
    
    if "up" in command or "increase" in command:
        new_volume = min(1.0, current_volume + 0.1)
        media_controller.set_volume(new_volume)
        return f"Volume increased to {int(new_volume * 100)}%"
    elif "down" in command or "decrease" in command or "lower" in command:
        new_volume = max(0.0, current_volume - 0.1)
        media_controller.set_volume(new_volume)
        return f"Volume decreased to {int(new_volume * 100)}%"
    elif "mute" in command:
        media_controller.set_volume(0.0)
        return "Volume muted"
    elif "max" in command or "maximum" in command:
        media_controller.set_volume(1.0)
        return "Volume set to maximum"
    else:
        return f"Current volume: {int(current_volume * 100)}%"

def record_audio_voice(command: str):
    """Record audio from voice command"""
    if "stop" in command:
        media_controller.stop_audio_recording()
        return "Audio recording stopped"
    else:
        success = media_controller.start_audio_recording()
        if success:
            return "Audio recording started. Say 'stop recording' to finish."
        else:
            return "Failed to start audio recording"

def library_stats_voice(command: str):
    """Get library statistics from voice command"""
    stats = media_controller.get_library_stats()
    
    return (f"Media Library Stats:\n"
            f"Total files: {stats['total_files']}\n"
            f"Audio files: {stats['audio_files']}\n"
            f"Video files: {stats['video_files']}\n"
            f"Total duration: {stats['total_duration_hours']:.1f} hours\n"
            f"Playlists: {stats['total_playlists']}")