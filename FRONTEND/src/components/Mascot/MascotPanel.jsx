import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const FOCUS_COLORS = {
    execution_flow: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Execution Flow' },
    logic_error: { bg: 'bg-red-100', text: 'text-red-700', label: 'Logic Error' },
    misconception: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Misconception' },
    strategy: { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Strategy' },
};

const INTERVENTION_ICONS = { 1: '🟢', 2: '🟡', 3: '🟠', 4: '🔴', 5: '🆘' };

/**
 * MascotPanel — Professor Hoot
 *
 * Props:
 *   mascotResponse: { message, reasoning_focus, suggested_next_step, intervention_level }
 *   compact: bool — render a narrow version for sidebar use
 *   isLoading: bool — show animated thinking state
 */
export default function MascotPanel({ mascotResponse, compact = false, isLoading = false }) {
    const [displayed, setDisplayed] = useState('');
    const [isDone, setIsDone] = useState(false);
    const intervalRef = useRef(null);
    const message = mascotResponse?.message || '';

    // Typewriter effect for mascot message
    useEffect(() => {
        if (!message) {
            setDisplayed('');
            setIsDone(false);
            return;
        }
        setDisplayed('');
        setIsDone(false);
        let i = 0;
        clearInterval(intervalRef.current);
        intervalRef.current = setInterval(() => {
            i++;
            setDisplayed(message.slice(0, i));
            if (i >= message.length) {
                clearInterval(intervalRef.current);
                setIsDone(true);
            }
        }, 18);
        return () => clearInterval(intervalRef.current);
    }, [message]);

    if (!mascotResponse && !isLoading) return null;

    const focus = FOCUS_COLORS[mascotResponse?.reasoning_focus] || FOCUS_COLORS.strategy;
    const level = mascotResponse?.intervention_level ?? 1;

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={message}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25 }}
                className={`bg-amber-50 border border-amber-200 rounded-2xl ${compact ? 'p-4' : 'p-6'} flex flex-col gap-3`}
            >
                {/* Header */}
                <div className="flex items-center gap-3">
                    <div className={`${compact ? 'w-10 h-10 text-2xl' : 'w-14 h-14 text-4xl'} bg-amber-200 rounded-full flex items-center justify-center shadow-inner select-none`}>
                        🦉
                    </div>
                    <div>
                        <div className="font-bold text-amber-900 text-sm">Professor Hoot</div>
                        {mascotResponse?.reasoning_focus && (
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${focus.bg} ${focus.text}`}>
                                {focus.label}
                            </span>
                        )}
                    </div>
                    {level >= 3 && (
                        <span className="ml-auto text-base" title={`Intervention level ${level}`}>
                            {INTERVENTION_ICONS[level] || '🟡'}
                        </span>
                    )}
                </div>

                {/* Message bubble */}
                <div className="bg-white rounded-xl px-4 py-3 shadow-sm text-sm text-gray-700 leading-relaxed min-h-[48px] relative">
                    {isLoading ? (
                        <div className="flex gap-1 items-center h-5">
                            {[0, 1, 2].map((i) => (
                                <motion.div
                                    key={i}
                                    className="w-2 h-2 bg-amber-400 rounded-full"
                                    animate={{ y: [0, -6, 0] }}
                                    transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.15 }}
                                />
                            ))}
                        </div>
                    ) : (
                        <>
                            {displayed}
                            {!isDone && <span className="animate-pulse ml-0.5">▋</span>}
                        </>
                    )}
                </div>

                {/* Suggested next step */}
                <AnimatePresence>
                    {isDone && mascotResponse?.suggested_next_step && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-amber-100 border border-amber-200 rounded-xl px-3 py-2 text-xs text-amber-800 flex gap-2 items-start"
                        >
                            <span className="text-base">→</span>
                            <span>{mascotResponse.suggested_next_step}</span>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </AnimatePresence>
    );
}
