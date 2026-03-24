import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, ChevronDown, ChevronUp, Loader } from 'lucide-react';
import MascotPanel from '../../components/Mascot/MascotPanel';
import useAuthStore from '../../stores/useAuthStore';
import useBeginnerLearningStore from '../../stores/useBeginnerLearningStore';

const API_BASE = import.meta.env.VITE_API_URL
    ? import.meta.env.VITE_API_URL.replace(/\/api$/, '')
    : 'http://localhost:5000';

/** Safely parse scaffold_data whether it arrives as a string or object */
function parseScaffoldData(raw) {
    if (!raw) return {};
    if (typeof raw === 'string') {
        try { return JSON.parse(raw); } catch { return {}; }
    }
    return raw;
}

/** Safely parse hints whether it arrives as a string or array */
function parseHints(raw) {
    if (!raw) return [];
    if (Array.isArray(raw)) return raw;
    if (typeof raw === 'string') {
        try { return JSON.parse(raw); } catch { return [raw]; }
    }
    return [];
}

// ─── Fill-in-the-Blank ────────────────────────────────────────────────────────
function FillInBlank({ challenge, onSubmit, loading }) {
    const scaffold = parseScaffoldData(challenge.scaffold_data);
    const template = scaffold.template || '';
    const blanks = scaffold.blanks || [];
    const labels = scaffold.blank_labels || [];
    const [values, setValues] = useState(Array(blanks.length).fill(''));

    const handleChange = (idx, val) => {
        setValues((prev) => prev.map((v, i) => (i === idx ? val : v)));
    };

    // Build a display version of the code showing ①②③ markers for each blank,
    // and a live preview replacing markers with user-typed values.
    const MARKERS = ['①', '②', '③', '④', '⑤'];
    let markerIdx = 0;
    const displayCode = template.replace(/___/g, () => MARKERS[markerIdx++] || '___');

    // Live preview: replace markers with current input values (or placeholder)
    let previewIdx = 0;
    const previewCode = template.replace(/___/g, () => {
        const v = values[previewIdx] || '_'.repeat((labels[previewIdx] || '').length || 3);
        previewIdx++;
        return v;
    });

    const allFilled = values.every((v) => v.trim() !== '');

    return (
        <div className="space-y-5">
            <h2 className="text-xl font-bold text-gray-800">Fill in the Blank</h2>
            <p className="text-gray-600 text-sm">{challenge.description}</p>

            {/* Code display — markers show where the blanks are */}
            <div>
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Template</div>
                <pre className="bg-gray-900 rounded-xl p-5 font-mono text-sm text-gray-100 leading-7 overflow-x-auto m-0">
                    {displayCode.split('').map((ch, i) => {
                        if (MARKERS.includes(ch)) {
                            const bIdx = MARKERS.indexOf(ch);
                            return (
                                <span key={i} className="bg-yellow-400 text-gray-900 font-bold rounded px-1">
                                    {ch}
                                </span>
                            );
                        }
                        return ch;
                    })}
                </pre>
            </div>

            {/* Labeled inputs — one per blank */}
            <div className="space-y-3">
                {labels.map((label, i) => (
                    <div key={i} className="flex items-center gap-3">
                        <span className="bg-yellow-400 text-gray-900 font-bold rounded px-2 py-0.5 text-sm min-w-[28px] text-center flex-shrink-0">
                            {MARKERS[i] || (i + 1)}
                        </span>
                        <label className="text-sm font-medium text-gray-600 w-44 flex-shrink-0">{label}</label>
                        <input
                            type="text"
                            value={values[i]}
                            onChange={(e) => handleChange(i, e.target.value)}
                            placeholder={blanks[i] || '...'}
                            className="flex-1 border border-gray-200 rounded-xl px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        />
                    </div>
                ))}
            </div>

            {/* Live preview */}
            {allFilled && (
                <div>
                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Preview</div>
                    <pre className="bg-indigo-950 border border-indigo-800 rounded-xl p-4 font-mono text-sm text-indigo-100 leading-7 overflow-x-auto m-0">
                        {previewCode}
                    </pre>
                </div>
            )}

            <button
                onClick={() => onSubmit({ filled_blanks: values })}
                disabled={loading || !allFilled}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
            >
                {loading ? <Loader size={18} className="animate-spin" /> : null}
                Run My Answer
            </button>
        </div>
    );
}


// ─── Predict-the-Output ────────────────────────────────────────────────────────
function PredictOutput({ challenge, onSubmit, loading }) {
    const scaffold = parseScaffoldData(challenge.scaffold_data);
    const code = scaffold.code || '';
    const [prediction, setPrediction] = useState('');

    return (
        <div className="space-y-6">
            <h2 className="text-xl font-bold text-gray-800">Predict the Output</h2>
            <p className="text-gray-600 text-sm">
                Read the code below. Before running it, write what you think it will print.
            </p>

            <div className="bg-gray-900 rounded-xl p-5 font-mono text-sm text-gray-100 whitespace-pre-wrap leading-relaxed">
                {code}
            </div>

            <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Your prediction (exactly as it would appear on screen):
                </label>
                <textarea
                    rows={3}
                    value={prediction}
                    onChange={(e) => setPrediction(e.target.value)}
                    placeholder="What will Python print?"
                    className="w-full border border-gray-200 rounded-xl p-3 font-mono text-sm resize-none focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                />
            </div>

            <button
                onClick={() => onSubmit({ prediction, code })}
                disabled={loading || !prediction.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
            >
                {loading ? <Loader size={18} className="animate-spin" /> : null}
                Submit Prediction &amp; Run
            </button>
        </div>
    );
}

// ─── Error Spotting ────────────────────────────────────────────────────────────
function ErrorSpotting({ challenge, onSubmit, loading }) {
    const scaffold = parseScaffoldData(challenge.scaffold_data);
    const buggyCode = scaffold.buggy_code || '';
    const lines = buggyCode.split('\n');
    const [selectedLine, setSelectedLine] = useState(null);
    const [explanation, setExplanation] = useState('');

    return (
        <div className="space-y-6">
            <h2 className="text-xl font-bold text-gray-800">Spot the Error</h2>
            <p className="text-gray-600 text-sm">
                Click the line you think contains the bug, then explain what's wrong.
            </p>

            <div className="bg-gray-900 rounded-xl p-4 font-mono text-sm">
                {lines.map((line, idx) => {
                    const lineNum = idx + 1;
                    const isSelected = selectedLine === lineNum;
                    return (
                        <div
                            key={idx}
                            onClick={() => setSelectedLine(lineNum)}
                            className={`flex items-center gap-3 px-2 py-1 rounded cursor-pointer transition-colors ${isSelected
                                ? 'bg-red-500/30 border border-red-400'
                                : 'hover:bg-gray-700/50'
                                }`}
                        >
                            <span className="text-gray-500 w-5 text-right select-none text-xs">{lineNum}</span>
                            <span className={isSelected ? 'text-red-200' : 'text-gray-100'}>{line}</span>
                        </div>
                    );
                })}
            </div>

            {selectedLine && (
                <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-2"
                >
                    <label className="block text-sm font-semibold text-gray-700">
                        Why is line {selectedLine} a problem?
                    </label>
                    <textarea
                        rows={2}
                        value={explanation}
                        onChange={(e) => setExplanation(e.target.value)}
                        placeholder="Explain the bug..."
                        className="w-full border border-gray-200 rounded-xl p-3 text-sm resize-none focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                    />
                </motion.div>
            )}

            <button
                onClick={() => onSubmit({ line_number: selectedLine, explanation, code: buggyCode })}
                disabled={loading || !selectedLine || !explanation.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
            >
                {loading ? <Loader size={18} className="animate-spin" /> : null}
                Submit Diagnosis
            </button>
        </div>
    );
}

// ─── Layered Feedback Panel ────────────────────────────────────────────────────
function FeedbackPanel({ result }) {
    const [showTech, setShowTech] = useState(false);
    if (!result) return null;

    const passed = result.passed;

    return (
        <div className="space-y-3">
            {/* Pass / Fail header */}
            <div
                className={`flex items-center gap-3 rounded-xl px-4 py-3 font-bold text-sm ${passed ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
                    }`}
            >
                {passed ? <CheckCircle size={18} /> : <XCircle size={18} />}
                {passed ? 'Correct!' : 'Not quite.'}
            </div>

            {/* Layered beginner feedback */}
            {result.what_happened && (
                <div className="text-sm text-gray-700 bg-gray-50 rounded-xl px-4 py-3">
                    <span className="font-semibold text-gray-500 text-xs uppercase tracking-wide">What happened</span>
                    <p className="mt-1">{result.what_happened}</p>
                </div>
            )}

            {result.why && (
                <div className="text-sm text-gray-700 bg-blue-50 rounded-xl px-4 py-3">
                    <span className="font-semibold text-blue-500 text-xs uppercase tracking-wide">Why</span>
                    <p className="mt-1">{result.why}</p>
                </div>
            )}

            {/* Beginner error translation */}
            {result.beginner_error && (
                <div className="text-sm text-red-700 bg-red-50 rounded-xl px-4 py-3">
                    <span className="font-semibold text-red-500 text-xs uppercase tracking-wide">Error Explained</span>
                    <p className="mt-1">{result.beginner_error}</p>
                </div>
            )}

            {/* Prediction comparison */}
            {result.prediction_feedback && (
                <div className="bg-amber-50 rounded-xl px-4 py-3 text-sm space-y-1">
                    <div><span className="font-semibold text-amber-700">Your prediction:</span> <code>{result.prediction_feedback.your_prediction || '(empty)'}</code></div>
                    <div><span className="font-semibold text-amber-700">Actual output:</span> <code>{result.prediction_feedback.actual_output || '(empty)'}</code></div>
                    <div>{result.prediction_feedback.matched ? '✅ Match!' : '❌ Mismatch'}</div>
                </div>
            )}

            {/* Technical details (collapsed) */}
            {result.show_technical_details && (
                <div>
                    <button
                        onClick={() => setShowTech((v) => !v)}
                        className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
                    >
                        {showTech ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        {showTech ? 'Hide' : 'Show'} Technical Details
                    </button>
                    <AnimatePresence>
                        {showTech && (
                            <motion.pre
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="mt-2 bg-gray-900 text-red-300 text-xs font-mono rounded-xl p-3 overflow-x-auto whitespace-pre-wrap"
                            >
                                {result.show_technical_details}
                            </motion.pre>
                        )}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
}

// ─── Main Component ────────────────────────────────────────────────────────────
export default function ScaffoldedChallenge({ challenge: challengeProp }) {
    const { id } = useParams();
    const navigate = useNavigate();
    const { token } = useAuthStore();
    const { markScaffoldedComplete, recordMisconceptionSeen } = useBeginnerLearningStore();

    const [challenge, setChallenge] = useState(challengeProp || null);
    const [loadingChallenge, setLoadingChallenge] = useState(!challengeProp);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const [mascotLoading, setMascotLoading] = useState(false);

    // Fetch challenge by ID if not passed as prop   
    useEffect(() => {
        if (challengeProp || !id) return;
        setLoadingChallenge(true);
        fetch(`${API_BASE}/api/beginner/challenges`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((r) => r.json())
            .then((data) => {
                const found = data.challenges?.find((c) => String(c.id) === String(id));
                setChallenge(found || null);
                setLoadingChallenge(false);
            })
            .catch(() => setLoadingChallenge(false));
    }, [id]);

    const handleSubmit = async (userInput) => {
        if (!challenge) return;
        setSubmitting(true);
        setMascotLoading(true);
        setResult(null);
        try {
            const res = await fetch(`${API_BASE}/api/beginner/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    challenge_id: challenge.id,
                    user_input: userInput,
                }),
            });
            const data = await res.json();
            setResult(data);
            setMascotLoading(false);

            // Update local store
            if (data.passed) {
                const scaffoldType = challenge.scaffold_data?.type || challenge.challenge_mode;
                markScaffoldedComplete(scaffoldType);
            }
            if (data.misconceptions_detected?.length) {
                data.misconceptions_detected.forEach((m) => recordMisconceptionSeen(m));
            }
            // Handle phase transition
            if (data.transition_notice) {
                // Store will be updated on next transition-check fetch
            }
        } catch (err) {
            setMascotLoading(false);
            console.error('Submit error:', err);
        } finally {
            setSubmitting(false);
        }
    };

    if (loadingChallenge) {
        return (
            <div className="flex items-center justify-center h-64 text-gray-400">
                <Loader className="animate-spin" /> <span className="ml-2">Loading challenge...</span>
            </div>
        );
    }

    if (!challenge) {
        return <div className="text-center text-gray-500 py-20">Challenge not found.</div>;
    }

    const scaffoldType = parseScaffoldData(challenge.scaffold_data)?.type || 'freeform';
    const hints = parseHints(challenge.hints);

    return (
        <div className="max-w-5xl mx-auto px-4 py-8">
            <div className="flex gap-6">
                {/* Left: challenge panel */}
                <div className="flex-1 space-y-6">
                    <div>
                        <span className="text-xs font-semibold uppercase tracking-wide text-indigo-500">
                            {scaffoldType === 'fill_in_blank'
                                ? 'Fill in the Blank'
                                : scaffoldType === 'predict_output'
                                    ? 'Predict the Output'
                                    : scaffoldType === 'error_spotting'
                                        ? 'Error Spotting'
                                        : 'Challenge'}
                        </span>
                        <h1 className="text-2xl font-bold text-gray-800 mt-1">{challenge.title}</h1>
                    </div>

                    {/* Scaffold input */}
                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                        {scaffoldType === 'fill_in_blank' && (
                            <FillInBlank challenge={challenge} onSubmit={handleSubmit} loading={submitting} />
                        )}
                        {scaffoldType === 'predict_output' && (
                            <PredictOutput challenge={challenge} onSubmit={handleSubmit} loading={submitting} />
                        )}
                        {scaffoldType === 'error_spotting' && (
                            <ErrorSpotting challenge={challenge} onSubmit={handleSubmit} loading={submitting} />
                        )}
                    </div>

                    {/* Layered feedback */}
                    <AnimatePresence>
                        {result && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6"
                            >
                                <FeedbackPanel result={result} />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Right: mascot sidebar */}
                <div className="w-72 flex-shrink-0">
                    <div className="sticky top-4 space-y-4">
                        <MascotPanel
                            mascotResponse={result?.mascot}
                            isLoading={mascotLoading}
                        />

                        {/* Hints (from challenge.hints) */}
                        {hints.length > 0 && (
                            <details className="bg-amber-50 border border-amber-100 rounded-2xl p-4">
                                <summary className="cursor-pointer text-sm font-semibold text-amber-800">
                                    💡 Hint available
                                </summary>
                                <p className="mt-2 text-sm text-amber-700">{hints[0]}</p>
                            </details>
                        )}

                        {/* Transition notice */}
                        {result?.transition_notice && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-green-50 border border-green-200 rounded-2xl p-4 text-sm text-green-700 space-y-2"
                            >
                                <div className="font-bold">Phase Transition!</div>
                                <div>You've moved from <strong>{result.transition_notice.previous_phase}</strong> to <strong>{result.transition_notice.new_phase}</strong>.</div>
                            </motion.div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
