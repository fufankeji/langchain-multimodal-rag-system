<div align="center"> <h1>🧠 Multimodal RAG QA System (based on LangChain 1.0)</h1> <p><em>A LangChain 1.0-based multimodal RAG system supporting text, images, PDFs, and audio</em></p> <span><a href="./README_zh.md">中文</a> | English</span> </div>

## ✨ Overview

This project is built on LangChain 1.0, supports multimodal inputs, and provides a traceable RAG question-answering system. The system adopts a FastAPI + React architecture.

<img src="./assets/demo1.png" alt="Project Demo 1" width="49%" /> <img src="./assets/demo2.png" alt="Project Demo 2" width="49%" />

## 🎯 Core Features
🧠 LangChain 1.0 powered: Build a unified multimodal knowledge pipeline with flexible extension and componentized management

📎 RAG source tracing badges: When generating answers, attach citation markers referencing retrieved sources; click markers to locate the corresponding fragment in the original document

🎧 Audio support: Upload audio files to automatically transcribe into text, supporting Q&A and summarization

⚡ Streaming output: Real-time generation and display of responses for smoother interaction

🖥️ Frontend UI: Supports file upload, answer display, retrieval tracing, and multimodal visualization

## 🎬 Demo


## 🚀 Quick Start

Start backend
```bash
cd backend
uv venv --python 3.10 
source .venv/bin/activate
uv pip install -r requirements.txt
python start.py
```

Start frontend
```bash
npm install
npm run dev
```

## 🙈 Contributing
We welcome contributions via PRs or issues. Any form of contribution is appreciated, including feature improvements, bug fixes, or documentation enhancements.

## 😎 Community
Explore our tech community 👉 [Large Model Tech Community | Fufan Space](https://kq4b3vgg5b.feishu.cn/wiki/JuJSwfbwmiwvbqkiQ7LcN1N1nhd)

Scan to join the chat group and connect with other developers.
<div align="center">
<img src="./assets/code.jpg" width="200" alt="Community QR code">
<div>