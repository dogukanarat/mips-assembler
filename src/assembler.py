import time
import numpy as np
import os


class Assembler:
    '''
    Definition: Assembler object takes a text file that includes MIPS instructions and
    turn it into machine code and save it as a file

    Usage: Object = Assembler(file=FILE_SOURCE, target=FILE_TARGET)
    '''

    def __init__(self, **kwargs):

        # defult values of object
        self.checkPrepare = False
        self.cpuMemorySize = None
        self.cpuMemoryLocation = 0
        self.targetDirectory = None
        self.sourceDirectory = None
        self.content = None
        self.contentLabels = ["None"]
        self.machineCode = None
        self.machineCodeHex = None
        self.commentSeen = False
        self.previewDetailed = False
        self.previewLine = "All"
        self.checkSingleLineCommand = False
        self.checkConvertContent = False
        self.executeFormatHex = True
        self.executeFormatLineIndex = False

        for key, value in kwargs.items():
            if key == 'source':
                self.sourceDirectory = value
            elif key == 'target':
                self.targetDirectory = value

        self.cpuVariables = {
            "$zero": "00000",
            "$at": "00001",
            "$t0": "01000",
            "$t1": "01001",
            "$t2": "01010",
            "$t3": "01011",
            "$t4": "01100",
            "$t5": "01101",
            "$t6": "01110",
            "$t7": "01111",
            "$s0": "10000",
            "$s1": "10001",
            "$s2": "10010",
            "$s3": "10011",
            "$s4": "10100",
            "$s5": "10101",
            "$s6": "10110",
            "$s7": "10111"
        }

    def checkFiles(self):

        if self.checkSingleLineCommand:
            return True

        try:
            file = open(self.sourceDirectory)
            file.close()
            return True

        except:
            return False

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
                "lw": "100011{}{}{}".format(line[2][1], line[1], line[2][0]),
                "beq": "0000000000000000{}".format(self.convertLabel(line, 'I'))
            }
            return instructions[line[0]]
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

    def takeLabels(self):
        for lineIndex, line in enumerate(self.content):
            if line[0].find(":") != -1:
                self.contentLabels.append(
                    [lineIndex, line[0].replace(":", "")])
                line.pop(0)
                if len(line) < 1:
                    self.content.pop(lineIndex)
            else:
                pass

        if len(self.contentLabels) != 1:
            self.contentLabels.pop(0)

    def convertLabel(self, line, type):

        lineIndex = np.binary_repr(
            int(self.content.index(list(line))), width=16)

        if type == 'I':
            return lineIndex
            # return '1111111111111111'
        elif type == 'J':
            return '11111111111111111111111111'
        else:
            return '0'

    def convertLineToBinary(self, line):
        '''
        convertLineToBinary function pass lines through getISA function

        Returns String
        '''
        return self.getISA(*line)

    def convertLineToHex(self, line):
        '''
        convertLineToHex function pass lines through getISA function

        Returns String
        '''

        try:
            hexValue = np.base_repr(int(self.getISA(*line), 2), base=16)
            hexValue = np.base_repr(
                int(self.getISA(*line), 2), base=16, padding=(8-len(hexValue)))
            return hexValue
        except:
            print(line)
            return '1'

    def convertContent(self):
        '''
        convertContent function converts all content, saves it

        Returns Boolean
        '''
        if self.checkPrepare:

            if not self.checkConvertContent:

                self.machineCode = ["FirstElement"]
                self.machineCodeHex = ["FirstElement"]
                for line in self.content:
                    self.machineCode.append(self.convertLineToBinary(line))
                    self.machineCodeHex.append(self.convertLineToHex(line))
                self.machineCode.pop(0)
                self.machineCodeHex.pop(0)
            else:
                pass

            self.checkConvertContent = True
            return True
        else:
            return False

    def prepare(self):
        '''
        Definition: Prepare function transforms the given file into meaningful data
        saving it into array while passing it through inherit functions \n
        Usage: Object.prepare()

        Returns Boolean
        '''
        if self.checkFiles():

            # reading the source file
            if not self.checkSingleLineCommand:
                fileContent = ['contentarray']
                with open(self.sourceDirectory, 'r') as file:
                    for line in file:
                        fileContent.append(line.split())
                    fileContent.pop(0)
                self.content = fileContent

            # taking program memory location from the file if exist
            if self.content[0][0].find('0x') != -1:
                self.cpuMemoryLocation = self.content[0][0]
                self.content.pop(0)

            self.takeLabels()

            # preparing content for execution
            self.content = list(
                map(lambda line: self.clearCommas(line), self.content))
            self.content = list(
                map(lambda line: self.placeVariables(line), self.content))
            self.content = list(
                map(lambda line: self.placeOffsets(line), self.content))
            self.content = list(
                map(lambda line: self.fillInTheBlanks(line), self.content))

            self.checkPrepare = True
            return True
        else:
            self.checkPrepare = False
            return False

    def preview(self, **kwargs):
        '''
        Definition: Preview function monitors required steps of process on terminal \n
        Usage: Object.preview(
            line = ["all", lineNumber], detailed = [True, False])
        '''
        if(self.checkPrepare):

            self.convertContent()

            for key, value in kwargs.items():
                if key == "detailed":
                    self.previewDetailed = value
                if key == "line":
                    self.previewLine = value

            print("Memory Location: ", self.cpuMemoryLocation)
            if self.previewDetailed:
                for lineIndex, line in enumerate(self.content):
                    print(lineIndex, line)

            elif self.previewLine == "all":
                for lineIndex, line in enumerate(self.content):
                    print(lineIndex, self.convertLineToBinary(line))

            elif isinstance(self.previewLine, int):
                print(self.convertLineToBinary(self.content[self.previewLine]))

            else:
                pass

            for lineIndex, line in enumerate(self.machineCodeHex):
                print(lineIndex, line)

            return True
        else:
            return False

    def execute(self):
        '''
        Definition: Execute function execute all needed process and save the machine code file
        into given target file \n
        Usage: Object.execute()
        '''
        if(self.checkPrepare):

            self.convertContent()

            with open(self.targetDirectory, "w+") as file:
                executeContent = self.machineCodeHex if self.executeFormatHex else self.machineCode
                for lineIndex, line in enumerate(executeContent):
                    if self.executeFormatLineIndex:
                        file.write(str(lineIndex) + " " + line + "\n")
                    else:
                        file.write(line + "\n")

            return True
        else:
            return False


def main():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    print("MIPS Assembler. Version is 1.0. It was developed by DFA")

    assembler = Assembler()

    while True:

        command = input(">> ")
        singleLineCommand = []
        singleLineCommand.insert(0, list(command.split()))
        command = list(command.split())

        if command[0] == "debugmode":
            assembler.sourceDirectory = BASE_DIR + '/' + "code.txt"
            assembler.targetDirectory = BASE_DIR + '/' + "result.txt"
            assembler.prepare()
            assembler.execute()
            assembler.preview(detailed=True)
            exit()

        elif command[0] == "source":
            assembler.sourceDirectory = BASE_DIR + '/' + command[1]

        elif command[0] == "target":
            assembler.targetDirectory = BASE_DIR + '/' + command[1]

        elif command[0] == "execute":
            if assembler.execute():
                print("Executing process is done!")
            else:
                print('First, you need to use "prepare" command!')

        elif command[0] == "prepare":
            if assembler.prepare():
                print("Preparing process is done!")
            else:
                print("There is a problem with files!")

        elif command[0] == "preview":
            if assembler.preview(detailed=False):
                pass
            else:
                print('First, you need to use "prepare" command!')

        elif command[0] == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')

        elif command[0] == "exit":
            exit()

        else:
            temp = Assembler()
            temp.checkSingleLineCommand = True
            temp.content = singleLineCommand
            temp.prepare()

            tempMachineCode = temp.convertLineToHex(temp.content[0])

            if tempMachineCode:
                print(tempMachineCode)
            else:
                print("Invalid command!")

            del temp


if __name__ == '__main__':
    main()
