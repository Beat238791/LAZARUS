# PROJECT: LAZARUS - Enhanced Edition
## The Ultimate Psychological Profiling Engine

A three-phase psychological analysis and AI persona simulation system with **document upload**, **web scraping**, and **AI-powered deep analysis**.

---

## 🔥 Features

### ⚡ PHASE 1: THE HUNT (Multi-Source Data Collection)
- **Deep Scan**: Automated target profiling simulation
- **Upload Documents**: PDF, TXT, DOCX support for manifestos, letters, writings
- **Web Scraping**: Extract content from any URL (news, social media, blogs)
- Real-time logging console with progress tracking
- Data source counter showing uploaded files and scraped pages

### ⚡ PHASE 2: THE WEB (AI-Powered Pattern Analysis)
- **AI Psychological Profile Generation** using Groq LLM
- Analyzes ALL uploaded documents and scraped web content
- Comprehensive forensic analysis:
  - Primary personality traits
  - Behavioral patterns
  - Emotional triggers
  - Communication style
  - Threat assessment
- Mindhunter-style visual board display

### ⚡ PHASE 3: THE RESURRECTION (Enhanced Persona Chat)
- **AI Persona Synchronization** with source material integration
- Reads and learns from uploaded documents
- Adopts linguistic patterns from real texts
- Ultra-realistic character simulation for interrogation
- Context-aware responses based on psychological profile

---

## Installation

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Note**: The app works even if optional dependencies are missing:
- Without `PyPDF2` & `python-docx`: Can't upload documents (but web scraping still works)
- Without `requests` & `beautifulsoup4`: Can't scrape web (but document upload still works)

### Step 2: Set Up Groq API Key
Get your API key from [Groq Console](https://console.groq.com/)

Create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

Or the app will prompt you on first launch.

---

## Usage

### Quick Start
```bash
python lazarus_app.py
```

### Full Workflow (Enhanced Method)

#### **PHASE 1: Collect Data**
1. Enter target name: e.g., "Ted Kaczynski"
2. **Click [UPLOAD DOCS]**:
   - Upload "Unabomber Manifesto.pdf"
   - Upload any letters, writings, manifestos
3. **Click [WEB SCRAPE]**:
   - Add URLs: news articles, Wikipedia, Twitter posts
   - Example: `https://en.wikipedia.org/wiki/Ted_Kaczynski`
4. **Click [DEEP SCAN]** to finalize

#### **PHASE 2: AI Analysis**
1. Click **[GENERATE AI PSYCHOLOGICAL PROFILE]**
2. AI analyzes ALL uploaded docs + scraped content
3. View comprehensive forensic report on Mindhunter Board

#### **PHASE 3: Interrogation**
1. Click **[SYNCHRONIZE PERSONA]**
2. AI becomes the target (learns from documents!)
3. Ask questions and watch it respond in character

---

## Tech Stack

- **GUI Framework**: CustomTkinter (dark theme)
- **LLM Provider**: Groq (llama-3.3-70b-versatile)
- **Environment**: python-dotenv
- **Threading**: For non-blocking operations
- **Data Format**: JSON

---

## Design Philosophy

**Cyberpunk/Hacker Aesthetic**
- Black background (#000000)
- Green accents (#00ff00) for primary actions
- Red accents (#ff0000) for critical features
- Monospace fonts (Consolas)
- Terminal-style logging

---

## Security & Ethics

This tool is designed for:
- Creative writing and character development
- Educational demonstrations of AI persona simulation
- Understanding psychological profiling concepts
- Entertainment purposes

**NOT for:**
- Real criminal profiling
- Actual interrogations
- Harassment or stalking
- Any illegal activities

---

## License

MIT License - Use responsibly and ethically.

---

## Credits

Built as a demonstration of advanced GUI design, AI integration, and psychological simulation concepts.
