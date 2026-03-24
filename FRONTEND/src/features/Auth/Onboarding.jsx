import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../stores/useAuthStore';

const SKILL_LEVELS = [
    { id: 'beginner', label: '🌱 Beginner', desc: "I'm just starting to learn programming" },
    { id: 'intermediate', label: '🌿 Intermediate', desc: 'I know the basics and want to go deeper' },
    { id: 'advanced', label: '🌳 Advanced', desc: 'I can build projects and want to master concepts' },
];

const INTERESTS = [
    { id: 'fundamentals', label: '📦 Fundamentals', desc: 'Variables, data types, I/O' },
    { id: 'control_flow', label: '🔀 Control Flow', desc: 'Conditionals, loops, logic' },
    { id: 'functions', label: '⚡ Functions', desc: 'Functions, scope, recursion' },
    { id: 'data_structures', label: '🗂️ Data Structures', desc: 'Lists, dicts, sets, tuples' },
    { id: 'debugging', label: '🐛 Debugging', desc: 'Error handling, debugging strategies' },
    { id: 'quality', label: '✨ Code Quality', desc: 'Readability, DRY, naming' },
];

export default function Onboarding() {
    const [step, setStep] = useState(0);
    const [skillLevel, setSkillLevel] = useState('beginner');
    const [selectedInterests, setSelectedInterests] = useState([]);
    const { user, completeOnboarding, loading } = useAuthStore();
    const navigate = useNavigate();

    const toggleInterest = (id) => {
        setSelectedInterests((prev) =>
            prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
        );
    };

    const handleComplete = async () => {
        try {
            await completeOnboarding(skillLevel, 'python', selectedInterests);
            navigate('/dashboard');
        } catch {
            // error handled in store
        }
    };

    const steps = [
        // Step 0: Welcome
        <div key="welcome" className="text-center space-y-6">
            <div className="text-7xl mb-4">🚀</div>
            <h2 className="text-3xl font-bold text-white">
                Welcome, {user?.username || 'Coder'}!
            </h2>
            <p className="text-blue-200/80 text-lg max-w-md mx-auto">
                Let's set up your learning profile so CodeNest can personalize your experience.
            </p>
            <button
                onClick={() => setStep(1)}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-500 hover:to-purple-500 transition-all shadow-lg shadow-blue-500/25"
            >
                Let's Go! →
            </button>
        </div>,

        // Step 1: Skill Level
        <div key="skill" className="space-y-6">
            <div className="text-center">
                <h2 className="text-2xl font-bold text-white mb-2">What's your coding level?</h2>
                <p className="text-blue-200/70">This helps us tailor content to your experience</p>
            </div>
            <div className="space-y-3">
                {SKILL_LEVELS.map((level) => (
                    <button
                        key={level.id}
                        onClick={() => setSkillLevel(level.id)}
                        className={`w-full p-4 rounded-2xl text-left transition-all duration-200 border-2 ${skillLevel === level.id
                                ? 'bg-blue-600/30 border-blue-400 shadow-lg shadow-blue-500/20'
                                : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                            }`}
                    >
                        <div className="text-lg font-semibold text-white">{level.label}</div>
                        <div className="text-sm text-blue-200/70 mt-1">{level.desc}</div>
                    </button>
                ))}
            </div>
            <div className="flex gap-3">
                <button onClick={() => setStep(0)} className="flex-1 py-3 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition">
                    ← Back
                </button>
                <button onClick={() => setStep(2)} className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold hover:from-blue-500 hover:to-purple-500 transition-all shadow-lg shadow-blue-500/25">
                    Next →
                </button>
            </div>
        </div>,

        // Step 2: Interests
        <div key="interests" className="space-y-6">
            <div className="text-center">
                <h2 className="text-2xl font-bold text-white mb-2">What interests you most?</h2>
                <p className="text-blue-200/70">Select the topics you want to focus on (optional)</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
                {INTERESTS.map((interest) => (
                    <button
                        key={interest.id}
                        onClick={() => toggleInterest(interest.id)}
                        className={`p-4 rounded-2xl text-left transition-all duration-200 border-2 ${selectedInterests.includes(interest.id)
                                ? 'bg-blue-600/30 border-blue-400 shadow-lg shadow-blue-500/20'
                                : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                            }`}
                    >
                        <div className="text-base font-semibold text-white">{interest.label}</div>
                        <div className="text-xs text-blue-200/70 mt-1">{interest.desc}</div>
                    </button>
                ))}
            </div>
            <div className="flex gap-3">
                <button onClick={() => setStep(1)} className="flex-1 py-3 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition">
                    ← Back
                </button>
                <button
                    onClick={handleComplete}
                    disabled={loading}
                    className="flex-1 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:from-green-500 hover:to-emerald-500 transition-all shadow-lg shadow-green-500/25 disabled:opacity-50"
                >
                    {loading ? 'Setting up...' : '🎯 Start Learning!'}
                </button>
            </div>
        </div>,
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
            <div className="w-full max-w-lg">
                {/* Progress indicators */}
                <div className="flex justify-center gap-2 mb-8">
                    {[0, 1, 2].map((i) => (
                        <div
                            key={i}
                            className={`h-2 rounded-full transition-all duration-300 ${i <= step ? 'bg-blue-400 w-12' : 'bg-white/20 w-8'
                                }`}
                        />
                    ))}
                </div>

                <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/10">
                    {steps[step]}
                </div>
            </div>
        </div>
    );
}
