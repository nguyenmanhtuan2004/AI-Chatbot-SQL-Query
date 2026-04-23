import React, { useRef, useEffect } from "react";
import { PaperPlaneRight, CircleNotch } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSend, isLoading }) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onSend();
      }
    }
  };

  return (
    <div className="w-full px-4 pb-8 pt-2 z-50 animate-in fade-in slide-in-from-bottom-6 duration-1000 shrink-0">
      <div className="glass-panel rounded-3xl p-1.5 shadow-2xl shadow-primary/10 border border-primary/10 backdrop-blur-2xl transition-all duration-300">
        <div className="relative flex">
          <textarea
            id="chat-input"
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Hỏi về cơ sở dữ liệu của bạn..."
            className="w-full min-h-[48px] max-h-[200px] py-3 pl-6 pr-16 bg-transparent border-none focus-visible:ring-0 focus-visible:outline-none text-base font-medium placeholder:text-muted-foreground/30 resize-none overflow-y-auto outline-none"
            rows={1}
            style={{ scrollbarWidth: "none" }}
          />
          <Button
            onClick={onSend}
            disabled={!value.trim() || isLoading}
            size="icon"
            className="absolute right-1.5 bottom-0.5 w-11 h-11 rounded-full bg-gradient-to-br from-primary via-primary to-primary/80 text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:scale-105 active:scale-95 transition-all duration-300 border border-white/20"
          >
            {isLoading ? (
              <CircleNotch size={22} className="animate-spin" />
            ) : (
              <PaperPlaneRight size={22} weight="bold" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
