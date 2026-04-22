"use client";

import * as React from "react";
import { Send, User, Bot, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Message = {
  role: "user" | "model";
  content: string;
};

export default function Home() {
  const [inputValue, setInputValue] = React.useState("");
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    // Lọc bỏ các tin nhắn trống để tránh lỗi API
    const chatHistory = messages
      .filter(msg => msg.content.trim() !== "")
      .map(msg => ({
        role: msg.role,
        parts: [{ text: msg.content }]
      }));

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [
            ...chatHistory,
            { role: "user", parts: [{ text: userMessage }] }
          ]
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        console.error("API Error:", errorBody);
        throw new Error(errorBody.error?.message || "Failed to fetch");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = "";
      let buffer = "";

      // Thêm tin nhắn trống của model để bắt đầu hiển thị
      setMessages((prev) => [...prev, { role: "model", content: "" }]);

      while (true) {
        const { done, value } = await reader?.read() || { done: true, value: undefined };
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Gemini streaming có thể trả về một mảng JSON [{}, {}] hoặc các object riêng lẻ
        // Logic này tìm kiếm các cặp ngoặc {} hoàn chỉnh
        let startIdx = buffer.indexOf('{');
        while (startIdx !== -1) {
          let stack = 0;
          let endIdx = -1;
          
          for (let i = startIdx; i < buffer.length; i++) {
            if (buffer[i] === '{') stack++;
            else if (buffer[i] === '}') {
              stack--;
              if (stack === 0) {
                endIdx = i;
                break;
              }
            }
          }
          
          if (endIdx !== -1) {
            const jsonStr = buffer.substring(startIdx, endIdx + 1);
            try {
              const json = JSON.parse(jsonStr);
              const text = json.candidates?.[0]?.content?.parts?.[0]?.text || "";
              assistantMessage += text;
              
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg && lastMsg.role === "model") {
                  lastMsg.content = assistantMessage;
                }
                return [...newMessages];
              });
            } catch (e) {
              console.warn("Lỗi parse chunk JSON:", e);
            }
            // Tiếp tục tìm object tiếp theo sau endIdx
            buffer = buffer.substring(endIdx + 1);
            startIdx = buffer.indexOf('{');
          } else {
            // Chưa có dấu đóng ngoặc hoàn chỉnh, chờ chunk tiếp theo
            break;
          }
        }
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { role: "model", content: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center p-4 overflow-hidden mesh-bg">
      {/* Visual Depth Layers */}
      <div className="absolute top-[-5%] left-[-5%] w-[40%] h-[40%] bg-blue-100/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-5%] right-[-5%] w-[40%] h-[40%] bg-indigo-100/20 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-3xl flex flex-col h-[85vh] z-10 animate-in fade-in zoom-in-95 duration-700 ease-out">
        {/* Chat Messages Area */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto mb-4 space-y-6 px-4 py-6 scrollbar-hide"
        >
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-60">
              <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center">
                <Bot className="w-8 h-8 text-indigo-500" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-zinc-900">Sẵn sàng hỗ trợ bạn</h2>
                <p className="text-sm text-zinc-500">Hãy bắt đầu cuộc hội thoại bằng cách nhập câu hỏi bên dưới.</p>
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div 
                key={index}
                className={cn(
                  "flex items-start gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300",
                  msg.role === "user" ? "flex-row-reverse" : "flex-row"
                )}
              >
                <div className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center shrink-0 border",
                  msg.role === "user" ? "bg-zinc-100 border-zinc-200" : "bg-indigo-50 border-indigo-100"
                )}>
                  {msg.role === "user" ? <User className="w-5 h-5 text-zinc-600" /> : <Bot className="w-5 h-5 text-indigo-500" />}
                </div>
                <div className={cn(
                  "max-w-[80%] rounded-2xl p-4 text-sm md:text-base leading-relaxed",
                  msg.role === "user" 
                    ? "bg-indigo-500 text-white rounded-tr-none shadow-sm" 
                    : "bg-white border border-zinc-200 text-zinc-800 rounded-tl-none shadow-sm"
                )}>
                  {msg.role === "user" ? (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  ) : (
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}
                  {isLoading && index === messages.length - 1 && !msg.content && (
                    <div className="flex gap-1 mt-1">
                      <span className="w-1.5 h-1.5 bg-zinc-300 rounded-full animate-bounce" />
                      <span className="w-1.5 h-1.5 bg-zinc-300 rounded-full animate-bounce [animation-delay:0.2s]" />
                      <span className="w-1.5 h-1.5 bg-zinc-300 rounded-full animate-bounce [animation-delay:0.4s]" />
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-2xl shadow-sm border border-zinc-200 p-2 pb-4 transition-all duration-500 hover:shadow-md focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-400">
          <div className="relative flex items-center">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Nhập câu hỏi hoặc lệnh của bạn..."
              className={cn(
                "w-full h-16 pl-6 pr-20 bg-transparent border-none shadow-none text-lg font-medium text-zinc-900",
                "placeholder:text-zinc-500 placeholder:font-medium focus-visible:ring-0",
                "transition-all duration-300"
              )}
            />
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              size="icon"
              className={cn(
                "absolute right-3 w-12 h-12 rounded-full",
                "bg-indigo-500 hover:bg-indigo-600 text-white transition-all duration-300 shadow-sm",
                "disabled:bg-indigo-500/20 disabled:text-indigo-300/50 disabled:shadow-none active:scale-95"
              )}
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5 fill-current" />}
              <span className="sr-only">Gửi</span>
            </Button>
          </div>
          
          <div className="flex justify-between px-7 text-[10px] font-semibold tracking-widest text-zinc-500 uppercase pointer-events-none">
            <span>AI-POWERED PROMPTING</span>
            <div className="flex items-center gap-1.5">
              <kbd className="font-sans">⌘</kbd>
              <span>ENTER TO SEND</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
