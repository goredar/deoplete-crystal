import json
import os
from subprocess import PIPE, Popen

from deoplete.util import getlines

from .base import Base


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'deocrystal'
        self.filetypes = ['crystal']
        self.mark = '[CR]'
        self.min_pattern_length = 1
        self.port = "1234"
        self.lib = self.vim.vars['deoplete#sources#crystal#lib']
        self.cracker = self.vim.vars['deoplete#sources#crystal#bin']

    def on_init(self, _context):
        if os.system(f"ss -tln 'src :{self.port}' | grep {self.port} -q"):
            os.system(
                f'sh -c "set -m; nohup {self.cracker} server '
                f'-p {self.port} {self.lib} >/dev/null 2>&1 &"'
            )

    def get_complete_position(self, context):
        pos = context['input'].rfind('.')
        return pos if pos < 0 else pos + 1

    def gather_candidates(self, context):
        cmd = [self.cracker, 'client', '-p', self.port, '--context']

        # Get lines before the current one
        buf = '\n'.join(getlines(self.vim, 1, context['position'][1]))

        try:
            process = Popen(cmd, stdout=PIPE, stdin=PIPE)
            res = process.communicate(input=str.encode(buf))[0]

            results = json.loads(res)['results']

            suggestions = []

            for result in results:
                word = result['name']
                if word.find("#") != -1:
                    word = word.split("#")[1]
                else:
                    word = word.split(".")[1]

                suggestions.append({
                    'abbr': word,
                    'word': word.split("(")[0]
                })

        except BaseException:
            suggestions = []

        return suggestions
