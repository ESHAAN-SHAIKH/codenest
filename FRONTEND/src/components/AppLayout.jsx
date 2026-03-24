import { Outlet, Link, useLocation } from 'react-router-dom';
import { Gamepad2, Map, LayoutDashboard, User } from 'lucide-react';
import { motion } from 'framer-motion';
import AiFloatingButton from './AiFloatingButton';

export default function AppLayout() {
    const location = useLocation();

    const navItems = [
        { path: '/', icon: Map, label: 'Map' },
        { path: '/arena', icon: Gamepad2, label: 'Arena' },
        { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    ];

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Top Navigation */}
            <header className="bg-white shadow-sm border-b border-gray-100 py-4 px-6 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-md">
                            CN
                        </div>
                        <span className="font-bold text-2xl text-gray-800 tracking-tight">CodeNest</span>
                    </Link>

                    <nav className="hidden md:flex items-center gap-1 bg-gray-100 p-1 rounded-2xl">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`relative px-6 py-2 rounded-xl flex items-center gap-2 transition-all duration-200 ${isActive ? 'text-primary-dark font-bold' : 'text-gray-500 hover:text-gray-700'
                                        }`}
                                >
                                    {isActive && (
                                        <motion.div
                                            layoutId="nav-bg"
                                            className="absolute inset-0 bg-white shadow-sm rounded-xl"
                                            transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                                        />
                                    )}
                                    <span className="relative z-10 flex items-center gap-2">
                                        <item.icon size={20} />
                                        {item.label}
                                    </span>
                                </Link>
                            );
                        })}
                    </nav>

                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex items-center gap-2 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-bold border border-yellow-200">
                            <span>⭐ 1,250 XP</span>
                        </div>
                        <button className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300 transition-colors">
                            <User size={20} className="text-gray-600" />
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 max-w-6xl mx-auto w-full p-6">
                <Outlet />
            </main>

            {/* Global AI Helper */}
            <AiFloatingButton />
        </div>
    );
}
