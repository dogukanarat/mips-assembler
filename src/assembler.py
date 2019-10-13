import time
import numpy as np


class Assembler:
    '''
    Definition: Assembler object takes a text file that includes MIPS instructions and
    turn it into machine code and save it as a file

    Usage: Object = Assembler(file=FILE_SOURCE, target=FILE_TARGET)
    '''

    def __init__(self, **kwargs):
        self.cpuMemorySize = None
        file = None
        self.machineCodeFile = None
        for key, value in kwargs.items():
            if key == 'file':
                file = value
            elif key == 'target':
                self.machineCodeFile = value

        filecontent = ['contentarray']
        with open(file, 'r') as file:
            for line in file:
                filecontent.append(line.split())
            filecontent.pop(0)

        self.content = filecontent
        self.machineCode = None
        self.commentSeen = False
        self.cpuVariables = {
            "$t0": "00000",
            "$t1": "00001",
            "$t2": "00010",
            "$t3": "00011",
            "$t4": "00100",
            "$t5": "00101",
            "$t6": "00110",
            "$t7": "00111",
            "$s0": "00000",
            "$s1": "00001",
            "$s2": "00010",
            "$s3": "00011",
            "$s4": "00100",
            "$s5": "00101",
            "$s6": "00110",
            "$s7": "00111"
        }

    def getISA(self, *line):
        '''
        getISA function keeps all of MIPS instruction and returns given line as machine code
        '''
        try:
            instructions = {
                "add": "000000{}{}{}00000100000".format(line[2], line[3], line[1]),
                "addu": "000000{}{}{}00000100001".format(line[2], line[3], line[1]),
                "and": "000000{}{}{}00000100100".format(line[2], line[3], line[1]),
                "mfhi": "0000000000000000{}00000010000".format(line[1]),
                "mflo": "0000000000000000{}00000010010".format(line[1]),
                "mult": "000000{}{}0000000000011000".format(line[1], line[2]),
                "multu": "000000{}{}0000000000011001".format(line[1], line[2]),
                "noop": "00000000000000000000000000000000",
                "or": "000000{}{}{}00000100101".format(line[2], line[3], line[1]),
                "slt": "000000{}{}{}00000101010".format(line[2], line[3], line[1]),
                "sltu": "000000{}{}{}00000101011".format(line[2], line[3], line[1]),
                "srlv": "000000{}{}{}00000000110".format(line[2], line[3], line[1]),
                "sub": "000000{}{}{}00000100010".format(line[2], line[3], line[1]),
                "subu": "000000{}{}{}00000100011".format(line[2], line[3], line[1]),
                "sw": "101011{}{}{}".format(line[2][1], line[1], line[2][0]),
                "lw": "100011{}{}{}".format(line[2][1], line[1], line[2][0])
            }
            return instructions.get(line[0])
        except:
            pass

    def clearCommas(self, line):
        '''
        clearCommas function clears the commas in the given line
        '''
        resultantLine = ["First"]
        for token in line:
            self.commentSeen = True if token == "#" else self.commentSeen
            if not self.commentSeen:
                resultantLine.append(token.replace(',', ''))
        resultantLine.pop(0)
        self.commentSeen = False
        return resultantLine

    def placeVariables(self, line):
        '''
        placeVariables function convert the tokens in the given line into CPU varialbe
        if it is a CPU variable. Otherwise, turns the original value
        '''
        return list(map(lambda element: self.cpuVariables.get(element) if self.cpuVariables.get(element) != None else element, line))

    def convertOffset(self, token):
        '''
        convertOffset function convert the tokens into array while placing its memory address
        and decimal offset number to binary number
        '''
        tempToken = token.replace('(', ' ').replace(')', '')

        if tempToken == token:
            return token
        else:
            tempToken = list(tempToken.split())
            newToken = []
            newToken.insert(0, np.binary_repr(int(tempToken[0]), width=16))
            newToken.insert(1, self.cpuVariables.get(tempToken[1]))
            return newToken

    def placeOffsets(self, line):
        '''
        placeOffsets function pass tokens of the lines trough convertOffset function
        '''
        return list(map(lambda element: self.convertOffset(element), line))

    def fillInTheBlanks(self, line):
        '''
        fillInTheBlanks function fill the lines with 'None' item to keep regularity 
        '''
        newLine = line.copy()
        size = len(line)
        if size <= 4:
            for _ in range(4 - size):
                newLine.append('None')
        return newLine

    def convertLine(self, line):
        '''
        convertLine function pass lines through getISA function
        '''
        return self.getISA(*line)

    def convertFile(self):
        '''
        convertFile function converts all file, saves and returns it
        '''
        for line in self.content:
            self.machineCode = self.machineCode + self.convertLine(line)
        return self.machineCode

    def prepare(self):
        '''
        Definition: Prepare function transforms the given file into meaningful data
        saving it into array while passing it through inherit functions \n
        Usage: Object.prepare()
        '''
        self.content = list(
            map(lambda line: self.clearCommas(line), self.content))
        self.content = list(
            map(lambda line: self.placeVariables(line), self.content))
        self.content = list(
            map(lambda line: self.placeOffsets(line), self.content))
        self.content = list(
            map(lambda line: self.fillInTheBlanks(line), self.content))

    def preview(self, **kwargs):
        '''
        Definition: Preview function monitors required steps of process on terminal \n
        Usage: Object.preview(line = ["all", lineNumber], detailed = [True, False])
        '''
        for key, value in kwargs.items():
            if key == "detailed" and value == True:
                for lineIndex, line in enumerate(self.content):
                    print(lineIndex, line)
            elif key == "line" and value == "all":
                for lineIndex, line in enumerate(self.content):
                    print(lineIndex, self.convertLine(line))
            elif key == "line" and value != "all":
                print(self.convertLine(self.content[value]))

    def execute(self):
        '''
        Definition: Execute function execute all needed process and save the machine code file
        into given target file \n
        Usage: Object.execute()
        '''
        with open(self.machineCodeFile, "w+") as file:
            for lineIndex, line in enumerate(self.content):
                file.write(str(lineIndex) + " " +
                           str(self.convertLine(line)) + "\n")


def main():
    assembler = Assembler(file='./assemblycode.txt',
                          target='./machinecode.txt')
    assembler.prepare()
    assembler.preview(line="all", detailed=False)
    assembler.execute()


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
