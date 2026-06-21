import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { sendChatBotMessage } from '../services/api';

// Initial default welcome snapshot message for the chat context
const WELCOME_MESSAGE = {
  sender: 'bot',
  text: "Hello! I'm your academic mentor. Ask me anything about your grades, attendance, or study plans.",
};

/**
 * Renders individual conversational message bubbles.
 * Handles specialized UI formatting states for user, bot, and active typing loading indicators.
 */
function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  const isTyping = message.sender === 'typing';

  // Render bounce animation sequence if the assistant state is actively processing a message
  if (isTyping) {
    return (
      <div className="flex items-end gap-2">
        <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
          <span className="text-[10px] font-bold text-indigo-600">AI</span>
        </div>
        <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
          <div className="flex gap-1 items-center h-4">
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
        </div>
      </div>
    );
  }

  // Render bubble format styling for user-sent messages
  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[78%] bg-indigo-600 text-white px-4 py-2.5 rounded-2xl rounded-br-sm shadow-sm">
          <p className="text-sm leading-relaxed">{message.text}</p>
        </div>
      </div>
    );
  }

  // Fallback default format styling for bot assistant responses
  return (
    <div className="flex items-end gap-2">
      <div className="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
        <span className="text-[10px] font-bold text-indigo-600">AI</span>
      </div>
      <div className="max-w-[78%] bg-white border border-gray-100 text-gray-800 px-4 py-2.5 rounded-2xl rounded-bl-sm shadow-sm">
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
      </div>
    </div>
  );
}

function Chatbot() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Automatically scroll the container down to view the newest messages on state updates
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  // Handle immediate input field refocus actions on container open triggers
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  // Strict boundary rule: Guard layout rendering to prevent access for non-student roles
  if (user?.role !== 'student') return null;

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    setInput('');
    setIsLoading(true);

    // Append current user candidate message string into state arrays
    setMessages(prev => [...prev, { sender: 'user', text }]);

    // Append intermediate typing bubble flag indicators into active tracking arrays
    setMessages(prev => [...prev, { sender: 'typing', text: '' }]);

    try {
      // Execute asymmetric API communication path towards the backend server gateway
      const data = await sendChatBotMessage(text);

      // Prune typing placeholders and safely attach valid response strings
      setMessages(prev => [
        ...prev.filter(m => m.sender !== 'typing'),
        { sender: 'bot', text: data.response },
      ]);
    } catch (err) {
      // Clean typography indicators and attach standardized error notice frames
      setMessages(prev => [
        ...prev.filter(m => m.sender !== 'typing'),
        {
          sender: 'bot',
          text: "Something went wrong. Please try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
      // Guarantee input element refocus locks even after error exceptions catch triggers
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Chat Container Window Wrapper */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-[360px] max-h-[560px] flex flex-col bg-gray-50 rounded-3xl shadow-2xl border border-gray-200 overflow-hidden">

          {/* Assistant Panel Branding Header */}
          <div className="flex items-center justify-between px-5 py-4 bg-indigo-950 flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-indigo-700 flex items-center justify-center text-sm shadow-inner">
                ✨
              </div>
              <div>
                <p className="text-sm font-bold text-white leading-none">Academic Mentor</p>
                <p className="text-[11px] text-indigo-300 mt-0.5">Powered by AI · Your data only</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 flex items-center justify-center rounded-xl text-indigo-300 hover:text-white hover:bg-indigo-800 transition-colors"
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Interactive Messages Display Layer viewport */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 min-h-0">
            {messages.map((msg, idx) => (
              <MessageBubble key={idx} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Context input and Submission operations segment */}
          <div className="px-4 py-3 bg-white border-t border-gray-100 flex-shrink-0">
            <div className="flex items-center gap-2 bg-gray-50 rounded-2xl border border-gray-200 px-4 py-2 focus-within:border-indigo-400 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your grades or attendance…"
                disabled={isLoading}
                className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="w-8 h-8 flex items-center justify-center rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
                aria-label="Send message"
              >
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
            <p className="text-[10px] text-gray-400 text-center mt-2">
              Responses are based on your academic records only.
            </p>
          </div>
        </div>
      )}

      {/* Floating Action Trigger Button Layout Segment (Bottom-Right) */}
      <button
        onClick={() => setIsOpen(prev => !prev)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-200 ${
          isOpen
            ? 'bg-indigo-800 hover:bg-indigo-900 rotate-0'
            : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-105'
        }`}
        aria-label={isOpen ? 'Close chat' : 'Open academic mentor chat'}
      >
        {isOpen ? (
          <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>
    </>
  );
}

export default Chatbot;