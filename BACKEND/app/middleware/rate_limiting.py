# Rate Limiting and Security Middleware

from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
try:
    import redis
except ImportError:
    redis = None
import hashlib
import logging

logger = logging.getLogger(__name__)

# Redis client for rate limiting
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=1,  # Use db 1 for rate limiting
        decode_responses=True
    )
except:
    redis_client = None
    logger.warning("Redis not available, rate limiting disabled")

# ==================== RATE LIMITING ====================

class RateLimiter:
    """Rate limiting using token bucket algorithm"""
    
    def __init__(self, requests_per_minute=60, burst_limit=100):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
    
    def is_allowed(self, identifier):
        """Check if request is allowed for given identifier"""
        if not redis_client:
            return True  # Allow if Redis unavailable

        try:
            key = f"rate_limit:{identifier}"
            current_time = datetime.utcnow().timestamp()

            pipe = redis_client.pipeline()
            pipe.get(f"{key}:tokens")
            pipe.get(f"{key}:last_update")
            tokens, last_update = pipe.execute()

            if tokens is None:
                tokens = self.burst_limit
                last_update = current_time
            else:
                tokens = float(tokens)
                last_update = float(last_update)

            time_elapsed = current_time - last_update
            tokens_to_add = time_elapsed * (self.requests_per_minute / 60.0)
            tokens = min(tokens + tokens_to_add, self.burst_limit)

            if tokens >= 1:
                tokens -= 1
                pipe = redis_client.pipeline()
                pipe.set(f"{key}:tokens", tokens, ex=3600)
                pipe.set(f"{key}:last_update", current_time, ex=3600)
                pipe.execute()
                return True

            return False
        except Exception:
            return True  # Allow if Redis operation fails
    
    def get_remaining(self, identifier):
        """Get remaining requests"""
        if not redis_client:
            return self.burst_limit
        try:
            key = f"rate_limit:{identifier}"
            tokens = redis_client.get(f"{key}:tokens")
            return int(float(tokens)) if tokens else self.burst_limit
        except Exception:
            return self.burst_limit

# Rate limiters for different endpoint types
default_limiter = RateLimiter(requests_per_minute=60, burst_limit=100)
code_execution_limiter = RateLimiter(requests_per_minute=10, burst_limit=20)
api_limiter = RateLimiter(requests_per_minute=120, burst_limit=200)

def rate_limit(limiter=default_limiter, identifier_func=None):
    """Decorator for rate limiting endpoints"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Determine identifier (IP or user ID)
            if identifier_func:
                identifier = identifier_func()
            else:
                identifier = request.remote_addr
            
            # Check rate limit
            if not limiter.is_allowed(identifier):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_data, status_code = response
            else:
                response_data = response
                status_code = 200
            
            # Add headers
            headers = {
                'X-RateLimit-Limit': str(limiter.requests_per_minute),
                'X-RateLimit-Remaining': str(limiter.get_remaining(identifier))
            }
            
            if isinstance(response_data, dict):
                return jsonify(response_data), status_code, headers
            return response_data, status_code, headers
        
        return wrapped
    return decorator

# ==================== RESOURCE QUOTA TRACKING ====================

class ResourceQuota:
    """Track and enforce resource quotas per user"""
    
    def __init__(self):
        self.limits = {
            'code_executions_per_day': 100,
            'arena_matches_per_day': 50,
            'api_calls_per_hour': 1000,
            'storage_mb': 100
        }
    
    def check_quota(self, user_id, resource_type):
        """Check if user has quota remaining"""
        if not redis_client:
            return True
        try:
            key = f"quota:{user_id}:{resource_type}"
            today = datetime.utcnow().strftime('%Y-%m-%d')
            full_key = f"{key}:{today}"
            current_usage = redis_client.get(full_key)
            current_usage = int(current_usage) if current_usage else 0
            limit = self.limits.get(resource_type, 1000)
            return current_usage < limit
        except Exception:
            return True
    
    def increment_usage(self, user_id, resource_type, amount=1):
        """Increment resource usage"""
        if not redis_client:
            return
        try:
            key = f"quota:{user_id}:{resource_type}"
            today = datetime.utcnow().strftime('%Y-%m-%d')
            full_key = f"{key}:{today}"
            redis_client.incr(full_key, amount)
            redis_client.expire(full_key, 86400 * 2)
        except Exception:
            pass
    
    def get_usage(self, user_id, resource_type):
        """Get current usage"""
        if not redis_client:
            return 0
        try:
            key = f"quota:{user_id}:{resource_type}"
            today = datetime.utcnow().strftime('%Y-%m-%d')
            full_key = f"{key}:{today}"
            usage = redis_client.get(full_key)
            return int(usage) if usage else 0
        except Exception:
            return 0

resource_quota = ResourceQuota()

def check_quota(resource_type):
    """Decorator to check resource quota"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get user ID from JWT identity (set by @jwt_required)
            try:
                from flask_jwt_extended import get_jwt_identity
                user_id = get_jwt_identity()
            except Exception:
                user_id = None

            if not user_id:
                # Fallback: try request body (legacy, non-JWT routes)
                user_id = request.json.get('user_id') if request.json else None

            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401

            # Check quota
            if not resource_quota.check_quota(user_id, resource_type):
                limit = resource_quota.limits.get(resource_type, 1000)
                return jsonify({
                    'error': 'Resource quota exceeded',
                    'limit': limit,
                    'usage': resource_quota.get_usage(user_id, resource_type)
                }), 429

            # Execute function
            response = f(*args, **kwargs)

            # Increment usage on success
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
            else:
                status_code = 200

            if 200 <= status_code < 300:
                resource_quota.increment_usage(user_id, resource_type)

            return response

        return wrapped
    return decorator

# ==================== ABUSE DETECTION ====================

class AbuseDetector:
    """Detect and prevent abuse patterns"""
    
    def __init__(self):
        self.suspicious_patterns = [
            'drop table',
            'delete from',
            '__import__',
            'eval(',
            'exec(',
            'os.system',
        ]
    
    def check_code(self, code):
        """Check code for suspicious patterns"""
        code_lower = code.lower()
        
        for pattern in self.suspicious_patterns:
            if pattern in code_lower:
                logger.warning(f"Suspicious pattern detected: {pattern}")
                return False, f"Suspicious pattern detected: {pattern}"
        
        # Check code length
        if len(code) > 50000:  # 50KB limit
            return False, "Code exceeds maximum length"
        
        return True, None
    
    def log_suspicious_activity(self, user_id, activity_type, details):
        """Log suspicious activity for review"""
        logger.warning(f"Suspicious activity - User: {user_id}, Type: {activity_type}, Details: {details}")
        
        if redis_client:
            key = f"suspicious:{user_id}:{activity_type}"
            redis_client.incr(key)
            redis_client.expire(key, 86400)  # 24 hours
            
            # Auto-ban if too many suspicious activities
            count = int(redis_client.get(key))
            if count > 10:
                ban_key = f"banned:{user_id}"
                redis_client.set(ban_key, 1, ex=86400)  # Ban for 24 hours
                logger.error(f"User {user_id} auto-banned for suspicious activity")
    
    def is_banned(self, user_id):
        """Check if user is banned"""
        if not redis_client:
            return False
        
        return redis_client.get(f"banned:{user_id}") is not None

abuse_detector = AbuseDetector()
