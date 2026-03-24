import * as Blockly from 'blockly';
import { javascriptGenerator } from 'blockly/javascript';
import { pythonGenerator } from 'blockly/python'; // Simulating C with Python generator for now as simple C gen is complex

// Define a custom theme
export const codeNestTheme = Blockly.Theme.defineTheme('codenest', {
    'base': Blockly.Themes.Classic,
    'componentStyles': {
        'workspaceBackgroundColour': '#F8F9FA',
        'toolboxBackgroundColour': '#FFFFFF',
        'toolboxForegroundColour': '#495057',
        'flyoutBackgroundColour': '#FFFFFF',
        'flyoutForegroundColour': '#495057',
        'flyoutOpacity': 0.9,
        'scrollbarColour': '#ADB5BD',
        'insertionMarkerColour': '#FF6B6B',
        'insertionMarkerOpacity': 0.3,
        'scrollbarOpacity': 0.4,
        'cursorColour': '#FF6B6B',
    },
    'fontStyle': {
        'family': '"Comic Neue", cursive, sans-serif',
        'weight': 'bold',
        'size': 12,
    },
    'startHats': true,
});

// Configure default blocks or generators here
javascriptGenerator.addReservedWords('exit');

export const supportedLanguages = {
    javascript: { name: 'JavaScript', generator: javascriptGenerator, mascot: '⚡' },
    java: { name: 'Java', generator: javascriptGenerator, mascot: '☕' }, // simplified: mapping to JS gen for demo
    c: { name: 'C', generator: pythonGenerator, mascot: '⚙️' }, // simplified
};
