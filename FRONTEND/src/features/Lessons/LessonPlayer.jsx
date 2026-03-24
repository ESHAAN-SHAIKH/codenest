import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, PlayCircle, CheckCircle, HelpCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const sections = ['intro', 'explanation', 'practice', 'quiz', 'challenge'];

export default function LessonPlayer() {
    const { id } = useParams();
    const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
    const currentSection = sections[currentSectionIndex];

    const nextSection = () => {
        if (currentSectionIndex < sections.length - 1) {
            setCurrentSectionIndex(prev => prev + 1);
        }
    };

    const prevSection = () => {
        if (currentSectionIndex > 0) {
            setCurrentSectionIndex(prev => prev - 1);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-100px)]">
            {/* Header / Progress */}
            <div className="flex items-center justify-between mb-6">
                <Link to="/" className="flex items-center gap-2 text-gray-500 hover:text-primary transition-colors font-bold">
                    <ChevronLeft /> Back to Map
                </Link>

                <div className="flex gap-2">
                    {sections.map((section, idx) => (
                        <div
                            key={section}
                            className={`h-2 w-16 rounded-full transition-colors ${idx <= currentSectionIndex ? 'bg-primary' : 'bg-gray-200'
                                }`}
                        />
                    ))}
                </div>

                <div className="font-bold text-gray-700">Lesson {id}: Loops</div>
            </div>

            {/* Main Split View */}
            <div className="flex-1 flex gap-6 overflow-hidden">
                {/* Left: Content */}
                <div className="flex-1 bg-white rounded-3xl shadow-sm border border-gray-100 p-8 overflow-y-auto">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentSection}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="h-full flex flex-col"
                        >
                            {currentSection === 'intro' && (
                                <div className="space-y-6 text-center pt-10">
                                    <h1 className="text-4xl font-bold text-gray-800">Welcome to Loops!</h1>
                                    <div className="w-full aspect-video bg-gray-900 rounded-2xl flex items-center justify-center text-white relative group cursor-pointer overflow-hidden">
                                        <div className="absolute inset-0 bg-primary/20 group-hover:bg-transparent transition-colors"></div>
                                        <PlayCircle size={64} className="group-hover:scale-110 transition-transform" />
                                        <span className="absolute bottom-4 text-sm font-bold opacity-80">Watch Video: 2 min</span>
                                    </div>
                                    <p className="text-xl text-gray-600 max-w-lg mx-auto">
                                        Learn how to make the computer repeat tasks for you without complaining!
                                    </p>
                                    <button onClick={nextSection} className="btn-primary text-lg px-8 py-3 rounded-xl mx-auto block">
                                        Start Learning
                                    </button>
                                </div>
                            )}

                            {currentSection === 'explanation' && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-gray-800">What is a Loop?</h2>
                                    <p className="text-lg text-gray-600 leading-relaxed">
                                        Imagine you have to eat 10 peas. You don't say "Eat pea" 10 times.
                                        You say "Eat peas UNTIL plate is empty". That's a loop!
                                    </p>
                                    <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 font-mono text-blue-800">
                                        <div className="font-bold mb-2">// JavaScript Example</div>
                                        for (let i = 0; i &lt; 5; i++) {'{'} <br />
                                        &nbsp;&nbsp; moveForward(); <br />
                                        {'}'}
                                    </div>
                                </div>
                            )}

                            {currentSection === 'practice' && (
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-800 mb-4">Let's Try It!</h2>
                                    <p className="text-gray-600 mb-6">Drag the blocks to make the character jump 3 times.</p>
                                    {/* Placeholder for mini-blockly */}
                                    <div className="h-64 bg-gray-100 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400">
                                        Mini Playground
                                    </div>
                                </div>
                            )}

                            {currentSection === 'quiz' && (
                                <div className="space-y-6">
                                    <h2 className="text-2xl font-bold text-gray-800">Quick Quiz</h2>
                                    <div className="space-y-3">
                                        <label className="block p-4 border-2 border-gray-100 rounded-xl hover:border-primary hover:bg-red-50 cursor-pointer transition-colors">
                                            <input type="radio" name="q1" className="mr-3" />
                                            A loop runs code only once.
                                        </label>
                                        <label className="block p-4 border-2 border-gray-100 rounded-xl hover:border-primary hover:bg-green-50 cursor-pointer transition-colors">
                                            <input type="radio" name="q1" className="mr-3" />
                                            A loop repeats code multiple times.
                                        </label>
                                    </div>
                                </div>
                            )}

                            {currentSection === 'challenge' && (
                                <div className="text-center pt-20 space-y-6">
                                    <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center text-green-500 mx-auto">
                                        <CheckCircle size={48} />
                                    </div>
                                    <h2 className="text-3xl font-bold text-gray-800">Ready for the Arena?</h2>
                                    <p className="text-gray-600">You've mastered the basics. Now prove your skills via a real coding challenge!</p>
                                    <Link to="/arena" className="inline-block bg-primary text-white font-bold text-xl px-8 py-4 rounded-2xl shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-1 transition-all">
                                        Go to CodeQuest Arena
                                    </Link>
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Right: Companion / Helper */}
                <div className="w-80 bg-orange-50 rounded-3xl p-6 border border-orange-100 flex flex-col items-center text-center">
                    <div className="w-32 h-32 bg-orange-200 rounded-full mb-4 flex items-center justify-center text-4xl shadow-inner">
                        🦉
                    </div>
                    <h3 className="font-bold text-xl text-orange-900 mb-2">Professor Hoot</h3>
                    <div className="bg-white p-4 rounded-xl shadow-sm text-sm text-gray-600 relative chat-bubble">
                        "Loops save us time! Instead of writing the same code over and over, we can write it once and repeat it."
                    </div>

                    <div className="mt-auto w-full space-y-2">
                        <button className="w-full bg-white text-orange-600 font-bold py-3 rounded-xl border border-orange-200 hover:bg-orange-100 transition-colors flex items-center justify-center gap-2">
                            <HelpCircle size={18} /> Ask for Help
                        </button>
                    </div>
                </div>
            </div>

            {/* Navigation Footer */}
            <div className="mt-6 flex justify-between">
                <button
                    onClick={prevSection}
                    disabled={currentSectionIndex === 0}
                    className="px-6 py-3 font-bold text-gray-500 disabled:opacity-30 hover:text-gray-800 transition-colors"
                >
                    Previous
                </button>

                {currentSection !== 'challenge' && (
                    <button
                        onClick={nextSection}
                        className="bg-primary text-white font-bold px-8 py-3 rounded-xl shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2"
                    >
                        Next Step <ChevronRight size={20} />
                    </button>
                )}
            </div>
        </div>
    );
}
