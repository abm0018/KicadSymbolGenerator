from XilinxPackageParser import getDeviceName, getPinTable

from os import listdir
import tkinter as tk
from tkinter.filedialog import askdirectory

def getFileNames(directory):
    allfiles = listdir(directory)
    rtn = []
    for filename in allfiles:
        if (filename.endswith('.txt')):
            rtn.append(filename)
    return rtn

def testFile(filename): # not really a good test, confirms that part number is correctly extracted.
    with open(filename, 'r') as f:
        data = f.read()
    name = getDeviceName(data)
    table = getPinTable(data)
    if ('x' in name or 'X' in name):
        print(f'PASSED: {name}')
    else:
        print(f'WARNING: {filename}')

def main():
    root = tk.Tk()
    root.withdraw()
    directory = askdirectory() # get the directory with xilinx package .txt files
    filenames = getFileNames(directory)

    for filename in filenames:
        testFile(directory + '/' + filename) # This will break if there are other .txt files that are NOT xilinx package files

    return

if __name__ == '__main__':
    main()
