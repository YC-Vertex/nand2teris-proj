from SymbolTable import SymbolTable
from VMWriter import VMWriter

import os

class CompilationEngine:

    __segDict = {'static': 'STATIC', 'field': 'FIELD', 'var': 'VAR'}

    def __init__(self, outfile):
        self.fout = open(os.path.splitext(outfile)[0] + '.xml', 'w')
        self.st = SymbolTable()
        self.vmw = VMWriter(outfile)

    def writeToken(self, tk, ind, tkSpec = None, tkType = None):
        typestr = tk.typestr[tk.tokenType()]
        if (tkSpec == None or (tk.getToken() in tkSpec)) and (tkType == None or (typestr in tkType)):
            self.fout.write(ind * '\t')
            self.fout.write('<' + typestr + '> ')
            self.fout.write(tk.getToken())
            self.fout.write(' </' + typestr + '>\n')
        else:
            self.raiseSyntaxError()

    def raiseSyntaxError(self, *trash, err = UserWarning):
        raise err

    


    # PROGRAM STRUCTURE

    def compileClass(self, tk, ind):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.fout.write(ind * '\t' + '<class>\n')

        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = 'class')
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # className
        self.className = tk.getToken()
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()

        while tk.getToken() in ('static', 'field'):
            self.compileClassVarDec(tk, ind + 1)
        while tk.getToken() != '}':
            self.compileSubroutineDec(tk, ind + 1)
        self.writeToken(tk, ind = 1, tkSpec = '}')

        self.fout.write(ind * '\t' + '</class>\n')
    
    def compileClassVarDec(self, tk, ind):
        # ('static' | 'field') type varName (',' varName)* ';'
        self.fout.write(ind * '\t' + '<classVarDec>\n')

        self.writeToken(tk, ind + 1, tkSpec = ('static', 'field'))
        kind = tk.getToken()
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier')) # type
        vtype = tk.getToken()
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
        name = tk.getToken()
        tk.advance()

        self.st.define(name, vtype, self.__segDict[kind])

        while tk.getToken() == ',':
            self.writeToken(tk, ind + 1, tkSpec = ',')
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
            name = tk.getToken()
            tk.advance()

            self.st.define(name, vtype, self.__segDict[kind])

        self.writeToken(tk, ind + 1, tkSpec = ';')
        tk.advance()

        self.fout.write(ind * '\t' + '</classVarDec>\n')
    
    def compileSubroutineDec(self, tk, ind):
        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        # '(' parameterList ')' subroutineBody
        self.fout.write(ind * '\t' + '<subroutineDec>\n')

        self.st.startSubroutine()
        if tk.getToken() == 'method':
            self.st.define('this', self.className, 'ARG')
        self.ifCount = 0
        self.whileCount = 0

        self.writeToken(tk, ind + 1, tkSpec = ('constructor', 'function', 'method'))
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier')) # ('void' | type)
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # subroutineName
        self.subroutineName = tk.getToken()
        tk.advance()

        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileParameterList(tk, ind + 1)
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()
        self.compileSubroutineBody(tk, ind + 1)

        self.fout.write(ind * '\t' + '</subroutineDec>\n')

    def compileParameterList(self, tk, ind):
        # ((type varName) (',' type varName)*)?
        self.fout.write(ind * '\t' + '<parameterList>\n')
        
        if tk.getToken() != ')':
            self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier'))
            vtype = tk.getToken()
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier')
            name = tk.getToken()
            tk.advance()

            self.st.define(name, vtype, 'ARG')

            while tk.getToken() == ',':
                self.writeToken(tk, ind + 1, tkSpec = ',')
                tk.advance()
                self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier'))
                vtype = tk.getToken()
                tk.advance()
                self.writeToken(tk, ind + 1, tkType = 'identifier')
                name = tk.getToken()
                tk.advance()

                self.st.define(name, vtype, 'ARG')

        self.fout.write(ind * '\t' + '</parameterList>\n')

    def compileSubroutineBody(self, tk, ind):
        # '{' varDec* statements '}'
        self.fout.write(ind * '\t' + '<subroutineBody>\n')

        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()
        while tk.getToken() == 'var':
            self.compileVarDec(tk, ind + 1)

        self.st.printSymbolTable()
        self.vmw.writeFunction(self.className + '.' + self.subroutineName, self.st.varCount('VAR'))

        self.compileStatements(tk, ind + 1)
        self.writeToken(tk, ind + 1, tkSpec = '}')
        tk.advance()

        self.fout.write(ind * '\t' + '</subroutineBody>\n')

    def compileVarDec(self, tk, ind):
        # 'var' type varName (',' varName)* ';'
        self.fout.write(ind * '\t' + '<varDec>\n')

        self.writeToken(tk, ind + 1, tkSpec = 'var')
        kind = tk.getToken()
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier')) # type
        vtype = tk.getToken()
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
        name = tk.getToken()
        tk.advance()

        self.st.define(name, vtype, self.__segDict[kind])

        while tk.getToken() == ',':
            self.writeToken(tk, ind + 1, tkSpec = ',')
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
            name = tk.getToken()
            tk.advance()

            self.st.define(name, vtype, self.__segDict[kind])

        self.writeToken(tk, ind + 1, tkSpec = ';')
        tk.advance()

        self.fout.write(ind * '\t' + '</varDec>\n')



    # STATEMENTS

    def compileStatements(self, tk, ind):
        # statement*
        self.fout.write(ind * '\t' + '<statements>\n')
        while tk.getToken() != '}':
            switch = {'let': self.compileLet, 'if': self.compileIf, \
                'while': self.compileWhile, 'do': self.compileDo, 'return': self.compileReturn}
            switch.get(tk.getToken(), self.raiseSyntaxError)(tk, ind + 1)
        self.fout.write(ind * '\t' + '</statements>\n')
    
    def compileLet(self, tk, ind):
        # 'let' varName '=' expression ';'
        self.fout.write(ind * '\t' + '<letStatement>\n')

        self.writeToken(tk, ind + 1, tkSpec = 'let')
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
        name = tk.getToken()
        tk.advance()

        array = False
        if tk.getToken() == '[':
            array = True
            self.writeToken(tk, ind + 1, tkSpec = '[')
            tk.advance()
            self.compileExpression(tk, ind + 1)
            self.writeToken(tk, ind + 1, tkSpec = ']')
            tk.advance()

            self.vmw.writePush(self.st.kindOf(name), self.st.indexOf(name))
            self.vmw.writeArithmetic('add')

        self.writeToken(tk, ind + 1, tkSpec = '=')
        tk.advance()
        self.compileExpression(tk, ind + 1) # expression
        self.writeToken(tk, ind + 1, tkSpec = ';')
        tk.advance()

        if array:
            self.vmw.writePop('TEMP', 0)
            self.vmw.writePop('POINTER', 1)
            self.vmw.writePush('TEMP', 0)
            self.vmw.writePop('THAT', 0)
        else:
            self.vmw.writePop(self.st.kindOf(name), self.st.indexOf(name))

        self.fout.write(ind * '\t' + '</letStatement>\n')
    
    def compileIf(self, tk, ind):
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.fout.write(ind * '\t' + '<ifStatement>\n')

        thisif = self.ifCount
        self.ifCount = self.ifCount + 1

        self.writeToken(tk, ind + 1, tkSpec = 'if')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileExpression(tk, ind + 1) # expression
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()

        self.vmw.writeIf('IF_' + str(thisif))
        self.vmw.writeGoto('ELSE_' + str(thisif))
        self.vmw.writeLabel('IF_' + str(thisif))

        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()
        self.compileStatements(tk, ind + 1) # statements
        self.writeToken(tk, ind + 1, tkSpec = '}')
        tk.advance()

        self.vmw.writeGoto('IFEND_' + str(thisif))
        self.vmw.writeLabel('ELSE_' + str(thisif))
        if tk.getToken() == 'else':
            self.writeToken(tk, ind + 1, tkSpec = 'else')
            tk.advance()
            self.writeToken(tk, ind + 1, tkSpec = '{')
            tk.advance()
            self.compileStatements(tk, ind + 1) # statements
            self.writeToken(tk, ind + 1, tkSpec = '}')
            tk.advance()
        self.vmw.writeLabel('IFEND_' + str(thisif))

        self.fout.write(ind * '\t' + '</ifStatement>\n')
    
    def compileWhile(self, tk, ind):
        # 'while' '(' expression ')' '{' statements '}'
        self.fout.write(ind * '\t' + '<whileStatement>\n')

        thiswhile = self.whileCount
        self.whileCount = self.whileCount + 1

        self.vmw.writeLabel('WHILE_' + str(thiswhile))
        self.writeToken(tk, ind + 1, tkSpec = 'while')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileExpression(tk, ind + 1) # expression
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()

        self.vmw.writeIf('WHILEBODY_' + str(thiswhile))
        self.vmw.writeGoto('WHILEEND_' + str(thiswhile))

        self.vmw.writeLabel('WHILEBODY_' + str(thiswhile))
        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()
        self.compileStatements(tk, ind + 1) # statements
        self.writeToken(tk, ind + 1, tkSpec = '}')
        tk.advance()
        self.vmw.writeGoto('WHILE_' + str(thiswhile))

        self.vmw.writeLabel('WHILEEND_' + str(thiswhile))

        self.fout.write(ind * '\t' + '</whileStatement>\n')
    
    def compileDo(self, tk, ind):
        self.fout.write(ind * '\t' + '<doStatement>\n')

        self.writeToken(tk, ind + 1, tkSpec = 'do')
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier')
        idtf = tk.getToken()
        tk.advance()
        if tk.getToken() == '.':
            self.writeToken(tk, ind + 1, tkSpec = '.')
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier') # subroutineName
            idtf = idtf + '.' + tk.getToken()
            tk.advance()

        flag = self.vmw.writePush(self.st.kindOf(idtf.split('.')[0]), self.st.indexOf(idtf.split('.')[0]))
        if flag:
            self.argCount = self.argCount + 1

        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileExpressionList(tk, ind + 1) # expressionList
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = ';')
        tk.advance()

        self.vmw.writeCall(idtf, self.argCount)
        self.vmw.writePop('TEMP', 0)

        self.fout.write(ind * '\t' + '</doStatement>\n')

    def compileReturn(self, tk, ind):
        self.fout.write(ind * '\t' + '<returnStatement>\n')

        self.writeToken(tk, ind + 1)
        tk.advance()
        if tk.getToken() == ';':
            self.writeToken(tk, ind + 1, tkSpec = ';')
            self.vmw.writePush('CONST', 0)
        else:
            self.compileExpression(tk, ind + 1)
            self.writeToken(tk, ind + 1, tkSpec = ';')
        tk.advance()
        self.vmw.writeReturn()

        self.fout.write(ind * '\t' + '</returnStatement>\n')



    # EXPRESSIONS

    def compileExpression(self, tk, ind):
        self.fout.write(ind * '\t' + '<expression>\n')

        self.compileTerm(tk, ind + 1)
        while tk.getToken() in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            self.writeToken(tk, ind + 1, tkType = 'symbol')
            op = tk.getToken()
            tk.advance()
            self.compileTerm(tk, ind + 1)

            if op == '+':
                self.vmw.writeArithmetic('add')
            elif op == '-':
                self.vmw.writeArithmetic('sub')
            elif op == '*':
                self.vmw.writeCall('Math.multiply', 2)
            elif op == '/':
                self.vmw.writeCall('Math.divide', 2)
            elif op == '&':
                self.vmw.writeArithmetic('and')
            elif op == '|':
                self.vmw.writeArithmetic('or')
            elif op == '<':
                self.vmw.writeArithmetic('lt')
            elif op == '>':
                self.vmw.writeArithmetic('gt')
            elif op == '=':
                self.vmw.writeArithmetic('eq')

        self.fout.write(ind * '\t' + '</expression>\n')
    
    def compileTerm(self, tk, ind):
        self.fout.write(ind * '\t' + '<term>\n')
        
        if tk.tokenType() == 'IDENTIFIER':
            self.writeToken(tk, ind + 1)
            idtf = tk.getToken()
            tk.advance()

            if tk.getToken() == '.':
                self.writeToken(tk, ind + 1, tkSpec = '.')
                tk.advance()
                self.writeToken(tk, ind + 1, tkType = 'identifier') # subroutineName
                idtf = idtf + '.' + tk.getToken()
                tk.advance()

                flag = self.vmw.writePush(self.st.kindOf(idtf.split('.')[0]), self.st.indexOf(idtf.split('.')[0]))
                if flag:
                    self.argCount = self.argCount + 1

                self.writeToken(tk, ind + 1, tkSpec = '(')
                tk.advance()
                self.compileExpressionList(tk, ind + 1) # expressionList
                self.writeToken(tk, ind + 1, tkSpec = ')')
                tk.advance()

                self.vmw.writeCall(idtf, self.argCount)
            
            elif tk.getToken() == '(':
                self.writeToken(tk, ind + 1, tkSpec = '(')
                tk.advance()
                self.compileExpressionList(tk, ind + 1) # expressionList
                self.writeToken(tk, ind + 1, tkSpec = ')')
                tk.advance()
                self.vmw.writeCall(idtf, self.argCount)
            
            elif tk.getToken() == '[':
                self.writeToken(tk, ind + 1, tkSpec = '[')
                tk.advance()
                self.compileExpression(tk, ind + 1) # expression
                self.writeToken(tk, ind + 1, tkSpec = ']')
                tk.advance()
                self.vmw.writePush(self.st.kindOf(idtf), self.st.indexOf(idtf))
                self.vmw.writeArithmetic('add')
                self.vmw.writePop('POINTER', 1)
                self.vmw.writePush('THAT', 0)

            else:
                self.vmw.writePush(self.st.kindOf(idtf), self.st.indexOf(idtf))
        
        elif tk.getToken() in ('-', '~'):
            self.writeToken(tk, ind + 1)
            op = tk.getToken()
            tk.advance()
            self.compileTerm(tk, ind + 1)
            if op == '-':
                self.vmw.writeArithmetic('neg')
            elif op == '~':
                self.vmw.writeArithmetic('not')

        elif tk.getToken() == '(':
            self.writeToken(tk, ind + 1, tkSpec = '(')
            tk.advance()
            self.compileExpression(tk, ind + 1)
            self.writeToken(tk, ind + 1, tkSpec = ')')
            tk.advance()

        else:
            self.writeToken(tk, ind + 1)
            val = tk.getToken()
            if val.isnumeric():
                self.vmw.writePush('CONST', int(tk.getToken()))
            elif val == 'true':
                self.vmw.writePush('CONST', 0)
                self.vmw.writeArithmetic('not')
            elif val == 'false':
                self.vmw.writePush('CONST', 0)
            elif val == 'this':
                self.vmw.writePush('POINTER', 0)
            elif val == 'null':
                self.vmw.writePush('CONST', 0)
            elif tk.tokenType() == 'STRING_CONST':
                self.vmw.writePush('CONST', len(val))
                self.vmw.writeCall('String.new', 1)
                strList = list(val)
                while len(strList) > 0:
                    self.vmw.writePush('CONST', ord(strList.pop(0)))
                    self.vmw.writeCall('String.appendChar', 2)
            tk.advance()

        self.fout.write(ind * '\t' + '</term>\n')
    
    def compileExpressionList(self, tk, ind):
        # (expression (',' expression)*)?
        self.fout.write(ind * '\t' + '<expressionList>\n')

        self.argCount = 0
        if tk.getToken() != ')':
            self.compileExpression(tk, ind + 1)
            self.argCount = self.argCount + 1
            while tk.getToken() == ',':
                self.writeToken(tk, ind + 1, tkSpec = ',')
                tk.advance()
                self.compileExpression(tk, ind + 1) # expression
                self.argCount = self.argCount + 1

        self.fout.write(ind * '\t' + '</expressionList>\n')