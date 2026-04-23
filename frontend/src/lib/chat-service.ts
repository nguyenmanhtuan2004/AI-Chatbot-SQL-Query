export type Message = {
  role: "user" | "model";
  content: string;
};

export class ChatService {
  private static MODE = process.env.NEXT_PUBLIC_API_MODE || 'direct';
  private static DOTNET_URL = process.env.NEXT_PUBLIC_DOTNET_API_URL || 'http://localhost:5026/api/chat/ask';

  static async *sendMessage(userMessage: string, history: Message[]): AsyncGenerator<string> {
    if (this.MODE === 'dotnet') {
      yield* this.sendToDotnet(userMessage);
    } else {
      yield* this.sendToDirect(userMessage, history);
    }
  }

  private static async *sendToDotnet(question: string): AsyncGenerator<string> {
    const response = await fetch(this.DOTNET_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ Question: question }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "Failed to fetch from .NET API");
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield decoder.decode(value, { stream: true });
    }
  }

  private static async *sendToDirect(userMessage: string, history: Message[]): AsyncGenerator<string> {
    const chatHistory = history
      .filter(msg => msg.content.trim() !== "")
      .map(msg => ({
        role: msg.role,
        parts: [{ text: msg.content }]
      }));

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

    if (!response.ok) throw new Error("Failed to fetch from Direct API");

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
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
            if (text) yield text;
          } catch (e) {
            console.error("Error parsing JSON chunk", e);
          }
          buffer = buffer.substring(endIdx + 1);
          startIdx = buffer.indexOf('{');
        } else {
          break;
        }
      }
    }
  }
}
