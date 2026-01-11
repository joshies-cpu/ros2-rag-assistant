# ♿ Hybrid RAG Autonomous Wheelchair Assistant

A comprehensive platform combining **ROS 2 Robotics Simulation** with a **Retrieval-Augmented Generation (RAG) AI Assistant**. This system monitors an autonomous wheelchair in a simulated environment, processes real-time telemetry, and provides an intelligent voice-interactive interface for technical support and control.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![ROS 2](https://img.shields.io/badge/ROS_2-Humble-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🚀 Key Features

### 🤖 Autonomous Simulation (ROS 2 & Gazebo)
*   **Full Simulation Stack**: Gazebo Fortress world with a differential drive wheelchair robot.
*   **Navigation Stack (Nav2)**: Autonomous path planning and obstacle avoidance (`dwb_core`).
*   **SLAM**: Real-time mapping and localization using `slam_toolbox` and `robot_localization` (EKF).
*   **Sensors**: Simulated Lidar, IMU (BNO055), and Wheel Encoders.

### 🧠 AI & Hybrid RAG
*   **Context-Aware**: Hybrid search retrieval combining vector semantic search (ChromaDB) with keyword matching.
*   **Live Telemetry Bridge**: Real-time ETL pipeline ingests ROS 2 topic data (`/odom`, `/battery_state`, `/scan`) into the knowledge base.
*   **PDF Knowledge Base**: Dynamically index technical manuals and safety documents.
*   **LLM Integration**: Powered by local LLMs (Ollama/Llama 3) for privacy-first assistance.

## 📂 Project Structure

The project follows a professional monorepo architecture:

```text
├── backend/            # FastAPI Application & ETL Logic
│   ├── app/            # Main application code
│   └── Dockerfile      # Backend container definition
├── frontend/           # Web Interface
│   └── static/         # HTML/JS/CSS assets
├── simulation/         # ROS 2 Workspace & Bridge
│   ├── workspace/      # ROS 2 packages (wheelchair, nav2 config)
│   └── bridge/         # ROS-to-ETL Python bridges
├── tools/              # Utility Scripts
│   ├── dev/            # Startup scripts (start_server.sh, start_simulation.sh)
│   └── etl/            # Data processing scripts
├── data/               # Persistent Storage
│   ├── documents/      # Uploaded PDFs
│   └── chroma_db/      # Vector Database
└── docker-compose.yaml # Container orchestration
```

## 🛠️ Getting Started

### Prerequisites
*   **OS**: Ubuntu 22.04 LTS (Required for ROS 2 Humble)
*   **ROS 2**: Humble Hawksbill installed
*   **Ollama**: Running locally (`ollama run llama3`)
*   **Docker**: Optional (for containerized web app)

### 1. 🐳 Run with Docker (Recommended for Web App)
This launches the Backend, Web UI, and Vector Database.

```bash
# Start the Web Stack
sudo docker compose up --build
```
*   **Web UI**: [http://localhost:8000](http://localhost:8000)

### 2. 🤖 Run the Simulation (Local Host)
The simulation requires a GUI and GPU access, so it runs best directly on the host machine.

```bash
# 1. Install ROS Dependencies
sudo apt install ros-humble-desktop ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-slam-toolbox

# 2. Build the Workspace
cd simulation/workspace
colcon build --symlink-install

# 3. Launch Simulation
cd ../..
./tools/dev/start_simulation.sh
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/telemetry` | Get latest robot sensor data |
| `POST` | `/upload` | Upload PDF manuals for indexing |
| `POST` | `/ask` | Ask the AI about the robot or manuals |

## 🤝 Contribution
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
