"""
Animal behavior system using Strategy pattern.

This module implements different animal behaviors as separate strategy classes,
making the code more maintainable and extensible.
"""
from .base import Behavior, BehaviorContext
from .idle import IdleBehavior
from .searching import SearchingBehavior
from .targeting import TargetingBehavior
from .fleeing import FleeingBehavior
from .social import SocialBehavior
from .manager import BehaviorManager

__all__ = [
    'Behavior',
    'BehaviorContext',
    'IdleBehavior',
    'SearchingBehavior',
    'TargetingBehavior',
    'FleeingBehavior',
    'SocialBehavior',
    'BehaviorManager',
]

