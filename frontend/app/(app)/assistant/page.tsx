"use client";

import { FormEvent, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { ChatCitation } from "@/lib/types";
import { PageHeader, EmptyState } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: ChatCitation[];
}

export default function AssistantPage() {
  const { selectedProject } = useProject();
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!selectedProject || !question.trim()) return;
    const q = question;
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setQuestion("");
    setLoading(true);
    try {
      const res = await api.post<{ answer: string; citations: ChatCitation[] }>("/api/v1/assistant/chat", {
        project_id: selectedProject.id,
        question: q,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer, citations: res.citations }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: err instanceof ApiError ? err.message : "Something went wrong." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (!selectedProject) {
    return <EmptyState title="No project selected" description="Select a project to chat with its documents." />;
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <PageHeader
        title="AI Assistant"
        description="Ask questions about uploaded specifications, FHWA manuals, inspection reports, RFIs, submittals, and plan sheets. Answers are cited to source documents."
      />

      <Card className="flex flex-1 flex-col overflow-hidden p-0">
        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.length === 0 && (
            <p className="text-sm text-slate-400">
              Try asking: “What are the concrete curing requirements?” or “Summarize open RFIs related to
              drainage.”
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={
                  "max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm " +
                  (m.role === "user" ? "bg-federal-900 text-white" : "bg-federal-50 text-federal-950")
                }
              >
                {m.content}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5 border-t border-federal-900/10 pt-2">
                    {m.citations.map((c, ci) => (
                      <span
                        key={ci}
                        title={c.snippet}
                        className="rounded-full border border-federal-900/20 bg-white px-2 py-0.5 text-[11px] text-federal-800"
                      >
                        [{ci + 1}] {c.document_title}
                        {c.page_number ? ` p.${c.page_number}` : ""}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <p className="text-xs text-slate-400">Thinking…</p>}
        </div>
        <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 p-4">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about project documents…"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-federal-600 focus:outline-none focus:ring-1 focus:ring-federal-600"
          />
          <Button type="submit" disabled={loading || !question.trim()}>
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
}
