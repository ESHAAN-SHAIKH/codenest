import { motion } from 'framer-motion';
import { Check, Lock, Star } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function SkillNode({ id, title, type, status, position, stars, mastery, onClick }) {
    const isLocked = status === 'locked';
    const isCompleted = status === 'completed';
    const isActive = status === 'unlocked';

    const getNodeColor = () => {
        if (isLocked) return 'bg-gray-200 border-gray-300 text-gray-400';
        if (isCompleted) return 'bg-success border-green-500 text-white shadow-success/40';
        if (type === 'boss') return 'bg-red-500 border-red-600 text-white shadow-red-500/40';
        return 'bg-primary border-primary-dark text-white shadow-primary/40';
    };

    // Mastery Ring Config
    const radius = 38; // Slightly larger than node radius
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (mastery / 100) * circumference;

    return (
        <motion.div
            className="absolute transform -translate-x-1/2 -translate-y-1/2"
            style={{ left: position.x, top: position.y }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            whileHover={!isLocked ? { scale: 1.1 } : {}}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
        >
            <Link to={!isLocked ? `/lesson/${id}` : '#'} className="relative group flex items-center justify-center">

                {/* Mastery Ring (SVG) */}
                {!isLocked && (
                    <svg className="absolute w-24 h-24 -rotate-90 pointer-events-none">
                        <circle
                            cx="48"
                            cy="48"
                            r={radius}
                            stroke="#E9ECEF"
                            strokeWidth="4"
                            fill="transparent"
                        />
                        <circle
                            cx="48"
                            cy="48"
                            r={radius}
                            stroke={isCompleted ? "#69DB7C" : "#FF6B6B"}
                            strokeWidth="4"
                            fill="transparent"
                            strokeDasharray={circumference}
                            strokeDashoffset={strokeDashoffset}
                            strokeLinecap="round"
                            className="transition-all duration-1000 ease-out"
                        />
                    </svg>
                )}

                {/* Node Circle */}
                <div
                    className={`w-16 h-16 md:w-20 md:h-20 rounded-full border-4 flex items-center justify-center shadow-lg transition-colors duration-300 z-10 ${getNodeColor()}`}
                >
                    {isLocked ? (
                        <Lock size={24} />
                    ) : isCompleted ? (
                        <Check size={32} strokeWidth={3} />
                    ) : (
                        <span className="font-bold text-2xl">{id}</span>
                    )}
                </div>

                {/* Stars for completed levels */}
                {isCompleted && stars > 0 && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 flex gap-0.5 z-20 bg-white/80 px-1 rounded-full backdrop-blur-sm">
                        {[...Array(3)].map((_, i) => (
                            <Star
                                key={i}
                                size={12}
                                className={`${i < stars ? "fill-yellow-400 text-yellow-400" : "text-gray-300 fill-gray-300"}`}
                            />
                        ))}
                    </div>
                )}

                {/* Tooltip */}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20">
                    <div className="bg-gray-800 text-white text-sm py-1 px-3 rounded-lg shadow-xl mb-1">
                        {title}
                        {mastery > 0 && <div className="text-xs text-gray-400 text-center">{mastery}% Mastered</div>}
                    </div>
                    {/* Triangle */}
                    <div className="w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-800 absolute -top-1 left-1/2 -translate-x-1/2"></div>
                </div>

                {/* Pulse effect for active node */}
                {isActive && !isCompleted && (
                    <div className="absolute inset-0 rounded-full bg-primary animate-ping opacity-20 z-0"></div>
                )}
            </Link>
        </motion.div>
    );
}
