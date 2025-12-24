import { Message } from "../pages/Chat";

interface ChatBubbleProps {
  message: Message;
}
import { 
  Search, 
  Lightbulb, 
  BarChart3, 
  AlertTriangle, 
  Activity,
  Heart,
  Stethoscope,
  FileText,
  TrendingUp,
  Users,
  Shield
} from "lucide-react";

interface ChatBubbleProps {
  message: Message;
}

function getSectionIcon(sectionName: string) {
  const lowerSection = sectionName.toLowerCase();
  
  if (lowerSection.includes('symptom') || lowerSection.includes('analysis')) {
    return <Search className="w-4 h-4 text-primary" />;
  }
  if (lowerSection.includes('recommendation') || lowerSection.includes('recommend')) {
    return <Lightbulb className="w-4 h-4 text-yellow-500" />;
  }
  if (lowerSection.includes('similar case') || lowerSection.includes('case')) {
    return <BarChart3 className="w-4 h-4 text-blue-500" />;
  }
  if (lowerSection.includes('disclaimer') || lowerSection.includes('warning')) {
    return <AlertTriangle className="w-4 h-4 text-orange-500" />;
  }
  if (lowerSection.includes('risk')) {
    return <Activity className="w-4 h-4 text-red-500" />;
  }
  if (lowerSection.includes('disease') || lowerSection.includes('condition')) {
    return <Heart className="w-4 h-4 text-pink-500" />;
  }
  if (lowerSection.includes('treatment') || lowerSection.includes('care')) {
    return <Stethoscope className="w-4 h-4 text-green-500" />;
  }
  if (lowerSection.includes('outcome') || lowerSection.includes('result')) {
    return <TrendingUp className="w-4 h-4 text-purple-500" />;
  }
  if (lowerSection.includes('patient') || lowerSection.includes('information')) {
    return <Users className="w-4 h-4 text-indigo-500" />;
  }
  if (lowerSection.includes('prevent') || lowerSection.includes('prevention')) {
    return <Shield className="w-4 h-4 text-teal-500" />;
  }
  
  return <FileText className="w-4 h-4 text-gray-500" />;
}

function formatMessage(text: string) {
  const lines = text.split('\n');
  const elements: JSX.Element[] = [];
  let currentSection: JSX.Element[] = [];
  let key = 0;

  lines.forEach((line, index) => {
    const trimmedLine = line.trim();
    
    // Handle separator lines
    if (trimmedLine === '⸻' || trimmedLine === '---' || trimmedLine === '=') {
      if (currentSection.length > 0) {
        elements.push(
          <div key={key++} className="space-y-1 mb-4">
            {currentSection}
          </div>
        );
        currentSection = [];
      }
      elements.push(
        <hr key={key++} className="my-4 border-border/50" />
      );
      return;
    }

    // Skip empty lines
    if (!trimmedLine) {
      if (currentSection.length > 0) {
        elements.push(
          <div key={key++} className="space-y-1 mb-2">
            {currentSection}
          </div>
        );
        currentSection = [];
      }
      return;
    }

    // Handle section headers - detect common section names
    const isSectionHeader = trimmedLine.match(/^(Symptom Analysis|Recommendations|Similar Cases|Disclaimer|Risk Assessment|Disease Information|Treatment|Outcome|Patient Information|Prevention)/i);
    
    if (isSectionHeader || trimmedLine.match(/^[🔍💡📊⚠️]/)) {
      if (currentSection.length > 0) {
        elements.push(
          <div key={key++} className="space-y-1 mb-3">
            {currentSection}
          </div>
        );
        currentSection = [];
      }
      
      const sectionName = trimmedLine.replace(/^[🔍💡📊⚠️]\s*/, '').trim();
      const icon = getSectionIcon(sectionName);
      
      currentSection.push(
        <div key={key++} className="flex items-center space-x-2 mb-2">
          {icon}
          <h3 className="font-semibold text-base">
            {sectionName}
          </h3>
        </div>
      );
      return;
    }

    // Handle bullet points
    if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
      const bulletText = trimmedLine.substring(1).trim();
      currentSection.push(
        <div key={key++} className="flex items-start space-x-2 ml-6">
          <span className="text-primary mt-1">•</span>
          <span className="flex-1">{bulletText}</span>
        </div>
      );
      return;
    }

    // Handle numbered lists
    if (trimmedLine.match(/^\d+\./)) {
      currentSection.push(
        <div key={key++} className="flex items-start space-x-2 ml-6">
          <span className="text-primary font-medium mt-0.5">{trimmedLine.match(/^\d+\./)?.[0]}</span>
          <span className="flex-1">{trimmedLine.replace(/^\d+\.\s*/, '')}</span>
        </div>
      );
      return;
    }

    // Handle risk level indicators (HIGH RISK, MEDIUM RISK, LOW RISK)
    if (trimmedLine.match(/^(HIGH|MEDIUM|LOW)\s+RISK/i)) {
      const riskMatch = trimmedLine.match(/^(HIGH|MEDIUM|LOW)\s+RISK\s*-\s*(.*)/i);
      if (riskMatch) {
        const riskLevel = riskMatch[1].toUpperCase();
        const explanation = riskMatch[2];
        const riskColor = riskLevel === 'HIGH' ? 'text-red-500' : riskLevel === 'MEDIUM' ? 'text-yellow-500' : 'text-green-500';
        const riskBg = riskLevel === 'HIGH' ? 'bg-red-50' : riskLevel === 'MEDIUM' ? 'bg-yellow-50' : 'bg-green-50';
        
        currentSection.push(
          <div key={key++} className={`${riskBg} border-l-4 ${riskLevel === 'HIGH' ? 'border-red-500' : riskLevel === 'MEDIUM' ? 'border-yellow-500' : 'border-green-500'} p-3 rounded-r mb-2`}>
            <div className="flex items-center space-x-2">
              <Activity className={`w-5 h-5 ${riskColor}`} />
              <div>
                <p className={`font-bold text-lg ${riskColor}`}>{riskLevel} RISK</p>
                {explanation && <p className="text-sm mt-1">{explanation}</p>}
              </div>
            </div>
          </div>
        );
        return;
      }
    }

    // Regular text
    currentSection.push(
      <p key={key++} className="leading-relaxed">
        {trimmedLine}
      </p>
    );
  });

  // Add remaining section
  if (currentSection.length > 0) {
    elements.push(
      <div key={key++} className="space-y-1">
        {currentSection}
      </div>
    );
  }

  return elements.length > 0 ? elements : <p>{text}</p>;
}

export default function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.sender === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}>
      <div
        className={`${isUser ? "max-w-xs lg:max-w-md" : "max-w-2xl lg:max-w-3xl"} px-6 py-4 rounded-2xl ${
          isUser
            ? "bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-sm"
            : "bg-card border border-border text-foreground shadow-sm"
        }`}
      >
        <div className="flex items-start space-x-3">
          {!isUser && (
            <div className="w-7 h-7 bg-gradient-to-r from-primary to-primary/80 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
          )}
          <div className="flex-1">
            <div className={`text-sm font-light ${isUser ? "text-primary-foreground" : "text-foreground"}`}>
              {isUser ? (
                <p className="leading-relaxed">{message.text}</p>
              ) : (
                formatMessage(message.text)
              )}
            </div>
            <p className={`text-xs mt-2 font-light ${isUser ? "text-primary-foreground/80" : "text-muted-foreground"}`}>
              {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
          {isUser && (
            <div className="w-7 h-7 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
