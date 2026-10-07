import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

const GREETING = {
  role: "assistant",
  content: "Hi! Welcome to Transindent Miami. Tap a question below or type your own.",
};

export default function App() {
  const [messages, setMessages] = useState([GREETING]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [faqs, setFaqs] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    fetch(`${API_URL}/faqs`)
      .then((r) => r.json())
      .then((d) => setFaqs(Array.isArray(d) ? d : []))
      .catch((err) => console.error("Could not load FAQs", err));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function addMessage(role, content) {
    setMessages((m) => [...m, { role, content }]);
  }

  async function askFaq(faq) {
    if (loading) return;
    addMessage("user", faq.question);
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/faqs/${faq.id}`);
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      addMessage("assistant", data.answer);
    } catch (err) {
      console.error(err);
      addMessage("assistant", "Something went wrong, please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    // the greeting is UI only, so don't send it to the server as history
    const history = messages.filter((m) => m !== GREETING);
    addMessage("user", text);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      addMessage("assistant", data.reply);
    } catch (err) {
      console.error(err);
      addMessage("assistant", "Something went wrong, please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="chat">
        <div className="chat-header">
          <h1>Transindent Miami</h1>
          <p>Front desk assistant</p>
        </div>

        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              {m.content}
            </div>
          ))}
          {loading && (
            <div className="bubble assistant typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="faqs">
          {faqs.map((f) => (
            <button
              key={f.id}
              className="chip"
              onClick={() => askFaq(f)}
              disabled={loading}
            >
              {f.question}
            </button>
          ))}
        </div>

        <div className="input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Type your question..."
          />
          <button onClick={send} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}