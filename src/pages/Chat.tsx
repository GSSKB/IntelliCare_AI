import { useState, useEffect, useRef } from "react";
import { sendMessage } from "../api/api";
import ChatBubble from "../components/ChatBubble";
import InputBox from "../components/InputBox";
import { Home, Heart, Brain } from "lucide-react";
import { useNavigate } from "react-router-dom";

export interface Message {
  sender: "user" | "ai";
  text: string;
}

export default function Chat() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    { sender: "ai", text: "Hello! I'm your AI medical assistant. How can I help you today?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    const userMessage: Message = { sender: "user", text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      console.log("Sending message:", text);
      const response = await sendMessage(text);
      console.log("Received response:", response);
      const aiMessage: Message = { sender: "ai", text: response.data.response };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat API Error:", error);
      const errorMessage: Message = {
        sender: "ai",
        text: `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-background flex flex-col overflow-hidden">
      <div className="flex-1 flex flex-col min-h-0 w-full">
        <div className="bg-card shadow-sm border overflow-hidden flex flex-col flex-1 h-full w-full">
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground p-4 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative w-12 h-12 bg-primary-foreground/20 rounded-xl flex items-center justify-center shadow-lg">
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary-foreground/30 to-transparent" />
                  <div className="relative flex items-center justify-center">
                    <Heart className="w-6 h-6 text-primary-foreground fill-primary-foreground" />
                    <Brain className="w-4 h-4 text-primary-foreground absolute -top-0.5 -right-0.5" />
                  </div>
                </div>
                <div>
                  <h2 className="text-xl font-light">AI Medical Consultation</h2>
                  <p className="text-primary-foreground/80 text-xs mt-0.5">Powered by IntelliCare AI</p>
                </div>
              </div>
              
              {/* Home Button */}
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 px-3 py-1.5 bg-primary-foreground/20 hover:bg-primary-foreground/30 rounded-lg transition-colors duration-200"
              >
                <Home className="w-4 h-4" />
                <span className="text-xs font-medium">Home</span>
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto bg-secondary/30 p-6 space-y-4 min-h-0">
            {messages.map((msg, idx) => (
              <ChatBubble key={idx} message={msg} />
            ))}
            {isLoading && (
              <div className="flex items-center space-x-3 text-muted-foreground">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <span className="text-sm font-light">AI is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-card border-t p-4 flex-shrink-0">
            <div className="max-w-4xl mx-auto">
              <div className="bg-primary/10 border border-primary/20 rounded-xl p-3 mb-3">
                <div className="flex items-start space-x-2">
                  <svg className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-xs text-primary">
                    <p className="font-medium">Remember:</p>
                    <p className="font-light">This is for informational purposes only. Always consult healthcare professionals for medical advice.</p>
                  </div>
                </div>
              </div>
              <InputBox onSend={handleSend} disabled={isLoading} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
