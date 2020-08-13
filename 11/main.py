from JackCompiler import JackCompiler
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

infile = 'Main.jack'
outfile = 'out'

def tokenizerTest():
    tk = JackTokenizer(infile)
    fout = open(outfile, 'w')
    while tk.hasMoreTokens():
        tk.advance()
        typestr = tk.typestr[tk.tokenType()]
        fout.write('<' + typestr + '> ')
        fout.write(tk.getToken())
        fout.write(' </' + typestr + '>\n')
    fout.close()

def analyzerTest():
    tk = JackTokenizer(infile)
    ce = CompilationEngine(outfile)
    ce.compileClass(tk, 0)

if __name__ == '__main__':
    # tokenizerTest()
    # analyzerTest()
    jc = JackCompiler('E:/Tsinghua/0_Material/19-20Spr/nand2tetris/projects/11/Square')
    jc.run()
    