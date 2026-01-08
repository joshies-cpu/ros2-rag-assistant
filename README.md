# AI Knowledge Assistant for Healthcare & Robotics

A professional-grade **Retrieval-Augmented Generation (RAG)** platform designed for autonomous wheelchair users. This assistant bridges clinical documentation with technical support using a local LLM.



## 🚀 Key Features
* **Dynamic PDF Indexing:** Instantly learns from uploaded technical manuals or medical schedules.
* **Page-Aware Citations:** Provides precise source attribution (File & Page Number) to ensure safety and transparency.
* **Voice-Enabled UI:** Built-in speech-to-text and manual read-aloud features for accessibility.
* **Dockerized Deployment:** Ready to run in any environment with a single command.

## 🛠️ Technical Stack
* **Backend:** FastAPI (Python)
* **Vector DB:** ChromaDB
* **AI Model:** Llama 3 (via Ollama)
* **DevOps:** Docker & Docker Compose

## 🔧 Hardware Readiness (Future Roadmap)
While currently a standalone software platform, this project is architected for **ROS2 integration**. Future updates will allow the AI to monitor:
* Live Battery & Sensor Status (via ESP32)
* Navigation Diagnostics
* Proactive Medical Alerts based on real-time data

## 📥 Getting Started
1. Install Docker and Ollama.
2. Run `docker compose up --build`.
3. Open `http://localhost:8000`.gi