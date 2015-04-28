'''
Created on 11-Aug-2014

@author: abhiagar90@gmail.com
'''

import re
import parsehelper
import utilFunc
import decoder
import mem, const
import traceback
import const

DEBUG_MODE=True
PC = 0
bkpoint=[]
hexes=[]
watchPause=False #

def isWatchPause():
    return  watchPause

def setWatchPause():
    global watchPause
    watchPause=True

def resetWatchPause():
    global watchPause
    watchPause=False    

def getHexes():
    global hexes
    return hexes

def setHexes(list_hex):
    global hexes
    hexes=list_hex
    
def startDebugMode():
    global DEBUG_MODE
    DEBUG_MODE=True
    
def endDebugMode():
    global DEBUG_MODE
    DEBUG_MODE=False
    
def isDebugMode():
    global DEBUG_MODE
    return DEBUG_MODE  
 
def checkIfValidBreakPoint2(givenHexString):
    length=parsehelper.getNumOfInst()
    givenHexInt=int(givenHexString, 16)
    prog_counter=getPC()
    ans=False
    if (givenHexInt-prog_counter)%4 == 0:
        if (givenHexInt-prog_counter)/4 < length:
            ans=True
    print 'the value here: '+str(ans)
    return ans

def checkIfValidBreakPoint(givenHexString):
    startAdd=parsehelper.getStartAddress()
    length=parsehelper.getNumOfInst()
    givenHexInt=int(givenHexString, 16)
    startAddInt=int(startAdd, 16)
    if (givenHexInt-startAddInt)%4 == 0:
        if(givenHexInt-startAddInt)/4 < length:
            return True
    return False

#Note could be 5 etc, any int
def setPC(givenInt):
    global PC
    PC = givenInt
    
def getPC():
    global PC
    return PC

def incPC():
    global PC
    PC=PC+4

def getCurrentInstNumber(): #starts at index 0
    prog_counter=getPC()
    start=int(parsehelper.getStartAddress(),16)
    return int((prog_counter-start)/4)

def getInstFromValidHexString(givenHexString): #starts at index 0
    startAdd=parsehelper.getStartAddress()
    givenHexInt=int(givenHexString, 16)
    startAddInt=int(startAdd, 16)
    return int((givenHexInt-startAddInt)/4)
   

def initBkPoint():
    global bkpoint
    length=parsehelper.getNumOfInst()
    bkpoint= [False for x in range(length)]
    #print bkpoint
    
def putBkPoint(givenHexString):
    num=-1
    if checkIfValidBreakPoint(givenHexString):
        num=getInstFromValidHexString(givenHexString)
    if num != -1:
        #list nuances
        del bkpoint[num]
        bkpoint.insert(num, True)
        return True
    else:
        return False
    
def resetBkPoint(givenHexString):
    num=-1
    if checkIfValidBreakPoint(givenHexString):
        num=getInstFromValidHexString(givenHexString)
    if num != -1:
        #list nuances
        del bkpoint[num]
        bkpoint.insert(num, False)
        return True
    else:
        return False
    
def isBkPoint(index):
    if(index < len(getHexes())):
        global bkpoint
        return bkpoint[index]

def isBkPointHex(givenHexString): #assume the hex is within limits and right always
    index=getInstFromValidHexString(givenHexString)
    return isBkPoint(index)
    
def startRunEngine():
    initBkPoint()
    setPC(parsehelper.getPC())
    executeRUN()

def startInteraction():
    flag = True
    initBkPoint()
    setPC(parsehelper.getPC())
    #print getPC()
    #print getCurrentInstNumber()
    print '------------------------------------'
    print 'The entry address for execution is: ' + hex(parsehelper.getPC())
    print 'The starting address of .text section is: ' + parsehelper.getStartAddress()
    print "Debug mode started. Type 'help' for list of options."
    while flag:
        print '------------------------------------'
        print '(debug) : ',
        x=raw_input()
        x=x.strip().lower()
        if x=='exit':
            flag=False
        else:
            parseCommand(x)

def parseCommand(command):
    if command=='' or command==None:
        return
    
    print 'Typed: '+command
    
    if command=='s':
        try:
            executeS()
        except Exception as e:
            if str(e)=='watch':
                print 'Watched register value changed. Halting.'
            else:  print traceback.format_exc()
        return
    
    if command=='run':
        try:
            executeRUN()
        except Exception as e:
            if str(e)=='watch':
                print 'Watched register value changed. Halting.'
            else:  print traceback.format_exc()
        return 
    
    if command=='c':
        try:
            executeC()
        except Exception as e:
            if str(e)=='watch':
                print 'Watched register value changed. Halting.'
            else:  print traceback.format_exc()
        return
    
    if command.startswith('break'):
        executeBreak(command.split()[1])
        return
    
    if command.startswith('del'):
        executeDel(command.split()[1])
        return
    
    if command.startswith('print'):
        executePrint(command)
        return
    
    if command == 'flags':
        executeFlag()
        return
    
    if command == 'regs':
        executeRegs()
        return
    
    if command == 'help':
        executeDebuggerHelp()
        return
    
    if command.startswith('watch'):
        executeWatch(command)
        return 
    else:
        print 'Not supported input (yet)!'
    
def executeS():
    #will have to take care of inst running also
    #not caring about break point or not -->DOESN't MATTER
    print "Executing command type: "+"'s'"
    executeNextInst()
    pass

def executeNextInst():
    if getCurrentInstNumber()<len(getHexes()):
        hexcode=hexes[getCurrentInstNumber()]
        utilFunc.resetInstrFlag()
        decoder.decodeInstr(hexcode)
        incPC()
        #now the inst has been executed!!!
        if isWatchPause():
            resetWatchPause()
            raise Exception("watch") #copied from stack overflow!!! ;)
    else:
        print 'instructions exhausted!!'
    #print 'PC: '+str(getPC())

def executeRUN():
    print "Executing command type: "+"'run'"
    x=getCurrentInstNumber()
    if(x>=len(getHexes())):
        print 'instructions exhausted!!'
        return
    while (x <  len(getHexes())):
        #print 'X: '+str(x)
        executeNextInst()
        x=getCurrentInstNumber()
        
def executeBreak(address): 
    #print 'You typed address: '+address
    #assuming should start with address
    '''
    if len(address)!=10:
        print 'Not valid hex address for current state.'
        return
    '''
    myhex=re.findall(r'0[x|X][0-9a-fA-F]+', address)
    print myhex #here so that we know where the bkpoint has been set
    if myhex:
        #print mylist[0]
        if(checkIfValidBreakPoint(myhex[0])):
            if not isBkPointHex(myhex[0]):
                putBkPoint(myhex[0])
                print 'break done...'
            else:
                print 'already a breakpoint'
        else:
            print 'Not valid hex address for current state'
    else:
        print 'Not valid hex address for current state'
        return
    
def executeDel(address): 
    #print 'You typed address: '+address
    #assuming should start with address
    '''
    if len(address)!=10:
        print 'Not valid hex address for current state'
        return
    '''
    myhex=re.findall(r'0[x|X][0-9a-fA-F]+', address)
    print myhex #here so that we know where the bkpoint has been set
    if myhex:
        #print mylist[0]
        if(checkIfValidBreakPoint(myhex[0])):
            if isBkPointHex(myhex[0]):
                resetBkPoint(myhex[0])
                print 'del done...'
            else:
                print 'already not a breakpoint'
        else:
            print 'Not valid hex address for current state'
    else:
        print 'Not valid hex address for current state'
        
    
def executeC():
    print "Executing command type: "+"'c'"
    x=getCurrentInstNumber()
    if(x >= len(getHexes())):
        print 'instructions exhausted!!'
        return
    while (x <  len(getHexes()) and (not isBkPoint(x))):
        #print 'X: '+str(x)
        executeNextInst()
        x=getCurrentInstNumber()
    if (x==len(getHexes())):
        print 'no breakpoints encountered. instructions exhausted!!'
        return
    print "Arrived at the break point. Type 's' or 'run'..."
    
def executePrint(command):
    print "Executing command type: "+"'print'"
    command=command.split()
    if(len(command)==3):
        executePrintReg(command)
    elif(len(command)==4):
        executePrintMem(command)#giving the splitted string
        pass
    else:
        print 'Invalid print command'

#there might be a problem of what is treated as what
def executePrintReg(command): #list of strings in command
    
    regbase=command[1].lower()
    
    if regbase!='x' and regbase!='d':
        print 'Invalid print reg command'
        return
    reginfo=command[2].lower()
    
    if len(reginfo)!=2:
        print 'Invalid print reg command'
        return
    regtype=reginfo[0]
    
    if regtype!='w' and regtype!='x':
        print 'Invalid print reg command'
        return
    regnum=int(reginfo[1])
    
    if regnum<0 or regnum>31:
        print 'Invalid print reg command'
        return
    
    if regtype == 'x':
        binary=mem.regFile[regnum]
        if regbase == 'd':            
            if binary[0]=='0':
                print 'Register value: ' + str(int(binary,2))
            else:
                neg_binary=utilFunc.twosComplement(binary, 64)
                print 'Register value: -' + str(int(neg_binary,2))
        else:
            print 'Register value: ' + utilFunc.binaryToHexStr(binary)
    elif regtype == 'w':
        binary=mem.regFile[regnum][32:64]
        if regbase == 'd':            
            if binary[0]=='0':
                print 'Register value: ' + str(int(binary,2))
            else:
                neg_binary=utilFunc.twosComplement(binary, 32)
                print 'Register value: -' + str(int(neg_binary,2))
        else:
            print 'Register value: ' + utilFunc.binaryToHexStr(binary)
            
def executePrintMem(command):
    base=command[2]
    address=command[3]
    freq=command[1]
    if base!='d' and base!='x':
        print 'Invalid print-from-memory command'
        return
    if not hexHelperForPrint(address):
        print 'Invalid print-from-memory command'
        return
    if not freqHelperForPrint(freq):
        print 'Invalid print-from-memory command'
        return
    #print 'all pass!!!'
    
    printMemEngine(command)
    
def printMemEngine(command):
    
    base=command[2] # x or d
    address=command[3]
    freq=command[1]
    listOfHex=''
    
    address=int(address,16)
    
    #assume to be in hex
    freqcount=int(freq[0:-1])
    freqtype=freq[-1] # b w or d
    numOfBits=''
    if freqtype=='w':
        for i in range(freqcount):
            data=mem.fetchWordFromMemory(address+(4*i))
            if data==const.TRAP:
                print 'Memory location could not be accessed'
                return
            listOfHex+=data+' '
            numOfBits=32
    elif freqtype=='d':
        for i in range(0,freqcount):
            data1=mem.fetchWordFromMemory(address+(8*i))
            data2=mem.fetchWordFromMemory(address+(8*i)+4)
            if data1==const.TRAP or data2==const.TRAP:
                print 'Memory location could not be accessed'
                return
            listOfHex+=data2+''+data1+' '
            numOfBits=64
    elif freqtype=='b':
        for i in range(0,freqcount):
            data=mem.fetchByteFromHelperMemory(address+i)
            if data==const.TRAP:
                print 'Memory location could not be accessed'
                return
            listOfHex+=data+' '
            numOfBits=8
    
    listOfHex=listOfHex.split()
    
    #print ''
    #print listOfHex
    #print '<'+command[3]+'>'+' : \t\t',
    
    pretty=0
    for i in listOfHex:
        if (pretty%4==0):
            print ''
            print '<'+command[3]+'>'+' + '+str((pretty*numOfBits)/8)+' : \t\t',
        if base=='x':
            print '0x'+i+'\t\t',
        elif base=='d':
            binary=utilFunc.hexToBin('0x'+i, numOfBits)
            print str(utilFunc.sInt(binary, numOfBits))+'\t\t',
        print ' ',
        pretty=pretty+1
    print ''
    

    
            
def executeFlag():
    utilFunc.printAllFlags()
    
def executeRegs():
    i=0;
    for x in mem.regFile:
        print 'Register'+str(i)+': '+utilFunc.binaryToHexStr(x)
        i=i+1
    
def printMainHelp():
    print ''
    print '------------------------------------'
    print 'Syntax: python <PATH-TO PROJECT>/main.py [--help,--debug] [filename]'
    print ''
    print 'Options: '
    print '1. --help : Prints this output. '
    print '2. --debug filename: Starts debugger for elf file with title filename'
    print '3. filename: Should be the relative/absolute path of the elf file directed towards ARMv8 architecture'
    print '------------------------------------'
    print ''
    
def executeDebuggerHelp():
    print ''
    print 'Debug Options List: '
    print ''
    print '1.  help : Prints this output. '
    print '2.  s : Runs next instruction and halt'
    print '3.  c : Runs all instructions, but halts at next breakpoint'
    print '4.  run : Runs all instructions till last and halt'
    print '5.  break <ADDRESS> : Puts a breakpoint at the hexadecimal <ADDRESS>'
    print '6.  del <ADDRESS> : Deletes the breakpoint at the hexadecimal <ADDRESS>'
    print '7.  flags: Print the state of all flags'
    print '8.  regs: Print the state of all registers in hex(64 binary digits)'
    print '9.  print <d/x> <w/x>num: prints the decimal/hexadecimal equivalent of register(32bit/64bit) number num'
    print '10. print num<b/d/w> <d/x> 0x<hex-address> : prints the num(count) bytes, words, or doublewords starting from hexaddress in decimal/hexadecimal'
    print "11. watch num: stops executing as soon as register num's value is changed"
    print '12. exit: Exits the program(with the debugger)'
    print ''
    
def executeWatch(command):
    try:
        command=command.split()
        index=int(command[1])
        mem.setWatchForReg(index)
        mem.printWatchStateAll()
    except:
        print 'Invalid watch command'
    return

def saveAllToMemoryModel():
    global hexes
    #print 'saveeeee : '+str(hexes)
    curAddrInt=int(parsehelper.getStartAddress(),16)
    for x in hexes:
        #x has the data
        mem.storeWordToMemory(curAddrInt, x)
        curAddrInt+=4
    #mem.printMemoryState()
    
#claimed is a string
def hexHelperForPrint(claimed):
    myhex=re.findall(r'0[x|X][0-9a-f]+', claimed)
    if myhex:
        if len(myhex[0])==len(claimed):
            return True
        else:
            return False
    else:
        return False
    
def freqHelperForPrint(claimed):
    myhex=re.findall(r'[[1-9][0-9]*[bwd]', claimed)
    if myhex:
        if len(myhex[0])==len(claimed):
            return True
        else:
            return False
    else:
        return False
