from XilinxPackageParser import getPinTable, getDeviceName, FPGA
import tkinter as tk
from tkinter.filedialog import askopenfilename
from pdb import set_trace

'''
    Command line utility for converting xilinx package files (e.g. xcau10pubva368pkg.txt)
        and generating a *.kicad_sym file for importing into a project. The symbols were tested 
        using Kicad 6.0

        This is a TEST SCRIPT to solve my one time problem - I don't care that it is not
            a polished script w/good error and type checks. This evolved from something 
            much simpler but has proved to be very useful as-is.

        To use the generated symbol, in Kicad's Symbol Editor, right click a library and hit "Import Symbol" and 
            select the .kicad_sym file this script generates

'''

class SymbolMaker: #this class takes in lists of pins and places them on kicad symbol sheets, the user is responsible for setting the correct symbol number for multi-part symbols
    def __init__(self, FPGA):
        self.data = f'(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)\n\
            \t(symbol \"{FPGA.name}\" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)\n'
        self.name = FPGA.name
        self.fname = FPGA.name + '.kicad_sym'
        self.f = open(self.fname, 'w')
        self.addProperties()

    def save(self): # when the user is finished adding parts/pins to the symbol, call this to save the kicad symbol file
        self.data += '\t)\n)\n'
        self.f.write(self.data)        
        self.f.close()
        print(f'Results saved to: {self.f.name}')

    def addProperties(self): # TODO - figure out way to set the footprint properly
        self.data += f'\
            \t\t(property \"Reference\" \"U\" (id 0) (at 43.18 10.16 0)\n\
            \t\t\t(effects (font (size 1.524 1.524)))\n)\n\
            \t\t(property \"Value\" \"{self.name}\" (id 1) (at 43.18 7.62 0)\n\
            \t\t\t(effects (font (size 1.524 1.524)))\n)\n\
            \t\t(property \"Footprint\" \"{self.name}\" (id 2) (at 0 0 0)\n\
            \t\t\t(effects (font (size 1.524 1.524) italic) hide)\n)\n\
            \t\t(property \"Datasheet\" \"{self.name}\" (id 3) (at 0 0 0)\n\
            \t\t\t(effects (font (size 1.524 1.524) italic) hide)\n)\n\
            \t\t(property \"ki_keywords\" \"{self.name}\" (id 4) (at 0 0 0)\n\
            \t\t\t(effects (font (size 1.524 1.524)) hide)\n)\n\
            \t\t(property \"ki_locked\" \"\" (id 5) (at 0 0 0)\n\
            \t\t\t(effects (font (size 1.524 1.524)) hide)\n)\n\
            \t\t(property \"ki_fp_filters\" \"\" (id 6) (at 0 0 0)\n\
            \t\t\t(effects (font (size 1.524 1.524)) hide)\n)\n'

            
    def addRectangle(self, x_start, y_start, x_end, y_end): # must place this within a symbol? Not called for entire symb?
        # TODO - Future feature - drawing boxes around pin groups. I don't care enough now, will do this manually
        self.data += f'\t(rectangle (start {x_start} {y_start}) (end {x_end} {y_end})\n\
            \t\t(stroke (width 0) (type default) (color 0 0 0 0))\n\
            \t\t(fill (type none))\n\
            \t)\n'

    def addPart(self, pins, partnum, title=''): 
        self.data += f'(symbol \"{self.name}_{partnum}_1\"\n'
        #self.addRectangle(0, 0, 40, -60) # just for testing - TODO - figure out necessary size of bounding box based on number of pins/cols
        self.data += f'(text \"{title}\" (at 0 5.08 0)\n\
            \t(effects (font (size 1.27 1.27) bold))\n)\n'
        dx, dy = 0,0

        ang = 0
        flipsides = False
        if (len(pins) > 80): # TODO - fix the side flipping logic, current approach is pretty braindead
            flipsides = True
            lastang = 180
            dx_last = 50.8

        for pin in pins:
            self.addPin(pin, dx, dy, ang)
            
            if (flipsides):
                currangle = ang
                ang = lastang
                lastang = currangle
                dx_curr = dx
                dx = dx_last
                dx_last = dx_curr
                dy -= 1.27
            else:
                dy -= 2.54

        self.data += f')\n'

    def addPin(self, pin, dx, dy, ang): # Setting ang=180 mirrors the pin (vertically?)
        if (pin.pintype == 'power'):
            pintype = 'power_in'
        elif (pin.pintype == 'hrio' or pin.pintype == 'hpio' or pin.pintype == 'mgt' or pin.pintype == 'config'):
            pintype = 'bidirectional'
        else:
            pintype = 'bidirectional'

        self.data += f'(pin {pintype} line (at {dx} {dy} {ang}) (length 7.62)\n\
                \t(name \"{pin.name}\" (effects (font (size 1.27 1.27))))\n\
                \t(number \"{pin.number}\" (effects (font (size 1.27 1.27))))\n\
                )\n'

def sortMGTPins(mgtpins): # I think a competent python developer could do this with a single list comprehension
    # TODO - I want to sort the fpga mgt pins such that the differential pairs are adjacent to each other
    # TODO - may also be nice when creating the symbol to put RX and clocks on the left side of symbol and TX on right
    # NOTE - maybe a better approach is to just identify the MTG banks, identify the MGT type (GTH, GTY, etc) and programmatically
    #   Regenerate the list based on the assumptions below w/o resorting to complicated sorting...
    # Valid assumptions - there are always 4 transceivers per tile
    #   for every rx there is a tx
    #   for every *N there is a *P
    '''
        Input list looks like this:
            *RXN0_224
            *RXN0_225
            *RXN0_226
            *RXN0_227
            *RXN1_224
            *RXN1_225
            ...
            *TXN0_224
            *TXN0_225
            *TXN0_226
            *TXN0_227
            *TXN1_224
            *TXN1_225
            ...
            
        I want this list to be arranged like this:
            *RXN0_224
            *RXP0_224
            *RXN1_224
            *RXP1_224
            ...
            *RXN0_225
            *RXP0_225
            ...
            *TXN0_224
            *TXP0_224

    '''
    # mgt_data_pins_sorted = []
    # for i in range(0, len(mgtpins), 16):
    #     mgt = mgtpins[i:i+16]
    #     for i in range(4):
    #         mgt_data_pins_sorted += mgt[i::len(mgtpins)//2]
    # mgtpins = mgt_data_pins_sorted

    return mgtpins

def main():
    root = tk.Tk()
    root.withdraw()
    fname = askopenfilename(filetypes=[('Xilinx Package Files', '*.txt')])
    with open(fname, 'r') as f:
        data = f.read()

    print(f'Processing file: {fname}')
    device = getDeviceName(data)
    print(f'Detected Device: {device}')
    pintable = getPinTable(data)
    fpga = FPGA(pintable, device)
    #fpga.dumpPins()

    power_pins = [pin for pin in fpga.pins if pin.pintype == 'power']
    config_pins = [pin for pin in fpga.pins if pin.pintype == 'config']    
    mgt_pins = [pin for pin in fpga.pins if pin.pintype == 'mgt']
    mgt_data_pins = [pin for pin in mgt_pins if ('TX' in pin.name) or ('RX' in pin.name)] # Big assumption, these data pins are sorted
    mgt_data_pins.sort()
    # TODO - identify 'NC' pins and place them in one of the sheets, but hide them...
    #mgt_data_pins = sorted(mgt_data_pins, key=lambda x: x.name[:-4]) # possibly exclude bank from sort?

    mgt_data_pins = sortMGTPins(mgt_data_pins)
    mgt_other_pins = [pin for pin in mgt_pins if pin not in mgt_data_pins]
    fpgabanks = list(set([pin.bank for pin in fpga.pins if pin.pintype.endswith('io')]))

    
    mgt_pins = mgt_data_pins + mgt_other_pins

    gnd_pins = [pin for pin in power_pins if'GND' in pin.name]
    vcco_pins = [pin for pin in power_pins if 'VCCO' in pin.name]
    vccint_pins = [pin for pin in power_pins if 'VCCINT' in pin.name]
    otherpwr_pins = [pin for pin in power_pins if pin not in gnd_pins and pin not in vcco_pins and pin not in vccint_pins]

    iopins = []
    iopins_lst = []
    for bank in fpgabanks: # could not figure out a way w/list comprehension to do this
        pins = [pin for pin in fpga.pins if pin.bank == bank]
        iopins.append( (bank, pins) )
        iopins_lst += pins
    #  iopins[<banknumber>][<fpgapinnumber>]

    other_pins = [pin for pin in fpga.pins if pin not in power_pins and pin not in config_pins and pin not in mgt_pins and pin not in iopins_lst] # lol

    symbols = [gnd_pins, vcco_pins, vccint_pins, otherpwr_pins, mgt_pins, other_pins]
    names = ['GND', 'VCCO', 'VCCINT', 'MISCPWR', 'MGT', 'NC']

    symbol = SymbolMaker(fpga)

    j = 1  # NOTE - placing objects on layer 0 causes them to show up on every layer, so j starts at 1
    for sym in symbols:
        # addPart( [list_of_FPGA_Pins], symbol_number (for multi-sheet symbols), title_string_for_sheet)
        symbol.addPart(sym, j, names[j-1])
        j += 1

    i = 0
    for bank in iopins:
        symbol.addPart(bank[1], i+j, 'BANK ' + bank[0])
        i += 1

    symbol.addPart(other_pins, i+j, 'Other Pins')

    symbol.save()

    return

if __name__ == '__main__':
    main()
