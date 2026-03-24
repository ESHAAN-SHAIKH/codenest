import { useState, useEffect } from 'react';
import useAuthStore from '../../stores/useAuthStore';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL + '/api' : 'http://localhost:5000/api';

const ARCHETYPE_CONFIG = {
    architect: {
        icon: '🏗️',
        color: 'blue',
        gradient: 'from-blue-500 to-blue-700',
        badge: 'bg-blue-100 text-blue-800 border-blue-300',
        name: 'Architect',
        description: 'Master of system design and code organization',
    },
    debugger: {
        icon: '🔍',
        color: 'red',
        gradient: 'from-red-500 to-red-700',
        badge: 'bg-red-100 text-red-800 border-red-300',
        name: 'Debugger',
        description: 'Expert at finding and fixing bugs',
    },
    optimizer: {
        icon: '⚡',
        color: 'yellow',
        gradient: 'from-yellow-500 to-yellow-700',
        badge: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        name: 'Optimizer',
        description: 'Specialist in performance and efficiency',
    },
    refactorer: {
        icon: '✨',
        color: 'purple',
        gradient: 'from-purple-500 to-purple-700',
        badge: 'bg-purple-100 text-purple-800 border-purple-300',
        name: 'Refactorer',
        description: 'Champion of clean, maintainable code',
    },
    guardian: {
        icon: '🛡️',
        color: 'green',
        gradient: 'from-green-500 to-green-700',
        badge: 'bg-green-100 text-green-800 border-green-300',
        name: 'Guardian',
        description: 'Protector against edge cases and errors',
    },
};

const RANK_NAMES = [
    '', 'Novice', 'Apprentice', 'Practitioner', 'Adept', 'Expert',
    'Master', 'Grandmaster', 'Legend', 'Mythic', 'Transcendent',
];

export default function ArchetypeDashboard() {
    const { token } = useAuthStore();
    const [archetypeProgress, setArchetypeProgress] = useState(null);
    const [selectedArchetype, setSelectedArchetype] = useState(null);
    const [evolutionPath, setEvolutionPath] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [evolutionLoading, setEvolutionLoading] = useState(false);

    const authHeaders = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
    };

    useEffect(() => {
        fetchArchetypeData();
    }, []);

    useEffect(() => {
        if (selectedArchetype) {
            fetchEvolutionPath(selectedArchetype);
        }
    }, [selectedArchetype]);

    const fetchArchetypeData = async () => {
        try {
            setLoading(true);
            setError(null);
            const res = await fetch(`${API_BASE}/archetypes/progress`, { headers: authHeaders });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to load archetype data');
            setArchetypeProgress(data.data);

            // Auto-select dominant archetype or first available
            const dominant = data.data?.dominant_archetype?.archetype_type;
            setSelectedArchetype(dominant || Object.keys(ARCHETYPE_CONFIG)[0]);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchEvolutionPath = async (archetypeType) => {
        try {
            setEvolutionLoading(true);
            const res = await fetch(`${API_BASE}/archetypes/evolution/${archetypeType}`, {
                headers: authHeaders,
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to load evolution path');
            setEvolutionPath(data.data);
        } catch (err) {
            console.error('Evolution path error:', err);
            setEvolutionPath(null);
        } finally {
            setEvolutionLoading(false);
        }
    };

    const getRankName = (level) => RANK_NAMES[level] || 'Unknown';

    // Safely render a behavior metric value:
    // - If value is a float in [0,1] → show as a progress bar with %
    // - If value is an integer > 1 → show as a raw count
    // - Otherwise → show as string
    const renderMetricValue = (metric, value) => {
        if (typeof value === 'number') {
            if (value >= 0 && value <= 1) {
                const pct = Math.round(value * 100);
                return (
                    <div className="flex items-center gap-3">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                                className="bg-blue-600 h-2 rounded-full transition-all"
                                style={{ width: `${pct}%` }}
                            />
                        </div>
                        <span className="text-sm font-bold text-gray-900 w-12 text-right">{pct}%</span>
                    </div>
                );
            }
            // Raw integer count (e.g. performance_improvements: 12)
            return (
                <div className="text-2xl font-bold text-gray-800">
                    {value.toLocaleString()}
                    <span className="text-sm font-normal text-gray-500 ml-1">actions</span>
                </div>
            );
        }
        return <div className="text-sm text-gray-700">{String(value)}</div>;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-2xl mx-auto p-6">
                <div className="bg-red-50 border border-red-300 rounded-lg p-4 text-red-800">
                    <p className="font-semibold">Failed to load Archetype data</p>
                    <p className="text-sm mt-1">{error}</p>
                    <button
                        onClick={fetchArchetypeData}
                        className="mt-3 text-sm underline hover:no-underline"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    const currentArchetype = archetypeProgress?.archetypes?.find(
        (a) => a.archetype_type === selectedArchetype,
    );

    const selectedConfig = ARCHETYPE_CONFIG[selectedArchetype] || {};

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Identity Progression System</h1>
                <p className="text-gray-600 mt-1">
                    Develop your coding identity across 5 skill archetypes
                </p>
            </div>

            {/* Dominant Archetype Banner */}
            {archetypeProgress?.dominant_archetype && (
                <div
                    className={`bg-gradient-to-r ${ARCHETYPE_CONFIG[archetypeProgress.dominant_archetype.archetype_type]?.gradient || 'from-blue-600 to-purple-600'} rounded-xl shadow-lg p-6 text-white`}
                >
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="text-sm font-semibold uppercase tracking-wide opacity-90">
                                Your Dominant Identity
                            </div>
                            <div className="text-4xl font-bold mt-2 flex items-center gap-3">
                                <span className="text-5xl">
                                    {ARCHETYPE_CONFIG[archetypeProgress.dominant_archetype.archetype_type]?.icon}
                                </span>
                                {ARCHETYPE_CONFIG[archetypeProgress.dominant_archetype.archetype_type]?.name}
                            </div>
                            <div className="mt-2 text-lg">
                                Rank {archetypeProgress.dominant_archetype.rank_level}:{' '}
                                {getRankName(archetypeProgress.dominant_archetype.rank_level)}
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-5xl font-bold">
                                {archetypeProgress.dominant_archetype.experience_points} XP
                            </div>
                            <div className="text-sm opacity-90 mt-1">Total Experience</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Archetype Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                {Object.keys(ARCHETYPE_CONFIG).map((type) => {
                    const progress = archetypeProgress?.archetypes?.find(
                        (a) => a.archetype_type === type,
                    );
                    const config = ARCHETYPE_CONFIG[type];
                    const isSelected = selectedArchetype === type;
                    const isDominant =
                        archetypeProgress?.dominant_archetype?.archetype_type === type;

                    return (
                        <button
                            key={type}
                            onClick={() => setSelectedArchetype(type)}
                            className={`relative p-4 rounded-xl border-2 transition-all text-left ${isSelected
                                ? `${config.badge} border-current shadow-lg scale-105`
                                : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                                }`}
                        >
                            {isDominant && (
                                <div className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-0.5 rounded-full shadow">
                                    ⭐ TOP
                                </div>
                            )}
                            <div className="text-4xl mb-2">{config.icon}</div>
                            <div className="font-bold text-sm">{config.name}</div>
                            <div className="text-xs text-gray-500 mt-0.5">
                                {progress
                                    ? `Rank ${progress.rank_level} · ${getRankName(progress.rank_level)}`
                                    : 'Not Started'}
                            </div>
                            {progress && (
                                <div className="mt-2 text-xs font-semibold text-gray-600">
                                    {progress.experience_points} XP
                                </div>
                            )}
                        </button>
                    );
                })}
            </div>

            {/* Selected Archetype Detail */}
            {currentArchetype && (
                <div className="bg-white rounded-xl shadow-md overflow-hidden">
                    {/* Archetype Header */}
                    <div className={`p-6 bg-gradient-to-r ${selectedConfig.gradient} text-white`}>
                        <div className="flex items-center gap-4">
                            <div className="text-6xl">{selectedConfig.icon}</div>
                            <div className="flex-1">
                                <h2 className="text-2xl font-bold">{selectedConfig.name}</h2>
                                <p className="text-sm mt-1 opacity-90">{selectedConfig.description}</p>
                                <div className="mt-3 flex items-center gap-6 text-sm">
                                    <div>
                                        <span className="opacity-75">Rank: </span>
                                        <span className="font-semibold">
                                            {getRankName(currentArchetype.rank_level)} (Level{' '}
                                            {currentArchetype.rank_level})
                                        </span>
                                    </div>
                                    <div>
                                        <span className="opacity-75">XP: </span>
                                        <span className="font-semibold">
                                            {currentArchetype.experience_points}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* XP Progress bar toward next rank */}
                        {currentArchetype.rank_level < 10 && (
                            <div className="mt-4">
                                <div className="flex justify-between text-xs opacity-80 mb-1">
                                    <span>Progress to next rank</span>
                                    <span>{currentArchetype.progress_to_next_rank ?? 0}%</span>
                                </div>
                                <div className="bg-white/30 rounded-full h-2">
                                    <div
                                        className="bg-white h-2 rounded-full transition-all"
                                        style={{
                                            width: `${currentArchetype.progress_to_next_rank ?? 0}%`,
                                        }}
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Evolution Path */}
                    <div className="p-6 border-t">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">🎯 Evolution Path</h3>

                        {evolutionLoading ? (
                            <div className="flex items-center gap-2 text-gray-500 text-sm">
                                <div className="animate-spin h-4 w-4 border-2 border-gray-400 border-t-transparent rounded-full" />
                                Loading evolution path…
                            </div>
                        ) : evolutionPath ? (
                            <>
                                {/* Next-rank progress */}
                                {evolutionPath.next_rank && (
                                    <div className="mb-6 bg-gray-50 rounded-lg p-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-semibold text-gray-800">
                                                Next: {evolutionPath.next_rank.rank_name} (Rank{' '}
                                                {evolutionPath.next_rank.rank})
                                            </span>
                                            <span className="text-sm text-gray-500">
                                                {evolutionPath.next_rank.xp_needed - evolutionPath.current_xp} XP to go
                                            </span>
                                        </div>
                                        <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div
                                                className={`bg-gradient-to-r ${selectedConfig.gradient} h-3 rounded-full transition-all`}
                                                style={{ width: `${evolutionPath.progress_to_next ?? 0}%` }}
                                            />
                                        </div>
                                        <div className="text-xs text-gray-500 mt-1">
                                            {evolutionPath.current_xp} / {evolutionPath.next_rank.xp_needed} XP
                                        </div>
                                    </div>
                                )}

                                {/* Full rank ladder */}
                                <h4 className="font-semibold text-gray-700 text-sm mb-3">All Ranks</h4>
                                <div className="space-y-2">
                                    {(evolutionPath.all_ranks || []).map((rank) => (
                                        <div
                                            key={rank.rank}
                                            className={`flex items-center justify-between p-3 rounded-lg border ${rank.current
                                                ? 'bg-blue-50 border-blue-300'
                                                : rank.completed
                                                    ? 'bg-green-50 border-green-200'
                                                    : 'bg-white border-gray-200'
                                                }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div
                                                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${rank.completed
                                                        ? 'bg-green-500 text-white'
                                                        : rank.current
                                                            ? 'bg-blue-500 text-white'
                                                            : 'bg-gray-200 text-gray-500'
                                                        }`}
                                                >
                                                    {rank.completed ? '✓' : rank.rank}
                                                </div>
                                                <div>
                                                    <div className="font-semibold text-gray-900 text-sm">
                                                        {rank.rank_name}
                                                    </div>
                                                    <div className="text-xs text-gray-500">Rank {rank.rank}</div>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-sm font-semibold text-gray-700">
                                                    {rank.xp_needed.toLocaleString()} XP
                                                </div>
                                                {rank.current && (
                                                    <div className="text-xs text-blue-600 font-medium">Current</div>
                                                )}
                                                {evolutionPath.next_rank?.rank === rank.rank && (
                                                    <div className="text-xs text-yellow-600 font-medium">Next Goal</div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <p className="text-gray-500 text-sm">
                                Evolution path not available. Try selecting a different archetype.
                            </p>
                        )}
                    </div>

                    {/* Behavior Metrics */}
                    <div className="p-6 border-t bg-gray-50">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">📊 Behavior Metrics</h3>
                        {currentArchetype.behavior_metrics &&
                            Object.keys(currentArchetype.behavior_metrics).length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {Object.entries(currentArchetype.behavior_metrics).map(([metric, value]) => (
                                    <div key={metric} className="bg-white rounded-lg p-4 border border-gray-100">
                                        <div className="text-sm text-gray-600 mb-2 font-medium">
                                            {metric.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                                        </div>
                                        {renderMetricValue(metric, value)}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <div className="text-4xl mb-3">📈</div>
                                <p className="text-sm">No behavior metrics yet.</p>
                                <p className="text-xs mt-1">
                                    Complete practice sessions, debug challenges, and arena matches to build your
                                    profile.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* No archetypes at all */}
            {!archetypeProgress?.archetypes?.length && (
                <div className="text-center py-12 text-gray-500">
                    <div className="text-5xl mb-4">🧬</div>
                    <p className="text-lg font-medium">No archetype data found.</p>
                    <p className="text-sm mt-1">
                        Complete your onboarding and start practicing to unlock your archetypes.
                    </p>
                </div>
            )}
        </div>
    );
}
