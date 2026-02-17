class Language:
    def __init__(self):
        self.curse_words = []
        with open("resources/curse_words.txt", "r", encoding="utf-8") as f:
            self.curse_words = [line.strip() for line in f.readlines()]

        self.really_bad_curse_words = []
        with open("resources/really_bad_curse_words.txt", "r", encoding="utf-8") as f:
            self.really_bad_curse_words = [line.strip() for line in f.readlines()]

    def number_of_curse_words(self, text) -> int:
        return sum(text.lower().count(curse_word) for curse_word in self.curse_words)

    def number_of_really_bad_curse_words(self, text) -> int:
        return sum(text.lower().count(curse_word) for curse_word in self.really_bad_curse_words)

    def contains_curse_words(self, text) -> bool:
        return any(curse_word in text.lower() for curse_word in self.curse_words)

    def contains_really_bad_language(self, text) -> bool:
        return any(curse_word in text.lower() for curse_word in self.really_bad_curse_words)
