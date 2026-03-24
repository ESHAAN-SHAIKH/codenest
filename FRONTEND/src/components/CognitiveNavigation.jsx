import { NavLink, useNavigate } from 'react-router-dom';
import useAuthStore from '../stores/useAuthStore';
import useBeginnerLearningStore from '../stores/useBeginnerLearningStore';




export default function CognitiveNavigation() {
    const { user, logout } = useAuthStore();
    const { is_beginner_mode, beginner_phase } = useBeginnerLearningStore();
    const navigate = useNavigate();
    const isEarlyBeginner = is_beginner_mode && ['scaffolded', 'guided'].includes(beginner_phase);

    // Build nav items dynamically so Arena gets labelled in early beginner phase
    const navItems = [
        ...(is_beginner_mode ? [{ path: '/beginner', label: 'Learn', icon: '🐣' }] : []),
        { path: '/dashboard', label: 'Dashboard', icon: '🧠' },
        { path: '/debugging', label: 'Debug Lab', icon: '🐛' },
        { path: '/archetypes', label: 'Archetypes', icon: '🎭' },
        { path: '/concept-map', label: 'Concept Map', icon: '🗺️' },
        { path: '/iteration/1', label: 'Iteration', icon: '🔄' },
        { path: '/skill-tree', label: 'Skill Tree', icon: '🌳' },
        {
            path: '/arena',
            label: isEarlyBeginner ? 'Arena' : 'Arena',
            icon: '⚔️',
            badge: isEarlyBeginner ? 'Advanced Challenge' : null,
        },
        { path: '/analytics', label: 'Analytics', icon: '📊' },
    ];

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-white/90 backdrop-blur-lg shadow-sm border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <NavLink to="/dashboard" className="flex items-center gap-2 group">
                        <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-md group-hover:shadow-lg transition">
                            CN
                        </div>
                        <span className="font-bold text-lg text-gray-800 hidden sm:block">CodeNest</span>
                    </NavLink>

                    {/* Navigation */}
                    <div className="flex items-center gap-1 overflow-x-auto scrollbar-hide">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) =>
                                    `flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${isActive
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                                    }`
                                }
                            >
                                <span className="text-base">{item.icon}</span>
                                <span className="hidden md:inline">{item.label}</span>
                                {item.badge && (
                                    <span className="hidden md:inline text-xs bg-gray-100 text-gray-400 rounded px-1 ml-0.5">
                                        {item.badge}
                                    </span>
                                )}
                            </NavLink>
                        ))}
                    </div>

                    {/* User section */}
                    <div className="flex items-center gap-3">
                        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
                            <span className="text-yellow-500 text-sm">⭐</span>
                            <span className="text-sm font-semibold text-gray-700">{user?.total_stars || 0}</span>
                            <span className="text-gray-400 text-xs">|</span>
                            <span className="text-sm font-medium text-purple-600">Lv.{user?.level || 1}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                                {user?.username?.[0]?.toUpperCase() || '?'}
                            </div>
                            <button
                                onClick={handleLogout}
                                className="text-gray-400 hover:text-red-500 transition text-lg"
                                title="Logout"
                            >
                                🚪
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
