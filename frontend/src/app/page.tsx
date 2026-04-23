"use client";

import * as React from "react";
import { ChatService, type Message } from "@/lib/chat-service";
import { useChatHistory } from "@/lib/use-chat-history";
import { Sidebar } from "@/components/chat/Sidebar";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";

export default function Home() {
  const { 
    sessions, 
    currentSession, 
    currentSessionId, 
    createNewChat, 
    saveChat, 
    deleteSession, 
    selectSession 
  } = useChatHistory();

  const [inputValue, setInputValue] = React.useState("");
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  // Sync messages when current session changes
  React.useEffect(() => {
    if (currentSession) {
      setMessages(currentSession.messages);
    } else {
      setMessages([]);
    }
  }, [currentSessionId, currentSession]);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    
    const newMessages: Message[] = [...messages, { role: "user", content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const assistantIdx = newMessages.length;
      const updatedMessagesWithPlaceholder = [...newMessages, { role: "model", content: "" } as Message];
      setMessages(updatedMessagesWithPlaceholder);
      
      let assistantMessage = "";

      for await (const chunk of ChatService.sendMessage(userMessage, messages)) {
        assistantMessage += chunk;
        setMessages((prev) => {
          const newMsgs = [...prev];
          const lastMsg = newMsgs[newMsgs.length - 1];
          if (lastMsg && lastMsg.role === "model") {
            lastMsg.content = assistantMessage;
          }
          return [...newMsgs];
        });
      }
      
      // Save after completion
      const finalMessages: Message[] = [...newMessages, { role: "model", content: assistantMessage }];
      saveChat(finalMessages);
      
    } catch (error) {
      console.error("Chat error:", error);
      const errorMsg: Message = { role: "model", content: "Xin lỗi, đã có lỗi xảy ra trong quá trình kết nối." };
      const finalMessagesWithError = [...newMessages, errorMsg];
      setMessages(finalMessagesWithError);
      saveChat(finalMessagesWithError);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = (content: string) => {
    setInputValue(content);
    // Sử dụng setTimeout để đảm bảo React cập nhật state trước khi focus
    setTimeout(() => {
      const inputEl = document.getElementById("chat-input") as HTMLTextAreaElement;
      if (inputEl) {
        inputEl.focus();
        // Đặt con trỏ ở cuối đoạn text
        inputEl.setSelectionRange(inputEl.value.length, inputEl.value.length);
      }
    }, 0);
  };

  return (
    <main className="relative h-screen flex flex-col items-center p-0 overflow-hidden mesh-bg font-sans selection:bg-primary/30">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-primary/5 rounded-full blur-[140px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-accent/5 rounded-full blur-[140px] pointer-events-none animate-pulse-slow [animation-delay:4s]" />

      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)}
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={selectSession}
        onDeleteSession={deleteSession}
        onNewChat={createNewChat}
      />
      
      <ChatHeader 
        onOpenSidebar={() => setIsSidebarOpen(true)} 
        apiMode={process.env.NEXT_PUBLIC_API_MODE} 
      />

      <div className="w-full max-w-3xl flex flex-col h-full pt-16 z-10 mx-auto">
        {/* Chat Messages Area */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto space-y-8 px-4 py-8 scrollbar-hide pb-4"
          style={{
            maskImage: 'linear-gradient(to bottom, transparent, black 60px, black calc(100% - 40px), transparent)',
            WebkitMaskImage: 'linear-gradient(to bottom, transparent, black 60px, black calc(100% - 40px), transparent)'
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
                    onClick={() => {
                      setInputValue(suggestion.value);
                      setTimeout(() => document.getElementById("chat-input")?.focus(), 0);
                    }}
                    className="px-4 py-2.5 rounded-xl glass-panel border border-primary/10 hover:border-primary/30 hover:bg-primary/5 text-[13px] font-semibold text-muted-foreground hover:text-primary transition-all duration-300 shadow-sm hover:shadow-md"
                  >
                    {suggestion.title}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <ChatMessage 
                key={index} 
                message={msg} 
                isLoading={isLoading} 
                isLast={index === messages.length - 1} 
                onEdit={handleEdit}
              />
            ))
          )}
        </div>

        <ChatInput 
          value={inputValue} 
          onChange={setInputValue} 
          onSend={handleSend} 
          isLoading={isLoading} 
        />
      </div>
    </main>
  );
}
