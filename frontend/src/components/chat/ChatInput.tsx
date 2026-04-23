import * as React from "react";
import { PaperPlaneRight, CircleNotch } from "@phosphor-icons/react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSend, isLoading }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      onSend();
    }
  };

  return (
    <div className="fixed bottom-10 left-1/2 -translate-x-1/2 w-full max-w-3xl px-4 z-50 animate-in fade-in slide-in-from-bottom-6 duration-1000">
      <div className="glass-panel rounded-full p-1.5 shadow-2xl shadow-primary/10 border border-primary/10 backdrop-blur-2xl">
        <div className="relative flex items-center">
          <Input
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Hỏi về cơ sở dữ liệu của bạn..."
            className="w-full h-12 pl-6 pr-16 bg-transparent border-none focus-visible:ring-0 text-base font-medium placeholder:text-muted-foreground/30"
          />
          <Button
            onClick={onSend}
            disabled={!value.trim() || isLoading}
            size="icon"
            className="absolute right-1.5 w-11 h-11 rounded-full bg-gradient-to-br from-primary via-primary to-primary/80 text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:scale-105 active:scale-95 transition-all duration-300 border border-white/20"
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
