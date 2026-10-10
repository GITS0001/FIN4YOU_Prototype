import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MarkdownMessage({ content, isBot }) {
  if (!isBot) {
    return <span className="whitespace-pre-wrap">{content}</span>;
  }

  return (
    <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed text-xs sm:text-sm">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="text-base font-bold my-2 text-gray-900 border-b pb-1 font-display">{children}</h1>,
          h2: ({ children }) => <h2 className="text-sm font-bold mt-3 mb-1.5 text-gray-900 font-display">{children}</h2>,
          h3: ({ children }) => <h3 className="text-xs font-bold mt-2.5 mb-1 text-gray-900 font-display">{children}</h3>,
          p: ({ children }) => <p className="my-1.5 leading-relaxed font-sans">{children}</p>,
          ul: ({ children }) => <ul className="list-disc pl-4 my-2 space-y-1 text-xs sm:text-sm">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-4 my-2 space-y-1 text-xs sm:text-sm">{children}</ol>,
          li: ({ children }) => <li className="my-0.5 leading-normal">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-3 border-[#2563EB] bg-blue-50/60 px-3 py-1.5 my-2 rounded-r-lg text-xs italic text-gray-700">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-3 border-gray-200" />,
          table: ({ children }) => (
            <div className="overflow-x-auto my-3 rounded-xl border border-gray-200 shadow-2xs">
              <table className="min-w-full text-xs text-left divide-y divide-gray-200">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-gray-100/90 font-bold text-gray-800 text-[11px] uppercase tracking-wider">{children}</thead>,
          tbody: ({ children }) => <tbody className="divide-y divide-gray-100 bg-white">{children}</tbody>,
          tr: ({ children }) => <tr className="hover:bg-blue-50/40 transition-colors">{children}</tr>,
          th: ({ children }) => <th className="px-3 py-2 font-bold">{children}</th>,
          td: ({ children }) => <td className="px-3 py-2 text-gray-700">{children}</td>,
          code: ({ inline, children }) =>
            inline ? (
              <code className="bg-gray-100 text-[#2563EB] font-mono text-[11px] px-1.5 py-0.5 rounded border border-gray-200">
                {children}
              </code>
            ) : (
              <pre className="bg-gray-900 text-gray-100 p-3 rounded-xl font-mono text-xs overflow-x-auto my-2">
                <code>{children}</code>
              </pre>
            ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
