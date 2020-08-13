class SymbolTable:

    def __init__(self):
        self.cTable = {} # class-level symbol table
        self.sTable = {} # subroutine-level symbol table
    
    def startSubroutine(self):
        self.sTable = {}

    def define(self, name, vtype, kind):
        index = self.varCount(kind)
        # class var dec
        if kind in ('STATIC', 'FIELD'):
            self.cTable[name] = (vtype, kind, index)
        # subroutine var dec
        elif kind in ('ARG', 'VAR'):
            self.sTable[name] = (vtype, kind, index)

    def varCount(self, kind):
        count = 0
        if kind in ('STATIC', 'FIELD'):
            for (k,v) in self.cTable.items():
                if v[1] == kind:
                    count = count + 1
        elif kind in ('ARG', 'VAR'):
            for (k,v) in self.sTable.items():
                if v[1] == kind:
                    count = count + 1
        return count

    def __find(self, name, index):
        get = self.cTable.get(name)
        if get:
            return get[index]
        get = self.sTable.get(name)
        if get:
            return get[index]
        else:
            return 'NONE'

    def kindOf(self, name):
        return self.__find(name, 1)

    def typeOf(self, name):
        return self.__find(name, 0)

    def indexOf(self, name):
        return self.__find(name, 2)

    def printSymbolTable(self):
        print('--- CLASS SYMBOL TABLE ---')
        print(self.cTable)
        print('--- SUBROUTINE SYMBOL TABLE ---')
        print(self.sTable)
        print('\n')
    