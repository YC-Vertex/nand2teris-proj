class CompilationEngine:

    def __init__(self, outfile):
        self.fout = open(outfile, 'w')

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
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()

        while tk.getToken() in ('static', 'field'):
            self.compileClassVarDec(tk, ind + 1)
            tk.advance()
        while tk.getToken() != '}':
            self.compileSubroutineDec(tk, ind + 1)
            tk.advance()
        self.writeToken(tk, ind = 1, tkSpec = '}')

        self.fout.write(ind * '\t' + '</class>\n')
    
    def compileClassVarDec(self, tk, ind):
        # ('static' | 'field') type varName (',' varName)* ';'
        self.fout.write(ind * '\t' + '<classVarDec>\n')

        self.writeToken(tk, ind + 1, tkSpec = ('static', 'field'))
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier')) # type
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
        tk.advance()
        while tk.getToken() == ',':
            self.writeToken(tk, ind + 1, tkSpec = ',')
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
            tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = ';')

        self.fout.write(ind * '\t' + '</classVarDec>\n')
    
    def compileSubroutineDec(self, tk, ind):
        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        # '(' parameterList ')' subroutineBody
        self.fout.write(ind * '\t' + '<subroutineDec>\n')

        self.writeToken(tk, ind + 1, tkSpec = ('constructor', 'function', 'method'))
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier')) # ('void' | type)
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # subroutineName
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileParameterList(tk, ind + 1)
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()
        self.compileSubroutineBody(tk, ind + 1)

        self.fout.write(ind * '\t' + '</subroutineDec>\n')

    # 0 -> +1
    def compileParameterList(self, tk, ind):
        # ((type varName) (',' type varName)*)?
        self.fout.write(ind * '\t' + '<parameterList>\n')
        while tk.getToken() != ')':
            self.writeToken(tk, ind + 1)
            tk.advance()
        self.fout.write(ind * '\t' + '</parameterList>\n')

    def compileSubroutineBody(self, tk, ind):
        # '{' varDec* statements '}'
        self.fout.write(ind * '\t' + '<subroutineBody>\n')

        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()
        while tk.getToken() == 'var':
            self.compileVarDec(tk, ind + 1)
            tk.advance()
        
        self.compileStatements(tk, ind + 1)
        self.writeToken(tk, ind + 1, tkSpec = '}')

        self.fout.write(ind * '\t' + '</subroutineBody>\n')

    def compileVarDec(self, tk, ind):
        # 'var' type varName (',' varName)* ';'
        self.fout.write(ind * '\t' + '<varDec>\n')

        self.writeToken(tk, ind + 1, tkSpec = 'var')
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = ('keyword', 'identifier')) # type
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
        tk.advance()
        while tk.getToken() == ',':
            self.writeToken(tk, ind + 1, tkSpec = ',')
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
            tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = ';')

        self.fout.write(ind * '\t' + '</varDec>\n')



    # STATEMENTS

    # 0 -> +1
    def compileStatements(self, tk, ind):
        # statement*
        self.fout.write(ind * '\t' + '<statements>\n')
        while tk.getToken() != '}':
            advFlag = (tk.getToken() != 'if')
            switch = {'let': self.compileLet, 'if': self.compileIf, \
                'while': self.compileWhile, 'do': self.compileDo, 'return': self.compileReturn}
            switch.get(tk.getToken(), self.raiseSyntaxError)(tk, ind + 1)
            if advFlag:
                tk.advance()
        self.fout.write(ind * '\t' + '</statements>\n')
    
    def compileLet(self, tk, ind):
        # 'let' varName '=' expression ';'
        self.fout.write(ind * '\t' + '<letStatement>\n')
        self.writeToken(tk, ind + 1, tkSpec = 'let')
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier') # varName
        tk.advance()
        if tk.getToken() == '[':
            self.writeToken(tk, ind + 1, tkSpec = '[')
            tk.advance()
            self.compileExpression(tk, ind + 1)
            self.writeToken(tk, ind + 1, tkSpec = ']')
            tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '=')
        tk.advance()
        self.compileExpression(tk, ind + 1) # expression
        self.writeToken(tk, ind + 1, tkSpec = ';')
        self.fout.write(ind * '\t' + '</letStatement>\n')
    
    # 0 -> +1
    def compileIf(self, tk, ind):
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.fout.write(ind * '\t' + '<ifStatement>\n')
        self.writeToken(tk, ind + 1, tkSpec = 'if')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileExpression(tk, ind + 1) # expression
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '{')
        tk.advance()
        self.compileStatements(tk, ind + 1) # statements
        self.writeToken(tk, ind + 1, tkSpec = '}')
        tk.advance()
        if tk.getToken() == 'else':
            self.writeToken(tk, ind + 1, tkSpec = 'else')
            tk.advance()
            self.writeToken(tk, ind + 1, tkSpec = '{')
            tk.advance()
            self.compileStatements(tk, ind + 1) # statements
            self.writeToken(tk, ind + 1, tkSpec = '}')
            tk.advance()
        self.fout.write(ind * '\t' + '</ifStatement>\n')
    
    def compileWhile(self, tk, ind):
        # 'while' '(' expression ')' '{' statements '}'
        self.fout.write(ind * '\t' + '<whileStatement>\n')
        self.writeToken(tk, ind + 1, tkSpec = 'while')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileExpression(tk, ind + 1) # expression
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()
        self.writeToken(tk, ind + 1) # '{'
        tk.advance()
        self.compileStatements(tk, ind + 1) # statements
        self.writeToken(tk, ind + 1, tkSpec = '}')
        self.fout.write(ind * '\t' + '</whileStatement>\n')
    
    def compileDo(self, tk, ind):
        self.fout.write(ind * '\t' + '<doStatement>\n')

        self.writeToken(tk, ind + 1, tkSpec = 'do')
        tk.advance()
        self.writeToken(tk, ind + 1, tkType = 'identifier')
        tk.advance()
        if tk.getToken() == '.':
            self.writeToken(tk, ind + 1, tkSpec = '.')
            tk.advance()
            self.writeToken(tk, ind + 1, tkType = 'identifier') # subroutineName
            tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = '(')
        tk.advance()
        self.compileExpressionList(tk, ind + 1) # expressionList
        self.writeToken(tk, ind + 1, tkSpec = ')')
        tk.advance()
        self.writeToken(tk, ind + 1, tkSpec = ';')

        self.fout.write(ind * '\t' + '</doStatement>\n')

    def compileReturn(self, tk, ind):
        self.fout.write(ind * '\t' + '<returnStatement>\n')
        self.writeToken(tk, ind + 1)
        tk.advance()
        if tk.getToken() == ';':
            self.writeToken(tk, ind + 1, tkSpec = ';')
        else:
            self.compileExpression(tk, ind + 1)
            self.writeToken(tk, ind + 1, tkSpec = ';')
        self.fout.write(ind * '\t' + '</returnStatement>\n')



    # EXPRESSIONS

    # 0 -> +1
    def compileExpression(self, tk, ind):
        self.fout.write(ind * '\t' + '<expression>\n')
        self.compileTerm(tk, ind + 1)
        while tk.getToken() in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            self.writeToken(tk, ind + 1, tkType = 'symbol')
            tk.advance()
            self.compileTerm(tk, ind + 1)
        self.fout.write(ind * '\t' + '</expression>\n')
    
    # 0 -> +1
    def compileTerm(self, tk, ind):
        self.fout.write(ind * '\t' + '<term>\n')
        
        if tk.tokenType() == 'IDENTIFIER':
            self.writeToken(tk, ind + 1)
            tk.advance()

            if tk.getToken() == '.':
                self.writeToken(tk, ind + 1, tkSpec = '.')
                tk.advance()
                self.writeToken(tk, ind + 1, tkType = 'identifier') # subroutineName
                tk.advance()
                self.writeToken(tk, ind + 1, tkSpec = '(')
                tk.advance()
                self.compileExpressionList(tk, ind + 1) # expressionList
                self.writeToken(tk, ind + 1, tkSpec = ')')
                tk.advance()
            
            elif tk.getToken() == '(':
                self.writeToken(tk, ind + 1, tkSpec = '(')
                tk.advance()
                self.compileExpressionList(tk, ind + 1) # expressionList
                self.writeToken(tk, ind + 1, tkSpec = ')')
                tk.advance()
            
            elif tk.getToken() == '[':
                self.writeToken(tk, ind + 1, tkSpec = '[')
                tk.advance()
                self.compileExpression(tk, ind + 1) # expression
                self.writeToken(tk, ind + 1, tkSpec = ']')
                tk.advance()
        
        elif tk.getToken() in ('-', '~'):
            self.writeToken(tk, ind + 1)
            tk.advance()
            self.compileTerm(tk, ind + 1)

        elif tk.getToken() == '(':
            self.writeToken(tk, ind + 1)
            tk.advance()
            self.compileExpression(tk, ind + 1)
            self.writeToken(tk, ind + 1)
            tk.advance()

        else:
            self.writeToken(tk, ind + 1)
            tk.advance()

        self.fout.write(ind * '\t' + '</term>\n')
    
    # 0 -> +1
    def compileExpressionList(self, tk, ind):
        # (expression (',' expression)*)?
        self.fout.write(ind * '\t' + '<expressionList>\n')
        if tk.getToken() != ')':
            self.compileExpression(tk, ind + 1)
            while tk.getToken() == ',':
                self.writeToken(tk, ind + 1, tkSpec = ',')
                tk.advance()
                self.compileExpression(tk, ind + 1) # expression
        self.fout.write(ind * '\t' + '</expressionList>\n')