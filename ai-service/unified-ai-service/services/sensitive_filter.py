import re
from typing import List, Tuple
import logging

from core.constants import SENSITIVE_WORDS, SENSITIVE_WORD_REPLACEMENT

logger = logging.getLogger(__name__)


class SensitiveWordFilter:
    def __init__(self):
        self.sensitive_words = set(SENSITIVE_WORDS)
        self.pattern = self._build_pattern()
    
    def _build_pattern(self) -> re.Pattern:
        escaped_words = [re.escape(word) for word in self.sensitive_words]
        pattern = '|'.join(escaped_words)
        return re.compile(pattern, re.IGNORECASE)
    
    def filter(self, text: str) -> Tuple[str, List[str]]:
        if not text:
            return text, []
        
        found_words = []
        
        def replace_match(match):
            word = match.group()
            found_words.append(word)
            return SENSITIVE_WORD_REPLACEMENT
        
        filtered_text = self.pattern.sub(replace_match, text)
        
        if found_words:
            logger.warning(f"检测到敏感词: {found_words}")
        
        return filtered_text, found_words
    
    def contains_sensitive(self, text: str) -> bool:
        if not text:
            return False
        return bool(self.pattern.search(text))
    
    def check_user_input(self, text: str) -> Tuple[bool, str, List[str]]:
        filtered_text, found_words = self.filter(text)
        
        has_sensitive = len(found_words) > 0
        
        if has_sensitive:
            message = f"您的输入包含不当内容，已自动过滤。请文明交流。"
        else:
            message = ""
        
        return has_sensitive, message, found_words
    
    def add_word(self, word: str):
        self.sensitive_words.add(word)
        self.pattern = self._build_pattern()
    
    def remove_word(self, word: str):
        self.sensitive_words.discard(word)
        self.pattern = self._build_pattern()


sensitive_filter = SensitiveWordFilter()
