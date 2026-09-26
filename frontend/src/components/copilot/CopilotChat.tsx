import React, { useEffect, useRef, useState } from 'react';

import { useCopilot } from '../../hooks/useCopilot';
import { useFinancialProfile } from '../../hooks/useFinancialProfile';
import { ChatMessage } from './ChatMessage';
import { Send, Trash2, ChevronRight } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  "I want to purchase an iPhone for ₹1,302.40",
  "How much should I save for an emergency fund?",
  "Can I afford to buy a car in 6 months?",
  "What if I invest ₹5,000 monthly?",
  "Give me a summary of my finances",
];

export const CopilotChat: React.FC = () => {
  const { data: profile } = useFinancialProfile();
  const { messages, isLoading, sendMessage, clearMessages } = useCopilot();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const currency = profile?.home_currency || 'USD';

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;
    setInput('');
    await sendMessage(text);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestion = async (prompt: string) => {
    setInput('');
    await sendMessage(prompt);
  };

  return (
    <div className="flex flex-col h-full" style={{ height: 'calc(100vh - var(--topbar-height) - 64px)' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        {messages.length > 0 && (
          <button
            className="btn-ghost flex items-center gap-1.5 text-xs"
            onClick={clearMessages}
            aria-label="Clear conversation"
          >
            <Trash2 size={13} aria-hidden="true" />
            Clear conversation
          </button>
        )}
        {messages.length === 0 && <div />}
        {profile && (
          <span className="badge-neutral text-xs">
            {profile.user_id} · {profile.home_currency}
          </span>
        )}
      </div>

      {/* Messages area */}
      <div
        className="flex-1 overflow-y-auto space-y-4 pb-4"
        role="log"
        aria-label="Conversation"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-14 h-14 bg-sidebar-bg rounded-2xl flex items-center justify-center mb-4">
              <span className="text-white text-xl font-bold">F</span>
            </div>
            <h2 className="text-lg font-semibold text-primary-dark mb-1">Artha AI</h2>
            <p className="text-sm text-muted max-w-xs mb-8">
              Ask questions about your money, spending, and future plans.
            </p>

            {/* Suggestions */}
            <div className="w-full max-w-lg">
              <p className="label-sm mb-3 text-center">Try asking</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    className="text-left text-sm px-3.5 py-2.5 rounded-xl border border-border bg-card-bg
                               hover:border-primary-accent hover:bg-primary-accent/5
                               transition-all duration-150 group flex items-center justify-between gap-2"
                    onClick={() => handleSuggestion(prompt)}
                  >
                    <span className="text-primary-dark">{prompt}</span>
                    <ChevronRight size={13} className="text-muted group-hover:text-primary-accent flex-shrink-0" aria-hidden="true" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} currency={currency} />
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex gap-2 animate-slide-up" aria-live="polite" aria-label="FIN4YOU is thinking">
            <div className="w-7 h-7 rounded-full bg-sidebar-bg flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-white text-xs font-bold">F</span>
            </div>
            <div className="chat-bubble-ai flex items-center gap-1 py-3.5 px-4">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-border pt-4">
        <form onSubmit={handleSubmit} className="flex items-end gap-3">
          <div className="flex-1 relative">
            <label htmlFor="copilot-input" className="sr-only">
              Ask FIN4YOU a financial question
            </label>
            <textarea
              id="copilot-input"
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your finances..."
              rows={1}
              className="form-input resize-none py-3 pr-12 leading-relaxed"
              style={{ minHeight: '48px', maxHeight: '140px' }}
              disabled={isLoading}
              aria-label="Financial question input"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2.5 bottom-2.5 w-8 h-8 bg-primary-accent text-white rounded-lg
                         flex items-center justify-center
                         hover:bg-accent-hover transition-colors
                         disabled:opacity-40 disabled:cursor-not-allowed"
              aria-label="Send message"
            >
              <Send size={14} aria-hidden="true" />
            </button>
          </div>
        </form>
        <p className="text-2xs text-muted/60 mt-2 text-center">
          FIN4YOU uses deterministic AI based on your actual financial data.
        </p>
      </div>
    </div>
  );
};
