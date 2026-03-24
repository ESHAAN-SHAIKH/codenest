import { motion, AnimatePresence } from 'framer-motion';
import MascotPanel from '../../components/Mascot/MascotPanel';

/**
 * TransitionPrompt
 *
 * Props:
 *   transitionData: { current_phase, new_phase, eligible, mascot, criteria }
 *   onStay: () => void
 *   onProceed: () => void
 */
export default function TransitionPrompt({ transitionData, onStay, onProceed }) {
    if (!transitionData?.eligible) return null;

    const phaseLabel = {
        guided: 'Guided Challenges',
        freeform: 'Freeform Coding',
        complete: 'Full Access',
    };

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.92, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 10 }}
                    className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 space-y-6"
                >
                    <div className="text-center space-y-2">
                        <div className="text-5xl">🚀</div>
                        <h2 className="text-2xl font-bold text-gray-800">Ready for the Next Level</h2>
                        <p className="text-gray-500 text-sm">
                            You've completed the structured exercises. You can now move to{' '}
                            <strong>{phaseLabel[transitionData.new_phase] || transitionData.new_phase}</strong>.
                        </p>
                    </div>

                    {/* Criteria met */}
                    <div className="bg-green-50 rounded-xl px-4 py-3 text-sm text-green-700 space-y-1">
                        {transitionData.criteria?.predict_output_passed && (
                            <div>✅ Prediction task completed</div>
                        )}
                        {transitionData.criteria?.error_spotting_passed && (
                            <div>✅ Error spotting task completed</div>
                        )}
                        {transitionData.criteria?.scaffolded_completed >= 4 && (
                            <div>✅ {transitionData.criteria.scaffolded_completed} scaffolded exercises done</div>
                        )}
                        {transitionData.criteria?.freeform_syntax_clean && (
                            <div>✅ Clean freeform submission</div>
                        )}
                    </div>

                    {/* Mascot message */}
                    {transitionData.mascot && (
                        <MascotPanel mascotResponse={transitionData.mascot} compact />
                    )}

                    <div className="flex gap-3">
                        <button
                            onClick={onStay}
                            className="flex-1 border border-gray-200 text-gray-600 font-semibold py-3 rounded-xl hover:bg-gray-50 transition-colors"
                        >
                            Stay Here
                        </button>
                        <button
                            onClick={onProceed}
                            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors"
                        >
                            Try {phaseLabel[transitionData.new_phase] || 'Next Phase'}
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
