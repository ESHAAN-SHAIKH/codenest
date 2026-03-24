import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL + '/api' : 'http://localhost:5000/api';

export default function AnalyticsDashboard({ userId }) {
    const [insights, setInsights] = useState(null);
    const [misconceptions, setMisconceptions] = useState([]);
    const [learningVelocity, setLearningVelocity] = useState(null);
    const [cognitiveLoad, setCognitiveLoad] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (userId) {
            fetchAnalytics();
        }
    }, [userId]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const [insightsRes, misconceptionsRes, velocityRes, loadRes] = await Promise.allSettled([
                axios.get(`${API_BASE}/analytics/insights/${userId}`),
                axios.get(`${API_BASE}/analytics/misconceptions/${userId}`),
                axios.get(`${API_BASE}/analytics/learning-velocity/${userId}`),
                axios.get(`${API_BASE}/analytics/cognitive-load/${userId}`)
            ]);

            if (insightsRes.status === 'fulfilled') setInsights(insightsRes.value.data.data);
            if (misconceptionsRes.status === 'fulfilled') setMisconceptions(misconceptionsRes.value.data.data.misconceptions || []);
            if (velocityRes.status === 'fulfilled') setLearningVelocity(velocityRes.value.data.data);
            if (loadRes.status === 'fulfilled') setCognitiveLoad(loadRes.value.data.data);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">📈 Analytics Dashboard</h1>
                <p className="text-gray-600 mt-1">Deep insights into your learning patterns and cognitive performance</p>
            </div>

            {/* Key Insights */}
            {insights && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium opacity-90">Overall Progress</span>
                            <span className="text-2xl">📊</span>
                        </div>
                        <div className="text-4xl font-bold">{Math.round(insights.overall_progress * 100)}%</div>
                        <div className="text-sm opacity-90 mt-1">Mastery across all concepts</div>
                    </div>

                    <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium opacity-90">Learning Streak</span>
                            <span className="text-2xl">🔥</span>
                        </div>
                        <div className="text-4xl font-bold">{insights.learning_streak || 0} days</div>
                        <div className="text-sm opacity-90 mt-1">Keep it going!</div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium opacity-90">Total Practice Time</span>
                            <span className="text-2xl">⏱️</span>
                        </div>
                        <div className="text-4xl font-bold">{Math.round((insights.total_time_spent || 0) / 60)}h</div>
                        <div className="text-sm opacity-90 mt-1">Coding and learning</div>
                    </div>
                </div>
            )}

            {/* Learning Velocity */}
            {learningVelocity && (
                <div className="bg-white rounded-xl shadow-md p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">📈 Learning Velocity</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <div className="text-sm text-gray-600 mb-2">Improvement Rate</div>
                            <div className="flex items-baseline gap-2">
                                <div className="text-3xl font-bold text-green-600">
                                    +{Math.round(learningVelocity.improvement_rate * 100)}%
                                </div>
                                <div className="text-sm text-gray-600">per week</div>
                            </div>
                            <div className="mt-4 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-2 bg-green-500 rounded-full transition-all"
                                    style={{ width: `${Math.min(learningVelocity.improvement_rate * 100, 100)}%` }}
                                ></div>
                            </div>
                        </div>

                        <div>
                            <div className="text-sm text-gray-600 mb-2">Consistency Score</div>
                            <div className="flex items-baseline gap-2">
                                <div className="text-3xl font-bold text-blue-600">
                                    {Math.round((learningVelocity.consistency_score || 0.5) * 100)}%
                                </div>
                            </div>
                            <div className="mt-4 text-sm text-gray-700">
                                {learningVelocity.consistency_score >= 0.8
                                    ? '🎯 Excellent consistency!'
                                    : learningVelocity.consistency_score >= 0.6
                                        ? '👍 Good rhythm, keep it up'
                                        : '💪 Try to practice more regularly'}
                            </div>
                        </div>
                    </div>

                    {learningVelocity.milestones && learningVelocity.milestones.length > 0 && (
                        <div className="mt-6">
                            <div className="text-sm font-semibold text-gray-700 mb-3">Recent Milestones</div>
                            <div className="space-y-2">
                                {learningVelocity.milestones.map((milestone, idx) => (
                                    <div key={idx} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                                        <span className="text-xl">🎖️</span>
                                        <div className="flex-1">
                                            <div className="font-medium text-gray-900">{milestone.achievement}</div>
                                            <div className="text-xs text-gray-600">{milestone.date}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Misconception Clusters */}
            {misconceptions.length > 0 && (
                <div className="bg-white rounded-xl shadow-md p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">🔍 Error Pattern Analysis</h3>
                    <p className="text-sm text-gray-600 mb-4">
                        Recurring mistakes to focus on during practice
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {misconceptions.map((misconception, idx) => (
                            <div
                                key={idx}
                                className="border-2 border-red-200 bg-red-50 rounded-lg p-4"
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div className="flex-1">
                                        <div className="font-semibold text-gray-900">
                                            {misconception.misconception_type.replace(/_/g, ' ').toUpperCase()}
                                        </div>
                                        <div className="text-sm text-gray-700 mt-1">
                                            {misconception.description || 'Common error pattern detected'}
                                        </div>
                                    </div>
                                    <div className="ml-4 text-center">
                                        <div className="text-2xl font-bold text-red-600">
                                            {misconception.occurrence_count}
                                        </div>
                                        <div className="text-xs text-gray-600">times</div>
                                    </div>
                                </div>

                                <div className="mt-3 flex items-center gap-2">
                                    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                        {misconception.concept_name}
                                    </span>
                                    {misconception.resolved && (
                                        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                                            ✓ Resolved
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Cognitive Load Analysis */}
            {cognitiveLoad && (
                <div className="bg-white rounded-xl shadow-md p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">🧠 Cognitive Load Analysis</h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-2">Average Challenge Difficulty</div>
                            <div className="text-3xl font-bold text-blue-600">
                                {cognitiveLoad.average_difficulty?.toFixed(1) || 'N/A'}/10
                            </div>
                        </div>

                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-2">Success Rate Under Pressure</div>
                            <div className="text-3xl font-bold text-purple-600">
                                {Math.round((cognitiveLoad.pressure_success_rate || 0) * 100)}%
                            </div>
                        </div>

                        <div className="text-center p-4 bg-green-50 rounded-lg">
                            <div className="text-sm text-gray-600 mb-2">Optimal Difficulty Zone</div>
                            <div className="text-3xl font-bold text-green-600">
                                {cognitiveLoad.optimal_difficulty_range?.join('-') || '5-7'}/10
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
                        <div className="flex items-start gap-3">
                            <span className="text-xl">💡</span>
                            <div>
                                <div className="font-semibold text-yellow-900">Recommendation</div>
                                <div className="text-sm text-yellow-800 mt-1">
                                    {cognitiveLoad.recommendation ||
                                        'Focus on challenges in your optimal difficulty zone for maximum learning efficiency'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!insights && !misconceptions.length && !learningVelocity && (
                <div className="bg-white rounded-xl shadow-md p-12 text-center">
                    <div className="text-6xl mb-4">📊</div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">Not Enough Data Yet</h3>
                    <p className="text-gray-600">
                        Complete more challenges to see detailed analytics and insights
                    </p>
                </div>
            )}
        </div>
    );
}
