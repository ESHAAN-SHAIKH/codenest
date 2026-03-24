import { useState } from 'react';
import BlocklyEditor from './BlocklyEditor';
import { Play, CheckCircle, XCircle, RotateCcw } from 'lucide-react';
import { supportedLanguages } from '../../lib/blocklyConfig';

export default function Arena() {
    const [output, setOutput] = useState([]);
    const [activeTab, setActiveTab] = useState('output'); // output | tests
    const [language, setLanguage] = useState('javascript');
    const [isRunning, setIsRunning] = useState(false);

    const runCode = async () => {
        setIsRunning(true);
        setActiveTab('output');
        setOutput(['> Compiling...']);

        // Simulate execution delay
        setTimeout(() => {
            const langName = supportedLanguages[language].name;
            setOutput(prev => [
                ...prev,
                `> Linked ${langName} runtime...`,
                `> Executing in sandbox...`,
                'Hello CodeNest!',
                '> Execution finished - Success!'
            ]);
            setIsRunning(false);
        }, 1500);
    };

    return (
        <div className="flex h-[calc(100vh-140px)] gap-4">
            {/* Left: Blockly Editor */}
            <div className="flex-1 flex flex-col gap-2">
                <div className="flex justify-between items-center bg-white p-2 rounded-xl shadow-sm">
                    <div className="flex items-center gap-4">
                        <h2 className="font-bold text-gray-700 ml-2">Level 3: Loop de Loop</h2>
                        {/* Language Switcher */}
                        <div className="flex bg-gray-100 p-1 rounded-lg">
                            {Object.entries(supportedLanguages).map(([key, config]) => (
                                <button
                                    key={key}
                                    onClick={() => setLanguage(key)}
                                    className={`px-3 py-1 rounded-md text-sm font-bold flex items-center gap-2 transition-all ${language === key
                                            ? 'bg-white text-primary shadow-sm'
                                            : 'text-gray-500 hover:text-gray-700'
                                        }`}
                                >
                                    <span>{config.mascot}</span>
                                    {config.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="flex gap-2">
                        <button className="flex items-center gap-2 bg-yellow-100 text-yellow-700 px-3 py-1.5 rounded-lg font-bold hover:bg-yellow-200 transition-colors">
                            <span>💡 Hint (10 XP)</span>
                        </button>
                        <button
                            onClick={runCode}
                            disabled={isRunning}
                            className={`flex items-center gap-2 text-white px-4 py-1.5 rounded-lg font-bold transition-all shadow-lg ${isRunning
                                    ? 'bg-gray-400 cursor-wait'
                                    : 'bg-green-500 hover:bg-green-600 shadow-green-500/30'
                                }`}
                        >
                            <Play size={18} fill="currentColor" />
                            {isRunning ? 'Running...' : 'Run Code'}
                        </button>
                    </div>
                </div>

                <BlocklyEditor language={language} />
            </div>

            {/* Right: Challenge & Console */}
            <div className="w-80 flex flex-col gap-4">
                {/* Challenge Description */}
                <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex-shrink-0">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-2xl">🐱</div>
                        <h3 className="font-bold text-gray-800">Code Cat says:</h3>
                    </div>
                    <p className="text-gray-600 text-sm leading-relaxed">
                        "We need to collect 5 stars! Can you use a <strong>Loop</strong> to make me walk forward 5 times?"
                    </p>
                </div>

                {/* Output / Tests Panel */}
                <div className="bg-gray-900 rounded-2xl flex-1 flex flex-col overflow-hidden shadow-lg border border-gray-800">
                    <div className="flex border-b border-gray-700">
                        <button
                            onClick={() => setActiveTab('output')}
                            className={`flex-1 py-2 text-sm font-bold ${activeTab === 'output' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800/50'}`}
                        >
                            Output
                        </button>
                        <button
                            onClick={() => setActiveTab('tests')}
                            className={`flex-1 py-2 text-sm font-bold ${activeTab === 'tests' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800/50'}`}
                        >
                            Test Cases
                        </button>
                    </div>

                    <div className="p-4 font-mono text-sm text-gray-300 overflow-y-auto flex-1">
                        {activeTab === 'output' ? (
                            output.length > 0 ? (
                                output.map((line, i) => <div key={i}>{line}</div>)
                            ) : (
                                <div className="text-gray-600 italic">Press Run to see output...</div>
                            )
                        ) : (
                            <div className="space-y-3">
                                <div className="flex items-center gap-2 text-green-400">
                                    <CheckCircle size={16} /> <span>Walked 5 steps</span>
                                </div>
                                <div className="flex items-center gap-2 text-red-400">
                                    <XCircle size={16} /> <span>Used 'Repeat' block</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-500">
                                    <div className="w-4 h-4 border-2 border-gray-600 rounded-full"></div> <span>Collected all stars</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
