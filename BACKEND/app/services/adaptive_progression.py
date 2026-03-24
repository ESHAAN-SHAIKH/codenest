# Adaptive Progression Logic

from datetime import datetime, timedelta
import random

class AdaptiveProgressionEngine:
    """
    Adaptive learning progression system that adjusts difficulty
    and content based on user performance and cognitive load
    """
    
    def __init__(self):
        self.difficulty_levels = list(range(1, 11))  # 1-10
        self.optimal_success_rate = 0.7  # 70% success is ideal
        self.adjustment_sensitivity = 0.1
    
    def calculate_optimal_difficulty(self, user_history):
        """
        Calculate optimal difficulty level based on user's recent performance
        
        Args:
            user_history: List of recent attempts with success/failure
        
        Returns:
            Recommended difficulty level (1-10)
        """
        if not user_history or len(user_history) < 5:
            return 5  # Default to medium
        
        # Calculate recent success rate
        recent_attempts = user_history[-10:]  # Last 10 attempts
        success_rate = sum(1 for attempt in recent_attempts if attempt['success']) / len(recent_attempts)
        
        # Get average difficulty attempted
        avg_difficulty = sum(attempt['difficulty'] for attempt in recent_attempts) / len(recent_attempts)
        
        # Adjust based on success rate
        if success_rate > 0.85:
            # Too easy, increase difficulty
            recommended = min(avg_difficulty + 1, 10)
        elif success_rate < 0.55:
            # Too hard, decrease difficulty
            recommended = max(avg_difficulty - 1, 1)
        else:
            # Goldilocks zone, maintain
            recommended = avg_difficulty
        
        return round(recommended)
    
    def select_next_concept(self, user_progress, concept_graph):
        """
        Select next concept to study based on:
        - Prerequisite mastery
        - Spaced repetition schedule
        - Knowledge gaps
        - Cognitive load
        
        Args:
            user_progress: Dict of concept_id -> UserConceptProgress
            concept_graph: Dict of concept relationships
        
        Returns:
            Recommended concept_id
        """
        candidates = []
        now = datetime.utcnow()
        
        for concept_id, progress in user_progress.items():
            score = 0
            
            # Priority 1: Concepts due for review (spaced repetition)
            if progress.next_review_date and progress.next_review_date <= now:
                score += 100
            
            # Priority 2: Prerequisites mastered
            prereqs = concept_graph.get(concept_id, {}).get('prerequisites', [])
            prereq_mastery = sum(
                user_progress.get(prereq_id, {}).get('mastery_score', 0)
                for prereq_id in prereqs
            ) / max(len(prereqs), 1)
            
            if prereq_mastery >= 0.7:
                score += 50
            elif prereq_mastery >= 0.5:
                score += 25
            
            # Priority 3: Low mastery (knowledge gaps)
            mastery = progress.mastery_score or 0
            if mastery < 0.5:
                score += 30
            
            # Priority 4: Not studied recently
            if progress.last_practiced:
                days_since = (now - progress.last_practiced).days
                score += min(days_since * 2, 40)
            else:
                score += 40  # Never studied
            
            # Penalty: Recently failed
            if progress.consecutive_failures > 2:
                score -= 20  # Let them recover
            
            candidates.append({
                'concept_id': concept_id,
                'score': score,
                'mastery': mastery
            })
        
        # Sort by score and add some randomness
        candidates.sort(key=lambda x: x['score'] + random.uniform(-10, 10), reverse=True)
        
        return candidates[0]['concept_id'] if candidates else None
    
    def should_inject_remediation(self, concept_progress, misconceptions):
        """
        Determine if remediation content should be injected
        
        Args:
            concept_progress: UserConceptProgress object
            misconceptions: List of recent misconceptions
        
        Returns:
            (should_inject: bool, remediation_type: str)
        """
        # Check for persistent misconceptions
        if len(misconceptions) >= 3:
            recent_types = [m['type'] for m in misconceptions[-5:]]
            most_common = max(set(recent_types), key=recent_types.count)
            
            if recent_types.count(most_common) >= 3:
                return True, most_common
        
        # Check for low mastery with multiple attempts
        if concept_progress.attempt_count >= 5 and concept_progress.mastery_score < 0.5:
            return True, 'fundamental_review'
        
        # Check for consecutive failures
        if concept_progress.consecutive_failures >= 3:
            return True, 'step_by_step_breakdown'
        
        return False, None
    
    def calculate_cognitive_load(self, session_data):
        """
        Calculate current cognitive load based on session data
        
        Args:
            session_data: Recent session activity
        
        Returns:
            Cognitive load score (0.0 - 1.0)
        """
        load_factors = []
        
        # Factor 1: Number of new concepts introduced
        new_concepts = session_data.get('new_concepts_count', 0)
        load_factors.append(min(new_concepts / 5.0, 1.0))
        
        # Factor 2: Difficulty variance
        difficulties = session_data.get('recent_difficulties', [])
        if difficulties:
            variance = sum(abs(d - sum(difficulties) / len(difficulties)) for d in difficulties) / len(difficulties)
            load_factors.append(min(variance / 3.0, 1.0))
        
        # Factor 3: Time pressure (errors made quickly)
        quick_errors = session_data.get('errors_under_60s', 0)
        total_attempts = session_data.get('total_attempts', 1)
        load_factors.append(quick_errors / total_attempts)
        
        # Factor 4: Context switching
        topic_switches = session_data.get('topic_switches', 0)
        load_factors.append(min(topic_switches / 5.0, 1.0))
        
        # Average load
        return sum(load_factors) / len(load_factors) if load_factors else 0.5
    
    def recommend_break(self, cognitive_load, session_duration_minutes):
        """
        Recommend if user should take a break
        
        Args:
            cognitive_load: Current cognitive load (0-1)
            session_duration_minutes: Minutes in current session
        
        Returns:
            (should_break: bool, reason: str)
        """
        # High cognitive load
        if cognitive_load > 0.8:
            return True, "High cognitive load detected. Take a 5-minute break."
        
        # Long session
        if session_duration_minutes > 90:
            return True, "You've been studying for over 90 minutes. Time for a break!"
        
        # Moderate session with high load
        if session_duration_minutes > 45 and cognitive_load > 0.6:
            return True, "Good progress! Take a short break to consolidate learning."
        
        return False, None
    
    def generate_adaptive_hints(self, concept, user_mastery, attempt_count):
        """
        Generate progressive hints based on mastery and attempts
        
        Args:
            concept: Concept being studied
            user_mastery: Current mastery level (0-1)
            attempt_count: Number of attempts on current problem
        
        Returns:
            Hint level and content
        """
        # Adjust hint granularity based on mastery
        if user_mastery < 0.3:
            hint_level = "detailed"  # Step-by-step guidance
        elif user_mastery < 0.7:
            hint_level = "moderate"  # Conceptual hints
        else:
            hint_level = "minimal"  # Subtle nudges
        
        # Increase help with more attempts
        if attempt_count > 3:
            hint_level = "detailed"
        elif attempt_count > 1:
            if hint_level == "minimal":
                hint_level = "moderate"
        
        return {
            'level': hint_level,
            'delay_seconds': 30 * attempt_count,  # Wait longer before each hint
            'should_explain': attempt_count > 4  # Explain solution after 4 attempts
        }
