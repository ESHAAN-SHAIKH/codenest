import { useState, useEffect } from 'react';
import useAuthStore from '../../stores/useAuthStore';
import PracticeModal from '../../components/PracticeModal';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const CATEGORY_META = {
    fundamentals: { icon: '📚', color: 'from-blue-500 to-blue-600', order: 1, desc: 'The building blocks — variables, types, and basic I/O. Start here!' },
    control_flow: { icon: '🔄', color: 'from-purple-500 to-purple-600', order: 2, desc: 'Make decisions and repeat actions with conditionals and loops.' },
    functions: { icon: '⚙️', color: 'from-indigo-500 to-indigo-600', order: 3, desc: 'Organize code into reusable blocks. Essential for any project.' },
    data_structures: { icon: '📦', color: 'from-teal-500 to-teal-600', order: 4, desc: 'Store and organize data with lists, dicts, sets, and tuples.' },
    debugging: { icon: '🔍', color: 'from-red-500 to-red-600', order: 5, desc: 'Find and fix bugs like a pro. Every developer needs this.' },
    quality: { icon: '✨', color: 'from-pink-500 to-pink-600', order: 6, desc: 'Write clean, readable code that others (and future you) will love.' },
    complexity: { icon: '⚡', color: 'from-yellow-500 to-orange-500', order: 7, desc: 'Understand performance — why some code is fast and some is slow.' },
};

function getCategoryMeta(category) {
    return CATEGORY_META[category] || { icon: '📝', color: 'from-gray-500 to-gray-600' };
}

function formatCategory(cat) {
    return (cat || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function difficultyLabel(level) {
    if (level <= 3) return { text: 'Beginner', cls: 'bg-green-100 text-green-700', emoji: '🌱' };
    if (level <= 6) return { text: 'Intermediate', cls: 'bg-yellow-100 text-yellow-700', emoji: '🌿' };
    return { text: 'Advanced', cls: 'bg-red-100 text-red-700', emoji: '🌲' };
}

function masteryBadge(score) {
    if (score == null) return { label: 'Not Started', cls: 'bg-gray-100 text-gray-500', bar: 'bg-gray-300' };
    if (score >= 0.8) return { label: `${Math.round(score * 100)}% ★ Strong`, cls: 'bg-green-100 text-green-700', bar: 'bg-green-500' };
    if (score >= 0.5) return { label: `${Math.round(score * 100)}% Progress`, cls: 'bg-yellow-100 text-yellow-700', bar: 'bg-yellow-500' };
    if (score > 0) return { label: `${Math.round(score * 100)}% Weak`, cls: 'bg-red-100 text-red-700', bar: 'bg-red-500' };
    return { label: '0% – Start', cls: 'bg-blue-100 text-blue-700', bar: 'bg-blue-300' };
}

export default function ConceptMap() {
    const { token, isAuthenticated } = useAuthStore();
    const [concepts, setConcepts] = useState([]);
    const [masteryMap, setMasteryMap] = useState({});
    const [selectedConcept, setSelectedConcept] = useState(null);
    const [practiceTarget, setPracticeTarget] = useState(null);
    const [filter, setFilter] = useState('all');
    const [conceptsLoading, setConceptsLoading] = useState(true);
    const [masteryLoading, setMasteryLoading] = useState(false);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState('');

    // Phase 1: Load concepts immediately — no auth needed
    useEffect(() => {
        loadConcepts();
    }, []);

    // Phase 2: Load mastery when authenticated
    useEffect(() => {
        if (isAuthenticated && token) loadMastery();
    }, [isAuthenticated, token]);

    const loadConcepts = async () => {
        setConceptsLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE}/cognitive/concepts`);
            if (!res.ok) throw new Error('Failed to load concepts');
            const data = await res.json();
            setConcepts(data.data?.concepts || []);
        } catch {
            setError('Could not load concepts. Is the backend running?');
        } finally {
            setConceptsLoading(false);
        }
    };

    const loadMastery = async () => {
        if (!token) return;
        setMasteryLoading(true);
        try {
            const res = await fetch(`${API_BASE}/cognitive/mastery/me`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error('Mastery fetch failed');
            const data = await res.json();
            const records = data.data?.concepts || [];
            const map = {};
            for (const m of records) map[m.concept_id] = m;
            setMasteryMap(map);
        } catch {
            // Mastery data is optional — fail silently
        } finally {
            setMasteryLoading(false);
        }
    };

    const getMastery = (id) => masteryMap[id] ?? null;
    // Treat concepts with 0 practices as 0% mastery (backend seeds fake scores)
    const getMasteryScore = (id) => {
        const record = masteryMap[id];
        if (!record || (record.practice_count ?? 0) === 0) return null;
        return record.mastery_score ?? null;
    };
    const hasPracticed = (id) => (masteryMap[id]?.practice_count ?? 0) > 0;
    const isDueForReview = (id) => hasPracticed(id) && (masteryMap[id]?.due_for_review === true);

    const groupByCategory = (conceptList) => {
        const groups = conceptList.reduce((acc, c) => {
            acc[c.category] = acc[c.category] || [];
            acc[c.category].push(c);
            return acc;
        }, {});
        // Sort concepts within each category by difficulty (easiest first)
        for (const cat of Object.keys(groups)) {
            groups[cat].sort((a, b) => (a.difficulty_level || 0) - (b.difficulty_level || 0));
        }
        return groups;
    };

    const filteredConcepts = concepts.filter(c => {
        // Search filter
        const q = search.toLowerCase();
        if (q && !c.name.toLowerCase().includes(q) && !c.category.toLowerCase().includes(q)) return false;
        // Mastery filter
        const score = getMasteryScore(c.id);
        if (filter === 'weak') return score !== null && score < 0.5;
        if (filter === 'strong') return score !== null && score >= 0.8;
        if (filter === 'due') return isDueForReview(c.id);
        if (filter === 'not_started') return !hasPracticed(c.id);
        return true;
    });

    const grouped = groupByCategory(filteredConcepts);

    // Sort category groups by recommended learning order
    const sortedCategories = Object.entries(grouped).sort(([a], [b]) => {
        return (CATEGORY_META[a]?.order ?? 99) - (CATEGORY_META[b]?.order ?? 99);
    });

    // Find the recommended next concept (easiest unpracticed)
    const recommendedConcept = concepts
        .slice()
        .sort((a, b) => {
            const orderA = CATEGORY_META[a.category]?.order ?? 99;
            const orderB = CATEGORY_META[b.category]?.order ?? 99;
            if (orderA !== orderB) return orderA - orderB;
            return (a.difficulty_level || 0) - (b.difficulty_level || 0);
        })
        .find(c => !hasPracticed(c.id));

    // Stats — only count concepts where user has actually practiced
    const practicedRecords = Object.values(masteryMap).filter(m => (m.practice_count ?? 0) > 0);
    const started = practicedRecords.length;
    const avgMastery = started === 0 ? 0
        : practicedRecords.reduce((s, m) => s + (m.mastery_score ?? 0), 0) / started;
    const strong = practicedRecords.filter(m => m.mastery_score >= 0.8).length;

    const handleMasteryUpdated = () => {
        setPracticeTarget(null);
        if (isAuthenticated && token) loadMastery();
    };

    const openPractice = (concept, e) => {
        e?.stopPropagation();
        setPracticeTarget(concept);
    };

    if (conceptsLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 gap-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-500 text-sm font-medium">Loading concept map…</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center max-w-sm">
                    <div className="text-4xl mb-3">😿</div>
                    <p className="text-red-700 font-semibold mb-4">{error}</p>
                    <button onClick={loadConcepts} className="px-5 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6">
            {/* Practice Modal */}
            {practiceTarget && (
                <PracticeModal
                    concept={practiceTarget}
                    token={token}
                    onClose={() => setPracticeTarget(null)}
                    onMasteryUpdated={handleMasteryUpdated}
                />
            )}

            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex-1">
                    <h1 className="text-3xl font-bold text-gray-900">🗺️ Concept Map</h1>
                    <p className="text-gray-500 mt-1 text-sm">
                        {isAuthenticated
                            ? masteryLoading ? 'Loading your mastery data…' : `${started} of ${concepts.length} concepts practiced`
                            : 'Log in to track your mastery progress'}
                    </p>
                </div>
                <button
                    onClick={() => { loadConcepts(); if (isAuthenticated && token) loadMastery(); }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium self-start sm:self-auto"
                >
                    ↺ Refresh
                </button>
            </div>

            {/* Beginner Welcome Banner */}
            {isAuthenticated && started === 0 && !conceptsLoading && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
                    <div className="flex items-start gap-4">
                        <div className="text-4xl">🚀</div>
                        <div className="flex-1">
                            <h2 className="text-lg font-bold text-gray-900 mb-1">Welcome! Here's how it works</h2>
                            <p className="text-sm text-gray-600 mb-3">
                                Each card is a <strong>programming concept</strong> you can learn. Click <strong>"Start →"</strong> to open a hands-on coding exercise.
                                Write code, submit it, and your mastery score grows! We recommend starting with <strong>Fundamentals</strong> and working down.
                            </p>
                            <div className="flex items-center gap-2 text-xs flex-wrap">
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-lg font-medium">🌱 Beginner = Easy</span>
                                <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-lg font-medium">🌿 Intermediate = Medium</span>
                                <span className="px-2 py-1 bg-red-100 text-red-700 rounded-lg font-medium">🌲 Advanced = Challenging</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Recommended Next Concept */}
            {isAuthenticated && recommendedConcept && started < concepts.length && (
                <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl p-5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-xl">🎯</div>
                            <div>
                                <div className="text-xs font-semibold text-emerald-600 uppercase tracking-wide">Recommended Next</div>
                                <div className="font-bold text-gray-900">{recommendedConcept.name}</div>
                                <div className="text-xs text-gray-500">{formatCategory(recommendedConcept.category)} · {difficultyLabel(recommendedConcept.difficulty_level).emoji} {difficultyLabel(recommendedConcept.difficulty_level).text}</div>
                            </div>
                        </div>
                        <button
                            onClick={e => openPractice(recommendedConcept, e)}
                            className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-all font-semibold text-sm shadow-sm"
                        >
                            Start This →
                        </button>
                    </div>
                </div>
            )}

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Concepts', value: concepts.length, sub: `${Object.keys(grouped).length} categories`, border: 'border-blue-500' },
                    { label: 'Started', value: started, sub: 'concepts practiced', border: 'border-indigo-500' },
                    { label: 'Avg Mastery', value: `${Math.round(avgMastery * 100)}%`, sub: 'across started', border: 'border-green-500' },
                    { label: 'Strong (≥80%)', value: strong, sub: 'mastered', border: 'border-purple-500' },
                ].map(s => (
                    <div key={s.label} className={`bg-white rounded-xl shadow-sm p-5 border-l-4 ${s.border}`}>
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{s.label}</div>
                        <div className="text-3xl font-bold text-gray-900 mt-1">{s.value}</div>
                        <div className="text-xs text-gray-400 mt-0.5">{s.sub}</div>
                    </div>
                ))}
            </div>

            {/* Filter + Search Bar */}
            <div className="flex flex-col sm:flex-row gap-3">
                {/* Search */}
                <div className="relative flex-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Search concepts…"
                        className="w-full pl-8 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
                    />
                </div>
                {/* Filter pills */}
                <div className="flex gap-2 flex-wrap">
                    {[
                        { key: 'all', label: 'All', active: 'bg-blue-600 text-white', inactive: 'bg-white text-gray-600 border border-gray-200' },
                        { key: 'not_started', label: '🆕 New', active: 'bg-blue-500 text-white', inactive: 'bg-white text-gray-600 border border-gray-200' },
                        { key: 'weak', label: 'Weak', active: 'bg-red-600 text-white', inactive: 'bg-white text-gray-600 border border-gray-200' },
                        { key: 'strong', label: 'Strong', active: 'bg-green-600 text-white', inactive: 'bg-white text-gray-600 border border-gray-200' },
                        { key: 'due', label: '⏰ Due', active: 'bg-orange-500 text-white', inactive: 'bg-white text-gray-600 border border-gray-200' },
                    ].map(f => (
                        <button
                            key={f.key}
                            onClick={() => setFilter(f.key)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all hover:shadow-sm ${filter === f.key ? f.active : f.inactive}`}
                        >
                            {f.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Empty Filter State */}
            {filteredConcepts.length === 0 && !conceptsLoading && (
                <div className="bg-white rounded-2xl shadow-sm p-12 text-center">
                    <div className="text-5xl mb-4">🔭</div>
                    <p className="text-gray-600 font-semibold text-lg">No concepts match this filter</p>
                    <p className="text-gray-400 text-sm mt-1">Try a different filter or clear your search</p>
                    <button onClick={() => { setFilter('all'); setSearch(''); }} className="mt-4 px-5 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                        Show All
                    </button>
                </div>
            )}

            {/* Concept Groups */}
            <div className="space-y-6">
                {sortedCategories.map(([category, conceptList]) => {
                    const meta = getCategoryMeta(category);
                    return (
                        <div key={category} className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100">
                            {/* Category Header */}
                            <div className={`bg-gradient-to-r ${meta.color} px-6 py-4`}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                            <span className="text-2xl">{meta.icon}</span>
                                            {formatCategory(category)}
                                        </h2>
                                        {meta.desc && (
                                            <p className="text-white/70 text-xs mt-0.5">{meta.desc}</p>
                                        )}
                                    </div>
                                    <span className="text-sm text-white/80 font-medium">
                                        {conceptList.length} concept{conceptList.length !== 1 ? 's' : ''}
                                    </span>
                                </div>
                            </div>

                            {/* Concepts Grid */}
                            <div className="p-5 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {conceptList.map(concept => {
                                    const mastery = getMastery(concept.id);
                                    const practiced = hasPracticed(concept.id);
                                    const score = practiced ? (mastery?.mastery_score ?? null) : null;
                                    const badge = masteryBadge(score);
                                    const isSelected = selectedConcept?.id === concept.id;

                                    return (
                                        <div
                                            key={concept.id}
                                            onClick={() => setSelectedConcept(isSelected ? null : concept)}
                                            className={`rounded-xl border-2 p-4 cursor-pointer transition-all select-none
                        ${score >= 0.8 ? 'border-green-200 bg-green-50' :
                                                    score >= 0.5 ? 'border-yellow-200 bg-yellow-50' :
                                                        score > 0 ? 'border-red-200 bg-red-50' :
                                                            'border-gray-100 bg-gray-50'}
                        ${isSelected ? 'ring-2 ring-blue-400 scale-[1.02] shadow-md' : 'hover:shadow-md hover:-translate-y-0.5'}
                      `}
                                        >
                                            {/* Concept name + badge */}
                                            <div className="flex items-start justify-between gap-2 mb-2">
                                                <h3 className="font-semibold text-gray-900 text-sm leading-snug flex-1">{concept.name}</h3>
                                                <span className={`text-xs px-2 py-0.5 rounded-full font-semibold whitespace-nowrap flex-shrink-0 ${badge.cls}`}>
                                                    {badge.label}
                                                </span>
                                            </div>

                                            {/* Description */}
                                            {concept.description && (
                                                <p className="text-xs text-gray-600 line-clamp-2 mb-3">{concept.description}</p>
                                            )}

                                            {/* Mastery bar */}
                                            <div className="w-full bg-gray-200 rounded-full h-1.5 mb-3 overflow-hidden">
                                                {!practiced ? (
                                                    <div
                                                        className="h-1.5 rounded-full w-full"
                                                        style={{ background: 'repeating-linear-gradient(90deg, #e5e7eb 0px, #e5e7eb 4px, #d1d5db 4px, #d1d5db 8px)' }}
                                                        title="Not started"
                                                    />
                                                ) : (
                                                    <div
                                                        className={`h-1.5 rounded-full transition-all duration-700 ${badge.bar}`}
                                                        style={{ width: `${Math.max(4, Math.round((score ?? 0) * 100))}%` }}
                                                    />
                                                )}
                                            </div>

                                            {/* Footer row */}
                                            <div className="flex items-center justify-between">
                                                <div className="text-xs text-gray-400">
                                                    <span className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded ${difficultyLabel(concept.difficulty_level).cls} text-xs font-medium mr-1`}>
                                                        {difficultyLabel(concept.difficulty_level).emoji} {difficultyLabel(concept.difficulty_level).text}
                                                    </span>
                                                    {practiced && mastery?.practice_count ? ` · ${mastery.practice_count} practices` : ''}
                                                    {isDueForReview(concept.id) && (
                                                        <span className="ml-1.5 text-orange-500 font-semibold">⏰ Due</span>
                                                    )}
                                                </div>
                                                <button
                                                    onClick={e => openPractice(concept, e)}
                                                    className={`px-3 py-1 text-xs rounded-lg font-semibold transition-all
                            ${score >= 0.8 ? 'bg-green-600 text-white hover:bg-green-700' :
                                                            score > 0 ? 'bg-yellow-500 text-white hover:bg-yellow-600' :
                                                                'bg-blue-600 text-white hover:bg-blue-700'}
                          `}
                                                >
                                                    {score >= 0.8 ? '✓ Review' : score > 0 ? 'Practice' : 'Start →'}
                                                </button>
                                            </div>

                                            {/* Prerequisites resolved to names */}
                                            {concept.prerequisite_concepts?.length > 0 && (
                                                <div className="mt-2 flex flex-wrap gap-1">
                                                    {concept.prerequisite_concepts.slice(0, 3).map((p, i) => {
                                                        const name = typeof p === 'string'
                                                            ? p
                                                            : concepts.find(c => c.id === p)?.name || `#${p}`;
                                                        return (
                                                            <span key={i} className="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">
                                                                needs: {name}
                                                            </span>
                                                        );
                                                    })}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Selected Concept Detail Panel */}
            {selectedConcept && (() => {
                const m = getMastery(selectedConcept.id);
                const practiced = hasPracticed(selectedConcept.id);
                const score = practiced ? (m?.mastery_score ?? null) : null;
                const badge = masteryBadge(score);
                const meta = getCategoryMeta(selectedConcept.category);
                return (
                    <div className="fixed bottom-0 left-0 right-0 bg-white border-t-4 border-blue-500 shadow-2xl z-40 max-h-72 overflow-y-auto">
                        <div className="max-w-7xl mx-auto p-5">
                            <div className="flex items-start justify-between mb-4 gap-4">
                                <div className="flex items-start gap-3 flex-1 min-w-0">
                                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${meta.color} flex items-center justify-center text-xl flex-shrink-0`}>
                                        {meta.icon}
                                    </div>
                                    <div className="min-w-0">
                                        <h2 className="text-xl font-bold text-gray-900 truncate">{selectedConcept.name}</h2>
                                        <p className="text-gray-500 text-sm">{selectedConcept.description}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 flex-shrink-0">
                                    <button
                                        onClick={() => openPractice(selectedConcept)}
                                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all
                      ${score >= 0.8 ? 'bg-green-600 text-white hover:bg-green-700' :
                                                score > 0 ? 'bg-yellow-500 text-white hover:bg-yellow-600' :
                                                    'bg-blue-600 text-white hover:bg-blue-700'}
                    `}
                                    >
                                        {score >= 0.8 ? '✓ Review Now' : score > 0 ? '↑ Practice Now' : '→ Start Learning'}
                                    </button>
                                    <button onClick={() => setSelectedConcept(null)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">
                                        ×
                                    </button>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                                {/* Details */}
                                <div>
                                    <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Details</h3>
                                    <div className="space-y-1.5 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Category</span>
                                            <span className="font-medium">{formatCategory(selectedConcept.category)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Difficulty</span>
                                            <span className="font-medium">{selectedConcept.difficulty_level}/10</span>
                                        </div>
                                        {selectedConcept.tags?.length > 0 && (
                                            <div className="flex flex-wrap gap-1 pt-1">
                                                {selectedConcept.tags.map((t, i) => (
                                                    <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{t}</span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Prerequisites */}
                                <div>
                                    <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Prerequisites</h3>
                                    {selectedConcept.prerequisite_concepts?.length > 0 ? (
                                        <div className="flex flex-col gap-1.5">
                                            {selectedConcept.prerequisite_concepts.map((p, i) => {
                                                const name = typeof p === 'string'
                                                    ? p
                                                    : concepts.find(c => c.id === p)?.name || `Concept #${p}`;
                                                return (
                                                    <div key={i} className="text-sm px-3 py-1.5 bg-blue-50 border border-blue-100 rounded-lg text-blue-800">
                                                        {name}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-400 italic">Foundational — no prerequisites</p>
                                    )}
                                </div>

                                {/* Your Progress */}
                                <div>
                                    <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">Your Progress</h3>
                                    {m && practiced ? (
                                        <div className="space-y-1.5 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-gray-500">Mastery</span>
                                                <span className={`font-bold ${badge.cls.split(' ')[1]}`}>{Math.round((m.mastery_score ?? 0) * 100)}%</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-500">Confidence</span>
                                                <span className="font-medium">{Math.round((m.confidence_score ?? 0) * 100)}%</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-500">Practices</span>
                                                <span className="font-medium">{m.practice_count ?? 0}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-500">Success Rate</span>
                                                <span className="font-medium">{Math.round((m.success_rate ?? 0) * 100)}%</span>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-center py-2">
                                            <p className="text-sm text-gray-400 mb-2">
                                                {isAuthenticated ? 'Not practiced yet' : 'Log in to track progress'}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            })()}
        </div>
    );
}
