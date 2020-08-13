commandTypeTable = {
    'add':      'C_ARITHMETIC',
    'sub':      'C_ARITHMETIC',
    'neg':      'C_ARITHMETIC',
    'and':      'C_ARITHMETIC',
    'or':       'C_ARITHMETIC',
    'not':      'C_ARITHMETIC',
    'push':     'C_PUSH',
    'pop':      'C_POP',
    'label':    'C_LABEL',
    'if-goto':  'C_IF',
    'goto':     'C_GOTO',
    'call':     'C_CALL',
    'function': 'C_FUNCTION',
    'return':   'C_RETURN'
}

JUMPFLAG = 0
RETURNFLAG = 0



def openFile(path, iotype):
    try:
        file = open(path, iotype)
        print('%s is successfully loaded' % path)
        return file
    except IOError:
        print('Failed to load %s' % path)
        return 0



class Parser:
    def __init__(self, filepath):
        self.filePath = filepath
        self.file = openFile(filepath, 'r')
        self.curLine = ''
        self.__preProcess()
    
    def hasMoreCommands(self):
        return (self.nxtLine != '')

    def advance(self):
        self.curLine = self.nxtLine
        self.curSplit = self.curLine.split()
        self.__preProcess()

    def __preProcess(self):
        while True:
            instr = self.file.readline()
            if instr == '':
                self.nxtLine = ''
                break
            index = instr.find('//')
            self.nxtLine = instr[:index]
            if instr != '\n' and index != 0:
                break

    def commandType(self):
        return commandTypeTable[self.curSplit[0]]

    def arg1(self):
        if self.commandType() == 'C_ARITHMETIC':
            return self.curSplit[0]
        else:
            return self.curSplit[1]

    def arg2(self):
        return int(self.curSplit[2])
        
    def closeFile(self):
        self.file.close()



class CodeWriter:
    def __init__(self, filepath):
        self.filePath = filepath
        self.fileName = ((filepath.split('/')[-1]).split('\\')[-1]).split('.')[0]
        self.file = openFile(filepath, 'w')

    def writeArithmetic(self, command):
        def vadd():
            return ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=D+M']
        def vsub():
            return ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M-D']
        def vneg():
            return ['@SP', 'AM=M-1', 'M=-M', '@SP', 'M=M+1']
        def vand():
            return ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=D&M']
        def vor():
            return ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=D|M']
        def vnot():
            return ['@SP', 'AM=M-1', 'M=!M', '@SP', 'M=M+1']
        def veq():
            global JUMPFLAG
            JUMPFLAG += 1
            return ['@SP', 'AM=M-1', 'D=M', '@SP', 'AM=M-1', 'D=M-D', \
                '@TRUE' + str(JUMPFLAG), 'D;JEQ', 'D=0', '@FALSE' + str(JUMPFLAG), '0;JMP', \
                '(TRUE' + str(JUMPFLAG) + ')', 'D=-1', '(FALSE' + str(JUMPFLAG) + ')', \
                '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def vgt():
            global JUMPFLAG
            JUMPFLAG += 1
            return ['@SP', 'AM=M-1', 'D=M', '@SP', 'AM=M-1', 'D=M-D', \
                '@TRUE' + str(JUMPFLAG), 'D;JGT', 'D=0', '@FALSE' + str(JUMPFLAG), '0;JMP', \
                '(TRUE' + str(JUMPFLAG) + ')', 'D=-1', '(FALSE' + str(JUMPFLAG) + ')', \
                '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def vlt():
            global JUMPFLAG
            JUMPFLAG += 1
            return ['@SP', 'AM=M-1', 'D=M', '@SP', 'AM=M-1', 'D=M-D', \
                '@TRUE' + str(JUMPFLAG), 'D;JLT', 'D=0', '@FALSE' + str(JUMPFLAG), '0;JMP', \
                '(TRUE' + str(JUMPFLAG) + ')', 'D=-1', '(FALSE' + str(JUMPFLAG) + ')', \
                '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        
        switch = {
            'add': vadd, 'sub': vsub, 'neg': vneg,
            'and': vand, 'or':  vor,  'not': vnot,
            'eq':  veq,  'gt':  vgt,  'lt':  vlt
        }
        lines = switch.get(command)()
        lines.insert(0, '// ' + command)

        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')

    def writePushPop(self, command, segment, index):
        def pushLCL():
            return ['@LCL', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushARG():
            return ['@ARG', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushTHIS():
            return ['@THIS', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushTHAT():
            return ['@THAT', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushCONST():
            return ['@' + str(index), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushSTT():
            return ['@' + self.fileName + '.' + str(index), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushTMP():
            return ['@' + str(5+index), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        def pushPTR():
            if index == 0:
                return ['@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
            else:
                return ['@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

        def popLCL():
            return ['@LCL', 'D=M', '@' + str(index), 'D=D+A', '@temp', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@temp', 'A=M', 'M=D', '@temp', 'M=0']
        def popARG():
            return ['@ARG', 'D=M', '@' + str(index), 'D=D+A', '@temp', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@temp', 'A=M', 'M=D', '@temp', 'M=0']
        def popTHIS():
            return ['@THIS', 'D=M', '@' + str(index), 'D=D+A', '@temp', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@temp', 'A=M', 'M=D', '@temp', 'M=0']
        def popTHAT():
            return ['@THAT', 'D=M', '@' + str(index), 'D=D+A', '@temp', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@temp', 'A=M', 'M=D', '@temp', 'M=0']
        def popSTT():
            return ['@SP', 'M=M-1', 'A=M', 'D=M', '@' + self.fileName + '.' + str(index), 'M=D']
        def popTMP():
            return ['@SP', 'M=M-1', 'A=M', 'D=M', '@' + str(5+index), 'M=D']
        def popPTR():
            if index == 0:
                return ['@SP', 'M=M-1', 'A=M', 'D=M', '@THIS', 'M=D']
            else:
                return ['@SP', 'M=M-1', 'A=M', 'D=M', '@THAT', 'M=D']

        def default():
            return []

        # C_PUSH
        if command == 'C_PUSH':
            switch = {
                'local': pushLCL, 'argument': pushARG, 'this': pushTHIS, 'that': pushTHAT,
                'constant': pushCONST, 'static': pushSTT, 'temp': pushTMP, 'pointer': pushPTR
            }
            lines = switch.get(segment, default)()
            lines.insert(0, '// push ' + segment + ' ' + str(index))

        # C_POP
        else:
            switch = {
                'local': popLCL, 'argument': popARG, 'this': popTHIS, 'that': popTHAT,
                'static': popSTT, 'temp': popTMP, 'pointer': popPTR
            }
            lines = switch.get(segment, default)()
            lines.insert(0, '// pop ' + segment + ' ' + str(index))

        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')
        
    def writeLabel(self, label):
        self.file.write('(' + label + ')\n')
        
    def writeIf(self, label):
        lines = ['@SP', 'M=M-1', 'A=M', 'D=M', '@' + label, 'D;JNE']
        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')
        
    def writeGoto(self, label):
        lines = ['@SP', 'A=M-1', 'D=M', '@' + label, 'D;JMP']
        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')
        
    def writeFunction(self, functionName, numlocals):
        lines = ['(' + functionName + ')', '@LCL', 'D=M', '@SP', 'M=D']
        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')
        
        for i in range(0, int(numlocals)):  
            lines = ['@SP', 'A=M', 'M=0', 'D=A+1', '@SP', 'M=D']
            for line in lines:
                self.file.write(line + '\n')
            self.file.write('\n')
            
    def writeReturn(self):
        lines = ['@LCL', 'D=M', '@R13', 'M=D', \
            '@5', 'A=D-A', 'D=M', '@R14', 'M=D', \
            '@SP', 'M=M-1', 'A=M', 'D=M', '@ARG', 'A=M', 'M=D', \
            '@ARG', 'D=M+1', '@SP', 'M=D', \
            '@R13', 'A=M-1', 'D=M', '@THAT', 'M=D', \
            '@13', 'D=M', '@2', 'A=D-A', 'D=M', '@THIS', 'M=D', \
            '@13', 'D=M', '@3', 'A=D-A', 'D=M', '@ARG', 'M=D', \
            '@13', 'D=M', '@4', 'A=D-A', 'D=M', '@LCL', 'M=D', \
            '@14', 'A=M', '0;JMP']
        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')
            
    def writeCall(self, functionName, numArgs):  
        global RETURNFLAG
        lines = ['@return_address' + str(RETURNFLAG), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', \
            '@LCL', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', \
            '@ARG', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', \
            '@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', \
            '@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', \
            '@' + str(numArgs), 'D=A', '@5', 'D=D+A', '@SP', 'D=M-D', '@ARG', 'M=D', '@SP', 'D=M', '@LCL', 'M=D', \
            '@' + functionName, '0;JMP', '(return_address' + str(RETURNFLAG) + ')']
        for line in lines:
            self.file.write(line + '\n')
        self.file.write('\n')
        RETURNFLAG += 1 
        
    def closeFile(self):
        self.file.close()
        
        

if __name__ == '__main__':
    infilePath = input('Input file: ')
    outfilePath = input('Output file: ')

    p = Parser(infilePath)
    c = CodeWriter(outfilePath)
    
    while p.hasMoreCommands():
        p.advance()
        ct = p.commandType()
        if ct == 'C_ARITHMETIC':
            c.writeArithmetic(p.arg1())
        elif ct == 'C_PUSH' or ct == 'C_POP':
            c.writePushPop(ct, p.arg1(), p.arg2())
        elif ct == 'C_ARITHMETIC':
            c.writeArithmetic(p.arg1())
        elif ct == 'C_IF':
            c.writeIf(p.arg1())
        elif ct == 'C_LABEL':
            c.writeLabel(p.arg1())
        elif ct == 'C_GOTO':
            c.writeGoto(p.arg1())
        elif ct == 'C_CALL':
            c.writeCall(p.arg1(), p.arg2())
        elif ct == 'C_FUNCTION':
            c.writeFunction(p.arg1(), p.arg2())
        elif ct == 'C_RETURN':
            c.writeReturn()
            
    p.closeFile()
    c.closeFile()
