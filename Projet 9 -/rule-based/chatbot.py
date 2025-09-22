import re
import json

class RuleBasedChatbot:
    def __init__(self, rules_file):
        with open(rules_file, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)['intents']
    
    def find_best_match(self, user_input):
        user_input = user_input.lower()
        for intent in self.rules:
            for pattern in intent['patterns']:
                if re.search(r'\b' + re.escape(pattern) + r'\b', user_input):
                    return intent['response']
        return "Je ne peux pas répondre à cette question. Voulez-vous que je cherche dans la documentation officielle ?"

    def get_response(self, user_input):
        return self.find_best_match(user_input)