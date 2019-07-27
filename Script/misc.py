'''
Created on 13 Aug 2018

@author: Femi
'''

class GameSettings:
    def __init__(self):
        self.FPS = 30
        self.height = 720
        self.width = 1280

class ValueHolder:
    def __init__(self):
        self.armyManager = None
        self.battle = None
        self.buttons = []
        self.colours = {"Aqua": (0, 255, 255), "Beige": (245, 245, 220), "Black": (0, 0, 0), 
                        "Dark Blue": (0, 48, 112), "Dark Green": (0, 100, 0), "Dark Olive Green": (85, 107, 47), 
                        "Forest Green": (34, 139, 34), "Green": (0, 128, 0), "Lime": (0, 255, 0), 
                        "Orange": (255, 128, 0), "Red": (255, 0, 0), "Sea Green": (46, 139, 87), 
                        "Slate Grey": (112, 128, 144), "White": (255, 255, 255), "Yellow": (255, 255, 0)}
        self.factions = []
        self.font20 = None
        self.font30 = None
        self.font60 = None
        self.font90 = None
        self.mageProfiles = None
        self.mode = None #0 = Same PC, 1 = Server, 2 = Direct
        self.screenManager = None
        self.settings = None
        self.state = 0 #0 = In menu screens, #1 = Army setup screens, #2 = battle
        self.version = "Version 0.1.1"
        
def cut_down_string(string, maxLength):
    #while string is above sum of strings
    sumOfStrings = 0
    i = 0
    text = []
    end = False
    while len(string) > sumOfStrings:
        space = None
        #loop from starting point to maxLength
        for j in range(i, i + maxLength):
            #Save most recent space
            try:
                if string[j] == ' ':
                    space = j
            except IndexError:
                space = i + maxLength
                newString = string[i:space]
                text.append(newString)
                end = True
                break
                
        if not end:
            #once end is reach, split by space if possible
            if space != None:
                newString = string[i:space]
                i = space + 1
            #otherwise, split at max length
            else:
                newString = string[i:i + maxLength]
                i += maxLength
            text.append(newString)
            
            #See if sum of strings is equal to the full string
            sumOfStrings = 0
            for t in text:
                sumOfStrings += len(t)
        else:
            break
            
    return text

def is_point_inside_rect(x, y, rect):
    if (x > rect.left) and (x < rect.right) and (y > rect.top) and (y < rect.bottom):
        return True
    else:
        return False
    
"""Old method
def string_to_list(strData, intValues=False, giveTuple=False):
    data = tuple(strData)
    finalData = []
    currentString = None
    previousChar = None
    ignored = ['(', ')', "'"]
    for char in data:
        if char in ignored:
            pass
        elif char == ' ' and previousChar == ',':
            pass
        elif char == ',':
            finalData.append(currentString)
            currentString = None
        else:
            if currentString == None:
                currentString = char
            else:
                currentString += char
                
        previousChar = char
    
    if currentString != None:
        finalData.append(currentString)
        
    if intValues:
        for d in finalData[:]:
            finalData.append(int(d))
            finalData.remove(d)
            
    if giveTuple:
        finalData = tuple(finalData)
    
    return finalData
"""
#new method
def string_to_list(strData, intValues=False, giveTuple=False):
    data = tuple(strData)
    finalData = []
    currentString = None
    previousChar = None
    ignored = ['(', ')', "'"]
    ignoring = False
    inBrackets = False
    deep = 0
    first = True
    for char in data:
        if char in ignored:
            ignoring = True
            if first and char == '(':
                first = False
            elif not first and char == '(':
                ignoring = False
                deep += 1
                inBrackets = True
            elif not first and char == ')':
                ignoring = False
                deep -= 1
                if deep == 0:
                    inBrackets = False
            elif inBrackets and char == ',':
                ignoring = False
        else:
            ignoring = False
        if ignoring:
            pass
        elif char == ' ' and previousChar == ',' and not inBrackets:
            pass
        elif char == ',' and not inBrackets:
            finalData.append(currentString)
            currentString = None
        else:
            if currentString == None:
                currentString = char
            else:
                currentString += char

        previousChar = char

    if currentString != None:
        currentString = currentString[:-1]
        if currentString != '':
            finalData.append(currentString)

    if intValues:
        for d in finalData[:]:
            finalData.append(int(d))
            finalData.remove(d)

    if giveTuple:
        finalData = tuple(finalData)

    return finalData