import React from 'react';
import type { ChatMessage as ChatMessageType } from '../../types';
import { Bot, User, ArrowRight } from 'lucide-react';
import { ConfidenceBadge } from '../shared/ConfidenceBadge';
import { CopilotStructuredResponse } from './CopilotStructuredResponse';
import { useNavigate } from 'react-router-dom';

interface ChatMessageProps {
  message: ChatMessageType;
  currency: string;
}



export const ChatMessage: React.FC<ChatMessageProps> = ({ message, currency }) => {
  const navigate = useNavigate();
  const isUser = message.role === 'user';
  const response = message.response;

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 animate-slide-up group">
        <div className="bg-gradient-to-br from-primary-accent to-purple text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%] sm:max-w-[75%] shadow-md shadow-primary-accent/10">
          <p className="leading-relaxed whitespace-pre-wrap text-sm">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-primary-accent/20 flex items-center justify-center flex-shrink-0 mt-auto border border-primary-accent/30 shadow-sm">
          <User size={15} className="text-primary-accent" aria-hidden="true" />
        </div>
      </div>
    );
  }

  // AI message
  return (
    <div className="flex gap-3 animate-slide-up group">
      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-accent to-purple flex items-center justify-center flex-shrink-0 mt-auto shadow-md shadow-primary-accent/20">
        <Bot size={15} className="text-white" aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="bg-card-bg border border-border shadow-sm rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-primary-dark max-w-[95%] sm:max-w-[85%]">
          <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {/* Structured result rendering */}
          {response && <CopilotStructuredResponse response={response} currency={currency} />}

          {/* Action Links */}
          {response?.action_links && response.action_links.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {response.action_links.map((link, idx) => (
                <button
                  key={idx}
                  onClick={() => navigate(link.url)}
                  className="flex items-center gap-1 text-xs font-medium bg-primary-accent/10 text-primary-accent px-3 py-1.5 rounded-lg hover:bg-primary-accent/20 transition-colors"
                >
                  {link.label}
                  <ArrowRight size={12} />
                </button>
              ))}
            </div>
          )}

          {/* Footer: confidence + data sources */}
          {response && (
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-border/50">
              <ConfidenceBadge confidence={response.confidence} />
              {response.data_sources?.length > 0 && (
                <span className="text-2xs text-muted truncate max-w-[160px] bg-background px-2 py-1 rounded-md border border-border" title={response.data_sources.join(', ')}>
                  {response.data_sources[0]}{response.data_sources.length > 1 ? ` +${response.data_sources.length - 1}` : ''}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
