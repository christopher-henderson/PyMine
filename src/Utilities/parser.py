class Parser(object):
    
    @staticmethod
    def _tokenize(command):
        return [token.strip() for token in command.split('>', 1)]

    @staticmethod
    def _getPattern(tokens):
        return Parser._translate(tokens[1]) if len(tokens) > 1 else None

    @staticmethod
    def _translate(pattern):
        return '.*' if pattern == 'all' else pattern

    @staticmethod
    def parse(command):
        tokens = Parser._tokenize(command)
        command = tokens[0]
        pattern = Parser._getPattern(tokens)
        return command,pattern