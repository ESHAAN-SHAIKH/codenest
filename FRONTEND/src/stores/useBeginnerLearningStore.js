import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const API_BASE = import.meta.env.VITE_API_URL
    ? import.meta.env.VITE_API_URL.replace(/\/api$/, '')
    : 'http://localhost:5000';

/**
 * useBeginnerLearningStore
 *
 * Mirrors server-side beginner state locally (persisted).
 * Does NOT replicate evaluation logic — all evaluation lives in the backend.
 * Acts as read/write cache of user.is_beginner_mode and user.beginner_phase.
 */
const useBeginnerLearningStore = create(
    persist(
        (set, get) => ({
            // Mirrored from user object
            is_beginner_mode: true,
            beginner_phase: 'scaffolded', // 'scaffolded' | 'guided' | 'freeform' | 'complete'

            // Progression signals (updated from server responses)
            scaffolded_completed: 0,
            predict_output_passed: false,
            error_spotting_passed: false,
            first_syntax_free_freeform: false,

            // Session tracking
            misconception_events_seen: [], // array of misconception type strings

            // ── Sync from user object (call after login/fetchUser) ──────────────
            syncFromUser: (user) => {
                if (!user) return;
                set({
                    is_beginner_mode: user.is_beginner_mode ?? true,
                    beginner_phase: user.beginner_phase ?? 'scaffolded',
                });
            },

            // ── Toggle beginner mode (calls API, then updates local state) ───────
            toggleBeginnerMode: async (token) => {
                try {
                    const res = await fetch(`${API_BASE}/api/beginner/settings`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            Authorization: `Bearer ${token}`,
                        },
                        body: JSON.stringify({}), // toggle — no explicit value
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Toggle failed');
                    set({
                        is_beginner_mode: data.is_beginner_mode,
                        beginner_phase: data.beginner_phase,
                    });
                    return data;
                } catch (err) {
                    console.error('toggleBeginnerMode error:', err);
                    throw err;
                }
            },

            // ── Record a scaffolded challenge completion ─────────────────────────
            markScaffoldedComplete: (scaffoldType) => {
                set((state) => {
                    const updates = {
                        scaffolded_completed: state.scaffolded_completed + 1,
                    };
                    if (scaffoldType === 'predict_output') updates.predict_output_passed = true;
                    if (scaffoldType === 'error_spotting') updates.error_spotting_passed = true;
                    if (scaffoldType === 'freeform') updates.first_syntax_free_freeform = true;
                    return updates;
                });
            },

            // ── Record a misconception event seen in UI ──────────────────────────
            recordMisconceptionSeen: (misconceptionType) => {
                set((state) => {
                    if (state.misconception_events_seen.includes(misconceptionType)) return {};
                    return {
                        misconception_events_seen: [
                            ...state.misconception_events_seen,
                            misconceptionType,
                        ],
                    };
                });
            },

            // ── Check transition eligibility (queries server) ────────────────────
            checkTransition: async (token) => {
                try {
                    const res = await fetch(`${API_BASE}/api/beginner/transition-check`, {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    const data = await res.json();
                    // API returns: { current_phase, eligible, criteria, mascot }
                    // Keep local phase in sync with server (phase may have advanced after last submit)
                    if (data.success && data.current_phase) {
                        set({ beginner_phase: data.current_phase });
                    }
                    return data;
                } catch (err) {
                    console.error('checkTransition error:', err);
                    return null;
                }
            },

            // ── Update phase from server response ────────────────────────────────
            updatePhase: (newPhase) => set({ beginner_phase: newPhase }),

            reset: () =>
                set({
                    is_beginner_mode: true,
                    beginner_phase: 'scaffolded',
                    scaffolded_completed: 0,
                    predict_output_passed: false,
                    error_spotting_passed: false,
                    first_syntax_free_freeform: false,
                    misconception_events_seen: [],
                }),
        }),
        {
            name: 'codenest-beginner',
            partialize: (state) => ({
                is_beginner_mode: state.is_beginner_mode,
                beginner_phase: state.beginner_phase,
                scaffolded_completed: state.scaffolded_completed,
                predict_output_passed: state.predict_output_passed,
                error_spotting_passed: state.error_spotting_passed,
                first_syntax_free_freeform: state.first_syntax_free_freeform,
                misconception_events_seen: state.misconception_events_seen,
            }),
        }
    )
);

export default useBeginnerLearningStore;
