import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello 👋 Upload a PDF to get started, then ask me questions about it.",
    },
  ]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const addMessage = (sender, text) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      addMessage("bot", "Please choose a PDF file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setUploading(true);
      addMessage("user", `Uploading: ${selectedFile.name}`);

      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      addMessage(
        "bot",
        `✅ "${response.data.filename}" uploaded and processed.\n\nAsk me anything about it.`
      );

      setSelectedFile(null);
      const fileInput = document.getElementById("pdf-upload");
      if (fileInput) fileInput.value = "";
    } catch (error) {
      const msg =
        error.response?.data?.detail || "Upload failed. Please try again.";
      addMessage("bot", `❌ Upload error: ${msg}`);
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;

    const currentQuestion = question.trim();
    addMessage("user", currentQuestion);
    setQuestion("");

    try {
      setLoading(true);

      const response = await axios.post(`${API_BASE}/ask`, {
        question: currentQuestion,
        top_k: 5,
      });

      addMessage("bot", response.data.answer);
    } catch (error) {
      const msg =
        error.response?.data?.detail || "Something went wrong while asking.";
      addMessage("bot", `❌ Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleAsk();
    }
  };

  return (
    <div className="app">
      <div className="chat-wrapper">
        <div className="chat-header">
          <h1>DocSense</h1>
        </div>

        <div className="upload-bar">
          <input
            id="pdf-upload"
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
          />
          <button onClick={handleUpload} disabled={uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>

        <div className="chat-container">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-row ${msg.sender === "user" ? "user-row" : "bot-row"}`}
            >
              <div className={`message-bubble ${msg.sender === "user" ? "user-bubble" : "bot-bubble"}`}>
                <pre>{msg.text}</pre>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row bot-row">
              <div className="message-bubble bot-bubble">
                <pre>Thinking...</pre>
              </div>
            </div>
          )}
        </div>

        <div className="input-bar">
          <input
            type="text"
            placeholder="Ask something..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button onClick={handleAsk} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}