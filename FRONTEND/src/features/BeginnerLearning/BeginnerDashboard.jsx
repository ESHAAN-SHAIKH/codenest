import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Loader, CheckCircle, Lock, ToggleLeft, ToggleRight } from 'lucide-react';
import useAuthStore from '../../stores/useAuthStore';
import useBeginnerLearningStore from '../../stores/useBeginnerLearningStore';
import TransitionPrompt from './TransitionPrompt';

const API_BASE = import.meta.env.VITE_API_URL
    ? import.meta.env.VITE_API_URL.replace(/\/api$/, '')
    : 'http://localhost:5000';

const MODE_LABEL = {
    fill_in_blank: 'Fill in the Blank',
    predict_output: 'Predict the Output',
    error_spotting: 'Error Spotting',
    freeform: 'Freeform',
};

const PHASE_BADGE = {
    scaffolded: { label: 'Scaffolded', color: 'bg-indigo-100 text-indigo-700' },
    guided: { label: 'Guided', color: 'bg-blue-100 text-blue-700' },
    freeform: { label: 'Freeform', color: 'bg-green-100 text-green-700' },
    complete: { label: 'Complete', color: 'bg-emerald-100 text-emerald-700' },
};

export default function BeginnerDashboard() {
    const { token, user } = useAuthStore();
    const {
        is_beginner_mode,
        beginner_phase,
        toggleBeginnerMode,
        checkTransition,
        updatePhase,
        syncFromUser,
    } = useBeginnerLearningStore();

    const [challenges, setChallenges] = useState([]);
    const [loading, setLoading] = useState(true);
    const [transitionData, setTransitionData] = useState(null);
    const [toggling, setToggling] = useState(false);
    const navigate = useNavigate();

    // Sync beginner mode from user on mount
    useEffect(() => {
        if (user) syncFromUser(user);
    }, [user]);

    // Load scaffolded challenges (filtered view of existing challenge system)
    useEffect(() => {
        if (!token) return;
        setLoading(true);
        fetch(`${API_BASE}/api/beginner/challenges`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((r) => r.json())
            .then((data) => {
                setChallenges(data.challenges || []);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, [token, beginner_phase]);

    // Check transition on mount
    useEffect(() => {
        if (!token) return;
        checkTransition(token).then((data) => {
            if (data?.eligible) setTransitionData(data);
        });
    }, [token]);

    const handleToggle = async () => {
        setToggling(true);
        try {
            await toggleBeginnerMode(token);
        } finally {
            setToggling(false);
        }
    };

    const handleTransitionProceed = () => {
        if (transitionData?.new_phase) updatePhase(transitionData.new_phase);
        setTransitionData(null);
        navigate('/dashboard');
    };

    const phase = PHASE_BADGE[beginner_phase] || PHASE_BADGE.scaffolded;

    return (
        <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Beginner Learning</h1>
                    <p className="text-gray-500 mt-1 text-sm">
                        Structured exercises to build execution intuition before free coding.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${phase.color}`}>
                        Phase: {phase.label}
                    </span>
                    <button
                        onClick={handleToggle}
                        disabled={toggling}
                        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition-colors disabled:opacity-40"
                        title={is_beginner_mode ? 'Disable beginner mode' : 'Enable beginner mode'}
                    >
                        {is_beginner_mode
                            ? <ToggleRight size={22} className="text-indigo-500" />
                            : <ToggleLeft size={22} />}
                        Beginner Mode
                    </button>
                </div>
            </div>

            {/* Challenge grid */}
            {loading ? (
                <div className="flex items-center justify-center h-40 text-gray-400">
                    <Loader className="animate-spin mr-2" /> Loading exercises...
                </div>
            ) : challenges.length === 0 ? (
                <div className="text-center text-gray-400 py-16">
                    No scaffolded challenges found. Try running the seed script.
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {challenges.map((ch, idx) => {
                        const scaffoldType = ch.scaffold_data?.type || ch.challenge_mode;
                        const isLocked = !ch.unlocked;

                        return (
                            <motion.div
                                key={ch.id}
                                initial={{ opacity: 0, y: 12 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.04 }}
                                className={`bg-white rounded-2xl border p-5 shadow-sm transition-all ${isLocked
                                        ? 'border-gray-100 opacity-60 cursor-not-allowed'
                                        : 'border-gray-200 hover:border-indigo-300 hover:shadow-md cursor-pointer'
                                    }`}
                                onClick={() => !isLocked && navigate(`/beginner/challenge/${ch.id}`, { state: { challenge: ch } })}
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <span className="text-xs font-semibold text-indigo-500 uppercase tracking-wide">
                                        {MODE_LABEL[scaffoldType] || 'Challenge'}
                                    </span>
                                    {isLocked
                                        ? <Lock size={14} className="text-gray-300" />
                                        : <CheckCircle size={14} className="text-gray-200" />}
                                </div>
                                <h3 className="font-bold text-gray-800 text-base leading-snug">{ch.title}</h3>
                                <p className="text-gray-500 text-sm mt-1 line-clamp-2">{ch.description}</p>
                                <div className="mt-3 flex items-center gap-2">
                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ch.difficulty === 'easy'
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-amber-100 text-amber-700'
                                        }`}>
                                        {ch.difficulty}
                                    </span>
                                    <span className="text-xs text-gray-400">{ch.points} pts</span>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            )}

            {/* Subtle links to advanced systems — always visible, never hidden */}
            <div className="border-t border-gray-100 pt-6">
                <p className="text-xs text-gray-400 mb-3 font-semibold uppercase tracking-wide">All systems remain available</p>
                <div className="flex flex-wrap gap-2">
                    {[
                        { to: '/arena', label: 'Arena', note: 'Advanced Challenge' },
                        { to: '/archetypes', label: 'Archetypes' },
                        { to: '/analytics', label: 'Analytics' },
                        { to: '/concept-map', label: 'Concept Map' },
                    ].map(({ to, label, note }) => (
                        <Link
                            key={to}
                            to={to}
                            className="text-sm text-gray-400 hover:text-indigo-600 transition-colors border border-gray-200 rounded-lg px-3 py-1.5 flex items-center gap-1"
                        >
                            {label}
                            {note && (
                                <span className="text-xs bg-gray-100 text-gray-400 rounded px-1 ml-1">{note}</span>
                            )}
                        </Link>
                    ))}
                </div>
            </div>

            {/* Transition prompt modal */}
            {transitionData?.eligible && (
                <TransitionPrompt
                    transitionData={transitionData}
                    onStay={() => setTransitionData(null)}
                    onProceed={handleTransitionProceed}
                />
            )}
        </div>
    );
}
