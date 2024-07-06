import re
from pdb import set_trace
import tkinter as tk
from tkinter.filedialog import askopenfilename

class FPGA:
    def __init__(self, pintable, name):
        self.name = name
        self.pintable = pintable
        self.pins = []
        self.getPins()

    def getPins(self):
        for pin in self.pintable:
            self.pins.append(FPGAPin(pin))
    
    def dumpPins(self):
        print('*** name, number, pintype ***')
        for pin in self.pins:
            print(f'*** {pin.name},\t{pin.number},\t{pin.pintype},\t{pin.bank} ***')


class FPGAPin:
    def __init__(self, row):
        self.row = row.split(',')
        self.number = self.row[0]
        self.name = self.row[1]
        self.pintype = None
        self.bank = ''
        if ('CONFIG' in row):
            self.pintype = 'config'
        elif ('VCC' in row or 'GND' in row or 'VTT' in row):
            self.pintype = 'power'
        elif ('MGT' in row):
            self.pintype = 'mgt'
            if ('TX' in row or 'RX' in row):
                self.bank = self.name[1+self.name.rfind('_'):]
        elif ('HR' in row):
            self.pintype = 'hrio'
            self.bank = self.name[1+self.name.rfind('_'):]
        elif ('HP' in row):
            self.pintype = 'hpio'
            self.bank = self.name[1+self.name.rfind('_'):]
        elif ('HD' in row):
            self.pintype = 'hdio'
            self.bank = self.name[1+self.name.rfind('_'):]
        elif ('NC' in row):
            self.pintype = 'nc'
        else:
            self.pintype = 'unknown'
    def __lt__(self, other): # Added these methods so I could call sort or sorted on a list of FPGAPins and they will get sorted by name
        return self.name < other.name
    def __le__(self, other):
        return self.name <= other.name
    def __gt__(self, other):
        return self.name > other.name
    def __ge__(self, other):
        return self.name >= other.name
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other):
        return self.name != other.name

def getDeviceName(data):
    if ('Copyright' in data):
        idx = data.find('Device')
        idx_l = idx + data[idx:].find(':') + 1
        idx_r = idx_l + data[idx_l:].find('\n')
        device = data[idx_l : idx_r].strip()
        return device
    return data[:data.find('\n')].split(' ')[1]

def getPinTable(data):
    rtn = []
    idx = data.find('Super Logic Region')
    idx += data[idx:].find('\n')+1
    table = data[idx:].split('\n')
    numpins = 0
    for row in table:
        if (row):
            if 'Total Number' in row:
                numpins = getNumPins(row)
            else:
                row = re.sub('\s+', ',', row.strip())
                if (row):
                    rtn.append(row)
    if (numpins != len(rtn)):
        print(f'WARNING: Numpins ({numpins}) != len(rtn) ({len(rtn)})')

    return rtn

def getNumPins(row):
    return int(row.strip().split(' ')[-1])

def dumpTable(table):
    for row in enumerate(table):
        print(f'{row[0]}: {row[1]}')

def main(): # For debugging only
    root = tk.Tk()
    root.withdraw()
    fname = askopenfilename(filetypes=[('Xilinx Package Files', '*.txt')])
    with open(fname, 'r') as f:
        data = f.read()
    print(f'Processing file: {fname}')
    device = getDeviceName(data)
    print(f'Detected Device: {device}')
    pintable = getPinTable(data)
    #dumpTable(pintable)
    fpga = FPGA(pintable, device)
    fpga.dumpPins()
    return

if __name__ == '__main__':
    main()
