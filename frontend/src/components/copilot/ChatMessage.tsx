import React from 'react';
import type { ChatMessage as ChatMessageType } from '../../types';
import { Bot, User } from 'lucide-react';
import { ConfidenceBadge } from '../shared/ConfidenceBadge';
import { CopilotStructuredResponse } from './CopilotStructuredResponse';

interface ChatMessageProps {
  message: ChatMessageType;
  currency: string;
}



export const ChatMessage: React.FC<ChatMessageProps> = ({ message, currency }) => {
  const isUser = message.role === 'user';
  const response = message.response;

  if (isUser) {
    return (
      <div className="flex justify-end gap-2 animate-slide-up">
        <div className="chat-bubble-user max-w-sm">{message.content}</div>
        <div className="w-7 h-7 rounded-full bg-primary-accent flex items-center justify-center flex-shrink-0 mt-0.5">
          <User size={14} className="text-white" aria-hidden="true" />
        </div>
      </div>
    );
  }

  // AI message
  return (
    <div className="flex gap-2 animate-slide-up">
      <div className="w-7 h-7 rounded-full bg-sidebar-bg flex items-center justify-center flex-shrink-0 mt-0.5">
        <Bot size={14} className="text-white" aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="chat-bubble-ai">
          <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {/* Structured result rendering */}
          {response && <CopilotStructuredResponse response={response} currency={currency} />}

          {/* Footer: confidence + data sources */}
          {response && (
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-border/50">
              <ConfidenceBadge confidence={response.confidence} />
              {response.data_sources?.length > 0 && (
                <span className="text-2xs text-muted/60 truncate max-w-[160px]" title={response.data_sources.join(', ')}>
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
