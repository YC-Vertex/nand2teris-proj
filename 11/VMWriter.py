class VMWriter:
    __segDict = {'CONST': 'constant', 'ARG': 'argument', 'VAR': 'local', 'STATIC': 'static', \
        'FIELD': 'this', 'THAT': 'that', 'POINTER': 'pointer', 'TEMP': 'temp'}

    def __init__(self, outfile):
        self.fout = open(outfile, 'w')

    def writePush(self, segment, index):
        if self.__segDict.get(segment):
            self.fout.write('push ' + self.__segDict[segment] + ' ' + str(index) + '\n')
            return True
        return False

    def writePop(self, segment, index):
        if self.__segDict.get(segment):
            self.fout.write('pop ' + self.__segDict[segment] + ' ' + str(index) + '\n')
            return True
        return False

    def writeArithmetic(self, command):
        self.fout.write(command + '\n')

    def writeLabel(self, label):
        self.fout.write('label ' + label + '\n')

    def writeGoto(self, label):
        self.fout.write('goto ' + label + '\n')

    def writeIf(self, label):
        self.fout.write('if-goto ' + label + '\n')

    def writeCall(self, name, nArgs):
        self.fout.write('call ' + name + ' ' + str(nArgs) + '\n')

    def writeFunction(self, name, nLocals):
        self.fout.write('function ' + name + ' ' + str(nLocals) + '\n')

    def writeReturn(self):
        self.fout.write('return\n')

    def close(self):
        self.fout.close()