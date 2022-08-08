import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks

def getdata(fname,sr=43):
    path=''
    if sr==43:
        for line in open(path+fname):
           if line.startswith('SampleID:'):
              material=line.split(':')[1]
    else:
        material=fname
    data=pd.read_csv(path+fname,skiprows=sr,delimiter='    ', engine='python')
    return material,data


def plotdata(fnames,sctypes,note='',legend=False, grid=False, zeroshift=0, shiftspeak=True, annotatepeaks=False, machine='ece'):
    
    for i in range(len(fnames)):
        fname=fnames[i]
        sctype=sctypes[i]
        if machine=='ece':
            mat,d=getdata(fname,sr=43)
        elif machine=='cemas':
            mat,d=getdata(fname,sr=381)
        title=fname.split('/')[1].split('/')[0]+mat+' '+note
        #plot
        if sctype=='xrd':
            plt.figure(1)
            pkshift=0
            if shiftspeak:
                indx_max = np.argmax(d.Count)
                pkshift = d.Position[indx_max]*2
            if annotatepeaks:
                peaks, _ = find_peaks(d.Count, height=30,distance=200)
                #print(peaks)
                for peak in peaks:
                    plt.annotate(str(2*d.Position[peak]+zeroshift-pkshift),[2*d.Position[peak]+zeroshift-pkshift,d.Count[peak]+30],fontsize=7)

            plt.title(title)
            plt.semilogy(2*d.Position+zeroshift-pkshift,d.Count,lw=1,label=title)
            plt.xlabel(r'$\Delta 2\theta$(deg)')
            if legend:
                plt.legend()
            if grid:
                plt.grid()
            plt.ylabel('intensity(cps)')
        elif sctype=='xrr':
            plt.figure(2)
            plt.title(title)
            plt.semilogy(2*d.Position,d.Count,lw=1,label=title)
            plt.xlabel(r'$\Delta 2\theta$(deg)')
            if legend:
                plt.legend()
            if grid:
                plt.grid()
            plt.ylabel('intensity(cps)')
        elif sctype=='rc':
            plt.figure(3)
            plt.title(title)
            plt.plot(d.Position,d.Count,lw=1,label=title)
            plt.xlabel(r'$\Delta \Omega$(deg)')
            if legend:
                plt.legend()
            if grid:
                plt.grid()
            plt.ylabel('intensity(cps)')
        else:
            print('valid types are xrd, xrr, or rc')
            
        
    plt.show()

def plotinfolder(fpath,**kwargs):
    fnames1=[fpath+fname for fname in os.listdir(fpath)]
    fnames=[]
    for fname in fnames1:
        if fname[-3:]=='X01':
            fnames.append(fname)
    sctypes=[]
    for fname in fnames:
        if 'XRD_' in fname:
            sctypes.append('xrd')
        elif 'XRR_' in fname:
            sctypes.append('xrr')
        elif 'RC_' in fname:
            sctypes.append('rc')
        else:
            sctypes.append('xrd')
    plotdata(fnames,sctypes,**kwargs)