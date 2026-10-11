import React, { useEffect, useRef, useState } from 'react';
import { useCopilot } from '../../hooks/useCopilot';
import { useFinancialProfile } from '../../hooks/useFinancialProfile';
import { useBackendStatus } from '../../hooks/useBackendStatus';
import { ChatMessage } from './ChatMessage';
import { Send, Trash2, Sparkles, Wifi, CreditCard, ShieldCheck, Car, TrendingUp, BarChart } from 'lucide-react';
import { formatCurrencySymbol } from '../../utils/format';
import arthaAiLogo from '../../assets/artha_ai_logo.jpg';

export const CopilotChat: React.FC = () => {
  const { data: profile } = useFinancialProfile();
  const { status } = useBackendStatus();
  const { messages, isLoading, sendMessage, clearMessages } = useCopilot();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const currency = profile?.home_currency || 'USD';
  const sym = formatCurrencySymbol(currency);

  const SUGGESTED_PROMPTS = [
    { icon: CreditCard, label: 'Where am I spending the most?', category: 'Spending' },
    { icon: TrendingUp, label: `What if I spend ${sym}2,000 less on food?`, category: 'Simulation' },
    { icon: ShieldCheck, label: `Can I afford a ${sym}15,000 purchase?`, category: 'Affordability' },
    { icon: BarChart, label: 'What happens if my income drops by 20%?', category: 'Simulation' },
  ];

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
    <div className="flex flex-col" style={{ height: '100%', minHeight: 0 }}>
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-2 border-b border-border/70">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full overflow-hidden shadow-sm flex items-center justify-center bg-white border border-border p-0.5">
            <img src={arthaAiLogo} alt="Artha AI Logo" className="w-full h-full object-contain" />
          </div>
          <div className="w-2.5 h-2.5 rounded-full bg-positive animate-pulse ml-1" />
          <span className="text-xs font-semibold text-primary-dark tracking-wide">Artha AI Assistant Engine</span>
          <span className="text-2xs bg-primary-accent/10 text-primary-accent px-2 py-0.5 rounded-full font-medium border border-primary-accent/20">v2.4 Ready</span>
        </div>

        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              className="btn-ghost flex items-center gap-1.5 text-xs text-muted hover:text-danger"
              onClick={clearMessages}
              aria-label="Clear conversation"
            >
              <Trash2 size={13} aria-hidden="true" />
              Clear Chat
            </button>
          )}
          {profile && (
            <span className="badge-neutral text-xs">
              {profile.user_id} · {profile.home_currency}
            </span>
          )}
        </div>
      </div>

      {/* Messages area */}
      <div
        className="flex-1 overflow-y-auto space-y-4 py-2 px-1"
        role="log"
        aria-label="Conversation"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-8">
            <div className="w-16 h-16 rounded-2xl overflow-hidden shadow-lg shadow-primary-accent/20 flex items-center justify-center mb-4 bg-white border border-border p-1">
              <img src={arthaAiLogo} alt="Artha AI" className="w-full h-full object-contain" />
            </div>
            <h2 className="text-xl font-bold text-primary-dark mb-1">How can I help your finances today?</h2>
            <p className="text-xs text-muted max-w-sm mb-4">
              Ask natural-language questions to analyze spending, run scenario simulations, or verify affordability constraints.
            </p>

            {/* Backend status hint */}
            {status === 'offline' && (
              <div className="flex items-center gap-2 mb-6 px-4 py-2.5 bg-warning/10 border border-warning/30 rounded-xl">
                <Wifi size={14} className="text-warning flex-shrink-0" />
                <p className="text-xs font-medium text-warning-dark">Backend server offline — start server on port 8000 for AI responses.</p>
              </div>
            )}

            {/* Suggestions Grid */}
            <div className="w-full max-w-xl mt-2">
              <p className="text-2xs font-semibold text-muted uppercase tracking-wider mb-3 text-center">Suggested Prompts</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {SUGGESTED_PROMPTS.map((item) => (
                  <button
                    key={item.label}
                    className="text-left p-3 rounded-xl border border-border bg-card-bg shadow-sm hover:border-primary-accent hover:shadow-md hover:bg-primary-accent/5 transition-all duration-200 group flex items-start gap-3"
                    onClick={() => handleSuggestion(item.label)}
                  >
                    <div className="w-8 h-8 rounded-lg bg-primary-accent/10 text-primary-accent flex items-center justify-center flex-shrink-0 group-hover:bg-primary-accent group-hover:text-white transition-colors">
                      <item.icon size={16} aria-hidden="true" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-2xs font-semibold text-primary-accent uppercase tracking-wider block mb-0.5">{item.category}</span>
                      <p className="text-xs font-medium text-primary-dark line-clamp-2">{item.label}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            currency={currency}
            onSelectPrompt={handleSuggestion}
          />
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex gap-2.5 animate-slide-up" aria-live="polite" aria-label="Artha AI is analyzing">
            <div className="w-8 h-8 rounded-xl bg-brand-gradient flex items-center justify-center flex-shrink-0 shadow-xs mt-0.5">
              <Sparkles size={14} className="text-white animate-pulse" />
            </div>
            <div className="flex items-center gap-1.5 py-3 px-4 rounded-2xl rounded-tl-sm bg-card-bg border border-border shadow-card">
              <span className="text-xs text-muted font-medium mr-1">Artha AI is synthesizing data</span>
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-border/80 pt-3 mt-1 bg-background relative z-10">
        <form onSubmit={handleSubmit} className="flex items-end gap-2.5">
          <div className="flex-1 relative">
            <label htmlFor="copilot-input" className="sr-only">
              Ask Artha AI a financial question
            </label>
            <textarea
              id="copilot-input"
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Artha AI about spending, affordability, or scenario forecasts (Press Enter to send)..."
              rows={1}
              className="form-input resize-none py-3 pl-4 pr-12 text-sm leading-relaxed rounded-xl shadow-sm border border-border focus:border-primary-accent focus:ring-1 focus:ring-primary-accent bg-card-bg"
              style={{ minHeight: '48px', maxHeight: '140px' }}
              disabled={isLoading}
              aria-label="Financial question input"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 bottom-2 w-8 h-8 bg-gradient-to-r from-primary-accent to-purple text-white rounded-lg
                         flex items-center justify-center shadow-xs hover:shadow-md hover:scale-105 active:scale-95 transition-all
                         disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none"
              aria-label="Send message"
            >
              <Send size={14} aria-hidden="true" />
            </button>
          </div>
        </form>
        <div className="flex items-center justify-between mt-2 px-1">
          <p className="text-2xs text-muted">
            ⚡ Grounded by deterministic financial engines &amp; cash flow models.
          </p>
          <span className="text-2xs text-muted hidden sm:inline">Press Shift + Enter for new line</span>
        </div>
      </div>
    </div>
  );
};
