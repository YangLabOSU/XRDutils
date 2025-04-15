import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import matplotlib as mpl
import argparse
import json
import os
from XRDutils_getdata import *
import matplotlib

plt.rcParams['savefig.dpi']=1000
plt.rcParams.update({'figure.autolayout': True})
font = {'family' : 'Times New Roman',
    'size'   : 16}

matplotlib.rc('font', **font)
#Get plot settings from config file
with open('plotconfig.json') as config_file:
    plot_settings= json.load(config_file)

def populate_plot_settings(args,plot_settings):
    if bool(args['reset_file_list']):
        plot_settings['file_list']=args['file_or_folder_names']
        if args['label_names'] != 'none':
            plot_settings['label_list']=args['label_names']
    else:
        plot_settings['file_list'] += args['file_or_folder_names']
        if args['label_names'] != 'none':
            plot_settings['label_list']+=args['label_names']

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
    d.dat=drop_zero(d.dat)
    return d

def shift_substrate_peak(d,shift_to):
    # function to normalize xrd by shifting the peak of the substrate
    # returns edited dataframe

    indx_max = np.argmax(d['y'])
    d['x'] = d['x']-(d['x'][indx_max]-shift_to)
    return d

def drop_zero(d):
    d = d[d.y != 0]
    return d
    
def convert_to_forwardslash(string_list):
    new_string_list=[]
    for string in string_list:
        new_string_list.append(string.replace('\\','/'))
    return new_string_list

def break_files_into_type(file_list):
    rc_files=[]
    xrr_files=[]
    xrd_files=[]
    for file in file_list:
        file_name=file.split('/')[-1]
        if 'rc' in file_name or 'RC' in file_name:
            rc_files.append(file)
        elif 'xrr' in file_name or 'XRR' in file_name:
            xrr_files.append(file)
        else:
            xrd_files.append(file)
    return rc_files, xrr_files, xrd_files

def plotXRDdat(d,axis='none',semilog=True, xlabel=r'2$\theta$ - $\omega$', colorset=-999, custom_label='none'):
    #  
    if axis == 'none':
        fig,ax=plt.subplots()
    else:
        ax=axis
    ax.set_xlabel(xlabel)

    # mpl.style.use('XRDplots')
    if colorset.dtype == -999:
        color=plot_settings["plot_style"]["linecolor"]
    else:
        color=colorset

    if custom_label == 'none':
        d.linename=d.name.split('/')[-2]
    else:
        d.linename=custom_label
    if semilog:
        ax.semilogy(d.dat['x'],d.dat['y'],linestyle=plot_settings["plot_style"]["linetype"],
        color=color,
        linewidth=plot_settings["plot_style"]["linewidth"],
        label=d.linename)
    else:
        ax.plot(d.dat['x'],d.dat['y'],linestyle=plot_settings["plot_style"]["linetype"],
        color=color,
        linewidth=plot_settings["plot_style"]["linewidth"],
        label=d.linename)
    if plot_settings["plot_style"]["legend"]:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], prop={'size': plot_settings['plot_style']['legend_fontsize']})
    ax.set_ylabel('Intensity (cps)')

#def make_current_plot_file(d,plot_settings):

def compare_between_folders_or_files(list_input,label_list=[],root_folder='',file_filter_string='none',folder_filter_string='none', shift_substrate_peak_value=-99,
                                     multiply_each_by=1, showplots=False, saveplots=True):
    file_extension='proc.xrd'
    folder_list=[]
    file_list=[]
    file_filters=[]
    folder_filters=[]
    for f in file_filter_string:
        file_filters.append(f.split(','))
    for f in folder_filter_string:
        folder_filters.append(f.split(','))
    # print(file_filters)
    # print(folder_filters)
    if len(list_input) == 0:
        list_input=[""]
    for input_string in list_input:
        if file_extension in input_string:
            file_list.append(root_folder + input_string)
        else:
            full_folder_path=root_folder+input_string
            getdatainfolder(full_folder_path, sdsearch=True, repl=False)
            for subdirectory,directories,file_names in os.walk(full_folder_path):
                for file_name in file_names:
                    full_file_address=subdirectory+os.sep+file_name
                    if file_extension in file_name:
                        if folder_filter_string == 'none':
                            if file_filter_string == 'none':
                                file_list.append(full_file_address)
                            else:
                                for file_filter_and in file_filters:
                                    if all (string_filter in file_name for string_filter in file_filter_and):
                                        file_list.append(full_file_address)
                        else:
                            for folder_filter_and in folder_filters:
                                if all (string_filter in subdirectory for string_filter in folder_filter_and):
                                    if file_filter_string == 'none':
                                        file_list.append(full_file_address)
                                    else:
                                        for file_filter_and in file_filters:
                                            if all (string_filter in file_name for string_filter in file_filter_and):
                                                file_list.append(full_file_address)

    file_list=convert_to_forwardslash(file_list)

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

    colorrange = cm.brg(np.linspace(0, 0.9, maxnumlines))
    for i in range(len(rc_files)):
        if len(label_list)==len(rc_files):
            custom_label=label_list[i]
        else:
            custom_label='none'
        color=colorrange[i]
        data_frame=loadXRDdat(rc_files[i],shift_substrate_peak_value=shift_substrate_peak_value)
        data_frame.dat['y']=data_frame.dat['y']-multiply_each_by/10*i
        plotXRDdat(data_frame, axis=ax_rc, semilog=False, colorset=color, xlabel='$\omega$', custom_label=custom_label)
    for i in range(len(xrr_files)):
        if len(label_list)==len(xrr_files):
            custom_label=label_list[i]
        else:
            custom_label='none'
        color=colorrange[i]
        data_frame=loadXRDdat(xrr_files[i])
        data_frame.dat['y']=data_frame.dat['y']*multiply_each_by**i
        plotXRDdat(data_frame, axis=ax_xrr, semilog=True, colorset=color, xlabel=r'$\omega$ - 2$\theta$', custom_label=custom_label)
    for i in range(len(xrd_files)):
        if len(label_list)==len(xrd_files):
            custom_label=label_list[i]
        else:
            custom_label='none'
        color=colorrange[i]
        data_frame=loadXRDdat(xrd_files[i],shift_substrate_peak_value=shift_substrate_peak_value)
        data_frame.dat['y']=data_frame.dat['y']*multiply_each_by**i
        plotXRDdat(data_frame, axis=ax_xrd, semilog=True, colorset=color, custom_label=custom_label)
    if showplots:
        plt.show()
    if saveplots:
        savloc=full_folder_path+'/'+full_folder_path.split('/')[-1]
        print('saving figures to {}...'.format(savloc))
        if len(rc_files)>0:
            fig_rc.savefig(full_folder_path+'/'+full_folder_path.split('/')[-1]+'_RC.png',dpi=300)
        if len(xrr_files)>0:
            fig_xrr.savefig(full_folder_path+'/'+full_folder_path.split('/')[-1]+'_xrr.png',dpi=300)
        if len(xrd_files)>0:
            fig_xrd.savefig(full_folder_path+'/'+full_folder_path.split('/')[-1]+'_xrd.png',dpi=300)
        # plt.close('all')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Command Line XRD plotter',
                                     description='Plots XRD files using a CLI.' + 
                                     ' Can convert from NSL, NTW, and ece file formats.')
    parser.add_argument('file_or_folder_names',type=str, action='store', nargs='*')
    parser.add_argument('-l','--label_names', type=str,default='none', action='store', nargs='*')
    parser.add_argument('-r','--root_directory',type=str, action='store')
    parser.add_argument('-f','--filename filter',type=str, action='store', default='none', nargs='*')
    parser.add_argument('-ff','--folder filter',type=str, action='store', default='none', nargs='*')
    parser.add_argument('-rst','--reset_file_list', action='store_true', default=False)
    parser.add_argument('-sf','--save_figures', action='store_true', default=False)
    args = parser.parse_args()
    args=vars(args)
    populate_plot_settings(args,plot_settings)
    # print(json.dumps(args, indent=4, sort_keys=True))
    compare_between_folders_or_files(plot_settings['file_list'],root_folder=plot_settings["root_dir"],
                        multiply_each_by=plot_settings['plot_style']['waterfall_step'], file_filter_string=args['filename filter'], 
                        showplots=True, saveplots=args['save_figures'], label_list=plot_settings['label_list'],
                        folder_filter_string=args['folder filter'])

    with open("plotconfig.json", "w") as write_plot_settings:
        write_plot_settings.write(json.dumps(plot_settings, indent=4, sort_keys=True))
        write_plot_settings.close()