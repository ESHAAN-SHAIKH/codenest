import { useState, useEffect } from 'react';
import axios from 'axios';
import PracticeModal from '../../components/PracticeModal';
import useAuthStore from '../../stores/useAuthStore';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL + '/api' : 'http://localhost:5000/api';


export default function CognitiveDashboard({ userId }) {
    const { token } = useAuthStore();
    const [allConcepts, setAllConcepts] = useState([]);
    const [masteryMap, setMasteryMap] = useState({});
    const [weakConcepts, setWeakConcepts] = useState([]);
    const [dueForReview, setDueForReview] = useState([]);
    const [conceptsLoading, setConceptsLoading] = useState(true);
    const [masteryLoading, setMasteryLoading] = useState(false);
    const [error, setError] = useState(null);
    const [activeConcept, setActiveConcept] = useState(null);
    const [categoryFilter, setCategoryFilter] = useState('all');

    // Phase 1: Load all concepts immediately — no userId needed
    useEffect(() => {
        loadAllConcepts();
    }, []);

    // Phase 2: Load mastery data when userId is available
    useEffect(() => {
        if (userId) {
            loadMasteryData();
        }
    }, [userId]);

    const loadAllConcepts = async () => {
        try {
            setConceptsLoading(true);
            setError(null);
            const res = await axios.get(`${API_BASE}/cognitive/concepts`);
            setAllConcepts(res.data.data?.concepts || []);
        } catch (err) {
            setError('Could not load concepts. Is the backend running?');
        } finally {
            setConceptsLoading(false);
        }
    };

    const loadMasteryData = async () => {
        if (!userId || !token) return;
        try {
            const authHeaders = { Authorization: `Bearer ${token}` };
            setMasteryLoading(true);
            const [masteryRes, weakRes, dueRes] = await Promise.all([
                axios.get(`${API_BASE}/cognitive/mastery/me`, { headers: authHeaders }).catch(() => ({ data: { data: { concepts: [] } } })),
                axios.get(`${API_BASE}/cognitive/weak-concepts`, { headers: authHeaders }).catch(() => ({ data: { data: { weak_concepts: [] } } })),
                axios.get(`${API_BASE}/cognitive/due-for-review`, { headers: authHeaders }).catch(() => ({ data: { data: { due_concepts: [] } } })),
            ]);

            const records = masteryRes.data.data?.concepts || [];
            const map = {};
            for (const m of records) map[m.concept_id] = m;

            setMasteryMap(map);
            setWeakConcepts(weakRes.data.data?.weak_concepts || []);
            setDueForReview(dueRes.data.data?.due_concepts || []);
        } catch (err) {
            console.error('Failed to load mastery data:', err);
        } finally {
            setMasteryLoading(false);
        }
    };

    // If no practice sessions done, treat mastery as 0 regardless of backend-seeded value
    const getMastery = (id) => {
        const record = masteryMap[id];
        if (!record || (record.practice_count ?? 0) === 0) return 0;
        return record.mastery_score ?? 0;
    };
    const getPracticeCount = (id) => masteryMap[id]?.practice_count ?? 0;
    const isDue = (id) => {
        const record = masteryMap[id];
        if (!record || (record.practice_count ?? 0) === 0) return false;
        return record.due_for_review ?? false;
    };

    const masteryColor = (score) => {
        if (score >= 0.8) return 'bg-green-500';
        if (score >= 0.5) return 'bg-yellow-500';
        if (score > 0) return 'bg-red-500';
        return 'bg-gray-300';
    };

    // Derive unique categories for filtering
    const categories = [...new Set(allConcepts.map(c => c.category).filter(Boolean))];
    const filteredConcepts = categoryFilter === 'all'
        ? allConcepts
        : allConcepts.filter(c => c.category === categoryFilter);

    const totalConcepts = allConcepts.length;
    // Only count concepts where the user has actually practiced
    const practicedRecords = Object.values(masteryMap).filter(m => (m.practice_count ?? 0) > 0);
    const trackedCount = practicedRecords.length;
    const avgMastery = trackedCount === 0 ? 0
        : practicedRecords.reduce((s, m) => s + (m.mastery_score ?? 0), 0) / trackedCount;
    const strongCount = practicedRecords.filter(m => (m.mastery_score ?? 0) >= 0.8).length;

    // Filter out unpracticed concepts from weak and due-for-review lists
    const actualWeakConcepts = weakConcepts.filter(c => (c.practice_count ?? 0) > 0);
    const actualDueForReview = dueForReview.filter(c => (c.practice_count ?? 0) > 0);

    const handlePracticeClose = () => setActiveConcept(null);
    const handleMasteryUpdated = () => {
        setActiveConcept(null);
        if (userId) loadMasteryData();
    };

    if (conceptsLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
                <p className="text-gray-500 text-sm">Loading concepts…</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center max-w-md">
                    <p className="text-red-700 font-medium">{error}</p>
                    <button onClick={loadAllConcepts} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 p-6">
            {/* Practice Modal */}
            {activeConcept && (
                <PracticeModal
                    concept={activeConcept}
                    userId={userId}
                    onClose={handlePracticeClose}
                    onMasteryUpdated={handleMasteryUpdated}
                />
            )}

            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">🧠 Cognitive Training</h1>
                    {!userId && (
                        <p className="text-sm text-amber-600 mt-1">🔒 Log in to track your mastery progress</p>
                    )}
                    {userId && trackedCount === 0 && (
                        <p className="text-sm text-blue-600 mt-1">🆕 New account — click Start on any concept to begin!</p>
                    )}
                </div>
                <button
                    onClick={() => { loadAllConcepts(); if (userId) loadMasteryData(); }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                    {masteryLoading ? 'Refreshing…' : 'Refresh'}
                </button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Concepts', value: totalConcepts, sub: `${trackedCount} started`, color: 'border-blue-500' },
                    { label: 'Avg Mastery', value: `${Math.round(avgMastery * 100)}%`, sub: 'tracked concepts', color: 'border-green-500' },
                    { label: 'Strong (≥80%)', value: strongCount, sub: 'concepts', color: 'border-purple-500' },
                    { label: 'Due for Review', value: actualDueForReview.length, sub: 'concepts', color: 'border-orange-500' },
                ].map(card => (
                    <div key={card.label} className={`bg-white rounded-xl shadow-sm p-5 border-l-4 ${card.color}`}>
                        <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">{card.label}</div>
                        <div className="text-3xl font-bold text-gray-900 mt-1">{card.value}</div>
                        <div className="text-xs text-gray-400 mt-0.5">{card.sub}</div>
                    </div>
                ))}
            </div>

            {/* Weak Concepts */}
            {actualWeakConcepts.length > 0 && (
                <div className="bg-red-50 border-l-4 border-red-500 rounded-xl p-5">
                    <h3 className="font-bold text-red-900 text-lg mb-3">⚠️ Needs Attention ({actualWeakConcepts.length})</h3>
                    <div className="space-y-2">
                        {actualWeakConcepts.slice(0, 5).map(c => (
                            <div key={c.concept_id} className="flex items-center justify-between bg-white rounded-lg px-4 py-3">
                                <div>
                                    <div className="font-medium text-gray-900">{c.concept_name}</div>
                                    <div className="text-xs text-gray-500">{c.category} · {c.practice_count} attempts</div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-red-600 font-bold text-sm">{Math.round(c.mastery_score * 100)}%</span>
                                    <button
                                        onClick={() => setActiveConcept(allConcepts.find(a => a.id === c.concept_id) || { id: c.concept_id, name: c.concept_name, category: c.category, description: '', difficulty_level: 1 })}
                                        className="px-3 py-1 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 transition-colors"
                                    >
                                        Practice
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Spaced Repetition Queue */}
            {actualDueForReview.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="font-bold text-gray-900 text-lg mb-1">📚 Due for Review</h3>
                    <p className="text-gray-500 text-sm mb-4">Reinforce these to maintain your mastery</p>
                    <div className="space-y-3">
                        {actualDueForReview.map(c => (
                            <div key={c.concept_id} className="flex items-center justify-between bg-orange-50 rounded-lg px-4 py-3 border border-orange-100">
                                <div>
                                    <div className="font-semibold text-gray-900">{c.concept_name}</div>
                                    <div className="text-xs text-gray-500 mt-0.5">
                                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded mr-2">{c.category}</span>
                                        {Math.round(c.mastery_score * 100)}% mastery ·
                                        <span className="text-orange-600 font-medium ml-1">{c.days_overdue}d overdue</span>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setActiveConcept(allConcepts.find(a => a.id === c.concept_id) || { id: c.concept_id, name: c.concept_name, category: c.category, description: '', difficulty_level: 1 })}
                                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Review Now
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* All Concepts */}
            <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-1">
                    <h3 className="font-bold text-gray-900 text-lg">📊 All Concepts Progress</h3>
                    {categories.length > 1 && (
                        <select
                            value={categoryFilter}
                            onChange={e => setCategoryFilter(e.target.value)}
                            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">All Categories</option>
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat.replace(/_/g, ' ')}</option>
                            ))}
                        </select>
                    )}
                </div>
                <p className="text-gray-500 text-sm mb-4">
                    {userId
                        ? trackedCount === 0
                            ? 'Click Start to begin practicing any concept and your mastery will be tracked here.'
                            : `You've started ${trackedCount} of ${totalConcepts} concepts.`
                        : 'Log in to track your mastery.'}
                </p>
                <div className="space-y-1">
                    {filteredConcepts.map(concept => {
                        const score = getMastery(concept.id);
                        const count = getPracticeCount(concept.id);
                        const due = isDue(concept.id);
                        return (
                            <div key={concept.id} className="flex items-center gap-3 py-2.5 border-b border-gray-50 last:border-0">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-gray-900 text-sm truncate">{concept.name}</span>
                                        {due && <span className="text-xs bg-orange-100 text-orange-600 px-1.5 py-0.5 rounded font-medium">Due</span>}
                                    </div>
                                    <div className="text-xs text-gray-400">{concept.category} · Difficulty {concept.difficulty_level}/10</div>
                                </div>

                                {/* Progress bar */}
                                <div className="w-44 flex-shrink-0">
                                    <div className="flex items-center gap-2">
                                        <div className="flex-1 bg-gray-100 rounded-full h-2 relative overflow-hidden">
                                            {score === 0 ? (
                                                <div
                                                    className="h-2 rounded-full w-full"
                                                    style={{
                                                        background: 'repeating-linear-gradient(90deg, #e5e7eb 0px, #e5e7eb 4px, #d1d5db 4px, #d1d5db 8px)',
                                                    }}
                                                    title="0% mastery — not started"
                                                />
                                            ) : (
                                                <div
                                                    className={`h-2 rounded-full transition-all duration-500 ${masteryColor(score)}`}
                                                    style={{ width: `${Math.max(4, Math.round(score * 100))}%` }}
                                                />
                                            )}
                                        </div>
                                        <span className={`text-xs font-bold w-9 text-right tabular-nums ${score === 0 ? 'text-gray-400' :
                                            score >= 0.8 ? 'text-green-600' :
                                                score >= 0.5 ? 'text-yellow-600' :
                                                    'text-red-600'
                                            }`}>
                                            {Math.round(score * 100)}%
                                        </span>
                                    </div>
                                    <div className="text-xs text-gray-400 mt-0.5">{count} practice{count !== 1 ? 's' : ''}</div>
                                </div>

                                {/* Practice button */}
                                <button
                                    onClick={() => setActiveConcept(concept)}
                                    className={`px-3 py-1 text-xs rounded-lg transition-colors flex-shrink-0 font-medium ${score === 0
                                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                                        : score >= 0.8
                                            ? 'bg-green-100 text-green-700 hover:bg-green-200 border border-green-200'
                                            : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200 border border-yellow-200'
                                        }`}
                                >
                                    {score === 0 ? 'Start' : score >= 0.8 ? 'Review' : 'Practice'}
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
