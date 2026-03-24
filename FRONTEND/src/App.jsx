import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useEffect } from 'react';
import CognitiveNavigation from './components/CognitiveNavigation';
import useAuthStore from './stores/useAuthStore';

// Auth pages
import Login from './features/Auth/Login';
import Register from './features/Auth/Register';
import Onboarding from './features/Auth/Onboarding';

// Feature components
import CognitiveDashboard from './features/Cognitive/CognitiveDashboard';
import DebuggingLab from './features/Debugging/DebuggingLab';
import ArchetypeDashboard from './features/Archetypes/ArchetypeDashboard';
import ConceptMap from './features/ConceptMap/ConceptMap';
import IterationChamber from './features/Iteration/IterationChamber';
import ArenaMatchmaking from './features/Arena/ArenaMatchmaking';
import AnalyticsDashboard from './features/Analytics/AnalyticsDashboard';
import SkillMap from './features/SkillTree/SkillMap';
import BeginnerDashboard from './features/BeginnerLearning/BeginnerDashboard';
import ScaffoldedChallenge from './features/BeginnerLearning/ScaffoldedChallenge';
import useBeginnerLearningStore from './stores/useBeginnerLearningStore';

function ProtectedRoute() {
    const { isAuthenticated, user } = useAuthStore();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    // If onboarding not completed, redirect to onboarding
    if (user && !user.onboarding_completed) {
        return <Navigate to="/onboarding" replace />;
    }

    return <Outlet />;
}

function AppLayout() {
    return (
        <div className="min-h-screen bg-gray-50">
            <CognitiveNavigation />
            <main className="pt-4">
                <Outlet />
            </main>
        </div>
    );
}

export default function App() {
    const { isAuthenticated, user, fetchUser } = useAuthStore();

    // Re-validate token on app load
    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    // Sync beginner mode from user object whenever user changes
    const { syncFromUser } = useBeginnerLearningStore();
    useEffect(() => {
        if (user) syncFromUser(user);
    }, [user]);

    return (
        <Routes>
            {/* Public routes */}
            <Route
                path="/login"
                element={isAuthenticated && user?.onboarding_completed ? <Navigate to="/dashboard" replace /> : <Login />}
            />
            <Route
                path="/register"
                element={isAuthenticated ? <Navigate to="/onboarding" replace /> : <Register />}
            />
            <Route
                path="/onboarding"
                element={
                    !isAuthenticated
                        ? <Navigate to="/login" replace />
                        : user?.onboarding_completed
                            ? <Navigate to="/dashboard" replace />
                            : <Onboarding />
                }
            />

            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                    {/* Main dashboard */}
                    <Route path="/dashboard" element={<CognitiveDashboard userId={user?.id} />} />

                    {/* Cognitive Training */}
                    <Route path="/cognitive" element={<CognitiveDashboard userId={user?.id} />} />
                    <Route path="/debugging" element={<DebuggingLab userId={user?.id} />} />
                    <Route path="/archetypes" element={<ArchetypeDashboard />} />
                    <Route path="/concept-map" element={<ConceptMap />} />
                    <Route path="/iteration/:challengeId" element={<IterationChamber userId={user?.id} />} />
                    <Route path="/arena" element={<ArenaMatchmaking />} />
                    <Route path="/analytics" element={<AnalyticsDashboard userId={user?.id} />} />
                    <Route path="/skill-tree" element={<SkillMap userId={user?.id} />} />

                    {/* Beginner Learning */}
                    <Route path="/beginner" element={<BeginnerDashboard />} />
                    <Route path="/beginner/challenge/:id" element={<ScaffoldedChallenge />} />

                    {/* Default redirect */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Route>
            </Route>
        </Routes>
    );
}
