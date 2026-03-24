import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/api$/, '') : 'http://localhost:5000';

const useAuthStore = create(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
            error: null,

            register: async (username, email, password) => {
                set({ loading: true, error: null });
                try {
                    const res = await fetch(`${API_BASE}/api/auth/register`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, email, password }),
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Registration failed');
                    set({ user: data.user, token: data.token, isAuthenticated: true, loading: false });
                    return data;
                } catch (err) {
                    set({ loading: false, error: err.message });
                    throw err;
                }
            },

            login: async (email, password) => {
                set({ loading: true, error: null });
                try {
                    const res = await fetch(`${API_BASE}/api/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password }),
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Login failed');
                    set({ user: data.user, token: data.token, isAuthenticated: true, loading: false });
                    return data;
                } catch (err) {
                    set({ loading: false, error: err.message });
                    throw err;
                }
            },

            fetchUser: async () => {
                const { token } = get();
                if (!token) return;
                try {
                    const res = await fetch(`${API_BASE}/api/auth/me`, {
                        headers: { 'Authorization': `Bearer ${token}` },
                    });
                    if (!res.ok) {
                        set({ user: null, token: null, isAuthenticated: false });
                        return;
                    }
                    const data = await res.json();
                    set({ user: data.user, isAuthenticated: true });
                } catch {
                    set({ user: null, token: null, isAuthenticated: false });
                }
            },

            completeOnboarding: async (skillLevel, preferredLanguage, interests) => {
                const { token } = get();
                set({ loading: true, error: null });
                try {
                    const res = await fetch(`${API_BASE}/api/auth/onboarding`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`,
                        },
                        body: JSON.stringify({
                            skill_level: skillLevel,
                            preferred_language: preferredLanguage,
                            interests,
                        }),
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Onboarding failed');
                    set({ user: data.user, loading: false });
                    return data;
                } catch (err) {
                    set({ loading: false, error: err.message });
                    throw err;
                }
            },

            logout: () => {
                set({ user: null, token: null, isAuthenticated: false, error: null });
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: 'codenest-auth',
            partialize: (state) => ({
                token: state.token,
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);

export default useAuthStore;
