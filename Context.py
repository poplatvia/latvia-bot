class Context:
    def __init__(self, client, db, craftprobe_db, config, language, ai, csdb):
        self.client = client
        self.db = db
        self.craftprobe_db = craftprobe_db
        self.config = config
        self.language = language
        self.ai = ai
        self.csdb = csdb