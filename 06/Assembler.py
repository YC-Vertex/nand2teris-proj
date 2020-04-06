aluTransTable = {
    '0'  : '101010',
    '1'  : '111111',
    '-1' : '111010',
    'D'  : '001100',
    'A'  : '110000',
    '!D' : '001101',
    '!A' : '110001',
    '-D' : '001111',
    '-A' : '110011',
    'D+1': '011111',
    'A+1': '110111',
    'D-1': '001110',
    'A-1': '110010',
    'D+A': '000010',
    'A+D': '000010', # duplicate
    'D-A': '010011',
    'A-D': '000111',
    'D&A': '000000',
    'A&D': '000000', #
    'D|A': '010101',
    'A|D': '010101', #
}

transTable = {
    'M'  : '001',
    'D'  : '010',
    'MD' : '011',
    'A'  : '100',
    'AM' : '101',
    'AD' : '110',
    'AMD': '111',

    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

constTable = {
    'R0': '0',
    'R1': '1',
    'R2': '2',
    'R3': '3',
    'R4': '4',
    'R5': '5',
    'R6': '6',
    'R7': '7',
    'R8': '8',
    'R9': '9',
    'R10': '10',
    'R11': '11',
    'R12': '12',
    'R13': '13',
    'R14': '14',
    'R15': '15',
    'SCREEN': '16384',
    'KBD': '24576'
}



def loadFile(path):
    '''
    load a asm file

    Args:
        path (str): path of target file

    Returns:
        file
    '''
    try:
        file = open(path, 'r')
        print('%s is successfully loaded' % path)
        return file
    except IOError:
        print('Failed to load %s' % path)
        return 0

def saveFile(path, macCode):
    '''
    save machine codes to a file

    Args:
        path (str): path of target file
        macCode (list)
    '''
    try:
        file = open(path, 'w')
        for line in macCode:
            file.write(line)
            file.write('\n')
        print('Machine codes are successfully saved to %s' % path)
    except IOError:
        print('Failed to open %s' % path)



def preProcess(instr, noComment = True, noSpace = True):
    '''
    delete comments and spaces from a single line of instruction

    Args:
        instr (str): a line of instruction
        noComment (bool)
        noSpace (bool)

    Returns:
        instr (str): pre-processed instruction
    '''
    # delete comments
    if noComment:
        index = instr.find('//')
        if index != -1:
            instr = instr[:index]
    # delete spaces
    if noSpace:
        instr = ''.join(instr.split())
    return instr 

def sym2numReplace(content, table):
    '''
    replace symbols with their corresponding numbers

    Args:
        content (list): target raw asm code
        table (dict): the correspondance between var names and their values

    Returns:
        content (list): translated asm code
    '''
    newContent = []
    for line in content:
        if line[0] == '@':
            if table.__contains__(line[1:]):
                line = '@' + table[line[1:]]
        newContent.append(line)
    return newContent

def constParse(content):
    '''
    replace const symbols with their corresponding numbers

    Args:
        content (list): target raw asm code

    Returns:
        content (list): translated asm code
    '''
    return sym2numReplace(content, constTable)

def pcVarParse(content):
    '''
    assign every program counter variables with a non-repetitive number, and replace them in the asm code

    Args:
        content (list): 

    Returns:
        content (list)
        pcVarTable (dict): the correspondance between var names and their values
    '''
    pcVarTable = {}
    lineCount = 0;
    for line in content:
        if line[0] == '(' and line[-1] == ')':
            if not pcVarTable.__contains__(line[1:-1]):
                pcVarTable[line[1:-1]] = str(lineCount)
            else:
                print('Error: Bad Syntax: a symbol representing multiple lines')
        else:
            lineCount = lineCount + 1
    for k,v in pcVarTable.items():
        content.pop(int(v))
        
    return sym2numReplace(content, pcVarTable), pcVarTable
    
def memVarParse(content):
    '''
    assign every memory location variables with a non-repetitive number, and replace them in the asm code

    Args:
        content (list): a list of target asm codes

    Returns:
        content (list)
        memVarTable (dict): the correspondance between var names and their nums
    '''
    memVarTable = {}
    val = 16
    for line in content:
        if line[0] == '@' and (not line[1:].isnumeric()):
            if not memVarTable.__contains__(line[1:]):
                memVarTable[line[1:]] = str(val)
                val = val + 1
 
    return sym2numReplace(content, memVarTable), memVarTable



def parse(file):
    '''
    main parsing process

    Args:
        file: input file given by loadFile()

    Returns:
        asmCode (list): a list of strings containing every pre-processed asm instruction lines
    '''
    asmCode = []
    for line in file.readlines():
        # delete comments and spaces
        line = preProcess(line)
        # insert the processed lines into the content list
        if line != '':
            asmCode.append(line)
    asmCode = constParse(asmCode)
    print(asmCode)
    asmCode, pcVarTable = pcVarParse(asmCode)
    print(asmCode)
    print(pcVarTable)
    asmCode, memVarTable = memVarParse(asmCode)
    print(asmCode)
    print(memVarTable)
    return asmCode

def translate(asmCode):
    '''
    main translation process

    Args:
        asmCode (list): a list of strings containing every pre-processed asm instruction lines

    Returns:
        macCode (list): a list of strings containing every translated maching code lines
    '''
    macCode = []
    for instr in asmCode:
        if instr[0] == '@':
            macCode.append('0' + '{:015b}'.format(int(instr[1:])))

        else:
            parts = [instr]
            # decompose by ';'
            if instr.find(';') != -1:
                parts = instr.split(';')
                parts[1] = transTable[parts[1]]
            else:
                parts = [instr, '000']
            # 2 elements in list after parsing ';'

            # decompose by '='
            front = parts.pop(0)
            if front.find('=') != -1:
                parts = front.split('=')[::-1] + parts
                parts[1] = transTable[parts[1]]
            else:
                parts.insert(0, '000')
                parts.insert(0, front)
            # 3 elements in list after parsing '='

            # parse alu instr (parts[0])
            aluInstr = parts.pop(0)
            if aluInstr.find('M') != -1:
                parts.insert(0, '1')
                aluInstr = aluInstr.replace('M', 'A')
            else:
                parts.insert(0, '0')
            parts.insert(1, aluTransTable[aluInstr])
            # 4 elements in list after parsing alu instr
                
            # translate into machine code
            macCode.append('111' + ''.join(parts))
    
    print(macCode)
    return macCode



if __name__ == '__main__':
    file = loadFile('test.asm')
    if file:
        asmCode = parse(file)
        macCode = translate(asmCode)
        file.close()
        saveFile('test.hack', macCode)
