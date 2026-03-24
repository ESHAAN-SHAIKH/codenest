import { useState } from 'react';
import { Bot } from 'lucide-react';
import AiAssistant from './AiAssistant';

export default function AiFloatingButton() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 w-16 h-16 bg-white border-4 border-primary rounded-full shadow-2xl flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-40 group"
                >
                    <div className="relative">
                        <Bot size={32} className="text-primary group-hover:rotate-12 transition-transform" />
                        <span className="absolute -top-1 -right-1 flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                        </span>
                    </div>
                </button>
            )}
            <AiAssistant isOpen={isOpen} onClose={() => setIsOpen(false)} />
        </>
    );
}
