/**
 * Centralized API Service for CodeNest Frontend
 * Handles all backend communication with proper error handling and loading states
 */

const API_BASE_URL = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/api$/, '') : 'http://localhost:5000';

class APIService {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Generic request handler with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        // Get auth token from Zustand persisted state
        let authToken = null;
        try {
            const stored = JSON.parse(localStorage.getItem('codenest-auth'));
            authToken = stored?.state?.token;
        } catch { /* no token */ }

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {}),
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.details || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, {
            method: 'GET',
        });
    }

    /**
     * POST request
     */
    async post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    // ============= Progress API =============

    /**
     * Get skill map with user progress
     * @param {string} userId - User ID
     */
    async getSkillMap(userId = 'demo_user') {
        return this.get(`/api/progress/map?user_id=${userId}`);
    }

    /**
     * Complete a lesson node
     * @param {string} userId - User ID
     * @param {number} lessonId - Lesson ID
     * @param {number} stars - Stars earned (1-3)
     */
    async completeLesson(userId, lessonId, stars = 1) {
        return this.post('/api/progress/complete', {
            user_id: userId,
            lesson_id: lessonId,
            stars,
        });
    }

    // ============= Execution API =============

    /**
     * Execute code in sandbox
     * @param {string} code - Code to execute
     * @param {string} language - Programming language ('python', 'java', 'javascript')
     */
    async executeCode(code, language = 'python') {
        return this.post('/api/execute/', {
            code,
            language,
        });
    }

    /**
     * Validate lesson output
     * @param {string} userOutput - User's code output
     * @param {string} expectedOutput - Expected output
     */
    async validateLesson(userOutput, expectedOutput) {
        return this.post('/api/execute/validate', {
            user_output: userOutput,
            expected_output: expectedOutput,
        });
    }

    /**
     * Get supported programming languages
     */
    async getSupportedLanguages() {
        return this.get('/api/execute/languages');
    }

    // ============= AI API =============

    /**
     * General chat with AI assistant
     * @param {string} message - User message
     * @param {string} code - Optional code context
     * @param {object} options - Additional options (context, user_level, language)
     */
    async chat(message, code = '', options = {}) {
        return this.post('/api/ai/chat', {
            message,
            code,
            context: options.context || 'general',
            user_level: options.user_level || 'beginner',
            language: options.language || 'python',
        });
    }

    /**
     * Explain code
     * @param {string} code - Code to explain
     * @param {object} options - Additional options
     */
    async explainCode(code, options = {}) {
        return this.post('/api/ai/explain', {
            code,
            question: options.question || 'Explain this code',
            context: options.context || 'general',
            user_level: options.user_level || 'beginner',
            language: options.language || 'python',
        });
    }

    /**
     * Get hint for lesson
     * @param {number} lessonId - Lesson ID
     * @param {string} userCode - User's current code
     * @param {string} expectedOutput - Expected output
     * @param {string} language - Programming language
     */
    async getHint(lessonId, userCode = '', expectedOutput = '', language = 'python') {
        return this.post('/api/ai/hint', {
            lesson_id: lessonId,
            user_code: userCode,
            expected_output: expectedOutput,
            language,
        });
    }

    /**
     * Get feedback for challenge
     * @param {string} userCode - User's submitted code
     * @param {string} expectedOutput - Expected output
     * @param {string} actualOutput - Actual output from execution
     * @param {string} language - Programming language
     */
    async getFeedback(userCode, expectedOutput, actualOutput, language = 'python') {
        return this.post('/api/ai/feedback', {
            user_code: userCode,
            expected_output: expectedOutput,
            actual_output: actualOutput,
            language,
        });
    }

    /**
     * Explain a programming concept
     * @param {string} concept - Concept to explain (e.g., 'loops', 'variables')
     * @param {object} options - Additional options
     */
    async explainConcept(concept, options = {}) {
        return this.post('/api/ai/concept', {
            concept,
            user_level: options.user_level || 'beginner',
            language: options.language || 'python',
        });
    }
}

// Create singleton instance
const apiService = new APIService();

export default apiService;
