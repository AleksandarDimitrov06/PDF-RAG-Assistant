import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

const API = "/api"; // proxied to FastAPI by vite.config.js

// Persisted so a page refresh keeps the same session.
// (Your Streamlit code used a fixed "test_session_id"; swap it in here if you need that.)
function getSessionId() {
  // try {
  //   let id = localStorage.getItem("rag_session_id");
  //   if (!id) {
  //     id = crypto.randomUUID();
  //     localStorage.setItem("rag_session_id", id);
  //   }
  //   return id;
  // } catch {
  //   return crypto.randomUUID();
  // }
  return "test_session_id";
}

async function readError(res) {
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return body.detail;
  } catch {
    /* not JSON */
  }
  return `Request failed (${res.status}).`;
}

const newId = () => Math.random().toString(36).slice(2);

/* ---------- Icons (inline SVG, inherit currentColor) ---------- */
function Icon({ children }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const FileIcon = () => (
  <Icon>
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <path d="M14 2v6h6" />
    <path d="M9 13h6M9 17h6" />
  </Icon>
);
const UploadIcon = () => (
  <Icon>
    <path d="M12 16V4" />
    <path d="m7 9 5-5 5 5" />
    <path d="M5 20h14" />
  </Icon>
);
const SwapIcon = () => (
  <Icon>
    <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
    <path d="M3 21v-5h5" />
  </Icon>
);
const SendIcon = () => (
  <Icon>
    <path d="M12 19V5" />
    <path d="m5 12 7-7 7 7" />
  </Icon>
);
const SparkIcon = () => (
  <Icon>
    <path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" />
  </Icon>
);

export default function App() {
  const [sessionId] = useState(getSessionId);
  const [doc, setDoc] = useState(null); // { name, hash, url }
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [dragging, setDragging] = useState(false);
  const [messages, setMessages] = useState([]);
  const [pending, setPending] = useState(false);
  const [input, setInput] = useState("");
  const [copiedId, setCopiedId] = useState(null);

  const fileInput = useRef(null);
  const endRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending]);

  useEffect(() => {
    return () => doc?.url && URL.revokeObjectURL(doc.url);
  }, [doc]);

  async function uploadFile(file) {
    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setUploadError("That file isn't a PDF. Choose a .pdf file.");
      return;
    }
    setUploadError("");
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file, file.name);
      const res = await fetch(
        `${API}/upload?session_id=${encodeURIComponent(sessionId)}`,
        { method: "POST", body: form }
      );
      if (!res.ok) throw new Error(await readError(res));
      const result = await res.json();
      setDoc({ name: file.name, hash: result.document_hash, url: URL.createObjectURL(file) });
      setMessages([
        {
          id: newId(),
          role: "system",
          content: result.message || "Document ready.",
        },
      ]);
    } catch (err) {
      setUploadError(`Could not upload the PDF. ${err.message}`);
    } finally {
      setUploading(false);
    }
  }

  async function ask(question, { retryOf } = {}) {
    setMessages((prev) => {
      const base = retryOf ? prev.filter((m) => m.id !== retryOf) : prev;
      return retryOf ? base : [...base, { id: newId(), role: "user", content: question }];
    });
    setPending(true);
    try {
      const res = await fetch(`${API}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          document_hash: doc.hash,
          question,
        }),
      });
      if (!res.ok) throw new Error(await readError(res));
      const { answer } = await res.json();
      setMessages((prev) => [...prev, { id: newId(), role: "assistant", content: answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: newId(), role: "assistant", content: err.message, error: true, question },
      ]);
    } finally {
      setPending(false);
    }
  }

  function submit() {
    const question = input.trim();
    if (!question || pending || !doc) return;
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    ask(question);
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function onInput(e) {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 180) + "px";
  }

  async function copy(m) {
    try {
      await navigator.clipboard.writeText(m.content);
      setCopiedId(m.id);
      setTimeout(() => setCopiedId(null), 1500);
    } catch {
      /* clipboard unavailable */
    }
  }

  function replaceDocument() {
    setDoc(null);
    setMessages([]);
    setUploadError("");
  }

  return (
    <div className="app">
      <section className="pane doc-pane" aria-label="Document">
        <header className="pane-head">
          <div className="brand">
            <span className="brand-mark"><FileIcon /></span>
            <h1>PDF Assistant</h1>
          </div>
          {doc && (
            <button className="link-btn" onClick={replaceDocument}>
              <SwapIcon />
              Replace PDF
            </button>
          )}
        </header>

        {doc ? (
          <>
            <p className="file-name" title={doc.name}>
              <FileIcon />
              <span>{doc.name}</span>
            </p>
            <iframe className="viewer" src={doc.url} title={doc.name} />
          </>
        ) : (
          <div
            className={`dropzone ${dragging ? "is-dragging" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              uploadFile(e.dataTransfer.files?.[0]);
            }}
          >
            {uploading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                <p className="dz-title">Processing your PDF…</p>
                <p className="dz-sub">Large files can take a minute.</p>
              </>
            ) : (
              <>
                <span className="dz-icon"><UploadIcon /></span>
                <p className="dz-title">Drop a PDF here</p>
                <p className="dz-sub">or</p>
                <button className="btn" onClick={() => fileInput.current?.click()}>
                  Choose a file
                </button>
              </>
            )}
            {uploadError && <p className="error" role="alert">{uploadError}</p>}
            <input
              ref={fileInput}
              type="file"
              accept="application/pdf,.pdf"
              hidden
              onChange={(e) => {
                uploadFile(e.target.files?.[0]);
                e.target.value = "";
              }}
            />
          </div>
        )}
      </section>

      <section className="pane chat-pane" aria-label="Conversation">
        <div className="chat-scroll" role="log" aria-live="polite">
          {!doc && (
            <p className="empty">Upload a PDF, then ask questions about it here.</p>
          )}

          {messages.map((m) => (
            <article key={m.id} className={`msg ${m.role} ${m.error ? "failed" : ""}`}>
              {m.role === "user" && <p>{m.content}</p>}
              {m.role === "system" && <p>{m.content}</p>}
              {m.role === "assistant" && (
                <>
                  <span className="avatar"><SparkIcon /></span>
                  <div className="msg-body">
                    {m.error ? <p>{m.content}</p> : <ReactMarkdown>{m.content}</ReactMarkdown>}
                    <div className="msg-actions">
                      {m.error ? (
                        <button className="link-btn" onClick={() => ask(m.question, { retryOf: m.id })}>
                          Try again
                        </button>
                      ) : (
                        <button className="link-btn" onClick={() => copy(m)}>
                          {copiedId === m.id ? "Copied" : "Copy"}
                        </button>
                      )}
                    </div>
                  </div>
                </>
              )}
            </article>
          ))}

          {pending && (
            <div className="msg assistant" aria-label="Assistant is thinking">
              <span className="avatar"><SparkIcon /></span>
              <span className="dots"><i /><i /><i /></span>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="composer">
          {messages.length > 1 && (
            <button className="link-btn clear" onClick={() => setMessages(messages.slice(0, 1))}>
              Clear chat
            </button>
          )}
          <div className="composer-row">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={onInput}
              onKeyDown={onKeyDown}
              placeholder={doc ? "Ask a question about the PDF" : "Upload a PDF to start"}
              disabled={!doc}
              aria-label="Your question"
            />
            <button
              className="btn send"
              onClick={submit}
              disabled={!doc || pending || !input.trim()}
              aria-label="Ask"
              title="Ask"
            >
              <SendIcon />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
