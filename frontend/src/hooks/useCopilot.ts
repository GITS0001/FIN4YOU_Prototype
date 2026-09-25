import { useState, useCallback } from 'react';
import { copilotApi } from '../api/copilot';
import { DEMO_USER_ID } from '../api/client';
import type { ChatMessage, CopilotResponse, ApiError } from '../types';

let messageIdCounter = 0;
const generateId = () => `msg-${++messageIdCounter}-${Date.now()}`;

export function useCopilot(userId: string = DEMO_USER_ID) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message immediately
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response: CopilotResponse = await copilotApi.query({
          user_id: userId,
          message: content.trim(),
        });

        const aiMessage: ChatMessage = {
          id: generateId(),
          role: 'ai',
          content: response.response,
          response,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);
      } catch (err) {
        const apiError = err as ApiError;
        setError(apiError);

        const errorMessage: ChatMessage = {
          id: generateId(),
          role: 'ai',
          content: apiError.message || "I'm sorry, I couldn't process your request right now.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, isLoading]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
