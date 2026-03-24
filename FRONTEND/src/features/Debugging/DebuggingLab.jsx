import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export default function DebuggingLab({ userId }) {
    const [currentSession, setCurrentSession] = useState(null);
    const [userExplanation, setUserExplanation] = useState('');
    const [correctedCode, setCorrectedCode] = useState('');
    const [bugLocationLine, setBugLocationLine] = useState('');
    const [debuggingSkills, setDebuggingSkills] = useState(null);
    const [result, setResult] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (userId) {
            fetchDebuggingSkills();
        }
    }, [userId]);

    const fetchDebuggingSkills = async () => {
        try {
            const response = await axios.get(`${API_BASE}/debugging/skills/${userId}`);
            setDebuggingSkills(response.data.data);
        } catch (error) {
            console.error('Error fetching debugging skills:', error);
        }
    };

    const startSession = async (difficulty = 'medium') => {
        try {
            const response = await axios.post(`${API_BASE}/debugging/start`, {
                user_id: userId,
                difficulty
            });
            setCurrentSession(response.data.data);
            setUserExplanation('');
            setCorrectedCode(response.data.data.challenge.code);
            setBugLocationLine('');
            setResult(null);
        } catch (error) {
            console.error('Error starting session:', error);
            alert('Failed to start debugging session');
        }
    };

    const submitSolution = async () => {
        if (!userExplanation.trim() || !correctedCode.trim()) {
            alert('Please provide both explanation and corrected code');
            return;
        }

        try {
            setIsSubmitting(true);
            const response = await axios.post(`${API_BASE}/debugging/submit`, {
                session_id: currentSession.session.id,
                user_explanation: userExplanation,
                corrected_code: correctedCode,
                bug_location_line: bugLocationLine ? parseInt(bugLocationLine) : null
            });

            setResult(response.data.data);
            fetchDebuggingSkills(); // Refresh skills
        } catch (error) {
            console.error('Error submitting solution:', error);
            alert('Failed to submit solution');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">🔍 Debugging Lab</h1>
                    <p className="text-gray-600 mt-1">Find bugs, explain them, fix them - level up your debugging skills</p>
                </div>
                {!currentSession && (
                    <div className="flex gap-3">
                        <button
                            onClick={() => startSession('easy')}
                            disabled={!userId}
                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                            Easy Bug
                        </button>
                        <button
                            onClick={() => startSession('medium')}
                            disabled={!userId}
                            className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                            Medium Bug
                        </button>
                        <button
                            onClick={() => startSession('hard')}
                            disabled={!userId}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        >
                            Hard Bug
                        </button>
                    </div>
                )}
            </div>

            {/* Welcome state when no session */}
            {!currentSession && !result && (
                <div className="bg-white rounded-xl shadow-md p-12 text-center">
                    <div className="text-6xl mb-4">🐛</div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">Ready to Debug?</h3>
                    <p className="text-gray-600 mb-4">
                        Choose a difficulty level above to start a debugging challenge.<br />
                        You'll see buggy code and need to explain the bug and fix it.
                    </p>
                    {!userId && (
                        <p className="text-sm text-amber-600">🔒 Log in to start debugging sessions</p>
                    )}
                </div>
            )}

            {/* Debugging Skills Overview */}
            {debuggingSkills && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-lg shadow-md p-4">
                        <div className="text-sm text-gray-600">Total Sessions</div>
                        <div className="text-2xl font-bold text-gray-900">{debuggingSkills.total_sessions}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow-md p-4">
                        <div className="text-sm text-gray-600">Pass Rate</div>
                        <div className="text-2xl font-bold text-green-600">
                            {Math.round(debuggingSkills.pass_rate * 100)}%
                        </div>
                    </div>
                    <div className="bg-white rounded-lg shadow-md p-4">
                        <div className="text-sm text-gray-600">Avg Debugging Skill</div>
                        <div className="text-2xl font-bold text-blue-600">
                            {Math.round(debuggingSkills.average_skill * 100)}%
                        </div>
                    </div>
                    <div className="bg-white rounded-lg shadow-md p-4">
                        <div className="text-sm text-gray-600">Avg Time</div>
                        <div className="text-2xl font-bold text-gray-900">
                            {Math.floor(debuggingSkills.average_time / 60)}m {debuggingSkills.average_time % 60}s
                        </div>
                    </div>
                </div>
            )}

            {/* Current Session */}
            {currentSession && !result && (
                <div className="space-y-6">
                    {/* Challenge Info */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="font-semibold text-blue-900">Bug Type: {currentSession.challenge.bug_type.replace(/_/g, ' ').toUpperCase()}</div>
                                <div className="text-sm text-blue-700 mt-1">Difficulty: {currentSession.challenge.difficulty}</div>
                            </div>
                            <div className="text-sm text-blue-700">
                                Session ID: #{currentSession.session.id}
                            </div>
                        </div>
                    </div>

                    {/* Code with Bug */}
                    <div className="bg-white rounded-lg shadow-md overflow-hidden">
                        <div className="bg-gray-800 text-white px-4 py-3 flex items-center justify-between">
                            <span className="font-semibold">🐛 Buggy Code</span>
                            <span className="text-sm text-gray-300">Find the bug and explain it</span>
                        </div>
                        <pre className="p-4 bg-gray-900 text-gray-100 overflow-x-auto text-sm font-mono">
                            {currentSession.challenge.code}
                        </pre>
                    </div>

                    {/* Expected vs Actual Output */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white rounded-lg shadow-md p-4">
                            <h3 className="font-semibold text-green-700 mb-2">✅ Expected Output</h3>
                            <pre className="bg-green-50 p-3 rounded text-sm font-mono text-gray-800">
                                {currentSession.challenge.expected_output}
                            </pre>
                        </div>
                        <div className="bg-white rounded-lg shadow-md p-4">
                            <h3 className="font-semibold text-red-700 mb-2">❌ Actual (Buggy) Output</h3>
                            <pre className="bg-red-50 p-3 rounded text-sm font-mono text-gray-800">
                                {currentSession.challenge.buggy_output}
                            </pre>
                        </div>
                    </div>

                    {/* User Input */}
                    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
                        <h3 className="text-xl font-bold text-gray-900">Your Solution</h3>

                        {/* Explanation */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                1. Explain the bug (what's wrong and why?)
                            </label>
                            <textarea
                                value={userExplanation}
                                onChange={(e) => setUserExplanation(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                rows="4"
                                placeholder="Describe what the bug is, where it's located, and why it causes the problem..."
                            />
                        </div>

                        {/* Bug Location (Optional) */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                2. Bug location (optional - which line number?)
                            </label>
                            <input
                                type="number"
                                value={bugLocationLine}
                                onChange={(e) => setBugLocationLine(e.target.value)}
                                className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                                placeholder="Line #"
                            />
                        </div>

                        {/* Corrected Code */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                3. Provide the corrected code
                            </label>
                            <textarea
                                value={correctedCode}
                                onChange={(e) => setCorrectedCode(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                                rows="10"
                            />
                        </div>

                        {/* Submit */}
                        <div className="flex gap-3">
                            <button
                                onClick={submitSolution}
                                disabled={isSubmitting}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                            >
                                {isSubmitting ? 'Submitting...' : 'Submit Solution'}
                            </button>
                            <button
                                onClick={() => setCurrentSession(null)}
                                className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Result */}
            {result && (
                <div className="space-y-6">
                    <div className={`border-l-4 rounded-lg p-6 ${result.passed ? 'bg-green-50 border-green-500' : 'bg-yellow-50 border-yellow-500'}`}>
                        <h2 className="text-2xl font-bold mb-4">
                            {result.passed ? '✅ Well Done!' : '⚠️ Not Quite There'}
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div>
                                <div className="text-sm text-gray-600">Explanation Quality</div>
                                <div className="text-2xl font-bold">{Math.round(result.explanation_quality * 100)}%</div>
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Code Correctness</div>
                                <div className="text-2xl font-bold">{Math.round(result.correctness * 100)}%</div>
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Debugging Skill</div>
                                <div className="text-2xl font-bold">{Math.round(result.debugging_skill * 100)}%</div>
                            </div>
                        </div>

                        {/* AI Feedback */}
                        {result.ai_evaluation && (
                            <div className="bg-white rounded-lg p-4 mt-4">
                                <h3 className="font-semibold text-gray-900 mb-2">AI Feedback</h3>
                                <div className="space-y-2 text-sm">
                                    <div>
                                        <span className="font-medium text-green-700">Strengths:</span>{' '}
                                        <span className="text-gray-700">{result.ai_evaluation.explanation_strengths}</span>
                                    </div>
                                    {result.ai_evaluation.explanation_weaknesses && (
                                        <div>
                                            <span className="font-medium text-orange-700">Areas to improve:</span>{' '}
                                            <span className="text-gray-700">{result.ai_evaluation.explanation_weaknesses}</span>
                                        </div>
                                    )}
                                    <div>
                                        <span className="font-medium text-blue-700">Code feedback:</span>{' '}
                                        <span className="text-gray-700">{result.ai_evaluation.code_feedback}</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <button
                            onClick={() => {
                                setCurrentSession(null);
                                setResult(null);
                            }}
                            className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                            Try Another Bug
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
