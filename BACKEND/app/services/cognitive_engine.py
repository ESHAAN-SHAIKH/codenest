"""
Cognitive Engine Service
Core service for concept mastery tracking and adaptive learning
"""

from app.extensions import db
from app.cognitive_models.cognitive import Concept, ConceptMastery, MisconceptionTag
from app.models import User
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CognitiveEngine:
    """Service for managing cognitive modeling and adaptive learning"""
    
    @staticmethod
    def get_or_create_mastery(user_id: int, concept_id: int) -> ConceptMastery:
        """
        Get or create a ConceptMastery record for a user and concept
        
        Args:
            user_id: User ID
            concept_id: Concept ID
            
        Returns:
            ConceptMastery instance
        """
        mastery = ConceptMastery.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        if not mastery:
            mastery = ConceptMastery(
                user_id=user_id,
                concept_id=concept_id
            )
            db.session.add(mastery)
            db.session.commit()
        
        return mastery
    
    @staticmethod
    def update_concept_mastery(
        user_id: int,
        concept_id: int,
        success: bool,
        time_taken: int,
        hints_used: int = 0
    ) -> Dict:
        """
        Update concept mastery based on user performance
        
        Args:
            user_id: User ID
            concept_id: Concept ID
            success: Whether the attempt was successful
            time_taken: Time taken in seconds
            hints_used: Number of hints used
            
        Returns:
            Dictionary with updated mastery information
        """
        mastery = CognitiveEngine.get_or_create_mastery(user_id, concept_id)
        
        old_score = mastery.mastery_score
        mastery.update_mastery(success, time_taken, hints_used)
        
        db.session.commit()
        
        return {
            'concept_id': concept_id,
            'old_mastery': round(old_score, 3),
            'new_mastery': round(mastery.mastery_score, 3),
            'confidence': round(mastery.confidence_score, 3),
            'improvement': round(mastery.mastery_score - old_score, 3),
            'next_review': mastery.spaced_repetition_due_date.isoformat() if mastery.spaced_repetition_due_date else None
        }
    
    @staticmethod
    def get_user_mastery_profile(user_id: int) -> Dict:
        """
        Get comprehensive mastery profile for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with mastery data for all concepts
        """
        mastery_records = ConceptMastery.query.filter_by(user_id=user_id).all()
        
        profile = {
            'total_concepts': len(mastery_records),
            'concepts': [],
            'average_mastery': 0.0,
            'strong_concepts': [],
            'weak_concepts': [],
            'due_for_review': []
        }
        
        if not mastery_records:
            return profile
        
        total_mastery = 0
        for mastery in mastery_records:
            current_mastery = mastery.calculate_decay()
            total_mastery += current_mastery
            
            concept_data = {
                'concept_id': mastery.concept_id,
                'concept_name': mastery.concept.name if mastery.concept else 'Unknown',
                'category': mastery.concept.category if mastery.concept else 'Unknown',
                'mastery_score': round(current_mastery, 3),
                'confidence_score': round(mastery.confidence_score, 3),
                'practice_count': mastery.practice_count,
                'total_attempts': mastery.total_attempts,
                'successful_attempts': mastery.successful_attempts,
                'success_rate': round(mastery.successful_attempts / mastery.total_attempts, 3) if mastery.total_attempts > 0 else 0,
                'due_for_review': mastery.is_due_for_review(),
                'next_review_date': mastery.spaced_repetition_due_date.isoformat() if mastery.spaced_repetition_due_date else None,
            }
            
            profile['concepts'].append(concept_data)
            
            # Categorize concepts
            if current_mastery >= 0.8:
                profile['strong_concepts'].append(concept_data)
            elif current_mastery < 0.5:
                profile['weak_concepts'].append(concept_data)
            
            if mastery.is_due_for_review():
                profile['due_for_review'].append(concept_data)
        
        profile['average_mastery'] = round(total_mastery / len(mastery_records), 3)
        
        # Sort weak concepts by mastery (lowest first)
        profile['weak_concepts'].sort(key=lambda x: x['mastery_score'])
        
        return profile
    
    @staticmethod
    def get_weak_concepts(user_id: int, threshold: float = 0.5) -> List[Dict]:
        """
        Get concepts that need remediation
        
        Args:
            user_id: User ID
            threshold: Mastery threshold below which concepts are considered weak
            
        Returns:
            List of weak concept dictionaries
        """
        mastery_records = ConceptMastery.query.filter_by(user_id=user_id).all()
        
        weak_concepts = []
        for mastery in mastery_records:
            current_mastery = mastery.calculate_decay()
            
            if current_mastery < threshold:
                weak_concepts.append({
                    'concept_id': mastery.concept_id,
                    'concept_name': mastery.concept.name if mastery.concept else 'Unknown',
                    'category': mastery.concept.category if mastery.concept else 'Unknown',
                    'mastery_score': round(current_mastery, 3),
                    'last_practiced': mastery.last_practiced_at.isoformat() if mastery.last_practiced_at else None,
                    'days_since_practice': (datetime.utcnow() - mastery.last_practiced_at).days if mastery.last_practiced_at else None,
                    'practice_count': mastery.practice_count
                })
        
        # Sort by mastery score (lowest first)
        weak_concepts.sort(key=lambda x: x['mastery_score'])
        
        return weak_concepts
    
    @staticmethod
    def get_concepts_due_for_review(user_id: int) -> List[Dict]:
        """
        Get concepts that are due for spaced repetition review
        
        Args:
            user_id: User ID
            
        Returns:
            List of concept dictionaries due for review
        """
        mastery_records = ConceptMastery.query.filter_by(user_id=user_id).all()
        
        due_concepts = []
        for mastery in mastery_records:
            if mastery.is_due_for_review():
                due_concepts.append({
                    'concept_id': mastery.concept_id,
                    'concept_name': mastery.concept.name if mastery.concept else 'Unknown',
                    'category': mastery.concept.category if mastery.concept else 'Unknown',
                    'mastery_score': round(mastery.calculate_decay(), 3),
                    'due_date': mastery.spaced_repetition_due_date.isoformat() if mastery.spaced_repetition_due_date else None,
                    'days_overdue': (datetime.utcnow() - mastery.spaced_repetition_due_date).days if mastery.spaced_repetition_due_date else 0
                })
        
        # Sort by days overdue (most overdue first)
        due_concepts.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return due_concepts
    
    @staticmethod
    def get_adaptive_next_challenge(user_id: int) -> Optional[Dict]:
        """
        Recommend next challenge based on user's mastery profile
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with recommended challenge information
        """
        # Get weak concepts
        weak_concepts = CognitiveEngine.get_weak_concepts(user_id, threshold=0.6)
        
        # Get concepts due for review
        due_concepts = CognitiveEngine.get_concepts_due_for_review(user_id)
        
        # Priority: 1) Due concepts, 2) Weak concepts, 3) New concepts
        target_concept = None
        recommendation_reason = ""
        
        if due_concepts:
            target_concept = due_concepts[0]
            recommendation_reason = "spaced_repetition_due"
        elif weak_concepts:
            target_concept = weak_concepts[0]
            recommendation_reason = "needs_remediation"
        else:
            # Get user's concepts to find what they haven't started
            mastered_concept_ids = [m.concept_id for m in ConceptMastery.query.filter_by(user_id=user_id).all()]
            all_concepts = Concept.query.all()
            
            for concept in all_concepts:
                if concept.id not in mastered_concept_ids:
                    # Check prerequisites
                    if CognitiveEngine._prerequisites_met(user_id, concept):
                        target_concept = {
                            'concept_id': concept.id,
                            'concept_name': concept.name,
                            'category': concept.category,
                            'mastery_score': 0.0
                        }
                        recommendation_reason = "new_concept"
                        break
        
        if not target_concept:
            return None
        
        # TODO: Link to actual challenges - for now return concept info
        return {
            'recommendation_reason': recommendation_reason,
            'concept': target_concept,
            'message': CognitiveEngine._get_recommendation_message(recommendation_reason, target_concept)
        }
    
    @staticmethod
    def _prerequisites_met(user_id: int, concept: Concept) -> bool:
        """Check if all prerequisites for a concept are met"""
        if not concept.prerequisite_concepts:
            return True
        
        for prereq_id in concept.prerequisite_concepts:
            mastery = ConceptMastery.query.filter_by(
                user_id=user_id,
                concept_id=prereq_id
            ).first()
            
            if not mastery or mastery.calculate_decay() < 0.6:
                return False
        
        return True
    
    @staticmethod
    def _get_recommendation_message(reason: str, concept: Dict) -> str:
        """Generate user-friendly recommendation message"""
        messages = {
            'spaced_repetition_due': f"Time to review {concept['concept_name']}! Let's reinforce your understanding.",
            'needs_remediation': f"Let's strengthen your {concept['concept_name']} skills. Practice makes perfect!",
            'new_concept': f"Ready for something new? Let's learn about {concept['concept_name']}!"
        }
        return messages.get(reason, f"Practice {concept['concept_name']}")
    
    @staticmethod
    def detect_knowledge_gaps(user_id: int) -> List[Dict]:
        """
        Identify prerequisite gaps in user's knowledge
        
        Args:
            user_id: User ID
            
        Returns:
            List of concepts with unmet prerequisites
        """
        mastery_records = ConceptMastery.query.filter_by(user_id=user_id).all()
        gaps = []
        
        for mastery in mastery_records:
            if not mastery.concept or not mastery.concept.prerequisite_concepts:
                continue
            
            current_mastery = mastery.calculate_decay()
            
            # If struggling with this concept, check prerequisites
            if current_mastery < 0.5:
                for prereq_id in mastery.concept.prerequisite_concepts:
                    prereq_mastery = ConceptMastery.query.filter_by(
                        user_id=user_id,
                        concept_id=prereq_id
                    ).first()
                    
                    prereq_score = prereq_mastery.calculate_decay() if prereq_mastery else 0.0
                    
                    if prereq_score < 0.7:
                        prereq_concept = Concept.query.get(prereq_id)
                        gaps.append({
                            'concept_id': mastery.concept_id,
                            'concept_name': mastery.concept.name,
                            'mastery_score': round(current_mastery, 3),
                            'prerequisite_id': prereq_id,
                            'prerequisite_name': prereq_concept.name if prereq_concept else 'Unknown',
                            'prerequisite_mastery': round(prereq_score, 3),
                            'gap_severity': round(0.7 - prereq_score, 3)
                        })
        
        # Sort by gap severity (largest first)
        gaps.sort(key=lambda x: x['gap_severity'], reverse=True)
        
        return gaps
    
    @staticmethod
    def update_spaced_repetition_schedule(user_id: int = None):
        """
        Update spaced repetition schedules (can be run as daily cron)
        
        Args:
            user_id: Optional user ID. If None, updates for all users
        """
        if user_id:
            mastery_records = ConceptMastery.query.filter_by(user_id=user_id).all()
        else:
            mastery_records = ConceptMastery.query.all()
        
        updated_count = 0
        for mastery in mastery_records:
            # Recalculate decay and update if needed
            current_mastery = mastery.calculate_decay()
            
            # If significantly decayed, update the stored mastery score
            if abs(current_mastery - mastery.mastery_score) > 0.1:
                mastery.mastery_score = current_mastery
                updated_count += 1
        
        db.session.commit()
        
        logger.info(f"Updated {updated_count} concept mastery records for decay")
        return updated_count
