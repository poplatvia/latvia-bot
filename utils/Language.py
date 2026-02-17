import re

class Language:
    # Character map for leetspeak or common substitutions
    LEETSPEAK_MAP = {
        'a': '[a@4]',
        'b': '[b8]',
        'c': '[c(<{]',
        'e': '[e3]',
        'g': '[g69]',
        'i': '[i1!|l]',
        'l': '[l1|]',
        'o': '[o0]',
        's': '[s5$]',
        't': '[t7+]',
        'z': '[z2]'
    }

    # Whitelist to prevent Scunthorpe problem (false positives)
    WHITELIST = {
        'snigger', 'raccoon', 'tycoon', 'cocoon', 'buffoon', 'analytics', 'bass', 'class', 'pass'
    }

    def __init__(self):
        self.curse_words = []
        with open("resources/curse_words.txt", "r", encoding="utf-8") as f:
            self.curse_words = [line.strip() for line in f.readlines()]

        self.really_bad_patterns = []
        with open("resources/really_bad_curse_words.txt", "r", encoding="utf-8") as f:
            raw_words = [line.strip() for line in f.readlines()]
            for word in raw_words:
                if not word: continue
                # Generate regex for each word
                pattern_str = self.get_regex_for_word(word)
                self.really_bad_patterns.append(re.compile(pattern_str, re.IGNORECASE))

    def get_regex_for_word(self, word: str) -> str:
        """
        Generates a regex pattern for a given word that allows for:
        - Leetspeak substitutions
        - Separators (dots, spaces, hyphens, etc.) between characters
        """
        pattern = ""
        for i, char in enumerate(word):
            # Get the regex for the character (or the character itself if no map)
            char_pattern = self.LEETSPEAK_MAP.get(char.lower(), re.escape(char))
            pattern += char_pattern
            
            # Allow for separators between characters, but not after the last one
            if i < len(word) - 1:
                # Allow any non-alphanumeric character as a separator, or spaces
                pattern += r'[\W_]*'
        
        return pattern

    def number_of_curse_words(self, text) -> int:
        return sum(text.lower().count(curse_word) for curse_word in self.curse_words)

    def number_of_really_bad_curse_words(self, text) -> int:
        # This count might be less accurate with regex, but we can try to find all matches
        count = 0
        for pattern in self.really_bad_patterns:
            matches = pattern.findall(text)
            for match in matches:
                 if not self.is_whitelisted(match, text):
                    count += 1
        return count

    def contains_curse_words(self, text) -> bool:
        return any(curse_word in text.lower() for curse_word in self.curse_words)

    def contains_really_bad_language(self, text) -> bool:
        for pattern in self.really_bad_patterns:
            # Search for the pattern in the text
            for match in pattern.finditer(text):
                matched_text = match.group()
                if not self.is_whitelisted(matched_text, text):
                    return True
        return False
        
    def is_whitelisted(self, match_text: str, full_text: str) -> bool:
        """
        Checks if the matched text is part of a whitelisted word.
        Current simple approach: check if the match is a substring of any whitelisted word
        and if that whitelisted word appears in the full_text around the match.
        """
        # Clean the match text to remove separators for checking against whitelist
        clean_match = re.sub(r'[\W_]', '', match_text.lower())
        
        # Simple check: if the exact match (cleaned) is in the whitelist, it's okay? 
        # No, 'coon' is in 'raccoon'. We need to check context.
        
        # If we found a match, check if it's surrounded by letters that form a whitelisted word.
        # This is hard with just the match. 
        # Let's try a simpler approach: 
        # 1. If the match IS a whitelisted word (unlikely with slur detection), return True.
        # 2. If the match is inside a word that IS in the whitelist.
        
        # Actually, let's look at the full text. 
        # If we detected "coon" inside "raccoon", we want to ignore it.
        # But we only have the match object in contains_really_bad_language if we pass it, 
        # or just the text.
        
        # Let's check if the match is part of a larger word that is safe.
        # Use word boundaries? No, because "r.a.c.c.o.o.n" might match "coon".
        
        # Heuristic: Check if the match is a substring of a whitelisted word 
        # AND that whitelisted word exists in the text.
        
        lower_text = full_text.lower()
        
        for safe_word in self.WHITELIST:
            if safe_word in lower_text:
                # If the matched text is inside this safe word instance in the text
                # We need to overlap check.
                # This is getting complicated.
                pass
        
        # Let's prioritize the specific failing test case: "raccoon" vs "coon".
        # The regex for "coon" matches the "coon" in "raccoon".
        # We need to verify if the match is preceded or followed by letters.
        
        # Since we are iterating finditer, we have match.start() and match.end().
        # We can check full_text[match.start()-1] and full_text[match.end()].
        
        # However, `contains_really_bad_language` logic needs to be robust. 
        # For now, let's just checking if the match is strictly "inside" a common false positive word 
        # effectively means checking boundaries if the match itself is just a simple string.
        
        # If the match was "c.o.o.n", it likely won't be inside "raccoon" unless it was "r.a.c.c.o.o.n".
        
        # Let's rely on a check: 
        # If the matched pattern has NO special separators (it's just letters),
        # treat it as a potential substring of a valid word.
        
        is_clean_match = match_text.isalpha()
        if is_clean_match:
             # Check if it's part of a whitelist word in the text
             # Get the full word surrounding this match
             # Find the word boundary around the match index
             pass
             
        # Actually, let's simply check if the detected specific "bad word" exists as a substring 
        # of any whitelisted word that is present in the text at that location.
        
        # We need the match object indices to do this properly.
        # I will update the caller to pass the match object if possible, 
        # or just implement the check here with finditer loop in caller.
        
        return False # Placeholder if we don't change signature. 
        # See updated `contains_really_bad_language` below for the actual logic.

    def contains_really_bad_language(self, text) -> bool:
        for pattern in self.really_bad_patterns:
            for match in pattern.finditer(text):
                if not self._is_false_positive(match, text):
                    return True
        return False

    def _is_false_positive(self, match, text) -> bool:
        start, end = match.span()
        
        # 1. Check if it's part of a larger word (surrounded by letters)
        # If the match is just letters (no separators), and it matches a "bad word",
        # but is surrounded by other letters, it might be a Scunthorpe problem.
        # e.g. "ass" in "bass".
        
        # Check character before match
        if start > 0 and text[start-1].isalpha():
            # It's part of a word suffix/middle
            # We should probably allow it IF the whole word is whitelisted.
            # But "pass" is whitelisted. "dumbass" is not.
            # So if it's "ass" in "pass", we ignore. If "ass" in "dumbass", we flag? 
            # The current prompt said "really_bad_curse_words.txt" -- usually slurs.
            # "coon" in "raccoon".
            
            # Simple heuristic: If the match is purely alphabetic, and is surrounded by letters,
            # we check if the *surrounding word* is in the whitelist.
            full_word = self._get_surrounding_word(text, start, end)
            if full_word.lower() in self.WHITELIST:
                return True
            
            # If not in whitelist, but "coon" is in "racoon" (misspelled) or "tycoon".
            # If we strictly whitelist, we are safe.
            
            # What if "racoon" isn't in whitelist? Then we flag it. 
            # That's acceptable for now, we can add to whitelist.
            
            # If "nigger" is inside "snigger", and "snigger" is whitelisted -> return True (ignore).
            
            # So: if surrounded by letters, check the full word against whitelist.
            return False # Flag it if not whitelisted
            
        # Check character after match
        if end < len(text) and text[end].isalpha():
             full_word = self._get_surrounding_word(text, start, end)
             if full_word.lower() in self.WHITELIST:
                 return True
             return False

        return False

    def _get_surrounding_word(self, text, start, end):
        # Expand left
        while start > 0 and text[start-1].isalpha():
            start -= 1
        # Expand right
        while end < len(text) and text[end].isalpha():
            end += 1
        return text[start:end]
