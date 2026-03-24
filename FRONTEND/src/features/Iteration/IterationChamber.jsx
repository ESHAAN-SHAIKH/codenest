import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import useAuthStore from '../../stores/useAuthStore';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL + '/api' : 'http://localhost:5000/api';

const REFINEMENT_STAGES = {
    functional: {
        name: 'Functional',
        icon: '✅',
        description: 'Make it work correctly',
        color: 'blue',
        guide: {
            heading: 'Focus on correctness:',
            points: [
                'Code runs without errors',
                'Produces correct output for test cases',
                'Implements all required functionality',
            ],
        },
    },
    quality: {
        name: 'Code Quality',
        icon: '✨',
        description: 'Make it readable and maintainable',
        color: 'purple',
        guide: {
            heading: 'Focus on maintainability:',
            points: [
                'Clear variable and function names',
                'Proper code structure and organisation',
                'Helpful comments for complex logic',
                'Consistent formatting and style',
            ],
        },
    },
    performance: {
        name: 'Performance',
        icon: '⚡',
        description: 'Make it efficient',
        color: 'yellow',
        guide: {
            heading: 'Focus on efficiency:',
            points: [
                'Optimal time complexity',
                'Efficient use of memory',
                'Remove unnecessary operations',
                'Use appropriate data structures',
            ],
        },
    },
    edge_cases: {
        name: 'Edge Cases',
        icon: '🛡️',
        description: 'Make it robust',
        color: 'green',
        guide: {
            heading: 'Focus on robustness:',
            points: [
                'Handle empty inputs',
                'Check for null/undefined values',
                'Handle boundary conditions',
                'Proper error handling',
            ],
        },
    },
};

const STAGE_COLOR_CLASSES = {
    functional: { active: 'border-blue-500   bg-blue-50', text: 'text-blue-700' },
    quality: { active: 'border-purple-500  bg-purple-50', text: 'text-purple-700' },
    performance: { active: 'border-yellow-500  bg-yellow-50', text: 'text-yellow-700' },
    edge_cases: { active: 'border-green-500   bg-green-50', text: 'text-green-700' },
};

const STAGE_KEYS = Object.keys(REFINEMENT_STAGES);

export default function IterationChamber() {
    const { challengeId } = useParams();
    // Bug fix: read token + user from auth store — don't rely on prop for userId
    const { token, user } = useAuthStore();

    const [challenge, setChallenge] = useState(null);
    const [currentStage, setCurrentStage] = useState('functional');
    const [code, setCode] = useState('');
    const [iterations, setIterations] = useState([]);
    const [currentIteration, setCurrentIteration] = useState(1);
    // Bug fix: clear feedback whenever stage changes (was showing stale data)
    const [feedback, setFeedback] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [engineeringScore, setEngineeringScore] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // ── Auth headers helper ───────────────────────────────────────────────────
    const authHeaders = useCallback(() => ({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
    }), [token]);

    // ── Fetch challenge ───────────────────────────────────────────────────────
    const fetchChallenge = useCallback(async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/challenges/${challengeId}`, {
                headers: authHeaders(),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setChallenge(data);
            // Bug fix: Challenge model has no starter_code — use description as prompt context
            setCode(data.starter_code || `# ${data.title || 'Challenge'}\n# ${data.description || ''}\n\n`);
        } catch (err) {
            console.error('Error fetching challenge:', err);
            setError('Could not load challenge. Make sure you are logged in.');
        } finally {
            setLoading(false);
        }
    }, [challengeId, authHeaders]);

    // ── Fetch iteration history ───────────────────────────────────────────────
    const fetchIterationHistory = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/iteration/history/${challengeId}`, {
                headers: authHeaders(),
            });
            if (!res.ok) return;
            const json = await res.json();
            const hist = json.data || {};
            setIterations(hist.iterations || []);
            if (hist.current_stage) setCurrentStage(hist.current_stage);
            if (hist.current_iteration) setCurrentIteration(hist.current_iteration);
        } catch (err) {
            console.error('Error fetching iteration history:', err);
        }
    }, [challengeId, authHeaders]);

    useEffect(() => {
        if (challengeId) {
            fetchChallenge();
            fetchIterationHistory();
        }
    }, [challengeId, fetchChallenge, fetchIterationHistory]);

    // Bug fix: clear stale feedback when stage changes
    useEffect(() => {
        setFeedback(null);
    }, [currentStage]);

    // ── Submit iteration ──────────────────────────────────────────────────────
    const submitIteration = async () => {
        if (!code.trim()) {
            alert('Please write some code first');
            return;
        }

        try {
            setSubmitting(true);
            setError(null);

            const res = await fetch(`${API_BASE}/iteration/submit`, {
                method: 'POST',
                headers: authHeaders(),
                body: JSON.stringify({
                    challenge_id: challengeId,
                    code,
                    stage: currentStage,
                    iteration_number: currentIteration,
                }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || `HTTP ${res.status}`);
            }

            const json = await res.json();
            const result = json.data;

            setFeedback(result.feedback);
            setEngineeringScore(result.engineering_maturity_score || 0);

            if (result.stage_passed) {
                const currentIndex = STAGE_KEYS.indexOf(currentStage);
                if (currentIndex < STAGE_KEYS.length - 1) {
                    // Advance to next stage — useEffect will clear feedback
                    setCurrentStage(STAGE_KEYS[currentIndex + 1]);
                    setCurrentIteration(1);
                } else {
                    alert("🎉 Congratulations! You've completed all refinement stages!");
                }
            } else {
                setCurrentIteration((prev) => prev + 1);
            }

            fetchIterationHistory();
        } catch (err) {
            console.error('Error submitting iteration:', err);
            setError(err.message || 'Failed to submit iteration. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    // ── View a historical iteration ───────────────────────────────────────────
    const viewIteration = (iteration) => {
        setCode(iteration.code_snapshot);
        setFeedback(iteration.feedback);
    };

    const getLanguageExtension = () => {
        if (!challenge) return python();
        return challenge.language === 'javascript' ? javascript() : python();
    };

    // ── Render ────────────────────────────────────────────────────────────────
    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
        );
    }

    if (error && !challenge) {
        return (
            <div className="max-w-2xl mx-auto p-6 mt-10 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center">
                <div className="text-2xl mb-2">⚠️</div>
                <div className="font-semibold">{error}</div>
            </div>
        );
    }

    const stageGuide = REFINEMENT_STAGES[currentStage]?.guide;

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">🔄 Iteration Chamber</h1>
                <p className="text-gray-600 mt-1">Refine your code through 4 stages of engineering excellence</p>
                {challenge && (
                    <h2 className="text-xl font-semibold text-gray-800 mt-3">{challenge.title}</h2>
                )}
                {error && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-red-600 text-sm">{error}</div>
                )}
            </div>

            {/* Stage Progress */}
            <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900">Refinement Progress</h3>
                    <div className="text-sm text-gray-600">
                        Engineering Maturity:{' '}
                        <span className="font-bold text-blue-600">{Math.round(engineeringScore * 100)}%</span>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {Object.entries(REFINEMENT_STAGES).map(([key, stage], index) => {
                        const stageIndex = STAGE_KEYS.indexOf(currentStage);
                        const isComplete = stageIndex > index;
                        const isCurrent = currentStage === key;
                        const isLocked = !isComplete && !isCurrent;

                        return (
                            <div key={key} className="flex-1">
                                <div
                                    onClick={() => {
                                        if (!isLocked) {
                                            setCurrentStage(key);
                                            setCurrentIteration(
                                                iterations.filter((it) => it.stage === key).length + 1
                                            );
                                        }
                                    }}
                                    title={isLocked ? 'Complete previous stages first' : `Switch to ${stage.name}`}
                                    className={`relative p-4 rounded-lg border-2 transition-all select-none
                                        ${isCurrent
                                            ? `${STAGE_COLOR_CLASSES[key]?.active || 'border-blue-500 bg-blue-50'} scale-105`
                                            : isComplete
                                                ? 'border-green-500 bg-green-50 hover:bg-green-100 hover:scale-105'
                                                : 'border-gray-300 bg-gray-50 opacity-50'
                                        }
                                        ${isLocked ? 'cursor-not-allowed' : 'cursor-pointer'}
                                    `}
                                >
                                    <div className="flex items-center gap-2">
                                        <div className="text-2xl">{isLocked ? '🔒' : stage.icon}</div>
                                        <div className="flex-1">
                                            <div className="font-semibold text-sm">{stage.name}</div>
                                            <div className="text-xs text-gray-600">{stage.description}</div>
                                        </div>
                                        {isComplete && <div className="text-green-600 text-xl">✓</div>}
                                        {isCurrent && (
                                            <div className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                                                ACTIVE
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="mt-4 text-sm text-gray-600 flex items-center gap-2">
                    <span className="font-medium">Current Iteration:</span>
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-semibold">
                        #{currentIteration}
                    </span>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Code Editor */}
                <div className="bg-white rounded-xl shadow-md overflow-hidden">
                    <div className="bg-gray-800 text-white px-6 py-3 flex items-center justify-between">
                        <span className="font-semibold">Code Editor</span>
                        <span className="text-sm text-gray-300">
                            {REFINEMENT_STAGES[currentStage]?.name} Stage
                        </span>
                    </div>
                    <div className="p-4">
                        <CodeMirror
                            value={code}
                            height="500px"
                            extensions={[getLanguageExtension()]}
                            onChange={(value) => setCode(value)}
                            theme="dark"
                        />
                        <button
                            onClick={submitIteration}
                            disabled={submitting || !code.trim()}
                            className="w-full mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-semibold"
                        >
                            {submitting ? 'Analysing…' : `Submit Iteration #${currentIteration}`}
                        </button>
                    </div>
                </div>

                {/* Feedback + Stage Guide */}
                <div className="space-y-6">
                    {/* AI Feedback */}
                    {feedback && (
                        <div className="bg-white rounded-xl shadow-md p-6">
                            <h3 className="text-lg font-bold text-gray-900 mb-4">
                                🤖 AI Feedback — {REFINEMENT_STAGES[currentStage]?.name} Analysis
                            </h3>

                            {/* Score bar */}
                            <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                                <div className="flex items-center justify-between">
                                    <span className="font-semibold text-gray-900">Quality Score:</span>
                                    <span className={`text-2xl font-bold ${feedback.stage_score >= 0.8
                                        ? 'text-green-600'
                                        : feedback.stage_score >= 0.6
                                            ? 'text-yellow-600'
                                            : 'text-red-600'
                                        }`}>
                                        {Math.round((feedback.stage_score || 0) * 100)}%
                                    </span>
                                </div>
                                <div className="mt-2 bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-blue-600 h-2 rounded-full transition-all"
                                        style={{ width: `${(feedback.stage_score || 0) * 100}%` }}
                                    />
                                </div>
                            </div>

                            {/* Detailed feedback */}
                            <div className="space-y-3">
                                {feedback.strengths?.length > 0 && (
                                    <div>
                                        <h4 className="font-semibold text-green-700 mb-2">✅ Strengths</h4>
                                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                            {feedback.strengths.map((s, i) => <li key={i}>{s}</li>)}
                                        </ul>
                                    </div>
                                )}
                                {feedback.issues?.length > 0 && (
                                    <div>
                                        <h4 className="font-semibold text-red-700 mb-2">⚠️ Issues to Address</h4>
                                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                            {feedback.issues.map((s, i) => <li key={i}>{s}</li>)}
                                        </ul>
                                    </div>
                                )}
                                {feedback.suggestions?.length > 0 && (
                                    <div>
                                        <h4 className="font-semibold text-blue-700 mb-2">💡 Suggestions</h4>
                                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                                            {feedback.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                                        </ul>
                                    </div>
                                )}
                            </div>

                            {/* Bug fix: stage_passed is now in feedback dict from backend */}
                            {feedback.stage_passed && (
                                <div className="mt-4 p-3 bg-green-50 border border-green-300 rounded-lg">
                                    <div className="flex items-center gap-2 text-green-800">
                                        <span className="text-xl">🎉</span>
                                        <span className="font-semibold">Stage Passed! Moving to next stage.</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Stage Guide */}
                    {stageGuide && (
                        <div className="bg-white rounded-xl shadow-md p-6">
                            <h3 className="text-lg font-bold text-gray-900 mb-3">
                                {REFINEMENT_STAGES[currentStage]?.icon} {REFINEMENT_STAGES[currentStage]?.name} Stage Guide
                            </h3>
                            <div className="text-sm text-gray-700">
                                <p className="font-medium mb-2">{stageGuide.heading}</p>
                                <ul className="list-disc list-inside space-y-1 ml-2">
                                    {stageGuide.points.map((p, i) => <li key={i}>{p}</li>)}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Iteration History */}
            {iterations.length > 0 && (
                <div className="bg-white rounded-xl shadow-md p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">📜 Iteration History</h3>
                    <div className="space-y-3">
                        {iterations.map((iteration, idx) => (
                            // Bug fix: key on the outermost element
                            <div
                                key={idx}
                                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                                onClick={() => viewIteration(iteration)}
                            >
                                <div className="flex items-center gap-4">
                                    <div className="text-2xl">{REFINEMENT_STAGES[iteration.stage]?.icon}</div>
                                    <div>
                                        <div className="font-semibold text-gray-900">
                                            Iteration #{iteration.iteration_number} — {REFINEMENT_STAGES[iteration.stage]?.name}
                                        </div>
                                        <div className="text-sm text-gray-600">
                                            {iteration.submitted_at
                                                ? new Date(iteration.submitted_at).toLocaleString()
                                                : 'Unknown time'}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="text-right">
                                        <div className="text-sm text-gray-600">Quality Score</div>
                                        <div className={`text-lg font-bold ${(iteration.quality_score || 0) >= 0.8
                                            ? 'text-green-600'
                                            : (iteration.quality_score || 0) >= 0.6
                                                ? 'text-yellow-600'
                                                : 'text-red-600'
                                            }`}>
                                            {Math.round((iteration.quality_score || 0) * 100)}%
                                        </div>
                                    </div>
                                    <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                                        onClick={(e) => { e.stopPropagation(); viewIteration(iteration); }}>
                                        View
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
