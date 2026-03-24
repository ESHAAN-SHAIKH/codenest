"""
Archetype Engine Service
Manages skill-based identity progression across 5 archetypes
"""

from app.extensions import db
from app.cognitive_models.progression import ArchetypeProgress
from app.models import User
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ArchetypeEngine:
    """Service for managing identity-based progression"""
    
    # Archetype definitions
    ARCHETYPES = {
        'architect': {
            'name': 'Architect',
            'description': 'Masters of system design and code organization',
            'icon': '🏗️',
            'metrics': ['system_design_quality', 'code_organization_score', 'abstraction_usage']
        },
        'debugger': {
            'name': 'Debugger',
            'description': 'Expert bug hunters with keen analytical skills',
            'icon': '🔍',
            'metrics': ['bug_identification_speed', 'explanation_quality', 'debug_success_rate']
        },
        'optimizer': {
            'name': 'Optimizer',
            'description': 'Performance specialists who make code faster',
            'icon': '⚡',
            'metrics': ['performance_improvements', 'complexity_reductions', 'avg_optimization_impact']
        },
        'refactorer': {
            'name': 'Refactorer',
            'description': 'Code quality advocates who improve readability',
            'icon': '✨',
            'metrics': ['code_quality_improvements', 'readability_score', 'refactor_frequency']
        },
        'guardian': {
            'name': 'Guardian',
            'description': 'Security-focused engineers who prevent bugs',
            'icon': '🛡️',
            'metrics': ['security_awareness_score', 'edge_case_coverage', 'error_handling_quality']
        }
    }
    
    @staticmethod
    def initialize_archetypes(user_id: int):
        """
        Initialize all archetype progress records for a user
        
        Args:
            user_id: User ID
        """
        for archetype_type in ArchetypeEngine.ARCHETYPES.keys():
            existing = ArchetypeProgress.query.filter_by(
                user_id=user_id,
                archetype_type=archetype_type
            ).first()
            
            if not existing:
                progress = ArchetypeProgress(
                    user_id=user_id,
                    archetype_type=archetype_type,
                    behavior_metrics={}
                )
                db.session.add(progress)
        
        db.session.commit()
    
    @staticmethod
    def track_behavior(user_id: int, archetype_type: str, behavior_data: Dict):
        """
        Track user behavior for archetype progression
        
        Args:
            user_id: User ID
            archetype_type: Type of archetype
            behavior_data: Dictionary with behavior metrics
        """
        progress = ArchetypeProgress.query.filter_by(
            user_id=user_id,
            archetype_type=archetype_type
        ).first()
        
        if not progress:
            progress = ArchetypeProgress(
                user_id=user_id,
                archetype_type=archetype_type,
                behavior_metrics={}
            )
            db.session.add(progress)
        
        # Update metrics
        progress.update_metrics(behavior_data)
        
        # Award XP based on behavior quality
        xp_earned = ArchetypeEngine._calculate_xp(archetype_type, behavior_data)
        rank_info = progress.add_experience(xp_earned)
        
        db.session.commit()
        
        return {
            'archetype': archetype_type,
            'xp_earned': xp_earned,
            'rank_info': rank_info,
            'updated_metrics': progress.behavior_metrics
        }
    
    @staticmethod
    def _calculate_xp(archetype_type: str, behavior_data: Dict) -> int:
        """Calculate XP earned from behavior"""
        base_xp = 10
        
        # Different XP calculations per archetype
        if archetype_type == 'architect':
            quality = behavior_data.get('code_organization_score', 0)
            return int(base_xp * (1 + quality))
        
        elif archetype_type == 'debugger':
            success = behavior_data.get('debug_success_rate', 0)
            speed_bonus = 1.5 if behavior_data.get('bug_identification_speed', 0) > 0.7 else 1.0
            return int(base_xp * success * speed_bonus)
        
        elif archetype_type == 'optimizer':
            improvements = behavior_data.get('performance_improvements', 0)
            return base_xp + (improvements * 5)
        
        elif archetype_type == 'refactorer':
            quality_delta = behavior_data.get('quality_improvement_delta', 0)
            return int(base_xp * (1 + quality_delta * 2))
        
        elif archetype_type == 'guardian':
            edge_cases = behavior_data.get('edge_case_coverage', 0)
            return int(base_xp * (1 + edge_cases))
        
        return base_xp
    
    @staticmethod
    def get_user_archetype_profile(user_id: int) -> Dict:
        """
        Get complete archetype profile for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with all archetype progress
        """
        archetypes = ArchetypeProgress.query.filter_by(user_id=user_id).all()
        
        if not archetypes:
            # Initialize if needed
            ArchetypeEngine.initialize_archetypes(user_id)
            archetypes = ArchetypeProgress.query.filter_by(user_id=user_id).all()
        
        profile = {
            'archetypes': [],
            'dominant_archetype': None,
            'total_xp': 0,
            'average_rank': 0
        }
        
        max_xp = 0
        total_ranks = 0
        
        for arch_progress in archetypes:
            arch_data = arch_progress.to_dict()
            arch_info = ArchetypeEngine.ARCHETYPES.get(arch_progress.archetype_type, {})
            
            arch_data['name'] = arch_info.get('name', arch_progress.archetype_type)
            arch_data['description'] = arch_info.get('description', '')
            arch_data['icon'] = arch_info.get('icon', '⭐')
            
            profile['archetypes'].append(arch_data)
            profile['total_xp'] += arch_progress.experience_points
            total_ranks += arch_progress.rank_level
            
            if arch_progress.experience_points > max_xp:
                max_xp = arch_progress.experience_points
                profile['dominant_archetype'] = arch_data
        
        if archetypes:
            profile['average_rank'] = round(total_ranks / len(archetypes), 1)
        
        # Sort by XP descending
        profile['archetypes'].sort(key=lambda x: x['experience_points'], reverse=True)
        
        return profile
    
    @staticmethod
    def get_archetype_leaderboard(archetype_type: str, limit: int = 10) -> List[Dict]:
        """
        Get top users for a specific archetype
        
        Args:
            archetype_type: Archetype type
            limit: Number of top users to return
            
        Returns:
            List of user rankings
        """
        top_users = db.session.query(
            ArchetypeProgress, User
        ).join(
            User, ArchetypeProgress.user_id == User.id
        ).filter(
            ArchetypeProgress.archetype_type == archetype_type
        ).order_by(
            ArchetypeProgress.experience_points.desc()
        ).limit(limit).all()
        
        leaderboard = []
        for rank, (progress, user) in enumerate(top_users, 1):
            leaderboard.append({
                'rank': rank,
                'username': user.username,
                'user_id': user.user_id,
                'archetype_level': progress.rank_level,
                'experience_points': progress.experience_points,
                'behavior_metrics': progress.behavior_metrics
            })
        
        return leaderboard
    
    @staticmethod
    def get_evolution_path(user_id: int, archetype_type: str) -> Dict:
        """
        Get full evolution path for a specific archetype.

        Returns:
            {archetype_type, current_rank, current_xp,
             all_ranks: [{rank, rank_name, xp_needed, completed, current}],
             next_rank: {rank, rank_name, xp_needed} | None,
             progress_to_next: float}
        """
        progress = ArchetypeProgress.query.filter_by(
            user_id=user_id,
            archetype_type=archetype_type
        ).first()

        # Auto-initialise if missing so first load never errors
        if not progress:
            ArchetypeEngine.initialize_archetypes(user_id)
            progress = ArchetypeProgress.query.filter_by(
                user_id=user_id,
                archetype_type=archetype_type
            ).first()

        if not progress:
            return {'error': 'Archetype not found'}

        rank_names = [
            '', 'Novice', 'Apprentice', 'Practitioner', 'Adept', 'Expert',
            'Master', 'Grandmaster', 'Legend', 'Mythic', 'Transcendent'
        ]

        current_rank = progress.rank_level
        current_xp = progress.experience_points

        # Full ladder of all 10 ranks
        all_ranks = []
        for rank in range(1, 11):
            threshold = ArchetypeProgress.RANK_THRESHOLDS.get(rank, 0)
            all_ranks.append({
                'rank': rank,
                'rank_name': rank_names[rank],
                'xp_needed': threshold,
                'completed': rank < current_rank,
                'current': rank == current_rank,
            })

        # Next rank info (None at max rank)
        next_rank = None
        if current_rank < 10:
            next_rank_num = current_rank + 1
            next_rank = {
                'rank': next_rank_num,
                'rank_name': rank_names[next_rank_num],
                'xp_needed': ArchetypeProgress.RANK_THRESHOLDS.get(next_rank_num, 0),
            }

        return {
            'archetype_type': archetype_type,
            'current_rank': current_rank,
            'current_xp': current_xp,
            'all_ranks': all_ranks,
            'next_rank': next_rank,
            'progress_to_next': progress.get_progress_to_next_rank(),
        }
