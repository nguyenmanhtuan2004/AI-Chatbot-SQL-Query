"use client";

import * as React from "react";
import { PaperPlaneRight, CircleNotch, Clock, List, X } from "@phosphor-icons/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

import { ChatService, type Message } from "@/lib/chat-service";

export default function Home() {
  const [inputValue, setInputValue] = React.useState("");
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
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

    try {
      setMessages((prev) => [...prev, { role: "model", content: "" }]);
      let assistantMessage = "";

      for await (const chunk of ChatService.sendMessage(userMessage, messages)) {
        assistantMessage += chunk;
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMsg = newMessages[newMessages.length - 1];
          if (lastMsg && lastMsg.role === "model") {
            lastMsg.content = assistantMessage;
          }
          return [...newMessages];
        });
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [...prev, { role: "model", content: "Xin lỗi, đã có lỗi xảy ra trong quá trình kết nối." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative h-screen flex flex-col items-center p-0 overflow-hidden mesh-bg font-sans selection:bg-primary/30">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-primary/5 rounded-full blur-[140px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-accent/5 rounded-full blur-[140px] pointer-events-none animate-pulse-slow [animation-delay:4s]" />

      {/* Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-[60] animate-in fade-in duration-300"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar - History */}
      <aside className={cn(
        "fixed top-0 left-0 h-full w-72 bg-black/95 backdrop-blur-2xl z-[70] shadow-2xl transition-all duration-500 ease-in-out border-r border-white/5",
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full p-6">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/30 shadow-[0_0_15px_rgba(var(--primary-rgb),0.1)]">
                <Clock size={20} weight="bold" className="text-primary" />
              </div>
              <h2 className="text-sm font-black text-white uppercase tracking-widest">History</h2>
            </div>
            <button 
              onClick={() => setIsSidebarOpen(false)}
              className="p-2 rounded-full hover:bg-white/10 text-white/40 hover:text-white transition-all active:scale-90"
            >
              <X size={20} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 scrollbar-hide flex flex-col items-center justify-center text-center px-4">
            <div className="w-14 h-14 rounded-[22px] bg-white/5 flex items-center justify-center mb-5 border border-white/10 shadow-inner">
              <Clock size={24} weight="light" className="text-white/40" />
            </div>
            <p className="text-[11px] font-bold text-white/40 uppercase tracking-[0.2em]">No history yet</p>
          </div>

          <div className="pt-6 border-t border-white/5 mt-auto">
            <button className="w-full py-3 rounded-xl bg-primary text-white text-[12px] font-bold uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-primary/20">
              New Chat
            </button>
          </div>
        </div>
      </aside>

      {/* Floating Header */}
      <header className="fixed top-6 left-0 right-0 z-50 px-8 flex justify-between items-center pointer-events-none animate-in fade-in duration-1000">
        {/* Left: Toggle & Branding */}
        <div className="flex items-center gap-4 pointer-events-auto">
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="w-10 h-10 flex items-center justify-center rounded-2xl glass-panel border border-primary/10 text-foreground/60 hover:text-primary hover:border-primary/30 transition-all shadow-sm active:scale-90"
          >
            <List size={22} weight="bold" />
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-sm font-black tracking-[0.1em] text-foreground uppercase">
              SQL AI <span className="text-primary/60">Insight</span>
            </h1>
            <div className="flex items-center gap-2">
              <div className="h-3 w-[1px] bg-foreground/10 hidden sm:block" />
              <div className={cn(
                "px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider border",
                process.env.NEXT_PUBLIC_API_MODE === 'dotnet' 
                  ? "bg-blue-500/10 text-blue-500 border-blue-500/20" 
                  : "bg-amber-500/10 text-amber-500 border-amber-500/20"
              )}>
                {process.env.NEXT_PUBLIC_API_MODE === 'dotnet' ? ".NET API" : "Direct Mode"}
              </div>
            </div>
            <p className="text-[9px] font-bold text-muted-foreground/30 uppercase tracking-[0.3em] hidden sm:block">Powered by Gemini</p>
          </div>
        </div>

        {/* Right: Nav Chips */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <div className="flex items-center p-1 rounded-full glass-panel border border-primary/5 shadow-sm">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-1.5 rounded-full text-[10px] font-black text-muted-foreground/60 hover:text-primary transition-all active:scale-95 uppercase tracking-[0.15em]"
            >
              New Chat
            </button>
          </div>
        </div>
      </header>

      <div className="w-full max-w-3xl flex flex-col h-full pt-16 z-10 mx-auto">
        {/* Chat Messages Area with Mask */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto space-y-8 px-4 py-8 scrollbar-hide pb-40"
          style={{
            maskImage: 'linear-gradient(to bottom, transparent, black 60px, black calc(100% - 120px), transparent)',
            WebkitMaskImage: 'linear-gradient(to bottom, transparent, black 60px, black calc(100% - 120px), transparent)'
          }}
        >
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center animate-in fade-in zoom-in-95 duration-1000">
              <div className="max-w-2xl mb-12">
                <h2 className="text-4xl font-heading font-extrabold text-foreground mb-4 tracking-tight leading-tight">
                  Tương lai của <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Truy vấn Dữ liệu</span>
                </h2>
                <p className="text-muted-foreground text-lg leading-relaxed max-w-lg mx-auto">
                  Khám phá dữ liệu của bạn thông qua sức mạnh AI. Lịch sử truy vấn hiện đã sẵn sàng ở Sidebar bên trái.
                </p>
              </div>

              <div className="flex flex-wrap justify-center gap-3 w-full max-w-2xl">
                {[
                  { title: "Phân tích Doanh thu", value: "Liệt kê doanh thu theo từng tháng trong năm nay" },
                  { title: "Schema", value: "Cấu trúc bảng Orders và Customers" },
                  { title: "Khách hàng", value: "Top 10 khách hàng có giá trị đơn hàng cao nhất" },
                  { title: "Tối ưu Query", value: "Tối ưu hóa query SQL cho bảng lớn" }
                ].map((suggestion, i) => (
                  <button 
                    key={i}
                    onClick={() => setInputValue(suggestion.value)}
                    className="px-4 py-2.5 rounded-xl glass-panel border border-primary/10 hover:border-primary/30 hover:bg-primary/5 text-[13px] font-semibold text-muted-foreground hover:text-primary transition-all duration-300 shadow-sm hover:shadow-md"
                  >
                    {suggestion.title}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div 
                key={index}
                className={cn(
                  "flex w-full animate-in fade-in slide-in-from-bottom-4 duration-500",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                <div className={cn(
                  "relative max-w-full rounded-2xl p-5 md:p-6 text-[15px] md:text-base leading-relaxed transition-all shadow-lg hover:shadow-xl",
                  msg.role === "user" 
                    ? "bg-white text-foreground border border-black/5 rounded-tr-none" 
                    : "glass-panel border border-primary/10 text-foreground rounded-tl-none"
                )}>
                  {msg.role === "user" ? (
                    <div className="whitespace-pre-wrap font-semibold text-foreground/90">{msg.content}</div>
                  ) : (
                    <div className="markdown-content prose-headings:font-heading prose-headings:font-bold">
                      {msg.content ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      ) : isLoading && index === messages.length - 1 && (
                        <div className="flex gap-2 py-2">
                          <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]" />
                          <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.15s]" />
                          <span className="w-2 h-2 bg-primary/40 rounded-full animate-bounce" />
                        </div>
                      )}
                    </div>
                  )}
                  {msg.role === "model" && msg.content && (
                    <div className="mt-4 pt-4 border-t border-primary/10 flex items-center gap-3 animate-in fade-in duration-500">
                      <div className="px-2 py-0.5 rounded bg-primary/10 text-[10px] font-bold text-primary uppercase tracking-tighter">AI INSIGHT</div>
                      <div className="text-[10px] text-muted-foreground/40 font-medium">Chat can make mistakes. Check important info.</div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Floating Input Dock */}
        <div className="fixed bottom-10 left-1/2 -translate-x-1/2 w-full max-w-3xl px-4 z-50 animate-in fade-in slide-in-from-bottom-6 duration-1000">
          <div className="glass-panel rounded-full p-1.5 shadow-2xl shadow-primary/10 border border-primary/10 backdrop-blur-2xl">
            <div className="relative flex items-center">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                placeholder="Hỏi về cơ sở dữ liệu của bạn..."
                className="w-full h-12 pl-6 pr-16 bg-transparent border-none focus-visible:ring-0 text-base font-medium placeholder:text-muted-foreground/30"
              />
              <Button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                size="icon"
                className="absolute right-1.5 w-10 h-10 rounded-full bg-gradient-to-br from-primary via-primary to-primary/80 text-white shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:scale-105 active:scale-95 transition-all duration-300 border border-white/20"
              >
                {isLoading ? (
                  <CircleNotch size={20} className="animate-spin" />
                ) : (
                  <PaperPlaneRight size={20} weight="bold" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
