
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import matplotlib as mpl
import json
import os


class XRDdat:
    #Class containing XRD data and metadata
    def __init__(self, fname):
        self.name = fname

def loadXRDdat(fname, shift_substrate_peak_value=-99):
    #function to load data from processed files
    d=XRDdat(fname)
    with open(d.name) as file:
        for num, line in enumerate(file, 1):
            if 'x,' in line:
                d.hlength=num-1
                
    #get the scan data using the header information gathered
    d.dat = pd.read_csv(d.name, skiprows=d.hlength,
                       delimiter=',', engine='python')

    if shift_substrate_peak_value != -99:
        d.dat=shift_substrate_peak(d.dat,shift_substrate_peak_value)
    return d

def shift_substrate_peak(d,shift_to):
    # function to normalize xrd by shifting the peak of the substrate
    # returns edited dataframe

    indx_max = np.argmax(d['y'])
    d['x'] = d['x']-(d['x'][indx_max]-shift_to)
    return d
    

def break_files_into_type(file_list):
    rc_files=[]
    xrr_files=[]
    xrd_files=[]
    for file in file_list:
        if 'rc' in file or 'RC' in file:
            rc_files.append(file)
        elif 'xrr' in file or 'XRR' in file:
            xrr_files.append(file)
        else:
            xrd_files.append(file)
    return rc_files, xrr_files, xrd_files

def plotXRDdat(d,axis='none',semilog=True, colorset='file'):
    #Get plot settings from config file
    with open('plotconfig.json') as config_file:
        plot_settings= json.load(config_file)
    #print(plot_settings)
    #  
    if axis == 'none':
        fig,ax=plt.subplots()
    else:
        ax=axis

    mpl.style.use('XRDplots')
    if colorset == 'file':
        color=plot_settings["plot_style"]["linecolor"]
    else:
        color=colorset

    d.linename=d.name.split('\\')[-1].split('proc')[0]
    if semilog:
        ax.semilogy(d.dat['x'],d.dat['y'],linestyle=plot_settings["plot_style"]["linetype"],
        color=color,
        linewidth=plot_settings["plot_style"]["linewidth"],
        label=d.linename)
        ax.set_xlabel(r'2$\theta$ - $\omega$')
    else:
        ax.plot(d.dat['x'],d.dat['y'],linestyle=plot_settings["plot_style"]["linetype"],
        color=color,
        linewidth=plot_settings["plot_style"]["linewidth"],
        label=d.linename)
        ax.set_xlabel('$\omega$')
    if plot_settings["plot_style"]["legend"]:
        ax.legend()
    ax.set_ylabel('Intensity (cps)')

#def make_current_plot_file(d,plot_settings):

def compare_between_folders(folder_list,root_folder='',file_filter='none', shift_substrate_peak_value=-99,multiply_each_by=1):
    file_extension='proc.xrd'
    file_list=[]
    full_folder_list=[root_folder+folder for folder in folder_list]
    for folder in full_folder_list:
        for file_name in os.listdir(folder):
            if file_extension in file_name:
                if file_filter == 'none':
                    file_list.append(os.path.join(folder, file_name))
                else:
                    if file_filter in file_name:
                        file_list.append(os.path.join(folder, file_name))

    rc_files, xrr_files, xrd_files = break_files_into_type(file_list)
    maxnumlines=0
    if len(rc_files) > 0:
        fig_rc,ax_rc=plt.subplots()
        if len(rc_files) > maxnumlines:
            maxnumlines=len(rc_files)
    if len(xrr_files) > 0:
        fig_xrr,ax_xrr=plt.subplots()
        if len(xrr_files) > maxnumlines:
            maxnumlines=len(xrr_files)
    if len(xrd_files) > 0:
        fig_xrd,ax_xrd=plt.subplots()
        if len(xrd_files) > maxnumlines:
            maxnumlines=len(xrd_files)

    colorrange = cm.rainbow(np.linspace(0, 1, maxnumlines))
    for i in range(len(rc_files)):
        color=colorrange[i]
        data_frame=loadXRDdat(rc_files[i])
        data_frame.dat['y']=data_frame.dat['y']*multiply_each_by**i
        plotXRDdat(data_frame, axis=ax_rc, semilog=False, colorset=color)
    for i in range(len(xrr_files)):
        color=colorrange[i]
        data_frame=loadXRDdat(xrr_files[i])
        data_frame.dat['y']=data_frame.dat['y']*multiply_each_by**i
        plotXRDdat(data_frame, axis=ax_xrr, semilog=True, colorset=color)
    for i in range(len(xrd_files)):
        color=colorrange[i]
        data_frame=loadXRDdat(xrd_files[i],shift_substrate_peak_value=shift_substrate_peak_value)
        data_frame.dat['y']=data_frame.dat['y']*multiply_each_by**i
        plotXRDdat(data_frame, axis=ax_xrd, semilog=True, colorset=color)
    plt.show()

# fold_list=[r'\Fe2O3_LNO_6-12-23']
# compare_between_folders(fold_list,root_folder=r'C:\Users\justi\OneDrive\Documents\Material_Characterization\XRD',
#                         shift_substrate_peak_value=38.9495,multiply_each_by=1)

fold_list=[r'\XE381_Pt(3)_Fe2O3(40min)_Al2O3(0001)_500C',
           r'\XE377A_Fe2O3(40min)_Al2O3(0001)_500C']
compare_between_folders(fold_list,root_folder=r'C:\Users\justi\OneDrive\Documents\Material_Characterization\XRD\6-9-23_NSL_XRD',
                        shift_substrate_peak_value=41.68,multiply_each_by=1)
