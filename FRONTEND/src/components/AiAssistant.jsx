import { useState, useRef, useEffect } from 'react';
import apiService from '../services/api';

export default function AiAssistant({ onClose }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hi! I\'m Code Cat 🐱 I\'m here to help you learn coding! Ask me anything!' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');

        // Add user message
        setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
        setLoading(true);

        try {
            // Call AI API
            const response = await apiService.chat(userMessage);

            // Add AI response
            setMessages(prev => [...prev, {
                role: 'assistant',
                text: response.content || response.explanation || 'I\'m here to help! 🐱'
            }]);
        } catch (error) {
            console.error('AI chat error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                text: '😿 Oops! I had trouble understanding that. Can you try asking in a different way?'
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="fixed right-6 bottom-6 w-96 h-[32rem] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border-4 border-blue-200">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-4 rounded-t-xl flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">🐱</span>
                    <div>
                        <h3 className="font-bold text-lg">Code Cat</h3>
                        <p className="text-xs opacity-90">Your Coding Assistant</p>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
                >
                    ✕
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] px-4 py-2 rounded-2xl ${msg.role === 'user'
                                ? 'bg-blue-500 text-white rounded-br-none'
                                : 'bg-white text-gray-800 rounded-bl-none shadow-md'
                            }`}>
                            {msg.text}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-white text-gray-800 px-4 py-2 rounded-2xl rounded-bl-none shadow-md">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 bg-white rounded-b-xl">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask me anything about coding..."
                        className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-full focus:outline-none focus:border-blue-400 transition-colors"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-semibold"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
