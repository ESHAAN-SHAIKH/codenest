import { useState, useEffect } from 'react';
import SkillNode from './SkillNode';
import apiService from '../../services/api';

export default function SkillMap({ userId }) {
    const [skillData, setSkillData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (userId) {
            loadSkillMap();
        } else {
            setLoading(false);
        }
    }, [userId]);

    const loadSkillMap = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiService.getSkillMap(userId);
            setSkillData(data);
        } catch (err) {
            console.error('Failed to load skill map:', err);
            setError('Failed to load skill map. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleNodeClick = async (lessonId) => {
        console.log('Node clicked:', lessonId);
        // Navigate to lesson player or open details
    };

    if (loading) {
        return (
            <div className="relative w-full h-[80vh] bg-white rounded-3xl shadow-xl flex items-center justify-center border-4 border-gray-100">
                <div className="text-center">
                    <div className="inline-block w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                    <p className="mt-4 text-gray-600 font-semibold">Loading Skill Tree...</p>
                </div>
            </div>
        );
    }

    if (error || !skillData) {
        return (
            <div className="relative w-full h-[80vh] bg-white rounded-3xl shadow-xl flex items-center justify-center border-4 border-red-200">
                <div className="text-center p-8">
                    <div className="text-6xl mb-4">😿</div>
                    <p className="text-red-600 font-semibold text-lg">{error || 'No data available'}</p>
                    <button
                        onClick={loadSkillMap}
                        className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const nodes = skillData?.nodes || [];

    return (
        <div className="relative w-full h-[80vh] bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-gray-100">
            {/* Background patterned grid */}
            <div className="absolute inset-0 opacity-5"
                style={{ backgroundImage: 'radial-gradient(#4DABF7 2px, transparent 2px)', backgroundSize: '30px 30px' }}>
            </div>

            {/* User Stats Header */}
            {skillData?.user && (
                <div className="absolute top-4 left-4 right-4 bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg p-4 z-10">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                                {skillData.user.username?.[0]?.toUpperCase() || '?'}
                            </div>
                            <div>
                                <h3 className="font-bold text-xl text-gray-800">{skillData.user.username}</h3>
                                <p className="text-sm text-gray-600">Level {skillData.user.level} · {skillData.user.xp} XP</p>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <div className="text-center">
                                <div className="text-2xl">⭐</div>
                                <p className="text-sm font-semibold text-gray-700">{skillData.user.total_stars}</p>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl">🏆</div>
                                <p className="text-sm font-semibold text-gray-700">{skillData.user.badges?.length || 0}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Connection Paths (SVG) - Simplified for dynamic data */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ marginTop: '100px' }}>
                {nodes.map((node, idx) => {
                    if (idx === 0) return null; // No line for first node
                    const prev = nodes[idx - 1];
                    const prevPos = prev.position || { x: idx * 50, y: (idx - 1) * 100 };
                    const currPos = node.position || { x: idx * 50, y: idx * 100 };
                    const color = prev.completed ? '#69DB7C' : '#E9ECEF';

                    return (
                        <line
                            key={`line-${idx}`}
                            x1={`${prevPos.x}%`}
                            y1={`${prevPos.y + 10}%`}
                            x2={`${currPos.x}%`}
                            y2={`${currPos.y}%`}
                            stroke={color}
                            strokeWidth="8"
                            opacity="0.6"
                        />
                    );
                })}
            </svg>

            {/* Nodes */}
            <div className="relative w-full h-full" style={{ paddingTop: '100px' }}>
                {nodes.map((node) => (
                    <SkillNode
                        key={node.id}
                        id={node.id}
                        title={node.title}
                        type={node.type || 'normal'}
                        position={node.position || { x: 50, y: 50 }}
                        status={node.completed ? 'completed' : (node.is_unlocked ? 'unlocked' : 'locked')}
                        stars={node.stars || 0}
                        mastery={node.mastery || 0}
                        onClick={() => handleNodeClick(node.id)}
                    />
                ))}
            </div>
        </div>
    );
}
