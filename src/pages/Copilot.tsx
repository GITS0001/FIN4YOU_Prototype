import React from 'react';
import { CopilotChat } from '../components/copilot/CopilotChat';

export const Copilot: React.FC = () => {
  return (
    <div className="h-[calc(100dvh-var(--topbar-height)-2rem)] sm:h-[calc(100dvh-var(--topbar-height)-3rem)]">
      <CopilotChat />
    </div>
  );
};
