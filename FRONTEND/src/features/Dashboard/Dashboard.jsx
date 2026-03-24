import { useState, useEffect } from 'react';
import { Users, TrendingUp, Trophy, Star } from 'lucide-react';
import apiService from '../../services/api';

export default function Dashboard() {
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const USER_ID = 'demo_user'; // In production, get from auth context

    useEffect(() => {
        loadUserData();
    }, []);

    const loadUserData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiService.getSkillMap(USER_ID);
            setUserData(data);
        } catch (err) {
            console.error('Failed to load user data:', err);
            setError('Failed to load dashboard data.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                    <div className="inline-block w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                    <p className="mt-4 text-gray-600 font-semibold">Loading Dashboard...</p>
                </div>
            </div>
        );
    }

    if (error || !userData) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center p-8">
                    <div className="text-6xl mb-4">😿</div>
                    <p className="text-red-600 font-semibold text-lg">{error || 'No data available'}</p>
                    <button
                        onClick={loadUserData}
                        className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const user = userData.user;
    const nodes = userData.nodes || [];
    const completedLessons = nodes.filter(n => n.completed).length;
    const totalLessons = nodes.length;
    const progress = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-800">Student Dashboard</h1>
                <p className="text-gray-500">Welcome back, {user.username}! Keep learning! 🚀</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {/* Level Card */}
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-3xl shadow-lg">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <Trophy size={24} />
                        </div>
                        <span className="font-bold opacity-90">Level</span>
                    </div>
                    <div className="text-5xl font-bold">{user.level}</div>
                    <div className="text-sm opacity-80 mt-1">{user.xp} XP</div>
                </div>

                {/* Total Stars */}
                <div className="bg-gradient-to-br from-yellow-400 to-yellow-500 text-white p-6 rounded-3xl shadow-lg">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <Star size={24} />
                        </div>
                        <span className="font-bold opacity-90">Total Stars</span>
                    </div>
                    <div className="text-5xl font-bold">{user.total_stars}</div>
                    <div className="text-sm opacity-80 mt-1">⭐ Earned</div>
                </div>

                {/* Progress */}
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-3xl shadow-lg">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <TrendingUp size={24} />
                        </div>
                        <span className="font-bold opacity-90">Progress</span>
                    </div>
                    <div className="text-5xl font-bold">{progress}%</div>
                    <div className="text-sm opacity-80 mt-1">{completedLessons}/{totalLessons} Lessons</div>
                </div>

                {/* Badges */}
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-3xl shadow-lg">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 bg-white/20 rounded-xl">
                            <Users size={24} />
                        </div>
                        <span className="font-bold opacity-90">Badges</span>
                    </div>
                    <div className="text-5xl font-bold">{user.badges?.length || 0}</div>
                    <div className="text-sm opacity-80 mt-1">🏆 Collected</div>
                </div>
            </div>

            {/* Recent Lessons */}
            <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Lessons</h2>
                <div className="space-y-3">
                    {nodes.slice(0, 5).map((lesson) => (
                        <div key={lesson.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${lesson.completed ? 'bg-green-100' : 'bg-gray-200'
                                }`}>
                                {lesson.completed ? '✅' : '📚'}
                            </div>
                            <div className="flex-1">
                                <div className="font-bold text-gray-800">{lesson.title}</div>
                                <div className="text-sm text-gray-500">
                                    {lesson.completed ? `Completed with ${lesson.stars} ⭐` : 'Not started yet'}
                                </div>
                            </div>
                            {lesson.stars > 0 && (
                                <div className="flex gap-1">
                                    {[...Array(3)].map((_, i) => (
                                        <Star
                                            key={i}
                                            size={16}
                                            className={i < lesson.stars ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Badges Section */}
            {user.badges && user.badges.length > 0 && (
                <div className="bg-white rounded-3xl shadow-sm border border-gray-100 p-6">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Earned Badges</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {user.badges.map((badge, idx) => (
                            <div key={idx} className="text-center p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl border-2 border-yellow-200">
                                <div className="text-4xl mb-2">🏆</div>
                                <div className="font-bold text-gray-800 text-sm">{badge.name || 'Achievement'}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
