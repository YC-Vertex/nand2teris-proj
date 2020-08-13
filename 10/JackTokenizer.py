from functools import reduce

class JackTokenizer:

    __types = ['KEYWORD', 'SYMBOL', 'IDENTIFIER', 'INT_CONST', 'STRING_CONST']
    __tokens = {
        'KEYWORD': ('class', 'constructor', 'function', 'method', 'field', 'static', 'var', \
               'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', \
               'let', 'do', 'if', 'else', 'while', 'return'),
        'SYMBOL': ('{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~')
    }
    typestr = {'KEYWORD': 'keyword', 'SYMBOL': 'symbol', 'IDENTIFIER': 'identifier', 'INT_CONST': 'integerConst', 'STRING_CONST': 'stringConst'}

    def __init__(self, infile):
        self.fin = open(infile, 'r')
        self.curLine = ''
        self.__f2lb()
        self.tokenBuf = []
        self.thisToken = ''

    def __replace(self, s, ori, new):
        ori.insert(0, s)
        return reduce(lambda s,c: s.replace(c, new), ori)

    # file -> line buffer
    def __f2lb(self):
        while True:
            instr = self.fin.readline()
            # EOF
            if instr == '':
                self.nxtLine = ''
                break
            # delete single line comment
            index = instr.find('//')
            self.nxtLine = instr[:index]
            index = instr.find('/*')
            self.nxtLine = self.nxtLine[:index]
            if instr.find('//') == -1 and instr.find('/*') == -1:
                self.nxtLine = instr
            # delete multi line comment
            if instr.find('/*') != -1:
                while instr.find('*/') == -1 and instr != '':
                    instr = self.fin.readline()
                index = instr.find('*/')
                if index != -1:
                    self.nxtLine = self.nxtLine + ' ' + instr[index+2:]
            # if not blank line, success and return
            instr = self.__replace(self.nxtLine, [' ', '\n', '\t'], '')
            if len(instr) != 0:
                break
    
    # line buf -> token buf
    def __lb2tb(self):
        self.curLine = self.nxtLine
        self.__f2lb()

        # make sure at least one complete statement is read into buffer
        while (self.curLine.find(';') == -1 and self.nxtLine != ''):
            self.curLine = self.curLine + self.nxtLine
            self.__f2lb()

        # split the statements by ';'
        temp = self.curLine.split(';')
        if len(temp) > 1:
            self.curLine = temp[0] + ';'
            self.nxtLine = ';'.join(temp[1:]) + self.nxtLine

        # add whitespaces before & after symbols
        for char in self.curLine:
            if self.__tokens['SYMBOL'].count(char) != 0:
                self.curLine = (' ' + char + ' ').join(self.curLine.split(char))
        
        # write curLine into buffer
        self.curLine = self.__replace(self.curLine, ['\n', '\t'], ' ')
        while self.curLine.find('  ') != -1:
            self.curLine = self.__replace(self.curLine, ['  '], ' ')
        self.tokenBuf = self.curLine.split(' ')
        while self.tokenBuf.count(''):
            self.tokenBuf.remove('')

    def hasMoreTokens(self):
        return (len(self.tokenBuf) != 0 or self.nxtLine != '')

    def advance(self):
        # if nothing left in buffer, then read from file
        while (len(self.tokenBuf) == 0 and self.nxtLine != ''):
            self.__lb2tb()
        # get first token in buffer
        self.thisToken = self.tokenBuf.pop(0)
        while self.thisToken[0] == '\"' and self.thisToken[-1] != '\"' and len(self.tokenBuf) != 0:
            self.thisToken = self.thisToken + ' ' + self.tokenBuf.pop(0)

    def tokenType(self):
        if self.__tokens['KEYWORD'].count(self.thisToken) != 0:
            return 'KEYWORD'
        elif self.__tokens['SYMBOL'].count(self.thisToken) != 0:
            return 'SYMBOL'
        elif self.thisToken.isnumeric():
            return 'INT_CONST'
        elif self.thisToken[0] == '\"' and self.thisToken[-1] == '\"':
            return 'STRING_CONST'
        else:
            return 'IDENTIFIER'

    def getToken(self):
        if self.tokenType() == 'STRING_CONST':
            return self.thisToken[1:-1]
        else:
            return self.thisToken
