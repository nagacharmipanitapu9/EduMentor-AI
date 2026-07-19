# EduMentor-AI

An intelligent AI-powered academic advisor system that provides personalized student support through multi-agent orchestration.

## 🎯 Overview

**EduMentor-AI** is a sophisticated multi-agent system built with LangGraph that analyzes student performance and provides comprehensive academic guidance. It processes student profiles, academic data, and interests to generate actionable insights including performance reports, personalized study plans, learning resources, and career recommendations.

### Key Features

- 🤖 **Multi-Agent Architecture** — Five specialized agents work together seamlessly
- 📊 **Performance Analysis** — Comprehensive GPA computation and subject strength assessment
- 📚 **Personalized Study Plans** — 4-week hour-allocated study schedules tailored to individual needs
- 🎓 **Career Guidance** — Data-driven career suggestions based on academic strengths and interests
- 🔗 **Intelligent Resource Matching** — Connects students with optimal learning materials
- 💾 **SQLite Backend** — Secure, local data storage for student profiles and academic records
- 🚀 **Zero-Setup Demo** — Runs with mock LLM fallback; upgrade to Ollama for real AI responses

---

## 🏗️ Architecture

```
student_profile → performance_analysis → study_planner → resource_recommendation → career_guidance
                        ^   |
                        └───┘ (loops back if no grade data yet, capped retries)
```

### The Five Agents

| Agent | File | Responsibility |
|---|---|---|
| **Student Profile Agent** | `src/agents/student_profile_agent.py` | Loads program/year/interests, summarizes them |
| **Performance Analysis Agent** | `src/agents/performance_analysis_agent.py` | Computes GPA, flags weak/strong subjects |
| **Study Planner Agent** | `src/agents/study_planner_agent.py` | Builds a 4-week, hour-allocated study plan |
| **Resource Recommendation Agent** | `src/agents/resource_recommendation_agent.py` | Matches open resources to weak subjects |
| **Career Guidance Agent** | `src/agents/career_guidance_agent.py` | Ranks careers by subject/interest overlap |

---

## 🛠️ Technology Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — Multi-agent orchestration framework
- **[Ollama](https://ollama.com)** (via `langchain-ollama`) — Local, open-source LLM support (llama3.1, etc.)
- **[SQLite](https://www.sqlite.org/)** — Lightweight, file-based data persistence
- **[Rich](https://rich.readthedocs.io/)** — Beautiful CLI output formatting
- **Python 3.8+** — Core language

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/nagacharmipanitapu9/EduMentor-AI.git
cd EduMentor-AI

# 2. Run setup (installs dependencies, creates .env, seeds database)
python setup.py

# 3. Start the application
python main.py
```

### Usage Modes

#### Interactive Mode (Recommended for First-Time Users)
```bash
python main.py
```
You'll be prompted to enter:
- Your name, academic program, and year
- Your interests
- Grades for each subject

#### Demo Mode (Pre-Loaded Student Data)
```bash
python main.py --student S001
python main.py --student S002
```

### Enable Real AI Responses (Optional)

By default, EduMentor-AI uses a deterministic mock LLM for zero-setup demos. To use a real open-source model:

```bash
# In a separate terminal, start Ollama
ollama pull llama3.1
ollama serve

# Then run the application (it will auto-detect Ollama)
python main.py
```

---

## 📁 Project Structure

```
EduMentor-AI/
├── setup.py                  # Bootstrap: install dependencies, seed DB, check Ollama
├── cleanup.py                # Remove generated artifacts
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
├── data/
│   ├── seed_data.json        # Sample students, grades, resources, careers
│   └── advisor.db            # Generated SQLite database (git-ignored)
├── src/
│   ├── llm.py                # Pluggable LLM interface (Ollama / mock)
│   ├── state.py              # Shared LangGraph state schema
│   ├── db.py                 # SQLite access layer
│   ├── graph.py              # Agent graph wiring
│   └── agents/               # Five specialized agents
│       ├── student_profile_agent.py
│       ├── performance_analysis_agent.py
│       ├── study_planner_agent.py
│       ├── resource_recommendation_agent.py
│       └── career_guidance_agent.py
└── tests/
    └── test_graph.py         # Unit & integration tests
```

---

## 🧹 Cleanup

Remove generated artifacts:

```bash
# Remove database and cache files
python cleanup.py

# Remove database, cache, and .env
python cleanup.py --all
```

---

## ✅ Testing

Run the test suite:

```bash
pytest
```

---

## 🗺️ Roadmap & Future Enhancements

- [ ] Migrate from SQLite to managed PostgreSQL with write support
- [ ] Add transcript and syllabus ingestion pipelines
- [ ] Implement Q&A node for subject-specific tutoring
- [ ] Multi-institution data isolation and authentication
- [ ] Real-time performance tracking and adaptive recommendations
- [ ] Web UI dashboard for enhanced student experience
- [ ] API endpoints for third-party LMS integration

---

## 🔒 Security & Privacy

**Current Status (Prototype):**
- ✅ Local SQLite database — no external data transmission
- ⚠️ Authentication: Not yet implemented
- ⚠️ Data isolation: Single-instance only

**Before Production Use:**
- Add user authentication and authorization
- Implement per-institution/per-student data isolation
- Enable role-based access control (RBAC)
- Set up secure data encryption
- Conduct security audit

---

## 📝 License

[Add your license here]

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support & Feedback

For issues, questions, or suggestions:
- Open an [issue](https://github.com/nagacharmipanitapu9/EduMentor-AI/issues)
- Check existing documentation in the repo
- Review the agent architecture for customization opportunities

---

## 🎓 Educational Purpose

EduMentor-AI was designed as a prototype to demonstrate multi-agent AI systems in practice. It's an excellent reference for learning:
- LangGraph multi-agent patterns
- State machine design for complex workflows
- LLM integration and fallback strategies
- Educational technology concepts

---

**Built with ❤️ for students everywhere.**
