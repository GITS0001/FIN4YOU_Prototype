import React from 'react';
import { Sparkles, ArrowRight, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';

interface StructuredMessageContentProps {
  content: string;
  currency?: string;
  onSelectPrompt?: (prompt: string) => void;
}

/**
 * Extracts a prompt question string from an "Ask: ..." or quoted string.
 */
function extractPrompt(text: string): string | null {
  const askMatch = text.match(/Ask:\s*["“'«]([^"”'»]+)["”'»]/i);
  if (askMatch) return askMatch[1].trim();

  const quotedMatch = text.match(/^["“'«]([^"”'»]+)["”'»]$/);
  if (quotedMatch && (quotedMatch[1].includes('?') || quotedMatch[1].toLowerCase().includes('can i') || quotedMatch[1].toLowerCase().includes('what happens'))) {
    return quotedMatch[1].trim();
  }

  // Check for bullet like • “Can I afford a phone worth ₹60,000 next month?”
  const bulletQuoted = text.match(/^[•\-*]?\s*["“'«]([^"”'»]+)["”'»]/);
  if (bulletQuoted && (bulletQuoted[1].includes('?') || bulletQuoted[1].toLowerCase().includes('can i') || bulletQuoted[1].toLowerCase().includes('what happens'))) {
    return bulletQuoted[1].trim();
  }

  return null;
}

/**
 * Renders inline Markdown (bold, italic, tags, currencies).
 */
function renderInline(text: string, onSelectPrompt?: (p: string) => void): React.ReactNode {
  // Normalize any accidental naira symbol to rupee in the Indian context if needed
  const normalized = text.replace(/₦/g, '₹');

  // Split by markdown bold (**text**)
  const parts = normalized.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|<br\s*\/?>)/g);

  return parts.map((part, index) => {
    if (!part) return null;

    if (part.startsWith('**') && part.endsWith('**')) {
      const inner = part.slice(2, -2);
      return (
        <strong key={index} className="font-semibold text-primary-dark">
          {inner}
        </strong>
      );
    }

    if (part.startsWith('*') && part.endsWith('*')) {
      const inner = part.slice(1, -1);
      return (
        <em key={index} className="italic text-muted">
          {inner}
        </em>
      );
    }

    if (part.startsWith('`') && part.endsWith('`')) {
      const inner = part.slice(1, -1);
      return (
        <code key={index} className="px-1.5 py-0.5 rounded bg-muted/15 font-mono text-2xs text-primary-accent border border-border">
          {inner}
        </code>
      );
    }

    if (part.match(/<br\s*\/?>/i)) {
      return <br key={index} />;
    }

    return <span key={index}>{part}</span>;
  });
}

export const StructuredMessageContent: React.FC<StructuredMessageContentProps> = ({
  content,
  currency = 'INR',
  onSelectPrompt,
}) => {
  if (!content) return null;

  // Split lines
  const rawLines = content.split('\n');

  // Group lines into blocks (tables, lists, headers, paragraphs, dividers)
  const blocks: Array<{
    type: 'header' | 'table' | 'prompt-card' | 'list-item' | 'hr' | 'paragraph' | 'greeting-card';
    level?: number;
    text?: string;
    items?: string[];
    headers?: string[];
    rows?: string[][];
  }> = [];

  let i = 0;
  while (i < rawLines.length) {
    const line = rawLines[i].trim();

    if (!line) {
      i++;
      continue;
    }

    // Horizontal Rule
    if (/^---+$|^\*\*\*+$/.test(line)) {
      blocks.push({ type: 'hr' });
      i++;
      continue;
    }

    // Greeting Banner (detect "Hello! I’m Artha AI" or similar)
    if (/Hello!\s*I[’']?m\s*Artha/i.test(line)) {
      blocks.push({ type: 'greeting-card', text: line });
      i++;
      continue;
    }

    // Headings: #, ##, ###
    const headerMatch = line.match(/^(#{1,4})\s+(.+)$/);
    if (headerMatch) {
      blocks.push({
        type: 'header',
        level: headerMatch[1].length,
        text: headerMatch[2],
      });
      i++;
      continue;
    }

    // Table detection: line starts and ends with | or contains |
    if (line.startsWith('|') && line.endsWith('|')) {
      const tableLines: string[] = [];
      while (i < rawLines.length && rawLines[i].trim().startsWith('|') && rawLines[i].trim().endsWith('|')) {
        tableLines.push(rawLines[i].trim());
        i++;
      }

      if (tableLines.length >= 2) {
        // Parse header and rows
        const headers = tableLines[0]
          .split('|')
          .slice(1, -1)
          .map((h) => h.trim());

        // Skip separator row (|---|---|)
        const rowLines = tableLines.slice(1).filter((l) => !/^\|[\s\-:|]+\|$/.test(l));
        const rows = rowLines.map((rowLine) =>
          rowLine
            .split('|')
            .slice(1, -1)
            .map((c) => c.trim())
        );

        blocks.push({
          type: 'table',
          headers,
          rows,
        });
        continue;
      }
    }

    // Single-line or bullet that is a prompt suggestion
    const promptText = extractPrompt(line);
    if (promptText && onSelectPrompt) {
      blocks.push({ type: 'prompt-card', text: promptText });
      i++;
      continue;
    }

    // Regular list item: starts with •, -, * or 1., 2.
    if (/^[•\-*]\s+/.test(line) || /^\d+\.\s+/.test(line)) {
      const cleanLine = line.replace(/^[•\-*]\s+/, '').replace(/^\d+\.\s+/, '');
      blocks.push({ type: 'list-item', text: cleanLine });
      i++;
      continue;
    }

    // Normal paragraph
    blocks.push({ type: 'paragraph', text: line });
    i++;
  }

  return (
    <div className="space-y-2.5 text-xs sm:text-sm text-primary-dark">
      {blocks.map((block, idx) => {
        // 1. Greeting Card
        if (block.type === 'greeting-card') {
          return (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-gradient-to-r from-primary-accent/15 via-purple/10 to-primary-accent/5 border border-primary-accent/30 shadow-xs flex items-center gap-3"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary-accent to-purple text-white flex items-center justify-center flex-shrink-0 shadow-sm">
                <Sparkles size={18} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-2xs uppercase tracking-wider font-semibold text-primary-accent">
                  Financial Health Copilot
                </div>
                <h3 className="text-sm font-bold text-primary-dark leading-tight mt-0.5">
                  {renderInline(block.text || 'Hello! I’m Artha AI', onSelectPrompt)}
                </h3>
              </div>
            </div>
          );
        }

        // 2. Heading
        if (block.type === 'header') {
          return (
            <div key={idx} className="pt-2 pb-1 border-b border-border/60 first:pt-0">
              <h4 className="text-xs sm:text-sm font-bold text-primary-dark flex items-center gap-1.5 tracking-tight">
                {renderInline(block.text || '', onSelectPrompt)}
              </h4>
            </div>
          );
        }

        // 3. Prompt Card (interactive)
        if (block.type === 'prompt-card') {
          const prompt = block.text || '';
          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectPrompt?.(prompt)}
              className="w-full text-left flex items-center justify-between gap-2.5 p-2.5 rounded-xl border border-primary-accent/25 bg-primary-accent/5 hover:bg-primary-accent/15 hover:border-primary-accent hover:shadow-xs transition-all duration-150 group cursor-pointer"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <span className="w-5 h-5 rounded-md bg-primary-accent/20 text-primary-accent flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                  <Sparkles size={12} />
                </span>
                <span className="text-xs font-medium text-primary-dark group-hover:text-primary-accent truncate">
                  {prompt}
                </span>
              </div>
              <span className="text-2xs bg-primary-accent/15 text-primary-accent px-2 py-0.5 rounded-md font-semibold flex items-center gap-1 flex-shrink-0 opacity-80 group-hover:opacity-100">
                Try this <ArrowRight size={10} />
              </span>
            </button>
          );
        }

        // 4. List item
        if (block.type === 'list-item') {
          return (
            <div key={idx} className="flex items-start gap-2.5 py-0.5 pl-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-accent flex-shrink-0 mt-1.5" />
              <div className="flex-1 leading-relaxed text-xs sm:text-sm">
                {renderInline(block.text || '', onSelectPrompt)}
              </div>
            </div>
          );
        }

        // 5. Divider
        if (block.type === 'hr') {
          return (
            <hr
              key={idx}
              className="my-3 border-0 h-px bg-gradient-to-r from-transparent via-border to-transparent"
            />
          );
        }

        // 6. Markdown Table
        if (block.type === 'table') {
          const headers = block.headers || [];
          const rows = block.rows || [];

          return (
            <div key={idx} className="my-3 overflow-x-auto rounded-xl border border-border bg-card-bg shadow-xs">
              <table className="w-full text-left text-xs border-collapse">
                {headers.length > 0 && (
                  <thead>
                    <tr className="border-b border-border bg-muted/20 text-muted uppercase text-2xs tracking-wider">
                      {headers.map((h, hIdx) => (
                        <th key={hIdx} className="py-2.5 px-3 font-semibold">
                          {renderInline(h, onSelectPrompt)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                )}
                <tbody className="divide-y divide-border/40">
                  {rows.map((row, rIdx) => (
                    <tr key={rIdx} className="hover:bg-primary-accent/5 transition-colors">
                      {row.map((cell, cIdx) => {
                        // Check if cell contains a prompt query
                        const cellPrompt = extractPrompt(cell);
                        const isPlaceholder = cell.includes('(none provided yet') || cell.includes('(none listed') || cell.includes('(none at this moment');

                        return (
                          <td key={cIdx} className="py-2.5 px-3 text-primary-dark align-top">
                            {isPlaceholder ? (
                              <span className="text-muted italic text-2xs">{cell}</span>
                            ) : cellPrompt && onSelectPrompt ? (
                              <button
                                type="button"
                                onClick={() => onSelectPrompt(cellPrompt)}
                                className="inline-flex items-center gap-1.5 text-xs text-primary-accent font-medium hover:underline text-left"
                              >
                                <Sparkles size={11} className="flex-shrink-0" />
                                {cellPrompt}
                              </button>
                            ) : (
                              renderInline(cell, onSelectPrompt)
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        // 7. Standard Paragraph
        return (
          <p key={idx} className="leading-relaxed">
            {renderInline(block.text || '', onSelectPrompt)}
          </p>
        );
      })}
    </div>
  );
};
