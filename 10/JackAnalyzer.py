from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

import os

class JackAnalyzer:
    def __init__(self, infile):
        self.infile = infile

    def run(self):
        infile = self.infile
        if infile.find('.jack') != -1:
            outfile = os.path.splitext(infile)[0] + '.xml'
            print()
            print(infile, '->', outfile)
            self.tk = JackTokenizer(infile)
            self.ce = CompilationEngine(outfile)
            try:
                self.ce.compileClass(self.tk, 0)
            except UserWarning:
                print('Syntax Error: \'', self.tk.getToken(), '\' is unexpected')
                print('Source Code:', self.tk.curLine)
        else:
            for root, dirs, files in os.walk(infile):
                for name in files:
                    if name.find('.jack') != -1:
                        inf = os.path.join(root, name)
                        outf = os.path.splitext(inf)[0] + '.xml'
                        print()
                        print(inf, '->', outf)
                        self.tk = JackTokenizer(inf)
                        self.ce = CompilationEngine(outf)
                        try:
                            self.ce.compileClass(self.tk, 0)
                        except UserWarning:
                            print('Syntax Error: \'', self.tk.getToken(), '\' is unexpected')
                            print('Source Code:', self.tk.curLine)

