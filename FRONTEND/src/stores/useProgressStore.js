import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useProgressStore = create(
    persist(
        (set) => ({
            // Start empty — populated from API after login
            xp: 0,
            level: 1,
            nodes: {},

            setProgress: (data) =>
                set({
                    xp: data.xp || 0,
                    level: data.level || 1,
                    nodes: data.nodes || {},
                }),

            unlockNode: (id) =>
                set((state) => ({
                    nodes: {
                        ...state.nodes,
                        [id]: { ...state.nodes[id], status: 'unlocked' },
                    },
                })),

            completeNode: (id, stars, mastery) =>
                set((state) => ({
                    xp: state.xp + 50,
                    nodes: {
                        ...state.nodes,
                        [id]: { status: 'completed', stars, mastery },
                    },
                })),

            updateMastery: (id, mastery) =>
                set((state) => ({
                    nodes: {
                        ...state.nodes,
                        [id]: { ...state.nodes[id], mastery },
                    },
                })),

            resetProgress: () =>
                set({ xp: 0, level: 1, nodes: {} }),
        }),
        {
            name: 'codenest-progress',
        }
    )
);

export default useProgressStore;
