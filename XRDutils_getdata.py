import pandas as pd
import numpy as np
import os
import sys
import getopt
import matplotlib.pyplot as plt
from XRDutils_plots import *

class XRDmachine:
    #Class defining XRD machine data header format. 
    def __init__(self, name):
        self.name = name
        if name == 'ece':
            self.timestp = 'Time: '
            self.datestp = 'Date: '
            self.stepsize = 'Scan Stepsize: '
            self.sttwothetaangl = '          2Theta    '
            self.datstart = 'Position '
            self.tpp = 'Counting time per point: '
            self.wvlnth = 'Wavelength: '
            self.delimiter= '    '
        elif name == 'NTW':
            self.timestp = 'Time='
            self.datestp = 'Date='
            self.stepsize = 'Increment='
            self.sttwothetaangl = 'Start='
            self.datstart = '     Angle'
            self.tpp = 'Time='
            self.wvlnth = 'ActuallyUsedLambda='
            self.delimiter= ','
        elif name == 'NSLxrdml':
            self.timestp = '<startTimeStamp>'
            self.datestp = 'T'
            self.sttwothetaangl = '<positions axis='
            self.datstart = '<counts unit="counts">'
            self.tpp = '<commonCountingTime unit="seconds">'
            self.wvlnth = '<kAlpha1 unit="Angstrom">'
            self.delimiter= ' '
            self.scanaxis = 'scanAxis='
            self.atten = '<beamAttenuationFactors>'

class scdata:
    #Class defninig scan data
    def __init__(self, name, machine):
        self.name = name
        self.fname = name.split('\\')[-1]
        self.fold = name.split(self.fname)[0]
        self.machine = machine

def getdata(fname, machinenm=''):
    #function to get the metadata and scan data from the file and populate the scdata class to save the data
    print('getting data from '+fname)

    # get the machine type that the scan was done on. 
    # If 'machinenm' option is not passed, determine this from the file extension
    if machinenm != '':
        machine = XRDmachine(machinenm)
    else:
        if fname.split('.')[-1] == 'X01':
            machine = XRDmachine('ece')
        elif fname.split('.')[-1] == 'txt':
            machine = XRDmachine('NTW')
        elif fname.split('.')[-1] == 'xrdml':
            machine = XRDmachine('NSLxrdml')
    
    #define the scan data class and populate it using the machine format settings.
    d=scdata(fname, machine)
    stposline=0
    endposline=0
    with open(d.name) as file:
        if machine.name != 'NSLxrdml':
            for num, line in enumerate(file, 1):
                if machine.timestp in line:
                    if ':' in line:
                        d.timestp = line.split(machine.timestp)[1].split(' ')[0].split('\n')[0]
                if machine.datestp in line:
                    d.datestp = line.split(machine.datestp)[1].split(' ')[0].split('\n')[0]
                if machine.stepsize in line:
                    if line.split(machine.stepsize)[0] == '':
                        d.stepsize = float(line.split(machine.stepsize)[1].split(' ')[0])
                if machine.sttwothetaangl in line:
                    d.sttwothetaangl = float(line.split(machine.sttwothetaangl)[1].split(' ')[0])
                if machine.datstart in line:
                    d.datstart = num-1
                if machine.tpp in line:
                    if line.split(machine.tpp)[0] == '' or line.split(machine.tpp)[0][-1] == ' ':
                        try:
                            d.tpp = float(line.split(machine.tpp)[1].split(' ')[0])
                        except:
                            """
                            There are 2 Time= lines for NTW data, so if the result can't be converted, skip it.
                            """
                if machine.wvlnth in line:
                    d.wvlnth = float(line.split(machine.wvlnth)[1].split(' ')[0])

            #get the scan data using the header information gathered
            d.datadf = pd.read_csv(d.name, skiprows=d.datstart,
                            delimiter=d.machine.delimiter, encoding='unicode_escape', engine='python')
        else:
            d.scanaxis='none'
            anglerangeline='not yet defined'
            attenlist=[1]
            for num, line in enumerate(file, 1):
                if machine.scanaxis in line:
                    d.scanaxis=line.split(machine.scanaxis)[-1].split(' ')[0]
                    if d.scanaxis == '"2Theta-Omega"':
                        anglerangeline=machine.sttwothetaangl+'"2Theta"'
                    elif d.scanaxis == '"Omega-2Theta"':
                        anglerangeline=machine.sttwothetaangl+'"Omega"'
                    else:
                        anglerangeline=machine.sttwothetaangl+d.scanaxis
                if machine.timestp in line:
                    d.timestp = line.split(machine.timestp)[-1].split('<')[0].split(machine.datestp)[-1].split('-')[0]
                    d.datestp = line.split(machine.timestp)[-1].split('<')[0].split(machine.datestp)[0]
                if anglerangeline in line:
                    stposline=num+1
                    endposline=num+2
                if num == stposline and stposline > 0:
                    d.sttwothetaangl=float(line.split('<startPosition>')[-1].split('<')[0])
                if num == endposline and endposline > 0:
                    d.endtwothetaangl=float(line.split('<endPosition>')[-1].split('<')[0])
                if machine.wvlnth in line:
                    d.wvlnth = float(line.split(machine.wvlnth)[1].split('<')[0])
                if machine.tpp in line:
                    d.tpp=float(line.split(machine.tpp)[1].split('<')[0])
                if machine.datstart in line:
                    ylist=line.split(machine.datstart)[1].split('<')[0]
                    ylist=ylist.split(machine.delimiter)
                    ylist=[float(i) for i in ylist]
                if machine.atten in line:
                    attenlist=line.split(machine.atten)[1].split('<')[0]
                    attenlist=attenlist.split(machine.delimiter)
                    attenlist=[float(i) for i in attenlist]
            if len(attenlist) > 1:
                ylist=[a*b for a,b in zip(attenlist,ylist)]
            d.datadf=pd.DataFrame()
            d.datadf['x']=np.linspace(d.sttwothetaangl,d.endtwothetaangl,len(ylist))
            d.datadf['y']=ylist
            d.stepsize=d.datadf['x'].iloc[1]-d.datadf['x'].iloc[0]


    return d

def cleandata(d):
    d.datadf=d.datadf[d.datadf.iloc[:, 1] >= 0]
    d.datadf=d.datadf[d.datadf.iloc[:, 1] != float('nan')]
    return d

def savedata(d):
    #save data object to '.xrd'(csv text) file at the location it was opened from
    fname=d.fold+d.fname.split(d.fname.split('.')[-1])[0]+'proc.xrd'
    with open(fname, 'w') as f:
        #save header info
        f.write("filename: "+d.fname+'\n')
        f.write("process folder: "+d.fold+'\n')
        f.write("machine: "+d.machine.name+'\n')
        f.write("date: "+d.datestp+'\n')
        f.write("time: "+d.timestp+'\n')
        f.write("start 2theta angle: "+str(d.sttwothetaangl)+'\n')
        f.write("step size: "+str(d.stepsize)+'\n')
        f.write("time per point: "+str(d.tpp)+'\n')
        f.write("wavelength: "+str(d.wvlnth)+'\n')
        f.write("x,y\n")

        #save data
        #if the machine is ece, shift x to be 2theta (default is theta) and add offset (default is relative)
        for i in range(len(d.datadf.iloc[:, 0])):
            if d.machine.name == 'ece':
                f.write(str(d.sttwothetaangl-2*d.datadf.iloc[0, 0]+2*d.datadf.iloc[i, 0]))
            else:
                f.write(str(d.datadf.iloc[i, 0]))
            f.write(', ')
            f.write(str(d.datadf.iloc[i, 1])+'\n')

def getdatainfolder(fpath, repl=False, sdsearch=True):
    #only look for files with these extensions
    extf=['.X01', '.xrdml']
    #disabled: '.txt',
    flist1=[]
    #get file names, depending on if subdirectories are searched or not
    if sdsearch:
        for path, subdirs, files in os.walk(fpath):
            for name in files:
                if any(ext in name for ext in extf):
                    flist1.append(os.path.join(path, name))
    else:
        for name in os.listdir(fpath):
            if any(ext in name for ext in extf):
                flist1.append(os.path.join(path, name))
    
    #check if processed file is already there - replace it if 'repl' is True
    flist=[]
    for f in flist1:
        if os.path.isfile(f.split(f.split('.')[-1])[0]+'proc.xrd'):
            if repl:
                print('xrd file {} already exists, replacing...'.format(f))
                flist.append(f)
            else:
                #print('xrd file {} already exists, NOT replacing...'.format(f))
                """
                """
        else:
            flist.append(f)

    for fname in flist:
        d=getdata(fname)
        d=cleandata(d)
        savedata(d)
        pd=loadXRDdat(fname.split(fname.split('.')[-1])[0]+'proc.xrd')


def main(argv):
    helpmsg = 'XRDutils_getdata.py -i <inputfolder/file> \n-r for replace already processed\n-s for ignore subdirs'
    repl = False
    sdsearch = True
    #default folder to look for new XRD data in. (will also look in +1 level subfolders)
    inputfolder = r"C:\Users\justi\Research\Data\XRD"
    try:
        opts, args = getopt.getopt(argv,"hrsi:",["ifolder="])
    except getopt.GetoptError:
        print(helpmsg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpmsg)
            sys.exit()
        elif opt == '-r':
            repl = True
            print('Replacing previously processed data files...')
        elif opt == '-s':
            sdsearch = False
            print('Ignoring subdirectories...')
        elif opt in ("-i", "--ifile"):
            inputfolder = arg
            print('Input file/folder is '+ inputfolder)
    if '.' in inputfolder:
        d=getdata(inputfolder)
        savedata(d)
    else:
        getdatainfolder(inputfolder, sdsearch=sdsearch, repl=repl)

if __name__ == "__main__":
    main(sys.argv[1:])