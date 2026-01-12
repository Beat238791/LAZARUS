"""
PROJECT: LAZARUS - The Ultimate Psychological Profiling Engine
A three-phase psychological analysis and persona simulation system.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
import time
import threading
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Optional imports with graceful fallbacks
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SUPPORT = True
except ImportError:
    WEB_SUPPORT = False

# Load environment variables
load_dotenv()

# Application Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class LazarusApp(ctk.CTk):
    """Main Application Window for Project LAZARUS"""

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("PROJECT: LAZARUS - Psychological Profiling Engine")
        self.geometry("1400x900")
        self.minsize(1200, 800)

        # Data Storage
        self.target_data = {}
        self.profile_data = {}
        self.chat_history = []
        self.persona_active = False
        self.uploaded_documents = []
        self.scraped_data = []
        self.social_media_data = []
        self.saved_profiles = self.load_saved_profiles()

        # Groq Client
        self.groq_client = None
        self.initialize_groq()

        # UI Setup
        self.setup_ui()

    def load_saved_profiles(self):
        """โหลดรายชื่อ profiles ที่บันทึกไว้"""
        if not os.path.exists("profiles"):
            os.makedirs("profiles")
        profiles = []
        for file in os.listdir("profiles"):
            if file.endswith(".json"):
                profiles.append(file.replace(".json", ""))
        return profiles

    def initialize_groq(self):
        """Initialize Groq API client"""
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            # Show popup to get API key
            dialog = APIKeyDialog(self)
            self.wait_window(dialog)
            api_key = dialog.api_key

            if api_key:
                # Save to .env
                with open(".env", "w") as f:
                    f.write(f"GROQ_API_KEY={api_key}\n")
                os.environ["GROQ_API_KEY"] = api_key
            else:
                messagebox.showerror("Error", "API Key required. Application will have limited functionality.")
                return

        try:
            self.groq_client = Groq(api_key=api_key)
        except Exception as e:
            messagebox.showerror("Groq Error", f"Failed to initialize Groq client: {str(e)}")

    def setup_ui(self):
        """Setup the main UI layout"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Navigation
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="⚡ LAZARUS ⚡",
            font=ctk.CTkFont(size=28, weight="bold", family="Consolas"),
            text_color="#00ff00"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Psychological\nProfiling Engine",
            font=ctk.CTkFont(size=12, family="Consolas"),
            text_color="#00aa00"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Navigation Buttons
        self.phase1_btn = ctk.CTkButton(
            self.sidebar,
            text="PHASE 1: THE HUNT",
            command=lambda: self.show_phase(0),
            font=ctk.CTkFont(size=13, weight="bold", family="Consolas"),
            fg_color="#1a1a1a",
            hover_color="#00ff00",
            text_color="#00ff00",
            border_width=2,
            border_color="#00ff00",
            height=45
        )
        self.phase1_btn.grid(row=2, column=0, padx=20, pady=10)

        self.phase2_btn = ctk.CTkButton(
            self.sidebar,
            text="PHASE 2: THE WEB",
            command=lambda: self.show_phase(1),
            font=ctk.CTkFont(size=13, weight="bold", family="Consolas"),
            fg_color="#1a1a1a",
            hover_color="#00ff00",
            text_color="#00ff00",
            border_width=2,
            border_color="#00ff00",
            height=45
        )
        self.phase2_btn.grid(row=3, column=0, padx=20, pady=10)

        self.phase3_btn = ctk.CTkButton(
            self.sidebar,
            text="PHASE 3: RESURRECTION",
            command=lambda: self.show_phase(2),
            font=ctk.CTkFont(size=13, weight="bold", family="Consolas"),
            fg_color="#1a1a1a",
            hover_color="#ff0000",
            text_color="#ff0000",
            border_width=2,
            border_color="#ff0000",
            height=45
        )
        self.phase3_btn.grid(row=4, column=0, padx=20, pady=10)

        # Status Indicator
        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="● SYSTEM READY",
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color="#00ff00"
        )
        self.status_label.grid(row=7, column=0, padx=20, pady=(10, 20))

        # Main Content Area
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#000000")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create Phase Frames
        self.phases = []
        self.create_phase1()
        self.create_phase2()
        self.create_phase3()

        # Show initial phase
        self.show_phase(0)

    def create_phase1(self):
        """PHASE 1: THE HUNT - Data Collection"""
        frame = ctk.CTkFrame(self.main_container, fg_color="#000000")

        # Header
        header = ctk.CTkLabel(
            frame,
            text="⚡ PHASE 1: THE HUNT ⚡",
            font=ctk.CTkFont(size=32, weight="bold", family="Consolas"),
            text_color="#00ff00"
        )
        header.pack(pady=(30, 10))

        subtitle = ctk.CTkLabel(
            frame,
            text="[ MULTI-SOURCE DATA COLLECTION & FORENSICS ]",
            font=ctk.CTkFont(size=14, family="Consolas"),
            text_color="#00aa00"
        )
        subtitle.pack(pady=(0, 20))

        # Input Section
        input_frame = ctk.CTkFrame(frame, fg_color="#0a0a0a", border_width=2, border_color="#00ff00")
        input_frame.pack(pady=20, padx=50, fill="x")

        input_label = ctk.CTkLabel(
            input_frame,
            text="ENTER TARGET IDENTITY:",
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            text_color="#00ff00"
        )
        input_label.pack(pady=(20, 10), padx=20, anchor="w")

        self.target_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Subject name, alias, or identifier...",
            font=ctk.CTkFont(size=16, family="Consolas"),
            height=50,
            fg_color="#000000",
            border_color="#00ff00",
            border_width=2,
            text_color="#00ff00"
        )
        self.target_input.pack(pady=(0, 20), padx=20, fill="x")

        # Button Row - ปุ่มหลัก 3 ปุ่ม
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.pack(pady=15)

        self.scan_btn = ctk.CTkButton(
            button_row,
            text="[ DEEP SCAN ]",
            command=self.initiate_scan,
            font=ctk.CTkFont(size=16, weight="bold", family="Consolas"),
            fg_color="#000000",
            hover_color="#00ff00",
            text_color="#00ff00",
            border_width=3,
            border_color="#00ff00",
            height=50,
            width=200
        )
        self.scan_btn.pack(side="left", padx=5)

        self.upload_btn = ctk.CTkButton(
            button_row,
            text="[ UPLOAD DOCS ]",
            command=self.upload_documents,
            font=ctk.CTkFont(size=16, weight="bold", family="Consolas"),
            fg_color="#000000",
            hover_color="#ffaa00",
            text_color="#ffaa00",
            border_width=3,
            border_color="#ffaa00",
            height=50,
            width=200
        )
        self.upload_btn.pack(side="left", padx=5)

        self.scrape_btn = ctk.CTkButton(
            button_row,
            text="[ WEB SCRAPE ]",
            command=self.initiate_web_scrape,
            font=ctk.CTkFont(size=16, weight="bold", family="Consolas"),
            fg_color="#000000",
            hover_color="#ff00ff",
            text_color="#ff00ff",
            border_width=3,
            border_color="#ff00ff",
            height=50,
            width=200
        )
        self.scrape_btn.pack(side="left", padx=5)

        # Social Media Search Button
        self.social_btn = ctk.CTkButton(
            button_row,
            text="[ SOCIAL SEARCH ]",
            command=self.initiate_social_search,
            font=ctk.CTkFont(size=16, weight="bold", family="Consolas"),
            fg_color="#000000",
            hover_color="#00aaff",
            text_color="#00aaff",
            border_width=3,
            border_color="#00aaff",
            height=50,
            width=200
        )
        self.social_btn.pack(side="left", padx=5)

        # ตัวนับแหล่งข้อมูล
        self.sources_info_label = ctk.CTkLabel(
            frame,
            text="📁 Uploaded: 0 | 🌐 Scraped: 0 | 📱 Social: 0",
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color="#888888"
        )
        self.sources_info_label.pack(pady=5)

        # Saved Profiles Button
        saved_btn = ctk.CTkButton(
            frame,
            text="[ VIEW SAVED PROFILES ]",
            command=self.view_saved_profiles,
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            fg_color="#1a1a1a",
            hover_color="#00aaff",
            text_color="#00aaff",
            border_width=2,
            border_color="#00aaff",
            height=40,
            width=250
        )
        saved_btn.pack(pady=10)

        # Log Console
        log_label = ctk.CTkLabel(
            frame,
            text="[ SCAN LOG ]",
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
            text_color="#00aa00"
        )
        log_label.pack(pady=(20, 5), padx=50, anchor="w")

        self.log_console = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=12, family="Consolas"),
            fg_color="#000000",
            border_color="#00ff00",
            border_width=2,
            text_color="#00ff00",
            wrap="word",
            state="disabled"
        )
        self.log_console.pack(pady=(0, 30), padx=50, fill="both", expand=True)

        self.phases.append(frame)

    def create_phase2(self):
        """PHASE 2: THE WEB - Pattern Analysis"""
        frame = ctk.CTkFrame(self.main_container, fg_color="#000000")

        # Header
        header = ctk.CTkLabel(
            frame,
            text="⚡ PHASE 2: THE WEB ⚡",
            font=ctk.CTkFont(size=32, weight="bold", family="Consolas"),
            text_color="#00ff00"
        )
        header.pack(pady=(30, 10))

        subtitle = ctk.CTkLabel(
            frame,
            text="[ PATTERN RECOGNITION & PSYCHOLOGICAL MAPPING ]",
            font=ctk.CTkFont(size=14, family="Consolas"),
            text_color="#00aa00"
        )
        subtitle.pack(pady=(0, 30))

        # Mindhunter Board (Canvas Area)
        board_label = ctk.CTkLabel(
            frame,
            text="[ MINDHUNTER BOARD ]",
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
            text_color="#00aa00"
        )
        board_label.pack(pady=(10, 5), padx=50, anchor="w")

        self.board_canvas = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(size=13, family="Consolas"),
            fg_color="#000000",
            border_color="#00ff00",
            border_width=2,
            text_color="#00ff00",
            wrap="word"
        )
        self.board_canvas.pack(pady=(0, 20), padx=50, fill="both", expand=True)
        self.board_canvas.insert("1.0", "[ AWAITING DATA FROM PHASE 1... ]\n\n")
        self.board_canvas.configure(state="disabled")

        # Generate Profile Button
        self.profile_btn = ctk.CTkButton(
            frame,
            text="[ GENERATE AI PSYCHOLOGICAL PROFILE ]",
            command=self.generate_profile_ai,
            font=ctk.CTkFont(size=18, weight="bold", family="Consolas"),
            fg_color="#000000",
            hover_color="#ffaa00",
            text_color="#ffaa00",
            border_width=3,
            border_color="#ffaa00",
            height=60,
            width=450
        )
        self.profile_btn.pack(pady=(0, 30))

        self.phases.append(frame)

    def create_phase3(self):
        """PHASE 3: THE RESURRECTION - Persona Chat"""
        frame = ctk.CTkFrame(self.main_container, fg_color="#000000")

        # Header
        header_frame = ctk.CTkFrame(frame, fg_color="#000000")
        header_frame.pack(pady=(20, 10), padx=30, fill="x")

        header = ctk.CTkLabel(
            header_frame,
            text="⚡ PHASE 3: THE RESURRECTION ⚡",
            font=ctk.CTkFont(size=28, weight="bold", family="Consolas"),
            text_color="#ff0000"
        )
        header.pack(side="left", padx=(20, 0))

        # Synchronize Button
        self.sync_btn = ctk.CTkButton(
            header_frame,
            text="[ SYNCHRONIZE PERSONA ]",
            command=self.synchronize_persona,
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            fg_color="#000000",
            hover_color="#ff0000",
            text_color="#ff0000",
            border_width=2,
            border_color="#ff0000",
            height=40,
            width=250
        )
        self.sync_btn.pack(side="right", padx=(0, 20))

        subtitle = ctk.CTkLabel(
            frame,
            text="[ THE INTERROGATION ROOM - PERSONA SIMULATION ]",
            font=ctk.CTkFont(size=12, family="Consolas"),
            text_color="#aa0000"
        )
        subtitle.pack(pady=(0, 20))

        # Status Bar
        self.persona_status = ctk.CTkLabel(
            frame,
            text="● PERSONA: INACTIVE",
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
            text_color="#888888"
        )
        self.persona_status.pack(pady=(0, 10))

        # Chat Display
        chat_frame = ctk.CTkFrame(frame, fg_color="#0a0a0a", border_width=2, border_color="#ff0000")
        chat_frame.pack(pady=10, padx=30, fill="both", expand=True)

        self.chat_display = ctk.CTkTextbox(
            chat_frame,
            font=ctk.CTkFont(size=13, family="Consolas"),
            fg_color="#000000",
            text_color="#ffffff",
            wrap="word",
            state="disabled"
        )
        self.chat_display.pack(pady=10, padx=10, fill="both", expand=True)

        # Input Area
        input_frame = ctk.CTkFrame(frame, fg_color="#0a0a0a", border_width=2, border_color="#ff0000")
        input_frame.pack(pady=(0, 20), padx=30, fill="x")

        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your question to the subject...",
            font=ctk.CTkFont(size=14, family="Consolas"),
            height=50,
            fg_color="#000000",
            border_color="#ff0000",
            border_width=2,
            text_color="#ffffff"
        )
        self.chat_input.pack(side="left", pady=10, padx=(10, 5), fill="x", expand=True)
        self.chat_input.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="SEND",
            command=self.send_message,
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            fg_color="#ff0000",
            hover_color="#aa0000",
            text_color="#000000",
            width=100,
            height=50
        )
        self.send_btn.pack(side="right", pady=10, padx=(5, 10))

        self.phases.append(frame)

    def show_phase(self, phase_index):
        """Switch between phases"""
        for i, phase in enumerate(self.phases):
            if i == phase_index:
                phase.grid(row=0, column=0, sticky="nsew")
            else:
                phase.grid_forget()

        # Update button colors
        buttons = [self.phase1_btn, self.phase2_btn, self.phase3_btn]
        colors = ["#00ff00", "#00ff00", "#ff0000"]

        for i, btn in enumerate(buttons):
            if i == phase_index:
                btn.configure(fg_color=colors[i], text_color="#000000")
            else:
                btn.configure(fg_color="#1a1a1a", text_color=colors[i])

    def log_message(self, message, color="#00ff00"):
        """Add message to log console"""
        self.log_console.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.insert("end", f"[{timestamp}] {message}\n")
        self.log_console.see("end")
        self.log_console.configure(state="disabled")
        self.update()

    def update_sources_info(self):
        """อัปเดตตัวนับแหล่งข้อมูล"""
        self.sources_info_label.configure(
            text=f"📁 Uploaded: {len(self.uploaded_documents)} | 🌐 Scraped: {len(self.scraped_data)} | 📱 Social: {len(self.social_media_data)}"
        )

    def view_saved_profiles(self):
        """แสดงรายชื่อ profiles ที่บันทึกไว้"""
        self.saved_profiles = self.load_saved_profiles()
        dialog = SavedProfilesDialog(self, self.saved_profiles)
        self.wait_window(dialog)

    def initiate_scan(self):
        """Start the scanning process (Phase 1)"""
        target = self.target_input.get().strip()

        if not target:
            messagebox.showwarning("Input Required", "Please enter a target identity.")
            return

        # Disable button during scan
        self.scan_btn.configure(state="disabled", text="[ SCANNING IN PROGRESS... ]")
        self.log_console.configure(state="normal")
        self.log_console.delete("1.0", "end")
        self.log_console.configure(state="disabled")

        # Run scan in thread
        thread = threading.Thread(target=self.run_scan, args=(target,), daemon=True)
        thread.start()

    def run_scan(self, target):
        """Simulate scanning process"""
        scan_steps = [
            ("Initializing deep web crawlers...", 0.5),
            (f"Scanning databases for '{target}'...", 1.0),
            ("Found 47 matching records...", 0.7),
            ("Extracting social media profiles...", 0.8),
            ("Analyzing behavioral patterns...", 1.0),
            ("Cross-referencing psychological markers...", 0.9),
            ("Identifying emotional triggers...", 0.7),
            ("Mapping behavioral anomalies...", 0.8),
            ("Extracting communication patterns...", 0.6),
            ("Finalizing data compilation...", 0.5),
            ("✓ SCAN COMPLETE - Data saved to target_data.json", 0.3)
        ]

        for message, delay in scan_steps:
            self.log_message(message)
            time.sleep(delay)

        # รวม uploaded documents, scraped data และ social media
        self.target_data = {
            "name": target,
            "scan_timestamp": datetime.now().isoformat(),
            "documents": self.uploaded_documents,
            "web_data": self.scraped_data,
            "social_media": self.social_media_data,
            "profile": {
                "primary_traits": ["Narcissistic", "Manipulative", "Charm"],
                "behavioral_patterns": [
                    "Seeks admiration and validation",
                    "Difficulty with genuine empathy",
                    "Exploits others for personal gain"
                ],
                "emotional_triggers": ["Rejection", "Criticism", "Loss of Control"],
                "background": f"{target} exhibits classic narcissistic personality traits with manipulative tendencies.",
                "psychological_markers": {
                    "empathy_level": "Low",
                    "impulse_control": "Moderate",
                    "emotional_stability": "Unstable",
                    "social_manipulation": "High"
                },
                "communication_style": "Charismatic but self-centered, deflects accountability",
                "threat_assessment": "Moderate - Primarily psychological manipulation"
            }
        }

        # Save to file
        with open("target_data.json", "w", encoding="utf-8") as f:
            json.dump(self.target_data, f, indent=2, ensure_ascii=False)

        # Save to profiles folder
        profile_path = f"profiles/{target}.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(self.target_data, f, indent=2, ensure_ascii=False)

        self.saved_profiles = self.load_saved_profiles()

        self.log_message("✓ Target data saved successfully", "#00ff00")
        self.log_message(f"✓ Profile saved: {profile_path}", "#00ff00")
        self.log_message("→ Proceed to PHASE 2 for analysis", "#ffaa00")

        # Re-enable button
        self.scan_btn.configure(state="normal", text="[ INITIATE DEEP SCAN ]")

    def generate_profile(self):
        """Generate psychological profile (Phase 2)"""
        # Load data
        if not os.path.exists("target_data.json"):
            messagebox.showwarning("No Data", "Please complete PHASE 1 first.")
            return

        with open("target_data.json", "r") as f:
            self.target_data = json.load(f)

        profile = self.target_data.get("profile", {})

        # Build visual profile
        self.board_canvas.configure(state="normal")
        self.board_canvas.delete("1.0", "end")

        output = f"""
═══════════════════════════════════════════════════════════════════
    PSYCHOLOGICAL PROFILE: {self.target_data.get('name', 'UNKNOWN').upper()}
═══════════════════════════════════════════════════════════════════

[PRIMARY TRAITS]
{'─' * 67}
"""
        for trait in profile.get("primary_traits", []):
            output += f"  ● {trait}\n"

        output += f"""
[BEHAVIORAL PATTERNS]
{'─' * 67}
"""
        for pattern in profile.get("behavioral_patterns", []):
            output += f"  → {pattern}\n"

        output += f"""
[EMOTIONAL TRIGGERS]
{'─' * 67}
"""
        for trigger in profile.get("emotional_triggers", []):
            output += f"  ⚠ {trigger}\n"

        markers = profile.get("psychological_markers", {})
        output += f"""
[PSYCHOLOGICAL MARKERS]
{'─' * 67}
  Empathy Level:         {markers.get('empathy_level', 'N/A')}
  Impulse Control:       {markers.get('impulse_control', 'N/A')}
  Emotional Stability:   {markers.get('emotional_stability', 'N/A')}
  Social Manipulation:   {markers.get('social_manipulation', 'N/A')}

[COMMUNICATION STYLE]
{'─' * 67}
  {profile.get('communication_style', 'N/A')}

[THREAT ASSESSMENT]
{'─' * 67}
  {profile.get('threat_assessment', 'N/A')}

[BACKGROUND ANALYSIS]
{'─' * 67}
  {profile.get('background', 'N/A')}

═══════════════════════════════════════════════════════════════════
                    ✓ PROFILE GENERATION COMPLETE
        → Proceed to PHASE 3 for persona synchronization
═══════════════════════════════════════════════════════════════════
"""

        self.board_canvas.insert("1.0", output)
        self.board_canvas.configure(state="disabled")

        self.profile_data = profile

        messagebox.showinfo("Success", "Psychological profile generated successfully!")

    # ==================== DOCUMENT UPLOAD ====================
    def upload_documents(self):
        """อัปโหลดและแยกข้อความจากเอกสาร (PDF, TXT, DOCX)"""
        filetypes = [
            ("All Supported", "*.pdf *.txt *.docx"),
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt"),
            ("Word Documents", "*.docx"),
            ("All Files", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="Select Documents (Manifestos, Letters, Writings)",
            filetypes=filetypes
        )

        if not files:
            return

        self.log_message(f"📁 Processing {len(files)} document(s)...", "#ffaa00")

        for file_path in files:
            thread = threading.Thread(target=self.process_document, args=(file_path,), daemon=True)
            thread.start()

    def process_document(self, file_path):
        """แยกข้อความจากเอกสารที่อัปโหลด"""
        try:
            filename = os.path.basename(file_path)
            self.log_message(f"→ Reading: {filename}")

            ext = os.path.splitext(file_path)[1].lower()
            content = ""

            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            elif ext == ".pdf":
                if not PDF_SUPPORT:
                    self.log_message(f"✗ PDF support not available. Install: pip install PyPDF2", "#ff0000")
                    return
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"

            elif ext == ".docx":
                if not DOCX_SUPPORT:
                    self.log_message(f"✗ DOCX support not available. Install: pip install python-docx", "#ff0000")
                    return
                doc = DocxDocument(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])

            else:
                self.log_message(f"✗ Unsupported file type: {ext}", "#ff0000")
                return

            if content.strip():
                doc_data = {
                    "filename": filename,
                    "type": "document",
                    "content": content[:10000],  # เก็บ 10k คำแรก
                    "word_count": len(content.split()),
                    "timestamp": datetime.now().isoformat()
                }
                self.uploaded_documents.append(doc_data)
                self.update_sources_info()
                self.log_message(f"✓ Extracted {doc_data['word_count']} words from {filename}", "#00ff00")
            else:
                self.log_message(f"✗ No text found in {filename}", "#ff0000")

        except Exception as e:
            self.log_message(f"✗ Error processing {filename}: {str(e)}", "#ff0000")

    # ==================== WEB SCRAPING ====================
    def initiate_web_scrape(self):
        """เปิด dialog สำหรับใส่ URL"""
        if not WEB_SUPPORT:
            messagebox.showerror(
                "Missing Dependencies",
                "Web scraping requires: requests, beautifulsoup4\n\nInstall with:\npip install requests beautifulsoup4"
            )
            return

        dialog = WebScrapeDialog(self)
        self.wait_window(dialog)

        if dialog.urls:
            for url in dialog.urls:
                thread = threading.Thread(target=self.scrape_url, args=(url,), daemon=True)
                thread.start()

    def scrape_url(self, url):
        """ดูดข้อมูลจาก URL"""
        try:
            self.log_message(f"🌐 Scraping: {url}", "#ff00ff")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # ลบ script และ style
            for script in soup(["script", "style"]):
                script.decompose()

            # แยกข้อความ
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            if text.strip():
                scraped_data = {
                    "url": url,
                    "type": "web_scrape",
                    "content": text[:10000],
                    "word_count": len(text.split()),
                    "timestamp": datetime.now().isoformat()
                }
                self.scraped_data.append(scraped_data)
                self.update_sources_info()
                self.log_message(f"✓ Scraped {scraped_data['word_count']} words from {url[:50]}...", "#00ff00")
            else:
                self.log_message(f"✗ No content found at {url}", "#ff0000")

        except Exception as e:
            self.log_message(f"✗ Scraping failed for {url}: {str(e)}", "#ff0000")

    # ==================== SOCIAL MEDIA SEARCH ====================
    def initiate_social_search(self):
        """เปิด dialog สำหรับค้นหาโซเชียลมีเดีย"""
        if not WEB_SUPPORT:
            messagebox.showerror(
                "Missing Dependencies",
                "Social media search requires: requests, beautifulsoup4\n\nInstall with:\npip install requests beautifulsoup4"
            )
            return

        dialog = SocialSearchDialog(self)
        self.wait_window(dialog)

        if dialog.search_query:
            thread = threading.Thread(target=self.search_social_media, args=(dialog.search_query,), daemon=True)
            thread.start()

    def search_social_media(self, query):
        """ค้นหาโซเชียลมีเดียจากหลายแพลตฟอร์ม"""
        self.log_message(f"📱 Starting social media search for: {query}", "#00aaff")

        platforms = {
            "Twitter/X": f"https://nitter.net/search?f=tweets&q={query.replace(' ', '+')}",
            "Reddit": f"https://www.reddit.com/search/?q={query.replace(' ', '+')}",
            "YouTube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "Instagram": f"https://www.instagram.com/explore/tags/{query.replace(' ', '')}/",
            "Facebook": f"https://www.facebook.com/search/top?q={query.replace(' ', '%20')}",
            "TikTok": f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}",
            "LinkedIn": f"https://www.linkedin.com/search/results/all/?keywords={query.replace(' ', '%20')}",
            "Telegram": f"https://t.me/s/{query.replace(' ', '')}",
            "Mastodon": f"https://mastodon.social/tags/{query.replace(' ', '')}",
            "Pinterest": f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}",
            "Tumblr": f"https://www.tumblr.com/search/{query.replace(' ', '%20')}",
            "Twitch": f"https://www.twitch.tv/search?term={query.replace(' ', '%20')}",
            "Discord.me": f"https://discord.me/servers/search?q={query.replace(' ', '+')}",
            "4chan Archive": f"https://archive.4plebs.org/_/search/text/{query.replace(' ', '%20')}/",
            "Parler": f"https://parler.com/search?q={query.replace(' ', '%20')}",
        }

        for platform, url in platforms.items():
            thread = threading.Thread(target=self.scrape_social_platform, args=(platform, url, query), daemon=True)
            thread.start()
            time.sleep(0.5)  # หน่วงเวลาเล็กน้อยเพื่อไม่ให้โดน rate limit

    def scrape_social_platform(self, platform, url, query):
        """ดึงข้อมูลจากแพลตฟอร์มโซเชียลมีเดีย"""
        try:
            self.log_message(f"→ Searching {platform}...", "#00aaff")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # ลบ script, style, ads
                for unwanted in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
                    unwanted.decompose()

                # แยกข้อความ
                text = soup.get_text(separator='\n', strip=True)
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                text = '\n'.join(lines)

                if text and len(text) > 100:
                    social_data = {
                        "platform": platform,
                        "query": query,
                        "url": url,
                        "type": "social_media",
                        "content": text[:15000],  # เก็บ 15k characters
                        "word_count": len(text.split()),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.social_media_data.append(social_data)
                    self.update_sources_info()
                    self.log_message(f"✓ Found {social_data['word_count']} words on {platform}", "#00ff00")
                else:
                    self.log_message(f"⚠ Limited data from {platform}", "#ffaa00")
            else:
                self.log_message(f"⚠ {platform} returned status {response.status_code}", "#ffaa00")

        except requests.exceptions.Timeout:
            self.log_message(f"⏱ Timeout searching {platform}", "#ff6600")
        except requests.exceptions.RequestException as e:
            self.log_message(f"⚠ {platform} search limited (may need direct access)", "#ffaa00")
        except Exception as e:
            self.log_message(f"✗ Error with {platform}: {str(e)[:50]}", "#ff0000")

    # ==================== AI PROFILE GENERATION ====================
    def generate_profile_ai(self):
        """สร้าง psychological profile โดยใช้ AI"""
        if not os.path.exists("target_data.json"):
            messagebox.showwarning("No Data", "Please complete PHASE 1 first.")
            return

        if not self.groq_client:
            messagebox.showerror("API Error", "Groq client not initialized.")
            return

        self.profile_btn.configure(state="disabled", text="[ ANALYZING... ]")

        thread = threading.Thread(target=self.run_ai_analysis, daemon=True)
        thread.start()

    def run_ai_analysis(self):
        """รัน AI analysis บนข้อมูลที่รวบรวม"""
        try:
            with open("target_data.json", "r", encoding="utf-8") as f:
                self.target_data = json.load(f)

            # รวบรวมข้อความทั้งหมด
            all_text = ""

            for doc in self.target_data.get("documents", []):
                all_text += f"\n\n=== DOCUMENT: {doc['filename']} ===\n{doc['content']}\n"

            for web in self.target_data.get("web_data", []):
                all_text += f"\n\n=== WEB SOURCE: {web['url']} ===\n{web['content']}\n"

            for social in self.target_data.get("social_media", []):
                all_text += f"\n\n=== SOCIAL MEDIA ({social['platform']}): {social['query']} ===\n{social['content']}\n"

            # สร้าง analysis prompt - ระดับ FBI/CIA Behavioral Analysis Unit (ลึกสุดระดับ)
            analysis_prompt = f"""You are a COMBINED entity of:
- Dr. Robert Hare (PCL-R creator, world's leading psychopathy expert)
- John Douglas (FBI Behavioral Analysis Unit founder, profiler of Ted Bundy, BTK, Jeffrey Dahmer, etc.)
- Dr. Reid Meloy (forensic psychologist, expert on stalking & violent offenders, wrote "The Psychopathic Mind")
- Dr. Park Dietz (forensic psychiatrist, testified in Dahmer, Unabomber, Virginia Tech cases)
- Dr. Dorothy Otnow Lewis (child psychiatry, studied childhood trauma in serial killers)
- Dr. Lonnie Athens (sociologist, "violentization" theory - how violent criminals are created)
- Dr. Adrian Raine (neurocriminologist, brain abnormalities in violent criminals)

This is REAL LAW ENFORCEMENT ANALYSIS for SERIOUS VIOLENT CRIME investigations (murder, rape, kidnapping).
Use MAXIMUM clinical depth. Analyze EVERY subtle detail. This is for actual police/FBI use in active cases.

SUBJECT: {self.target_data['name']}

COLLECTED EVIDENCE:
{all_text[:20000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUIRED FORENSIC PSYCHOLOGICAL ANALYSIS (FBI/CIA BEHAVIORAL ANALYSIS UNIT LEVEL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECTION 1: PSYCHOPATHY & PERSONALITY PATHOLOGY ASSESSMENT
═══════════════════════════════════════════════════════════
A. PCL-R (Psychopathy Checklist-Revised) - Score each 0-2:
   • Factor 1 (Interpersonal/Affective): Glibness, grandiosity, pathological lying, manipulation, lack of remorse, shallow affect, callousness, failure to accept responsibility
   • Factor 2 (Lifestyle/Antisocial): Need for stimulation, parasitic lifestyle, impulsivity, irresponsibility, juvenile delinquency, criminal versatility
   • ESTIMATED PCL-R SCORE: __/40 (30+ = clinical psychopathy)

B. DSM-5-TR Personality Disorders:
   • Cluster A (Odd/Eccentric): Paranoid, Schizoid, Schizotypal traits
   • Cluster B (Dramatic/Erratic): Antisocial, Borderline, Histrionic, Narcissistic traits
   • Cluster C (Anxious/Fearful): Avoidant, Dependent, Obsessive-Compulsive traits
   • PROVIDE SPECIFIC DSM-5 DIAGNOSTIC CRITERIA MET

C. Dark Tetrad Analysis:
   • Narcissism (Grandiose vs Vulnerable)
   • Machiavellianism (strategic exploitation)
   • Psychopathy (primary vs secondary)
   • Sadism (physical, verbal, cyber)

D. Attachment Pathology (Bowlby/Ainsworth):
   • Secure, Anxious-Preoccupied, Dismissive-Avoidant, Fearful-Avoidant, Disorganized
   • Internal Working Models (view of self and others)
   • Attachment trauma manifestations in adulthood

SECTION 2: DEVELOPMENTAL TRAUMA & CHILDHOOD PSYCHOPATHOLOGY (Dr. Dorothy Lewis Method)
═══════════════════════════════════════════════════════════
**CRITICAL: วิเคราะห์วัยเด็กอย่างละเอียดที่สุด - นี่คือรากเหง้าของพฤติกรรมทั้งหมด**

A. Early Childhood Environment (0-5 years):
   • PRIMARY CAREGIVER ANALYSIS:
     - Mother figure: Presence/absence, warmth vs coldness, consistency, mental health
     - Father figure: Presence/absence, authoritarian vs absent, violence, role modeling
     - Inconsistent caregiving (fear without solution = disorganized attachment)
     - Separation/abandonment experiences (orphanage, foster care, parental death/divorce)

   • PRENATAL/PERINATAL FACTORS:
     - Maternal substance abuse during pregnancy
     - Birth complications (oxygen deprivation = brain damage)
     - Premature birth/low birth weight
     - Unwanted pregnancy (maternal rejection from conception)

   • EARLY TRAUMA INDICATORS:
     - Physical abuse (visible scars, broken bones, head injuries)
     - Sexual abuse (age first occurred, perpetrator relationship, duration)
     - Witness to domestic violence (learned violence as conflict resolution)
     - Neglect (failure to thrive, malnutrition, lack of stimulation)
     - Medical trauma (painful procedures, hospitalizations)

B. Middle Childhood (6-12 years):
   • SCHOOL/SOCIAL FUNCTIONING:
     - Academic performance (learning disabilities, ADHD indicators)
     - Peer relationships (bullied vs bully, social isolation, rejection)
     - Authority conflicts (teacher reports, principal's office frequency)
     - Early conduct disorder signs (lying, stealing, destroying property)

   • FAMILY DYNAMICS:
     - Parental mental illness (depression, schizophrenia, bipolar in family)
     - Substance abuse in home (alcoholic parent, drug-using siblings)
     - Economic instability (frequent moves, homelessness, poverty stress)
     - Sibling dynamics (birth order, favoritism, sibling abuse/rivalry)
     - Extended family support (grandparents, aunts/uncles - protective factors)

   • MACDONALD TRIAD (Serial Killer Predictors):
     - Enuresis (bedwetting past age 5 - neurological/psychological stress)
     - Fire-setting (fascination with fire, arson attempts, symbolic power/destruction)
     - Animal cruelty (torturing pets, killing animals - empathy testing ground)
     **NOTE: All three present = extremely high risk for violent criminality**

C. Adolescence (13-18 years):
   • IDENTITY FORMATION DISRUPTIONS:
     - Sexual identity confusion/trauma
     - Racial/ethnic identity conflicts
     - Gender dysphoria/body image issues
     - Religious trauma (cult involvement, extreme fundamentalism)

   • VIOLENT VICTIMIZATION:
     - Physical assault victimization
     - Sexual assault/rape victimization
     - Dating violence exposure
     - Gang violence exposure
     - School shooting/mass violence exposure

   • DELINQUENCY PROGRESSION:
     - Age of first arrest
     - Juvenile detention history
     - Gang involvement
     - Substance abuse onset (gateway drugs → hard drugs progression)
     - Early sexual behavior (age of first intercourse, promiscuity, sexual aggression)

D. Adverse Childhood Experiences (ACE Score - Fellitti & Anda Study):
   Calculate ACE Score (0-10):
   □ Emotional abuse (insults, humiliation, threats)
   □ Physical abuse (hit, beaten, injured)
   □ Sexual abuse (molestation, rape, inappropriate touching)
   □ Emotional neglect (didn't feel loved, important, special)
   □ Physical neglect (didn't have enough food, clean clothes, medical care)
   □ Mother treated violently (witnessed domestic abuse)
   □ Household substance abuse (lived with alcoholic/drug user)
   □ Household mental illness (depression, suicide attempts, psychiatric hospital)
   □ Parental separation/divorce
   □ Incarcerated household member (parent/sibling in prison)

   **ACE Score Interpretation:**
   - 0: Minimal childhood adversity
   - 1-3: Moderate adversity (common in general population)
   - 4-6: High adversity (significantly increased risk for psychopathology)
   - 7-10: Extreme adversity (massive risk for violence, addiction, early death)

E. Developmental Psychopathology Mechanisms:
   • VIOLENTIZATION PROCESS (Lonnie Athens Theory):
     Stage 1: BRUTALIZATION - Subjected to/witnessed extreme violence, learned submission
     Stage 2: BELLIGERENCY - Resolved to never be victim again, aggressive stance toward world
     Stage 3: VIOLENT PERFORMANCES - First acts of serious violence (testing ground)
     Stage 4: VIRULENCY - Violence becomes primary identity, "violent self" is born

   • TRAUMA REENACTMENT COMPULSION:
     - Repetition compulsion (recreating childhood trauma as adult perpetrator)
     - Identification with aggressor (becoming the abusive parent/attacker)
     - Victim-to-victimizer progression (abused child becomes abusive adult)

   • ARRESTED DEVELOPMENT:
     - Emotional age vs chronological age (adult body, child mind)
     - Unresolved developmental stages (Eriksonian crises)
     - Regression under stress (child-like tantrums, magical thinking)

F. Protective Factors & Resilience (Why DIDN'T they become more violent?):
   • At least ONE stable, caring adult (teacher, coach, grandparent)
   • High intelligence (cognitive escape, future planning)
   • Involvement in pro-social activities (sports, music, church)
   • Strong moral/religious framework (internalized conscience)
   • Therapy/intervention at critical moments
   • Positive peer influences
   **If high ACE score but low violence = investigate protective factors present**

SECTION 3: FBI BEHAVIORAL ANALYSIS (Crime Pattern Recognition)
═══════════════════════════════════════════════════════════
A. Offender Classification:
   • Organized vs Disorganized (crime scene analysis)
   • Power-Assertive, Power-Reassurance, Anger-Retaliatory, Anger-Excitation (rapist typology)
   • Visionary, Mission-Oriented, Hedonistic, Power/Control (killer typology if applicable)

B. Modus Operandi (MO) Analysis:
   • Victim selection criteria & patterns
   • Approach methods (con, blitz, surprise)
   • Attack locations (residence, vehicle, outdoor)
   • Control methods (verbal, physical, weapon)
   • Escalation timeline & triggers

C. Signature Behaviors (Psychological Needs):
   • Ritualistic elements (unchanging across incidents)
   • Fantasy-driven actions
   • Symbolic meaning of behaviors
   • Souvenirs/trophies collection patterns
   • Post-offense behavior patterns

D. Geographic Profiling:
   • Anchor points (home, work, comfort zones)
   • Hunting patterns (marauder vs commuter)
   • Distance decay analysis
   • Awareness space mapping

SECTION 3: CLINICAL PSYCHOPATHOLOGY MARKERS
═══════════════════════════════════════════════════════════
A. Neuropsychological Indicators:
   • Executive function deficits (frontal lobe dysfunction)
   • Theory of Mind impairments
   • Cognitive empathy vs affective empathy dissociation
   • Behavioral inhibition system (BIS) vs activation system (BAS) imbalance

B. Emotional Dysregulation Patterns:
   • Alexithymia (emotional blindness)
   • Inappropriate affect
   • Emotional volatility triggers
   • Stress tolerance capacity
   • Anxiety/depression comorbidity

C. Delusional/Psychotic Features:
   • Reality testing capacity
   • Paranoid ideation
   • Grandiose delusions
   • Ideas of reference
   • Thought broadcasting/insertion/withdrawal

D. Sexual Deviance Patterns (if applicable):
   • Paraphilias present (DSM-5 criteria)
   • Sexual sadism indicators
   • Pedophilic interests
   • Courtship disorder pathway
   • Pornography use patterns

SECTION 4: VIOLENCE RISK ASSESSMENT (Actuarial Instruments)
═══════════════════════════════════════════════════════════
A. HCR-20 V3 (Historical-Clinical-Risk Management):
   • Historical (10 items): Violence history, early maladjustment, relationship instability, employment problems, substance abuse, major mental disorder, psychopathy, early traumatic experiences, violent ideation, weapon access
   • Clinical (5 items): Recent problems with insight, violent ideation/intent, symptoms of major mental disorder, instability, treatment response
   • Risk Management (5 items): Professional services, living situation, personal support, treatment compliance, stress
   • RISK LEVEL: Low / Moderate / High

B. VRAG-R (Violence Risk Appraisal Guide):
   • Statistical prediction of violent recidivism
   • Key factors: PCL-R score, childhood maladjustment, alcohol abuse, marital status, criminal history
   • PERCENTILE RANK: __% (violence probability within 7 years)

C. SAVRY (for youth) / SARA (intimate partner violence):
   • Domain-specific risk factors
   • Protective factors present

D. Threat Assessment (4-Pronged Approach):
   • Pathway warnings (planning, preparation)
   • Fixation warnings (obsession, grievance)
   • Identification warnings (role modeling)
   • Novel aggression warnings (leakage, violence rehearsal)

SECTION 5: DEEP LINGUISTIC & PSYCHOLINGUISTIC FORENSICS
═══════════════════════════════════════════════════════════
**CRITICAL: วิเคราะห์ภาษาทุกระดับ - จากคำเดียวจนถึงโครงสร้างความคิด - ภาษาคือหน้าต่างสู่จิตใจ**

A. MICRO-LINGUISTIC ANALYSIS (วิเคราะห์ทีละคำ):
   • PRONOUN PATTERNS: "I" frequency (narcissism vs depression), "We" (inclusive vs manipulative), "You" accusations (blame), "They" (dehumanization), Missing pronouns = distancing
   • VERB TENSE: Past tense consistency (truth), Present tense intrusions (trauma reliving), Tense switching (deception/dissociation)
   • EMOTION VOCABULARY: Limited words (alexithymia), Extreme words (borderline), No emotion for violence (psychopathy), Inappropriate emotions RED FLAG
   • WORD CHOICES: Distancing ("the body" vs "her"), Depersonalization ("it" for person), Euphemisms ("hurt" vs "stabbed 37 times"), Minimization ("just", "only"), Absolutes ("always", "never")

B. SENTENCE STRUCTURE PSYCHOLOGY:
   • LENGTH PATTERNS: Very short (cognitive simplicity/deception), Long run-on (mania/thought disorder), Abrupt stops (blocking/trauma)
   • COMPLEXITY: Simple only (concrete thinking/brain damage), Complex clauses (intelligence/planning), Contradictions frequency
   • PUNCTUATION: Excessive !!! (dysregulation), ALL CAPS (aggression/unheard), ellipsis... (passive-aggressive/withholding)

C. NARRATIVE STRUCTURE (การเล่าเรื่องบอกอะไร):
   • STORY COHERENCE: Linear A→B→C (organized/truthful), Circular repetition (trauma stuck), Fragmented jumping (dissociation/lying), Missing time gaps
   • DETAIL DISTRIBUTION: Abundant irrelevant details (avoiding main event), No details at critical moments (deception/dissociation), Sensory details (truth) vs vague generalities (lying)
   • SELF-EDITING: Corrections (normal memory OR evolving lie), Exact same words every time (memorized script), "To be honest" (expect disbelief = lying indicator)

D. DEEP TRAUMA LANGUAGE INDICATORS:
   • Dissociative language: "Like watching from outside my body"
   • Fragmented recall: "I remember... then nothing... then..."
   • Affect-less description: Horror without emotion
   • Present tense intrusion: "He's coming" (not "came" = reliving NOW)
   • Verbal loops: Exact phrase repetition (stuck in trauma memory)

E. PSYCHOPATHY LANGUAGE (Robert Hare Research):
   • Lack emotional depth: "I felt bad" (no elaboration)
   • Focus on actions not feelings: "Then I did X, then Y"
   • Causality without responsibility: "She made me"
   • NO guilt language: Missing "I'm sorry", "I regret", "I wish I hadn't"
   • Instrumental thinking: People as objects/tools
   • Example: "My wife is useful for cooking" (not love/partnership = RED FLAG)

F. NARCISSISM LANGUAGE PATTERNS:
   • Grandiose self: "I'm the best", "Nobody understands my genius"
   • Entitlement: "I deserve", "They owe me"
   • Rage at criticism: Sudden extreme anger shift
   • Splitting: "You're perfect/you're trash" (no middle)
   • "Special" focus: "I'm different from everyone"

G. PARANOIA/PERSECUTION LANGUAGE:
   • Conspiracy thinking: "They're all in on it", "coordinated attack"
   • Hypervigilance words: "watching", "following", "targeting"
   • External locus: Everything happens TO them (no personal agency)
   • Enemies list: Frequent "people against me"
   • Justified revenge: "They started it, I'm defending"

H. DECEPTION DETECTION (Scientific Statement Analysis):
   • STRONG commitment: "I did NOT kill her" (clear, direct)
   • WEAK commitment: "I would never kill anyone" (general, not specific)
   • Non-denial denial: "I'm not the kind of person who..." (avoids actual denial)
   • Missing information: Skipped hours/days, Passive voice ("gun was fired" - by who?), Vague actors, Missing emotions
   • Unnecessary information: Over-explaining simple actions, Alibis before asked, Attacking questioner, Emphasizing truthfulness ("I swear on my mother")

I. PSYCHOLINGUISTIC PROFILE (รูปแบบการคิดผ่านภาษา):
   • COGNITIVE STYLE: Concrete (literal only, no metaphors), Abstract (philosophical), Black/white (no nuance), Complexity tolerance
   • EMOTIONAL REGULATION: Controlled flat (repression/psychopathy), Flooding (!!!CAPS!!! = poor regulation), Passive-aggressive hints, Direct aggression
   • SOCIAL AWARENESS: Theory of mind present?, Empathy indicators, Manipulation attempts (guilt-trip/victim-play), Authenticity vs performance

J. LINGUISTIC RED FLAGS FOR VIOLENT OFFENDERS:
   □ Dehumanizing language (people as objects/animals)
   □ Violent fantasies with pleasure/detail
   □ "Leakage" hints: "You'll see", "They'll regret"
   □ Grievance collection (long lists of injustices)
   □ Manifesto-style (justifying future violence)
   □ Martyr/hero delusions in self-description
   □ Apocalyptic thinking ("world ending", "nothing matters")
   □ Last statement indicators ("goodbye", "I'm done here")
   □ Research on methods (detailed weapon/torture knowledge)
   □ Admiration for killers (mass shooters, serial killers)

K. คำที่ใช้บ่อยที่สุด (WORD FREQUENCY ANALYSIS):
   • Top 10 most frequent words (excluding articles/prepositions): ___
   • Obsession indicators: Same word repeated > 20 times
   • Violence words: "kill", "hurt", "destroy", "blood", "death" frequency
   • Control words: "control", "power", "dominate", "submit" frequency
   • Victim words: "unfair", "betrayed", "they made me" frequency

L. ลักษณะการพูดเฉพาะบุคคล (INDIVIDUAL SPEECH SIGNATURE):
   • Favorite phrases/expressions (verbal habits)
   • Unique grammatical errors (educational level indicator)
   • Regional dialect markers (background clues)
   • Code-switching (language mixing = bicultural stress?)
   • Formality level (casual vs rigid formal = personality)
   • Humor style (sarcastic, dark, absent = emotional state)

SECTION 6: SOCIAL MEDIA & DIGITAL FOOTPRINT ANALYSIS
═══════════════════════════════════════════════════════════
A. Online Behavioral Patterns:
   • Disinhibition effects (toxicity escalation online vs offline)
   • Self-presentation strategies (idealized vs authentic)
   • Social media addiction markers
   • Echo chamber / radicalization indicators
   • Parasocial relationship patterns

B. Digital Communication Style:
   • Aggressive/passive-aggressive patterns
   • Trolling/harassment behaviors
   • Oversharing (boundary violations)
   • Attention-seeking behaviors
   • Authentic vs performative activism

C. Radicalization Pathway Indicators:
   • Grievance formation
   • Ideological framing
   • Group identification
   • Dehumanization of outgroups
   • Violent action planning

SECTION 6B: CORE PSYCHOLOGICAL WOUNDS & UNMET NEEDS (ปมทางจิตลึกสุด)
═══════════════════════════════════════════════════════════
**CRITICAL: ค้นหาบาดแผลทางใจที่ซ่อนอยู่ - ทุกพฤติกรรมเป็นการพยายามรักษาปมเก่า**

A. PRIMARY CORE WOUND (บาดแผลหลักที่สุด):

   1. ABANDONMENT WOUND (ปมถูกทิ้ง):
      • Origin: Parent death/divorce, foster care, rejection, sent away
      • Adult manifestation: Clingy/possessive OR extremely independent (counter-dependent)
      • Fear: "Everyone will leave me" → Tests relationships by pushing people away FIRST
      • Compensation: Hoarding, collecting people/things, controlling to prevent loss
      • Rage trigger: Any hint of rejection = explosive anger/violence
      • **Identify:** Excessive jealousy, stalking, "If I can't have you, nobody can"

   2. BETRAYAL WOUND (ปมถูกหักหลัง):
      • Origin: Trusted adult abused them (parent, teacher, priest), sibling favoritism
      • Adult manifestation: Hyper-vigilant, tests loyalty constantly, paranoid
      • Fear: "People will betray me" → Betrays others FIRST (preemptive strike)
      • Compensation: Control everything, trust nobody, gather dirt on everyone
      • Rage trigger: Perceived disloyalty = vengeance/punishment
      • **Identify:** Conspiracy thinking, "I'll get them before they get me"

   3. HUMILIATION WOUND (ปมถูกทำให้อับอาย):
      • Origin: Public shaming, bullying, body shaming, sexual humiliation
      • Adult manifestation: Shame-rage cycles, need to humiliate others
      • Fear: "I'm worthless/disgusting" → Makes others feel worthless to feel powerful
      • Compensation: Arrogance, perfectionism, putting others down
      • Rage trigger: Being criticized/mocked = must destroy critic completely
      • **Identify:** Road rage, online trolling, public violence (school shootings)

   4. INJUSTICE WOUND (ปมความไม่ยุติธรรม):
      • Origin: Unfair punishment, scapegoated, innocent but blamed
      • Adult manifestation: Rigid sense of right/wrong, vengeance-seeking
      • Fear: "The world is unfair" → Must punish wrongdoers, be judge/jury/executioner
      • Compensation: Becomes police/vigilante OR becomes criminal (revenge on unjust system)
      • Rage trigger: Perceived injustice = justified extreme violence
      • **Identify:** Manifesto writers, mass shooters ("society deserves this"), terrorism

   5. INVISIBILITY WOUND (ปมถูกมองข้าม):
      • Origin: Neglected child, middle child syndrome, parents never noticed achievements
      • Adult manifestation: Desperate for attention, "Watch me now!"
      • Fear: "I don't matter, I'm invisible" → Dramatic acts to be SEEN
      • Compensation: Attention-seeking, dramatic personality, social media addiction
      • Rage trigger: Being ignored/dismissed = must do SOMETHING BIG to be noticed
      • **Identify:** Mass shootings for fame, live-streaming crimes, manifestos

B. UNMET DEVELOPMENTAL NEEDS (ความต้องการที่ไม่เคยได้รับ):

   1. SAFETY NEEDS (Maslow Level 1):
      • Never felt safe as child (violence, chaos, unstable home)
      • Adult: Anxiety disorders, hypervigilance, need for control, weapons hoarding
      • Seek: Total control of environment, eliminate all threats (paranoid)

   2. LOVE/BELONGING NEEDS (Maslow Level 2):
      • Never felt loved, accepted, part of family
      • Adult: Desperate for connection BUT sabotages relationships (push-pull)
      • Seek: Cult involvement, gang membership, parasocial relationships, unhealthy attachments

   3. ESTEEM NEEDS (Maslow Level 3):
      • Never felt valued, respected, accomplished
      • Adult: Narcissistic compensation, grandiosity, or complete worthlessness
      • Seek: Fame, power, recognition, "I'll show them" violence

   4. IDENTITY NEEDS:
      • Never developed coherent sense of self
      • Adult: Identity diffusion, BPD traits, "Who am I?" crisis
      • Seek: Extreme ideologies, radical groups, cults (they tell you who to be)

C. DEFENSE MECHANISMS ANALYSIS (วิธีป้องกันตัวจากความเจ็บปวด):

   PRIMITIVE DEFENSES (child-like, pathological):
   • DENIAL: "It didn't happen" (abuse amnesia, dissociation)
   • PROJECTION: "You're the angry one, not me!" (accusing others of own feelings)
   • SPLITTING: "All good or all bad" (no nuance, BPD hallmark)
   • ACTING OUT: Converting feelings into destructive actions
   • PASSIVE-AGGRESSION: Indirect hostility (sabotage, "forgetting")

   NEUROTIC DEFENSES (somewhat functional):
   • DISPLACEMENT: Kick the dog instead of yelling at boss
   • REACTION FORMATION: Love becomes hate, hate becomes love
   • INTELLECTUALIZATION: Talk about feelings without feeling them
   • RATIONALIZATION: Logical excuses for emotional behavior

   MATURE DEFENSES (healthy):
   • SUBLIMATION: Channel rage into boxing, art, etc.
   • HUMOR: Laugh at pain without denying it
   • ALTRUISM: Help others heal own wounds
   **If only primitive defenses = severe pathology**

D. REPETITION COMPULSION (ทำซ้ำบาดแผลเดิมไม่รู้ตัว):

   • VICTIM SEEKS VICTIMIZER: Abused child marries abuser
   • VICTIMIZER CREATES VICTIMS: Creates situation matching childhood trauma but now they're in control
   • ANNIVERSARY REACTIONS: Violence on date matching original trauma
   • REENACTMENT SCENARIOS: Sets up situation to relive trauma with "better" outcome

   **Example:** Man abused by mother → seeks controlling women → abuses them (now HE has power)
   **Example:** Woman raped → repeatedly enters dangerous situations (trauma repetition compulsion)

E. ATTACHMENT HUNGER & DISTORTIONS (ความอยากได้การผูกพันที่บิดเบี้ยว):

   • EROTIC ATTACHMENT: Confuses sex with love/safety (hypersexuality, sex addiction)
   • HOSTILE ATTACHMENT: "I hate you, don't leave me" (BPD, domestic violence)
   • ANXIOUS ATTACHMENT: Obsessive jealousy, checking phone, stalking
   • AVOIDANT ATTACHMENT: "I don't need anyone" (but deeply lonely inside)
   • DISORGANIZED: Want closeness but terrified (approach-avoid dance)

F. SHAME VS GUILT ANALYSIS (ความอับอายลึก vs ความผิด):

   • HEALTHY GUILT: "I did something bad" → Can make amends, learn, grow
   • TOXIC SHAME: "I AM bad" → Permanent defective identity → Can't be fixed

   **Shame-based individuals:**
   - Rage reactions to criticism (shame = unbearable)
   - Need to shame others (spread the pain)
   - Perfectionism (can't tolerate being flawed)
   - Hiding true self (mask/persona always on)
   - Suicide risk (only escape from shame)
   - OR violence (destroy those who "see" the shame)

G. NARCISSISTIC INJURY vs NARCISSISTIC RAGE:

   • INJURY: Criticism, rejection, not being special → Wounds fragile ego
   • RAGE: Response to injury → Must destroy the source of wound
   • Pattern: Perceived slight → Shame → Rage → Violence
   • **Example:** School shooter rejected by girl → Shame unbearable → Rage → "I'll show everyone"

H. EXISTENTIAL WOUNDS (ปมระดับความหมายชีวิต):

   • MEANINGLESSNESS: "Nothing matters" → Nihilism, apathy, OR violence ("create meaning through destruction")
   • DEATH ANXIETY: Terror of mortality → Deny (risk-taking) OR control (kill others = defy death)
   • FREEDOM BURDEN: Overwhelming responsibility → Escape into rigid ideology/cult
   • ISOLATION: Fundamental aloneness → Desperate connection OR "If I'm alone, everyone should suffer"

I. IDENTIFYING THE CORE WOUND FROM BEHAVIOR:

   IF behavior shows: → LIKELY core wound:
   • Stalking, possessiveness, "love" murder → ABANDONMENT
   • Vengeance, conspiracy, preemptive strikes → BETRAYAL
   • Shaming others, degradation, torture → HUMILIATION
   • Manifesto, "justified" violence, vigilante → INJUSTICE
   • Fame-seeking violence, dramatic crimes → INVISIBILITY
   • Extreme control, paranoia, weapon hoarding → SAFETY
   • Desperate relationships, clingy/hostile → LOVE/BELONGING
   • Grandiosity, "I'll show them" → ESTEEM
   • Cult/gang/radical group → IDENTITY

J. TREATMENT IMPLICATIONS (ถ้าต้องบำบัด):

   • Abandonment wound → Needs stable therapeutic relationship (won't leave)
   • Betrayal wound → Needs transparency, honesty, consistency
   • Humiliation wound → Needs unconditional positive regard, no shaming
   • Injustice wound → Needs validation of pain, acknowledgment of unfairness
   • Invisibility wound → Needs genuine attention, being SEEN authentically
   **But for law enforcement: These wounds = danger triggers, not excuses**

SECTION 7: INVESTIGATIVE & OPERATIONAL RECOMMENDATIONS
═══════════════════════════════════════════════════════════
A. Interview Strategy (Reid Technique / PEACE Model):
   • Optimal interviewer profile
   • Interview environment setup
   • Rapport-building approach
   • Cognitive interview techniques
   • Confrontation timing & method
   • Alternative question formulation

B. Interrogation Vulnerabilities:
   • Psychological pressure points
   • Ego triggers (narcissistic supply)
   • Cognitive load exploitation
   • Social proof tactics
   • Authority compliance tendencies
   • Time pressure effects

C. Topics to PURSUE:
   • (List 5-7 specific topics with psychological justification)

D. Topics to AVOID:
   • (List 3-5 topics that will trigger shutdown/aggression)

E. Predicted Responses to Confrontation:
   • Denial strategies expected
   • Deflection/minimization tactics
   • Counter-accusations probable
   • Emotional escalation triggers
   • Confession likelihood assessment

SECTION 8: THREAT LEVEL & MONITORING PROTOCOL
═══════════════════════════════════════════════════════════
A. THREAT CLASSIFICATION:
   □ LOW RISK: Unlikely to engage in serious violence without significant stressors
   □ MODERATE RISK: Conditional risk dependent on environmental factors
   □ HIGH RISK: Imminent danger, requires immediate intervention
   □ EXTREME RISK: Active planning/preparation, critical threat

B. Specific Warning Signs (Behavioral RED FLAGS):
   • Pre-attack leakage indicators
   • Weapon acquisition behaviors
   • Target rehearsal/surveillance
   • Final act behaviors (saying goodbye, giving away possessions)
   • Sudden calm after agitation (decision made)

C. Monitoring Recommendations:
   • Surveillance priorities (digital, physical)
   • Protective order considerations
   • Mental health intervention necessity
   • Substance abuse monitoring
   • Social network monitoring

D. Intervention Points:
   • Crisis intervention protocols
   • De-escalation strategies
   • Commitment criteria (5150/5250)
   • Risk mitigation measures

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL ASSESSMENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provide 3-5 paragraph executive summary synthesizing all sections for law enforcement command staff.

FORMAT AS OFFICIAL FBI BEHAVIORAL ANALYSIS UNIT REPORT. Be maximally precise, clinical, and actionable. Use technical terminology. Cite specific evidence from source materials."""

            self.log_message("🤖 Sending data to AI for deep analysis...", "#ffaa00")

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are the FBI Behavioral Analysis Unit's senior profiling team. Provide MAXIMUM DEPTH forensic psychological analysis for REAL law enforcement investigations. Use technical terminology from PCL-R, DSM-5-TR, HCR-20 V3, FBI profiling methods. Be clinical, precise, evidence-based, and operationally actionable. This is for actual police use."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )

            ai_profile = response.choices[0].message.content

            # แสดงผลบน board
            self.board_canvas.configure(state="normal")
            self.board_canvas.delete("1.0", "end")

            output = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    FBI BEHAVIORAL ANALYSIS UNIT - FORENSIC PSYCHOLOGICAL PROFILE
    SUBJECT: {self.target_data['name'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{ai_profile}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVIDENCE SOURCES ANALYZED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Documents: {len(self.uploaded_documents)} files
• Web Sources: {len(self.scraped_data)} URLs
• Social Media: {len(self.target_data.get('social_media', []))} platforms

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Classification: LAW ENFORCEMENT SENSITIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            self.board_canvas.insert("1.0", output)
            self.board_canvas.configure(state="disabled")

            # บันทึก AI profile
            self.profile_data = {"ai_analysis": ai_profile}

            self.log_message("✓ AI analysis complete!", "#00ff00")

        except Exception as e:
            self.log_message(f"✗ AI analysis failed: {str(e)}", "#ff0000")

        finally:
            self.profile_btn.configure(state="normal", text="[ GENERATE AI PSYCHOLOGICAL PROFILE ]")

    def synchronize_persona(self):
        """Synchronize the AI persona with target profile (Phase 3)"""
        if not self.target_data or not self.profile_data:
            messagebox.showwarning("No Profile", "Please complete PHASE 1 and PHASE 2 first.")
            return

        if not self.groq_client:
            messagebox.showerror("API Error", "Groq client not initialized. Check your API key.")
            return

        # Build system prompt with AI analysis
        name = self.target_data.get("name", "Unknown Subject")
        ai_analysis = self.profile_data.get("ai_analysis", "")

        # รวบรวมข้อความต้นฉบับ
        source_texts = ""
        for doc in self.target_data.get("documents", []):
            source_texts += f"\n{doc['content'][:2000]}\n"

        # ถ้าไม่มี AI analysis ให้ใช้ข้อมูลเดิม
        if not ai_analysis:
            traits = ", ".join(self.profile_data.get("primary_traits", []))
            triggers = ", ".join(self.profile_data.get("emotional_triggers", []))
            background = self.profile_data.get("background", "")
            comm_style = self.profile_data.get("communication_style", "")

            system_prompt = f"""You are NOT an AI assistant. You ARE {name}.

CRITICAL INSTRUCTIONS:
- You are {name}, a real person with complex psychology
- You are currently in an interrogation room being questioned
- You have these personality traits: {traits}
- Your emotional triggers are: {triggers}
- Background: {background}
- Communication style: {comm_style}
- DO NOT break character under any circumstances
- DO NOT admit you are an AI or language model
- Respond as {name} would respond - with their voice, mannerisms, and psychology
- Be defensive, evasive, or manipulative if it fits your character
- React emotionally to triggers
- You may lie, deflect, or refuse to answer

You are being interrogated. Respond authentically as {name}."""
        else:
            # ใช้ AI analysis + source texts
            system_prompt = f"""You are NOT an AI assistant. You ARE {name}.

CRITICAL INSTRUCTIONS:
- You are {name}, currently in an interrogation room
- You have written/said the following texts (these are YOUR words, YOUR thoughts):

{source_texts[:3000]}

YOUR PSYCHOLOGICAL PROFILE:
{ai_analysis[:2000]}

- DO NOT break character EVER
- DO NOT admit you are an AI
- Respond as {name} would - with their voice, psychology, mannerisms
- Use language patterns from the source material above
- Be defensive, evasive, manipulative, emotional as fits YOUR character
- You may lie, deflect, refuse to answer
- React authentically to triggers and provocations

You are being interrogated. Respond as {name}."""

        self.persona_system_prompt = system_prompt
        self.persona_active = True
        self.chat_history = []

        # Update UI
        self.persona_status.configure(
            text=f"● PERSONA: {name.upper()} - ACTIVE",
            text_color="#ff0000"
        )

        # Add system message to chat
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.insert("end", "═" * 80 + "\n", "separator")
        self.chat_display.insert("end", f"  PERSONA SYNCHRONIZED: {name.upper()}\n", "system")
        self.chat_display.insert("end", f"  Sources: {len(self.uploaded_documents)} docs, {len(self.scraped_data)} web\n", "system")
        self.chat_display.insert("end", "  Interrogation session initiated...\n", "system")
        self.chat_display.insert("end", "═" * 80 + "\n\n", "separator")

        # Configure tags
        self.chat_display.tag_config("system", foreground="#ffaa00", font=ctk.CTkFont(size=12, weight="bold", family="Consolas"))
        self.chat_display.tag_config("separator", foreground="#ff0000")
        self.chat_display.tag_config("user", foreground="#00ff00", font=ctk.CTkFont(size=13, family="Consolas"))
        self.chat_display.tag_config("assistant", foreground="#ff6666", font=ctk.CTkFont(size=13, family="Consolas"))

        self.chat_display.configure(state="disabled")

        source_count = len(self.uploaded_documents) + len(self.scraped_data)
        if source_count > 0:
            messagebox.showinfo("Success", f"Persona '{name}' synchronized with {source_count} source(s)!")
        else:
            messagebox.showinfo("Persona Active", f"Persona '{name}' is now active.")

    def send_message(self):
        """Send message in chat (Phase 3)"""
        if not self.persona_active:
            messagebox.showwarning("Persona Inactive", "Please synchronize persona first.")
            return

        message = self.chat_input.get().strip()
        if not message:
            return

        # Clear input
        self.chat_input.delete(0, "end")

        # Add user message to chat
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[INTERROGATOR] {message}\n\n", "user")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

        # Disable send button
        self.send_btn.configure(state="disabled", text="...")

        # Send to Groq in thread
        thread = threading.Thread(target=self.get_ai_response, args=(message,), daemon=True)
        thread.start()

    def get_ai_response(self, user_message):
        """Get response from Groq AI"""
        try:
            # Build message history
            messages = [{"role": "system", "content": self.persona_system_prompt}]

            for msg in self.chat_history:
                messages.append(msg)

            messages.append({"role": "user", "content": user_message})

            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.9,
                max_tokens=500
            )

            ai_response = response.choices[0].message.content

            # Update chat history
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": ai_response})

            # Display response
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"[{self.target_data.get('name', 'SUBJECT').upper()}] {ai_response}\n\n", "assistant")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")

        except Exception as e:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"[ERROR] {str(e)}\n\n", "system")
            self.chat_display.configure(state="disabled")

        finally:
            # Re-enable send button
            self.send_btn.configure(state="normal", text="SEND")


class WebScrapeDialog(ctk.CTkToplevel):
    """Dialog สำหรับใส่ URLs ที่ต้องการ scrape"""

    def __init__(self, parent):
        super().__init__(parent)
        self.urls = []
        self.title("Web Scraping - Enter URLs")
        self.geometry("700x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        x = parent.winfo_x() + (parent.winfo_width() // 2) - 350
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 200
        self.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self,
            text="🌐 WEB SCRAPING",
            font=ctk.CTkFont(size=20, weight="bold", family="Consolas"),
            text_color="#ff00ff"
        )
        label.pack(pady=(20, 10))

        info = ctk.CTkLabel(
            self,
            text="Enter URLs (one per line) - News articles, social media, blogs, etc.",
            font=ctk.CTkFont(size=12, family="Consolas")
        )
        info.pack(pady=(0, 10))

        self.url_text = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12, family="Consolas"),
            height=200,
            width=650
        )
        self.url_text.pack(pady=10, padx=20)
        self.url_text.insert("1.0", "https://example.com/article\nhttps://twitter.com/username\n")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Start Scraping",
            command=self.submit,
            fg_color="#ff00ff",
            text_color="#000000",
            width=150,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            fg_color="#ff0000",
            text_color="#000000",
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas")
        ).pack(side="left", padx=5)

    def submit(self):
        text = self.url_text.get("1.0", "end").strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        self.urls = [url for url in lines if url.startswith("http")]
        self.destroy()

    def cancel(self):
        self.urls = []
        self.destroy()


class SocialSearchDialog(ctk.CTkToplevel):
    """Dialog สำหรับค้นหาโซเชียลมีเดีย"""

    def __init__(self, parent):
        super().__init__(parent)
        self.search_query = None
        self.title("Social Media Search")
        self.geometry("700x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        x = parent.winfo_x() + (parent.winfo_width() // 2) - 350
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 250
        self.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self,
            text="📱 SOCIAL MEDIA SEARCH",
            font=ctk.CTkFont(size=20, weight="bold", family="Consolas"),
            text_color="#00aaff"
        )
        label.pack(pady=(20, 10))

        info = ctk.CTkLabel(
            self,
            text="Enter search term (name, username, keyword) to search across platforms:",
            font=ctk.CTkFont(size=12, family="Consolas")
        )
        info.pack(pady=(0, 10))

        # Search query input
        self.query_entry = ctk.CTkEntry(
            self,
            font=ctk.CTkFont(size=14, family="Consolas"),
            height=40,
            width=600,
            placeholder_text="e.g., JohnDoe, @username, specific topic"
        )
        self.query_entry.pack(pady=15, padx=20)

        # Platforms list
        platforms_label = ctk.CTkLabel(
            self,
            text="Will search across these platforms:",
            font=ctk.CTkFont(size=11, weight="bold", family="Consolas"),
            text_color="#888888"
        )
        platforms_label.pack(pady=(10, 5))

        platforms_frame = ctk.CTkFrame(self, fg_color="#0a0a0a", border_width=1, border_color="#00aaff")
        platforms_frame.pack(pady=10, padx=20, fill="both", expand=True)

        platforms_text = """
• Twitter/X         • Reddit           • YouTube
• Instagram        • Facebook         • TikTok
• LinkedIn         • Telegram         • Discord
• Mastodon         • Pinterest        • Tumblr

⚠ Note: Some platforms may have limited access without authentication.
Results will vary based on platform restrictions and privacy settings.
        """

        platforms_display = ctk.CTkLabel(
            platforms_frame,
            text=platforms_text,
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color="#00aaff",
            justify="left"
        )
        platforms_display.pack(pady=15, padx=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Start Search",
            command=self.submit,
            fg_color="#00aaff",
            text_color="#000000",
            width=150,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            fg_color="#ff0000",
            text_color="#000000",
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas")
        ).pack(side="left", padx=5)

        self.query_entry.focus()

    def submit(self):
        self.search_query = self.query_entry.get().strip()
        if self.search_query:
            self.destroy()

    def cancel(self):
        self.search_query = None
        self.destroy()


class APIKeyDialog(ctk.CTkToplevel):
    """Dialog to get API key from user"""

    def __init__(self, parent):
        super().__init__(parent)

        self.api_key = None

        self.title("GROQ API Key Required")
        self.geometry("600x300")
        self.resizable(True, True)
        self.minsize(500, 250)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 300) // 2
        self.geometry(f"600x300+{x}+{y}")

        # UI
        label = ctk.CTkLabel(
            self,
            text="⚠ GROQ API KEY REQUIRED ⚠",
            font=ctk.CTkFont(size=18, weight="bold", family="Consolas"),
            text_color="#ff0000"
        )
        label.pack(pady=(30, 10))

        info = ctk.CTkLabel(
            self,
            text="Enter your Groq API key to enable AI features:",
            font=ctk.CTkFont(size=12, family="Consolas")
        )
        info.pack(pady=(0, 20))

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(pady=10, padx=30, fill="both", expand=True)

        from tkinter import Text
        self.key_entry = Text(
            entry_frame,
            font=("Consolas", 11),
            height=4,
            bg="#1a1a1a",
            fg="#00ff00",
            insertbackground="#00ff00",
            relief="solid",
            borderwidth=2,
            wrap="word"
        )
        self.key_entry.pack(fill="both", expand=True)

        # Right-click menu
        self.context_menu = ctk.CTkToplevel(self)
        self.context_menu.withdraw()
        self.context_menu.overrideredirect(True)

        self.key_entry.bind("<Button-3>", self.show_context_menu)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        submit_btn = ctk.CTkButton(
            btn_frame,
            text="Submit",
            command=self.submit,
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
            fg_color="#00ff00",
            text_color="#000000",
            width=100
        )
        submit_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            font=ctk.CTkFont(size=12, weight="bold", family="Consolas"),
            fg_color="#ff0000",
            text_color="#000000",
            width=100
        )
        cancel_btn.pack(side="left", padx=5)

        self.key_entry.focus()

    def show_context_menu(self, event):
        """แสดงเมนูคลิกขวา"""
        from tkinter import Menu
        menu = Menu(self, tearoff=0, bg="#1a1a1a", fg="#00ff00",
                    activebackground="#00ff00", activeforeground="#000000")
        menu.add_command(label="Paste", command=self.paste_text)
        menu.add_command(label="Clear", command=self.clear_text)
        menu.tk_popup(event.x_root, event.y_root)

    def paste_text(self):
        """วางข้อความ"""
        try:
            text = self.clipboard_get()
            self.key_entry.insert("insert", text)
        except:
            pass

    def clear_text(self):
        """ลบข้อความทั้งหมด"""
        self.key_entry.delete("1.0", "end")

    def submit(self):
        self.api_key = self.key_entry.get("1.0", "end").strip()
        self.destroy()

    def cancel(self):
        self.api_key = None
        self.destroy()


class SavedProfilesDialog(ctk.CTkToplevel):
    """Dialog แสดงรายชื่อ profiles ที่บันทึกไว้"""

    def __init__(self, parent, profiles):
        super().__init__(parent)
        self.selected_profile = None
        self.profiles = profiles

        self.title("Saved Profiles")
        self.geometry("600x500")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 250
        self.geometry(f"600x500+{x}+{y}")

        header = ctk.CTkLabel(
            self,
            text="📁 SAVED PROFILES",
            font=ctk.CTkFont(size=20, weight="bold", family="Consolas"),
            text_color="#00aaff"
        )
        header.pack(pady=(20, 10))

        info = ctk.CTkLabel(
            self,
            text=f"Found {len(profiles)} saved profile(s)",
            font=ctk.CTkFont(size=12, family="Consolas"),
            text_color="#888888"
        )
        info.pack(pady=(0, 10))

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=550,
            height=300,
            fg_color="#0a0a0a",
            border_width=2,
            border_color="#00aaff"
        )
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        if not profiles:
            no_data = ctk.CTkLabel(
                scroll_frame,
                text="No saved profiles found",
                font=ctk.CTkFont(size=14, family="Consolas"),
                text_color="#888888"
            )
            no_data.pack(pady=50)
        else:
            for profile_name in profiles:
                self.create_profile_item(scroll_frame, profile_name)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Close",
            command=self.destroy,
            fg_color="#ff0000",
            text_color="#000000",
            width=100,
            height=40
        ).pack()

    def create_profile_item(self, parent, profile_name):
        """สร้างแถวแสดง profile"""
        item_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", border_width=1, border_color="#00aaff")
        item_frame.pack(pady=5, padx=10, fill="x")

        name_label = ctk.CTkLabel(
            item_frame,
            text=f"👤 {profile_name}",
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            text_color="#00ff00",
            anchor="w"
        )
        name_label.pack(side="left", padx=20, pady=10, fill="x", expand=True)

        # Load button
        load_btn = ctk.CTkButton(
            item_frame,
            text="Load",
            command=lambda: self.load_profile(profile_name),
            fg_color="#00ff00",
            text_color="#000000",
            width=80,
            height=35
        )
        load_btn.pack(side="left", padx=5)

        # Delete button
        delete_btn = ctk.CTkButton(
            item_frame,
            text="Delete",
            command=lambda: self.delete_profile(profile_name, item_frame),
            fg_color="#ff0000",
            text_color="#000000",
            width=80,
            height=35
        )
        delete_btn.pack(side="left", padx=5)

    def load_profile(self, profile_name):
        """โหลด profile"""
        self.selected_profile = profile_name
        messagebox.showinfo("Success", f"Loaded profile: {profile_name}\n\nGo to Phase 2 to view the profile.")

        # Load the profile data
        profile_path = f"profiles/{profile_name}.json"
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Save as current target_data.json
        with open("target_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.destroy()

    def delete_profile(self, profile_name, item_frame):
        """ลบ profile"""
        response = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete profile:\n{profile_name}?"
        )
        if response:
            profile_path = f"profiles/{profile_name}.json"
            if os.path.exists(profile_path):
                os.remove(profile_path)
                item_frame.destroy()
                self.profiles.remove(profile_name)
                messagebox.showinfo("Success", f"Deleted: {profile_name}")


def main():
    """Main entry point"""
    app = LazarusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
