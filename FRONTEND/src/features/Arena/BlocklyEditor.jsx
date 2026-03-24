import { useEffect, useRef, useState } from 'react';
import * as Blockly from 'blockly';
import { javascriptGenerator } from 'blockly/javascript';
import { pythonGenerator } from 'blockly/python';
import { codeNestTheme } from '../../lib/blocklyConfig';
import apiService from '../../services/api';
import 'blockly/blocks';

export default function BlocklyEditor({ initialXml, onCodeChange, language = 'python' }) {
    const blocklyDiv = useRef(null);
    const workspaceRef = useRef(null);
    const [generatedCode, setGeneratedCode] = useState('');
    const [output, setOutput] = useState('');
    const [executing, setExecuting] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!blocklyDiv.current) return;

        // Initialize Blockly
        workspaceRef.current = Blockly.inject(blocklyDiv.current, {
            toolbox: `
        <xml xmlns="https://developers.google.com/blockly/xml">
          <category name="Logic" colour="#5d9cec">
            <block type="controls_if"></block>
            <block type="logic_compare"></block>
          </category>
          <category name="Loops" colour="#5d9cec">
            <block type="controls_repeat_ext"></block>
            <block type="controls_whileUntil"></block>
          </category>
          <category name="Math" colour="#5d9cec">
            <block type="math_number"></block>
            <block type="math_arithmetic"></block>
          </category>
          <category name="Text" colour="#5d9cec">
            <block type="text"></block>
            <block type="text_print"></block>
          </category>
          <category name="Variables" colour="#a2d9ce" custom="VARIABLE"></category>
        </xml>
      `,
            scrollbars: true,
            move: {
                scrollbars: true,
                drag: true,
                wheel: true,
            },
            theme: codeNestTheme,
            renderer: 'zelos', // Scratch-like renderer
        });

        const onResize = () => {
            Blockly.svgResize(workspaceRef.current);
        };
        window.addEventListener('resize', onResize);

        // Initial load
        if (initialXml) {
            const xml = Blockly.utils.xml.textToDom(initialXml);
            Blockly.Xml.domToWorkspace(xml, workspaceRef.current);
        }

        // Change listener - generate code when blocks change
        const listener = (event) => {
            if (event.type === Blockly.Events.FINISHED_LOADING || event.isUiEvent) return;
            generateCode();
        };
        workspaceRef.current.addChangeListener(listener);

        return () => {
            window.removeEventListener('resize', onResize);
            if (workspaceRef.current) {
                workspaceRef.current.dispose();
            }
        };
    }, [language]); // Re-init when language changes

    const generateCode = () => {
        if (!workspaceRef.current) return '';

        const generator = language === 'python' ? pythonGenerator : javascriptGenerator;
        const code = generator.workspaceToCode(workspaceRef.current);
        setGeneratedCode(code);

        if (onCodeChange) {
            onCodeChange(code);
        }

        return code;
    };

    const executeCode = async () => {
        const code = generateCode();

        if (!code || !code.trim()) {
            setError('No code to execute! Add some blocks first.');
            return;
        }

        setExecuting(true);
        setError(null);
        setOutput('');

        try {
            const result = await apiService.executeCode(code, language);

            if (result.success) {
                setOutput(result.output || '(No output)');
            } else {
                setError(result.error || 'Execution failed');
                setOutput(result.output || '');
            }
        } catch (err) {
            setError(`Failed to execute code: ${err.message}`);
        } finally {
            setExecuting(false);
        }
    };

    return (
        <div className="flex flex-col h-full gap-4">
            {/* Blockly Workspace */}
            <div className="flex-1 relative rounded-2xl overflow-hidden border-2 border-gray-200 bg-white">
                <div ref={blocklyDiv} className="absolute inset-0" />
            </div>

            {/* Controls */}
            <div className="flex gap-3">
                <button
                    onClick={executeCode}
                    disabled={executing}
                    className="px-6 py-3 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                    {executing ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Running...
                        </>
                    ) : (
                        <>▶ Run Code</>
                    )}
                </button>
                <button
                    onClick={() => {
                        setOutput('');
                        setError(null);
                        setGeneratedCode('');
                    }}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
                >
                    Clear Output
                </button>
            </div>

            {/* Output Panel */}
            {(output || error || generatedCode) && (
                <div className="bg-gray-900 text-white rounded-2xl p-4 max-h-64 overflow-y-auto">
                    {error && (
                        <div className="mb-3 p-3 bg-red-900/50 border border-red-500 rounded-lg">
                            <div className="font-bold text-red-300 mb-1">❌ Error:</div>
                            <div className="text-red-200 text-sm font-mono">{error}</div>
                        </div>
                    )}

                    {output && (
                        <div className="mb-3">
                            <div className="font-bold text-green-300 mb-1">✅ Output:</div>
                            <pre className="text-sm font-mono whitespace-pre-wrap">{output}</pre>
                        </div>
                    )}

                    {generatedCode && (
                        <div>
                            <div className="font-bold text-blue-300 mb-1">📝 Generated {language} Code:</div>
                            <pre className="text-sm font-mono bg-gray-800 p-3 rounded-lg overflow-x-auto">{generatedCode}</pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
