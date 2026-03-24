import { useState, useEffect, useRef, useCallback } from 'react';
import useAuthStore from '../../stores/useAuthStore';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL + '/api' : 'http://localhost:5000/api';

const MATCH_TYPES = {
    debug_duel: {
        name: 'Debug Duel',
        icon: '🔍',
        description: 'Race to find and fix bugs',
        color: '#ef4444',
        gradient: 'linear-gradient(135deg, #fef2f2, #fecaca)',
    },
    refactor_race: {
        name: 'Refactor Race',
        icon: '✨',
        description: 'Improve code quality fastest',
        color: '#8b5cf6',
        gradient: 'linear-gradient(135deg, #f5f3ff, #ede9fe)',
    },
    optimization_battle: {
        name: 'Optimization Battle',
        icon: '⚡',
        description: 'Create the most efficient solution',
        color: '#f59e0b',
        gradient: 'linear-gradient(135deg, #fffbeb, #fef3c7)',
    },
};

// ─── inline styles ──────────────────────────────────────────────────────
const s = {
    page: { maxWidth: 1100, margin: '0 auto', padding: 24, fontFamily: "'Inter','Segoe UI',sans-serif" },
    header: { marginBottom: 24 },
    h1: { fontSize: 28, fontWeight: 800, color: '#111827', margin: 0 },
    subtitle: { color: '#6b7280', marginTop: 4, fontSize: 15 },

    // cards grid
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 },

    card: (sel, color, gradient) => ({
        background: sel ? gradient : '#fff',
        border: `2px solid ${sel ? color : '#e5e7eb'}`,
        borderRadius: 16, padding: 24, cursor: 'pointer',
        transform: sel ? 'scale(1.03)' : 'scale(1)',
        boxShadow: sel ? `0 8px 25px ${color}30` : '0 1px 3px rgba(0,0,0,.08)',
        transition: 'all .2s ease', position: 'relative', textAlign: 'center',
    }),
    checkBadge: (color) => ({
        position: 'absolute', top: -10, right: -10, width: 28, height: 28,
        borderRadius: '50%', background: color, color: '#fff', display: 'flex',
        alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 14,
    }),
    cardIcon: { fontSize: 48, marginBottom: 8 },
    cardTitle: { fontSize: 18, fontWeight: 700, color: '#111827', margin: '4px 0' },
    cardDesc: { fontSize: 13, color: '#6b7280' },
    ratingRow: { display: 'flex', justifyContent: 'space-between', fontSize: 13, marginTop: 6 },
    ratingLabel: { color: '#6b7280' },

    // big button
    bigBtn: (color) => ({
        display: 'block', margin: '28px auto 0', padding: '16px 48px', fontSize: 17,
        fontWeight: 700, color: '#fff', background: color || '#3b82f6', border: 'none',
        borderRadius: 14, cursor: 'pointer', boxShadow: `0 4px 14px ${color || '#3b82f6'}50`,
        transition: 'transform .15s', textAlign: 'center',
    }),

    // stats
    statsBox: { background: '#fff', borderRadius: 16, padding: 24, marginTop: 24, boxShadow: '0 1px 3px rgba(0,0,0,.08)' },
    statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 12, marginTop: 12 },
    statCard: (bg) => ({ textAlign: 'center', padding: 16, borderRadius: 12, background: bg }),
    statVal: (color) => ({ fontSize: 26, fontWeight: 800, color }),
    statLabel: { fontSize: 12, color: '#6b7280', marginTop: 2 },

    // history
    historyBox: { background: '#fff', borderRadius: 16, padding: 24, marginTop: 16, boxShadow: '0 1px 3px rgba(0,0,0,.08)' },
    histItem: (won) => ({
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 16px', borderRadius: 12, marginTop: 8,
        border: `2px solid ${won ? '#bbf7d0' : '#fecaca'}`,
        background: won ? '#f0fdf4' : '#fef2f2',
    }),
    badge: (bg, fg) => ({
        display: 'inline-block', padding: '3px 10px', borderRadius: 8,
        fontWeight: 700, fontSize: 13, background: bg, color: fg,
    }),

    /* ── LiveMatch styles ── */
    matchOverlay: {
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'linear-gradient(135deg,#0f172a,#1e293b)',
        display: 'flex', flexDirection: 'column', overflow: 'auto',
    },
    matchHeader: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '16px 24px', borderBottom: '1px solid #334155',
    },
    matchTitle: { color: '#f1f5f9', fontWeight: 700, fontSize: 18 },
    timer: (urgent) => ({
        fontFamily: 'monospace', fontSize: 22, fontWeight: 800,
        color: urgent ? '#ef4444' : '#34d399',
        animation: urgent ? 'pulse 1s infinite' : 'none',
    }),
    matchBody: { display: 'flex', flex: 1, gap: 0, minHeight: 0 },
    challengePane: {
        width: '40%', padding: 24, overflowY: 'auto',
        borderRight: '1px solid #334155', color: '#e2e8f0',
    },
    editorPane: { flex: 1, display: 'flex', flexDirection: 'column', padding: 0 },
    codeArea: {
        flex: 1, width: '100%', padding: 20, border: 'none', outline: 'none', resize: 'none',
        fontFamily: "'Fira Code','Consolas',monospace", fontSize: 14, lineHeight: 1.6,
        background: '#0f172a', color: '#e2e8f0', tabSize: 4,
    },
    submitBar: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '12px 24px', background: '#1e293b', borderTop: '1px solid #334155',
    },
    hintBtn: {
        padding: '10px 20px', borderRadius: 10, border: '2px solid #fbbf24',
        background: 'transparent', color: '#fbbf24', fontWeight: 700, cursor: 'pointer',
    },
    submitBtn: {
        padding: '12px 32px', borderRadius: 12, border: 'none', fontWeight: 800, fontSize: 16,
        color: '#fff', cursor: 'pointer',
        background: 'linear-gradient(135deg,#22c55e,#16a34a)',
        boxShadow: '0 4px 14px rgba(34,197,94,.4)',
    },

    /* ── Result overlay ── */
    resultOverlay: {
        position: 'fixed', inset: 0, zIndex: 10000, display: 'flex',
        alignItems: 'center', justifyContent: 'center',
        background: 'rgba(0,0,0,.85)', backdropFilter: 'blur(8px)',
    },
    resultCard: {
        background: '#fff', borderRadius: 24, padding: 40, maxWidth: 480,
        width: '90%', textAlign: 'center', animation: 'slideUp .4s ease-out',
    },
    resultEmoji: { fontSize: 64, marginBottom: 8 },
    resultTitle: (won) => ({ fontSize: 32, fontWeight: 900, color: won ? '#16a34a' : '#dc2626' }),
    ratingBadge: (positive) => ({
        display: 'inline-block', padding: '6px 20px', borderRadius: 12, marginTop: 12,
        fontWeight: 800, fontSize: 20,
        background: positive ? '#dcfce7' : '#fef2f2',
        color: positive ? '#16a34a' : '#dc2626',
    }),
    feedbackBox: {
        marginTop: 16, padding: 16, borderRadius: 12, background: '#f8fafc',
        textAlign: 'left', fontSize: 14, color: '#374151', lineHeight: 1.6,
    },
    continueBtn: {
        marginTop: 20, padding: '14px 40px', borderRadius: 14, border: 'none',
        fontWeight: 700, fontSize: 16, color: '#fff', cursor: 'pointer',
        background: 'linear-gradient(135deg,#3b82f6,#2563eb)',
        boxShadow: '0 4px 14px rgba(59,130,246,.4)',
    },

    aiBar: {
        display: 'flex', alignItems: 'center', gap: 12, padding: '10px 24px',
        background: '#1e293b', borderBottom: '1px solid #334155', color: '#94a3b8',
        fontSize: 13,
    },
    aiAvatar: {
        width: 32, height: 32, borderRadius: '50%', background: '#3b82f6',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16,
    },
    codeBlock: {
        background: '#0f172a', borderRadius: 10, padding: 16, margin: '12px 0',
        fontFamily: "'Fira Code','Consolas',monospace", fontSize: 13,
        overflowX: 'auto', lineHeight: 1.5, whiteSpace: 'pre-wrap',
        color: '#a5f3fc', border: '1px solid #334155',
    },

    spinner: {
        width: 40, height: 40, borderRadius: '50%',
        border: '4px solid #334155', borderTopColor: '#3b82f6',
        animation: 'spin 1s linear infinite', margin: '40px auto',
    },
    loadingText: { color: '#94a3b8', textAlign: 'center', marginTop: 8 },

    noHistory: { textAlign: 'center', color: '#9ca3af', padding: 32, fontSize: 14 },
};

// ═══════════════════════════════════════════════════════════════════════════════
//  LIVE MATCH INTERFACE
// ═══════════════════════════════════════════════════════════════════════════════
function LiveMatchInterface({ matchId, matchType, challenge, aiName, timeLimit, token, onMatchEnd }) {
    const [code, setCode] = useState(challenge?.buggy_code || '');
    const [timeLeft, setTimeLeft] = useState(timeLimit || 180);
    const [showHint, setShowHint] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const timerRef = useRef(null);
    const startTime = useRef(Date.now());

    // countdown timer
    useEffect(() => {
        timerRef.current = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(timerRef.current);
                    handleSubmit(true); // auto-submit on timeout
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timerRef.current);
    }, []);

    const formatTime = (sec) => {
        const m = Math.floor(sec / 60);
        const ss = sec % 60;
        return `${m}:${ss.toString().padStart(2, '0')}`;
    };

    const handleSubmit = useCallback(async (timedOut = false) => {
        if (submitting || result) return;
        clearInterval(timerRef.current);
        setSubmitting(true);
        const timeTaken = Math.round((Date.now() - startTime.current) / 1000);

        try {
            if (!token) throw new Error('Not logged in');
            const res = await fetch(`${API_BASE}/arena/match/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    match_id: matchId,
                    code,
                    time_taken: timeTaken,
                }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Submission failed');
            setResult({ ...data.data, timed_out: timedOut });
        } catch (err) {
            console.error('Submit error:', err);
            setResult({
                user_won: false, user_score: 0, ai_score: 50,
                rating_change: 0, new_rating: 1500,
                feedback: 'Submission failed. Please try again.',
                improvements: [], timed_out: timedOut,
            });
        } finally {
            setSubmitting(false);
        }
    }, [code, matchId, token, submitting, result]);

    const handleKeyDown = (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const val = e.target.value;
            setCode(val.substring(0, start) + '    ' + val.substring(end));
            setTimeout(() => { e.target.selectionStart = e.target.selectionEnd = start + 4; }, 0);
        }
    };

    const mtInfo = MATCH_TYPES[matchType] || MATCH_TYPES.debug_duel;

    return (
        <>
            {/* Inject animation keyframes */}
            <style>{`
                @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
                @keyframes spin { to{transform:rotate(360deg)} }
                @keyframes slideUp { from{opacity:0;transform:translateY(40px)} to{opacity:1;transform:translateY(0)} }
                @keyframes confettiFall { 0%{transform:translateY(-10px) rotate(0deg);opacity:1} 100%{transform:translateY(100vh) rotate(720deg);opacity:0} }
            `}</style>

            <div style={s.matchOverlay}>
                {/* Header */}
                <div style={s.matchHeader}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <span style={{ fontSize: 28 }}>{mtInfo.icon}</span>
                        <span style={s.matchTitle}>{mtInfo.name}</span>
                        <span style={{ color: '#64748b', fontSize: 13 }}>vs {aiName || 'AI'}</span>
                    </div>
                    <div style={s.timer(timeLeft < 30)}>⏱ {formatTime(timeLeft)}</div>
                </div>

                {/* AI Opponent bar */}
                <div style={s.aiBar}>
                    <div style={s.aiAvatar}>🤖</div>
                    <span><b>{aiName}</b> is working on their solution...</span>
                    <div style={{ marginLeft: 'auto', display: 'flex', gap: 4 }}>
                        {[0, 1, 2].map(i => (
                            <div key={i} style={{
                                width: 6, height: 6, borderRadius: '50%', background: '#3b82f6',
                                animation: `pulse 1.5s ease-in-out ${i * 0.3}s infinite`,
                            }} />
                        ))}
                    </div>
                </div>

                {/* Main body */}
                <div style={s.matchBody}>
                    {/* Left: Challenge description */}
                    <div style={s.challengePane}>
                        <h2 style={{ margin: '0 0 8px', fontSize: 22, color: '#f1f5f9' }}>
                            {challenge?.title || 'Coding Challenge'}
                        </h2>
                        <p style={{ color: '#94a3b8', fontSize: 14, lineHeight: 1.6 }}>
                            {challenge?.description}
                        </p>

                        <div style={{ marginTop: 16 }}>
                            <div style={{ color: '#64748b', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
                                Expected Output
                            </div>
                            <div style={s.codeBlock}>{challenge?.expected_output}</div>
                        </div>

                        {showHint && challenge?.hint && (
                            <div style={{
                                marginTop: 16, padding: 14, borderRadius: 12,
                                background: '#fefce8', border: '1px solid #fde68a', color: '#854d0e',
                                fontSize: 14,
                            }}>
                                💡 <strong>Hint:</strong> {challenge.hint}
                            </div>
                        )}

                        {challenge?.difficulty && (
                            <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
                                <span style={s.badge(
                                    challenge.difficulty === 'easy' ? '#dcfce7' : '#fef3c7',
                                    challenge.difficulty === 'easy' ? '#16a34a' : '#d97706',
                                )}>
                                    {challenge.difficulty === 'easy' ? '🟢' : '🟡'} {challenge.difficulty}
                                </span>
                                {challenge.llm_generated && (
                                    <span style={s.badge('#ede9fe', '#7c3aed')}>🤖 AI Generated</span>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Right: Code editor */}
                    <div style={s.editorPane}>
                        <div style={{ padding: '8px 20px', background: '#1e293b', color: '#64748b', fontSize: 12, fontWeight: 600 }}>
                            📝 YOUR SOLUTION — Python
                        </div>
                        <textarea
                            style={s.codeArea}
                            value={code}
                            onChange={e => setCode(e.target.value)}
                            onKeyDown={handleKeyDown}
                            spellCheck={false}
                            disabled={submitting || !!result}
                        />
                    </div>
                </div>

                {/* Bottom bar */}
                <div style={s.submitBar}>
                    <button style={s.hintBtn} onClick={() => setShowHint(true)} disabled={showHint}>
                        {showHint ? '💡 Hint shown' : '💡 Show Hint'}
                    </button>
                    <button
                        style={{ ...s.submitBtn, opacity: submitting ? 0.6 : 1 }}
                        onClick={() => handleSubmit(false)}
                        disabled={submitting || !!result}
                    >
                        {submitting ? '⏳ Evaluating...' : '🚀 SUBMIT SOLUTION'}
                    </button>
                </div>
            </div>

            {/* Result overlay */}
            {result && (
                <div style={s.resultOverlay}>
                    {/* confetti */}
                    {result.user_won && Array.from({ length: 30 }).map((_, i) => (
                        <div key={i} style={{
                            position: 'fixed', top: -20,
                            left: `${Math.random() * 100}%`,
                            fontSize: 20,
                            animation: `confettiFall ${1.5 + Math.random() * 2}s ease-in ${Math.random() * 0.5}s forwards`,
                            pointerEvents: 'none',
                        }}>
                            {['🎉', '⭐', '🏆', '✨', '🎊'][i % 5]}
                        </div>
                    ))}

                    <div style={s.resultCard}>
                        <div style={s.resultEmoji}>{result.user_won ? '🏆' : '💪'}</div>
                        <div style={s.resultTitle(result.user_won)}>
                            {result.user_won ? 'VICTORY!' : 'DEFEAT'}
                        </div>
                        {result.timed_out && (
                            <div style={{ color: '#f59e0b', fontSize: 13, marginTop: 4 }}>⏰ Time ran out</div>
                        )}

                        <div style={s.ratingBadge(result.rating_change >= 0)}>
                            {result.rating_change >= 0 ? '+' : ''}{result.rating_change} ELO
                        </div>
                        <div style={{ color: '#6b7280', fontSize: 13, marginTop: 4 }}>
                            New rating: <b>{result.new_rating}</b>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'center', gap: 24, margin: '16px 0' }}>
                            <div><div style={{ fontSize: 24, fontWeight: 800, color: '#3b82f6' }}>{result.user_score}</div><div style={{ fontSize: 11, color: '#9ca3af' }}>Your Score</div></div>
                            <div style={{ fontSize: 24, fontWeight: 300, color: '#d1d5db' }}>vs</div>
                            <div><div style={{ fontSize: 24, fontWeight: 800, color: '#ef4444' }}>{result.ai_score}</div><div style={{ fontSize: 11, color: '#9ca3af' }}>AI Score</div></div>
                        </div>

                        <div style={s.feedbackBox}>
                            <b>💬 Feedback:</b> {result.feedback}
                            {result.improvements?.length > 0 && (
                                <ul style={{ margin: '8px 0 0', paddingLeft: 20 }}>
                                    {result.improvements.map((imp, i) => <li key={i}>{imp}</li>)}
                                </ul>
                            )}
                        </div>

                        <button style={s.continueBtn} onClick={onMatchEnd}>
                            Continue
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
//  MAIN ARENA MATCHMAKING PAGE
// ═══════════════════════════════════════════════════════════════════════════════
export default function ArenaMatchmaking() {
    const { token, user, isAuthenticated } = useAuthStore();
    const userId = user?.id;
    const [selectedMatchType, setSelectedMatchType] = useState('debug_duel');
    const [userRatings, setUserRatings] = useState({});
    const [matchHistory, setMatchHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [starting, setStarting] = useState(false);

    // live match state
    const [activeMatch, setActiveMatch] = useState(null);

    useEffect(() => {
        if (isAuthenticated && token) {
            fetchUserRatings();
            fetchMatchHistory();
        } else {
            setLoading(false);
        }
    }, [isAuthenticated, token]);

    const fetchUserRatings = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_BASE}/arena/rating/me`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            const data = await res.json();
            setUserRatings(data.data?.ratings || {});
        } catch (err) {
            console.error('Error fetching ratings:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchMatchHistory = async () => {
        try {
            const res = await fetch(`${API_BASE}/arena/history/me`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            const data = await res.json();
            setMatchHistory(data.data?.matches || []);
        } catch (err) {
            console.error('Error fetching match history:', err);
        }
    };

    const startMatch = async () => {
        if (!isAuthenticated || !token) return;
        setStarting(true);
        try {
            const res = await fetch(`${API_BASE}/arena/match/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ match_type: selectedMatchType }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to start match');
            const d = data.data;
            setActiveMatch({
                matchId: d.match_id,
                matchType: selectedMatchType,
                challenge: d.challenge,
                aiName: d.ai_opponent,
                timeLimit: d.time_limit,
            });
        } catch (err) {
            console.error('Error starting match:', err);
            alert('Failed to start match – please try again.');
        } finally {
            setStarting(false);
        }
    };

    const handleMatchEnd = () => {
        setActiveMatch(null);
        fetchUserRatings();
        fetchMatchHistory();
    };

    const getRatingForType = (mt) => userRatings[mt] || { rating: 1000, matches_played: 0, wins: 0, losses: 0 };

    const getRatingColor = (r) => {
        if (r >= 1800) return '#7c3aed';
        if (r >= 1600) return '#2563eb';
        if (r >= 1400) return '#16a34a';
        if (r >= 1200) return '#d97706';
        return '#6b7280';
    };

    const getRatingTier = (r) => {
        if (r >= 2000) return '👑 Master';
        if (r >= 1800) return '💎 Diamond';
        if (r >= 1600) return '🔷 Platinum';
        if (r >= 1400) return '🥇 Gold';
        if (r >= 1200) return '🥈 Silver';
        return '🥉 Bronze';
    };

    // ─── Show live match ─────────────────────────────────────────────────────
    if (activeMatch) {
        return (
            <LiveMatchInterface
                matchId={activeMatch.matchId}
                matchType={activeMatch.matchType}
                challenge={activeMatch.challenge}
                aiName={activeMatch.aiName}
                timeLimit={activeMatch.timeLimit}
                token={token}
                onMatchEnd={handleMatchEnd}
            />
        );
    }

    // ─── Not logged in gate ────────────────────────────────────────────────────
    if (!isAuthenticated) {
        return (
            <div style={{ ...s.page, textAlign: 'center', paddingTop: 80 }}>
                <div style={{ fontSize: 64, marginBottom: 16 }}>🔐</div>
                <h2 style={{ color: '#111827', fontSize: 24, fontWeight: 800 }}>Log in to enter the Arena</h2>
                <p style={{ color: '#6b7280', marginTop: 8 }}>You need an account to battle, earn Elo, and track your history.</p>
            </div>
        );
    }

    // ─── Loading ─────────────────────────────────────────────────────────────
    if (loading) {
        return (
            <div style={s.page}>
                <div style={s.spinner} />
                <div style={s.loadingText}>Loading Arena...</div>
            </div>
        );
    }

    // ─── Stats derived from real history data ────────────────────────────────
    const totalWins = matchHistory.filter(m => m.winner_id === userId).length;
    // AI losses are stored with winner_id===null, so we can't filter by !== userId.
    // Correct: losses = total matches minus wins.
    const totalLosses = matchHistory.length - totalWins;
    const winRate = matchHistory.length > 0 ? Math.round((totalWins / matchHistory.length) * 100) : 0;

    return (
        <div style={s.page}>
            {/* Header */}
            <div style={s.header}>
                <h1 style={s.h1}>⚔️ Coding Arena</h1>
                <p style={s.subtitle}>Challenge the AI in real-time coding battles — earn Elo rating!</p>
            </div>

            {/* Match type cards */}
            <div style={s.grid}>
                {Object.entries(MATCH_TYPES).map(([key, mt]) => {
                    const rating = getRatingForType(key);
                    const sel = selectedMatchType === key;
                    return (
                        <div key={key} style={s.card(sel, mt.color, mt.gradient)}
                            onClick={() => setSelectedMatchType(key)}>
                            {sel && <div style={s.checkBadge(mt.color)}>✓</div>}
                            <div style={s.cardIcon}>{mt.icon}</div>
                            <div style={s.cardTitle}>{mt.name}</div>
                            <div style={s.cardDesc}>{mt.description}</div>
                            <div style={{ borderTop: '1px solid #e5e7eb', marginTop: 14, paddingTop: 12 }}>
                                <div style={s.ratingRow}>
                                    <span style={s.ratingLabel}>Rating</span>
                                    <span style={{ fontWeight: 800, color: getRatingColor(rating.rating) }}>{rating.rating}</span>
                                </div>
                                <div style={s.ratingRow}>
                                    <span style={s.ratingLabel}>Tier</span>
                                    <span style={{ fontWeight: 600 }}>{getRatingTier(rating.rating)}</span>
                                </div>
                                <div style={{ fontSize: 12, color: '#9ca3af', textAlign: 'center', marginTop: 8 }}>
                                    {rating.matches_played} matches • {rating.wins}W / {rating.losses}L
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Start Match button */}
            <button
                style={{ ...s.bigBtn(MATCH_TYPES[selectedMatchType].color), opacity: starting ? 0.7 : 1 }}
                onClick={startMatch}
                disabled={starting || !isAuthenticated}
            >
                {starting ? '⏳ Finding Challenge...' : `⚔️ Start ${MATCH_TYPES[selectedMatchType].name}`}
            </button>

            {/* Overall Stats */}
            <div style={s.statsBox}>
                <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: '#111827' }}>📊 Overall Stats</h3>
                <div style={s.statsGrid}>
                    <div style={s.statCard('#f9fafb')}>
                        <div style={s.statVal('#111827')}>{matchHistory.length}</div>
                        <div style={s.statLabel}>Total Matches</div>
                    </div>
                    <div style={s.statCard('#f0fdf4')}>
                        <div style={s.statVal('#16a34a')}>{totalWins}</div>
                        <div style={s.statLabel}>Wins</div>
                    </div>
                    <div style={s.statCard('#fef2f2')}>
                        <div style={s.statVal('#dc2626')}>{totalLosses}</div>
                        <div style={s.statLabel}>Losses</div>
                    </div>
                    <div style={s.statCard('#eff6ff')}>
                        <div style={s.statVal('#2563eb')}>{winRate}%</div>
                        <div style={s.statLabel}>Win Rate</div>
                    </div>
                </div>
            </div>

            {/* Match History */}
            <div style={s.historyBox}>
                <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: '#111827' }}>📜 Recent Matches</h3>
                {matchHistory.length === 0 ? (
                    <div style={s.noHistory}>
                        No matches yet — start your first battle above! ⚔️
                    </div>
                ) : (
                    matchHistory.slice(0, 10).map((match, idx) => {
                        const won = match.winner_id === userId;
                        const rc = match.rating_change || 0;
                        return (
                            <div key={idx} style={s.histItem(won)}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <span style={{ fontSize: 28 }}>
                                        {MATCH_TYPES[match.match_type]?.icon || '⚔️'}
                                    </span>
                                    <div>
                                        <div style={{ fontWeight: 600, color: '#111827' }}>
                                            {MATCH_TYPES[match.match_type]?.name || match.match_type}
                                        </div>
                                        <div style={{ fontSize: 12, color: '#9ca3af' }}>
                                            {match.completed_at ? new Date(match.completed_at).toLocaleDateString() : '—'}
                                        </div>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                    <span style={{ fontWeight: 800, color: won ? '#16a34a' : '#dc2626' }}>
                                        {won ? 'VICTORY' : 'DEFEAT'}
                                    </span>
                                    <span style={s.badge(
                                        rc >= 0 ? '#dcfce7' : '#fef2f2',
                                        rc >= 0 ? '#16a34a' : '#dc2626',
                                    )}>
                                        {rc >= 0 ? '+' : ''}{rc}
                                    </span>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
