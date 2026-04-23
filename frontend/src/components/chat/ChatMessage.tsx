import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { type Message } from "@/lib/chat-service";

interface ChatMessageProps {
  message: Message;
  isLoading?: boolean;
  isLast?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, isLoading, isLast }) => {
  const isUser = message.role === "user";

  return (
    <div className={cn(
      "flex w-full animate-in fade-in slide-in-from-bottom-4 duration-500",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "relative max-w-full md:max-w-[75ch] rounded-2xl p-5 md:p-6 text-[15px] md:text-base leading-relaxed transition-all shadow-lg hover:shadow-xl",
        isUser 
          ? "bg-white text-foreground border border-black/5 rounded-tr-none" 
          : "glass-panel border border-primary/10 text-foreground rounded-tl-none"
      )}>
        {isUser ? (
          <div className="whitespace-pre-wrap font-semibold text-foreground/90">{message.content}</div>
        ) : (
          <div className="markdown-content prose-headings:font-heading prose-headings:font-bold">
            {message.content ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            ) : isLoading && isLast && (
              <div className="flex gap-2 py-2">
                <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce" />
              </div>
            )}
          </div>
        )}
        
        {!isUser && message.content && (
          <div className="mt-4 pt-4 border-t border-primary/10 flex items-center gap-3 animate-in fade-in duration-500">
            <div className="px-2 py-0.5 rounded bg-primary/10 text-[10px] font-bold text-primary uppercase tracking-tighter">AI INSIGHT</div>
            <div className="text-[10px] text-muted-foreground/40 font-medium">Chat can make mistakes. Check important info.</div>
          </div>
        )}
      </div>
    </div>
  );
};
