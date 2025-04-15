import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import matplotlib as mpl
import argparse
import json
import os
# from XRDutils_getdata import *
import matplotlib
from numpy import pi, sin
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox

plt.rcParams['savefig.dpi']=1000
# plt.rcParams.update({'figure.autolayout': True})
font = {'family' : 'Times New Roman',
    'size'   : 10}

matplotlib.rc('font', **font)
#Get plot settings and material database
with open('fitconfig.json') as config_file:
    fit_settings= json.load(config_file)
with open('material_database.json') as material_database_file:
    matdb= json.load(material_database_file)

def populate_fit_settings(args,plot_settings):
    substrates=[]
    films=[]
    if args['file_name'] != []:
        fit_settings['file_name']=args['file_name']
    if args['substrates'] != None:
        for substrate_argstr in args['substrates']:
            substrate_type =  substrate_argstr.split(' ')[0].split('(')[0]
            name='not found'
            for db_mat in matdb['materials']:
                if substrate_type == db_mat['name']:
                    name=substrate_type
                    hkl=db_mat['default_hkl']
                    pass
                if "(" in substrate_argstr:
                    arg_hkl=substrate_argstr.split('(')[-1].split(')')[0]
                    hkl=list(map(int, arg_hkl.split(' ')))
            if name=='not found':
                raise ValueError("Material not found in material_database.json! Please add it first.")
            new_substrate = {
                                    "name": name,
                                    "hkl": hkl,
                                    "fwhm": 0.0001,
                                    "intensity": 1e5
                                }
            substrates.append(new_substrate)
        if len(substrates)>0:
            fit_settings["layers"]['substrates']=substrates
    if args['films'] != None:
        for film_argstr in args['films']:
            film_type =  film_argstr.split(' ')[0].split('(')[0]
            name='not found'
            for db_mat in matdb['materials']:
                if film_type == db_mat['name']:
                    name=film_type
                    hkl=db_mat['default_hkl']
                    thickness=30
                    pass
                if "(" in film_argstr:
                    arg_hkl=film_argstr.split('(')[-1].split(')')[0]
                    hkl=list(map(int, arg_hkl.split(' ')))
                if " " in film_argstr.split(')')[-1]:
                    thickness=float(film_argstr.split(')')[-1].split(' ')[-1])

            if name=='not found':
                raise ValueError("Material not found in material_database.json! Please add it first.")
            new_film = {
                                    "name": name,
                                    "hkl": hkl,
                                    "thickness": thickness,
                                    "lattice_constant_percent": 100,
                                    "intensity": 1e2
                                }
            films.append(new_film)
        if len(films)>0:
            fit_settings["layers"]['films']=films
            
def q_to_twotheta(q,Kalpha=1.5406):
    return 2*np.arcsin(q*Kalpha/(4*np.pi))*180/np.pi

def twotheta_to_q(twotheta,Kalpha=1.5406):
    return np.sin(np.radians(twotheta)/2)*4*np.pi/Kalpha

def d_to_q(d,Kalpha=1.5406):
    return 2*np.pi/d

def q_to_d(q,Kalpha=1.5406):
    return 2*np.pi/q

def calc_fully_strained(a_bulk,c_bulk,a_substrate, v=0.3):
    parallel_strain=(a_substrate-a_bulk)/a_bulk

    c_strained=c_bulk*(1-2*v*parallel_strain/(1-v))
    return parallel_strain, c_strained

def calc_relaxation_from_c(c,c_relaxed,c_strained):
    relaxation=100*(c-c_strained)/(c_relaxed-c_strained)
    return relaxation

def substrate_amplitude(q, d_sub, ss_peak_intensity=1,fwhm_ss=1):
    q_sub=d_to_q(d_sub)
    A_scale = np.sqrt(ss_peak_intensity) * fwhm_ss
    lorentz = 1 / (q - q_sub + 1j * fwhm_ss)
    return A_scale*lorentz * np.exp(1j * -np.pi/2)

def drop_zero(d):
    d = d[d.y != 0]
    return d

def loadXRDdat(fname):
    #function to load data from processed files
    with open(fname) as file:
        for num, line in enumerate(file, 1):
            if 'x,' in line:
                hlength=num-1
                
    #get the scan data using the header information gathered
    d = pd.read_csv(fname, skiprows=hlength,
                       delimiter=',', engine='python')

    d=drop_zero(d)
    return d

def calc_d_from_hkl(a,c,hkl,unitcell="orthorhombic"):
    h=hkl[0]
    k=hkl[1]
    l=hkl[2]
    if not unitcell == "orthorhombic":
        raise
    return np.sqrt(1/(h**2/a**2+k**2/a**2+l**2/c**2))

def calc_c_from_d_hkl(d,hkl,unitcell="cubic"):
    h=hkl[0]
    k=hkl[1]
    l=hkl[2]
    if not unitcell == "cubic":
        raise
    return d*np.sqrt(h**2+k**2+l**2)

def get_material_properties(matname,matdb):
    name='not found'
    for db_mat in matdb['materials']:
        if matname == db_mat['name']:
            return db_mat

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Command Line XRD fitting',
                                     description='Fits XRD files using a CLI.')
    parser.add_argument('file_name',type=str, action='store', nargs='*')
    parser.add_argument('-r','--root_directory',type=str, action='store')
    parser.add_argument('-s','--substrates',type=str, action='store', nargs='*')
    parser.add_argument('-f','--films',type=str, action='store', nargs='*')
    parser.add_argument('-sf','--save_figures', action='store_true', default=False)
    args = parser.parse_args()
    args=vars(args)
    print(args['substrates'])
    populate_fit_settings(args,fit_settings)
    print(json.dumps(args, indent=4, sort_keys=True))

    if type(fit_settings["file_name"]) == list:
        d=loadXRDdat(fit_settings["root_directory"]+fit_settings["file_name"][0])
    else:
        d=loadXRDdat(fit_settings["root_directory"]+fit_settings["file_name"])


    with open("fitconfig.json", "w") as write_fit_settings:
        write_fit_settings.write(json.dumps(fit_settings, indent=4, sort_keys=True))
        write_fit_settings.close()

    # Load film properties and material properties into lists to give the simulation function (should be faster to load these first)
    film_props=fit_settings["layers"]['films']
    film_mat_props=[]
    for fit_settings_film in film_props:
        film_mat_props.append(get_material_properties(fit_settings_film["name"],matdb))

    # Load substrate properties and material properties into lists to give the simulation function (should be faster to load these first)
    ss_props=fit_settings["layers"]['substrates']
    ss_mat_props=[]
    for fit_settings_ss in ss_props:
        ss_mat_props.append(get_material_properties(fit_settings_ss["name"],matdb))
    
    # Calculate strain relaxation and print
    # 4/15/25 this only works for c oriented substrates, and it only reports it for the top substrate layer and bottom film layer
    in_plane_strain,c_fullystrained=calc_fully_strained(film_mat_props[0]["a_lattice_constant"],
                                                        film_mat_props[0]["c_lattice_constant"],
                                                        ss_mat_props[-1]["a_lattice_constant"],
                                                        v=film_mat_props[0]["poisson_ratio"])
    print('for {}({} {} {}) on {}({} {} {}) the in-plane strain is {}A\nthe fully strained c parameter is {}A'.format(film_mat_props[0]["name"],
                                                                                                                      *film_props[0]["hkl"],
                                                                                                                      ss_mat_props[0]["name"],
                                                                                                                      *ss_props[0]["hkl"],
                                                                                                                      in_plane_strain,c_fullystrained))
    
    def simulate_xrd(num_points=1000, fit_settings=fit_settings, film_mats=film_mat_props, ss_mats=ss_mat_props, 
                     startdeg=np.min(d.x),stopdeg=np.max(d.x)):
        # Function for simulating xrd 2theta-omega scans
        # Define the function using the defaults from the fit settings when the CLI is run. This way we don't need to call it with so many arguments
        
        startq=twotheta_to_q(startdeg)
        stopq=twotheta_to_q(stopdeg)

        # Set up film d spacings for simulation. Just treat whole film stack as a continuous number of planes stacked ontop of eachother with 
        # material defined d-spacings
        layer_ds=[]
        layer_is=[]
        film_ds=[]
        for i in range(len(fit_settings["layers"]['films'])):
            film=fit_settings["layers"]['films'][i]
            film_mat=film_mats[i]
            film_d=(film["lattice_constant_percent"]/100)*calc_d_from_hkl(film_mat["a_lattice_constant"],film_mat["c_lattice_constant"],film["hkl"])
            film_ds.append(film_d)
            film_planes=round(film["thickness"]/(film_d/10))
            layer_ds=np.hstack([layer_ds,np.ones(film_planes)*film_d])
            layer_is=np.hstack([layer_is,np.ones(film_planes)*np.sqrt(film["intensity"])/film_planes])
        number_of_planes=len(layer_ds)
        q_range = np.linspace(startq, stopq, num_points)  # Scattering vector range to plot

        # Compute Laue oscillations of films using interference condition
        amplitude=0+0j
        for layer_number in range(number_of_planes):
            amplitude += layer_is[layer_number]*np.exp(1j*q_range*layer_ds[layer_number]*layer_number)
        
        # Add amplitudes of substrates
        for i in range(len(fit_settings["layers"]['substrates'])):
            ss=fit_settings["layers"]['substrates'][i]
            ss_mat=ss_mats[i]
            amplitude += substrate_amplitude(q_range, d_sub=calc_d_from_hkl(ss_mat["a_lattice_constant"],ss_mat["c_lattice_constant"],ss["hkl"]), 
                    fwhm_ss=ss["fwhm"], ss_peak_intensity=ss["intensity"])
            
        # Calculate total intensity
        intensity = np.abs(amplitude)**2

        
        return q_to_twotheta(q_range), intensity+fit_settings["background_intensity"], film_ds
    



    axis_color = 'lightgoldenrodyellow'

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Adjust the subplots region to leave some space for the sliders and buttons
    fig.subplots_adjust(left=0.3, bottom=0.4)

    twothetas, Is, film_ds =simulate_xrd()
    # Draw the initial plot
    # The 'line' variable is used for modifying the line later
    [line2]=ax.semilogy(d.x,d.y)
    [line] = ax.semilogy(twothetas, Is, linewidth=1, color='red')
    def make_legend_str(film_ds,fit_settings,film_mats):
        legstr=''
        for i in range(len(film_ds)):
            film=fit_settings["layers"]["films"][i]
            film_mat=film_mats[i]
            film_d=film_ds[i]
            if i>0:
                legstr+='\n'
            legstr+='{}: {:.3f}deg {:.5f}A'.format(film["name"],q_to_twotheta(film_d),calc_c_from_d_hkl(film_d,film["hkl"]))
        return legstr
    print(make_legend_str(film_ds,fit_settings,film_mat_props))
    ax.legend([make_legend_str(film_ds,fit_settings,film_mat_props)])
    # ax.set_xlim([0, 1])
    # ax.set_ylim([-10, 10])

    # Add two sliders for tweaking the parameters

    # Define an axes area and draw a slider in its
    slider_height=0.03
    slider_gap=0.05
    button_width=0.015
    button_height=0.015
    button_vertical_offset=0.025
    top_slider_y0=0.33
    slider_x=0.25
    slider_width=0.4
    c_sliders=[]
    c_slider_axs=[]
    i_sliders=[]
    i_slider_axs=[]
    t_sliders=[]
    t_slider_axs=[]
    for i in range(len(fit_settings["layers"]["films"])):
        top_slider_y=top_slider_y0-slider_gap*i*2
        mid_slider_y=top_slider_y-slider_gap
        film=fit_settings["layers"]["films"][i]
        c_slider_ax  = fig.add_axes([slider_x, top_slider_y-slider_height/2, slider_width+slider_x, slider_height], facecolor=axis_color)
        c_slider = Slider(c_slider_ax, 'c  {}'.format(film["name"]), 95.0, 105.0, valinit=film["lattice_constant_percent"])
        c_sliders.append(c_slider)
        c_slider_axs.append(c_slider_ax)
        t_slider_ax  = fig.add_axes([slider_x, mid_slider_y-slider_height/2, slider_width+slider_x, slider_height], facecolor=axis_color)
        t_slider = Slider(t_slider_ax, 't  {}'.format(film["name"]), 0, 100, valinit=film["thickness"])
        t_sliders.append(t_slider)
        t_slider_axs.append(t_slider_ax)
        i_slider_ax = fig.add_axes([0.02+slider_gap*i,0.1,slider_height/2,slider_width*2], facecolor=axis_color)
        i_slider = Slider(i_slider_ax, 'i \n{}'.format(film["name"]), -1, 4.5, valinit=np.log10(film["intensity"]),orientation='vertical')
        i_sliders.append(i_slider)
        i_slider_axs.append(i_slider_ax)

    # Define an action for modifying the line when any slider's value changes
    def sliders_on_changed(val):
        for i in range(len(c_sliders)):
            slider=c_sliders[i]
            fit_settings["layers"]["films"][i]["lattice_constant_percent"]=slider.val
        for i in range(len(i_sliders)):
            slider=i_sliders[i]
            fit_settings["layers"]["films"][i]["intensity"]=10**slider.val
        for i in range(len(t_sliders)):
            slider=t_sliders[i]
            fit_settings["layers"]["films"][i]["thickness"]=slider.val
        twothetas, Is, film_ds =simulate_xrd(fit_settings=fit_settings)
        line.set_ydata(Is)
        ax.legend([make_legend_str(film_ds,fit_settings,film_mat_props)])
        fig.canvas.draw_idle()
    for i in range(len(c_sliders)):
        c_sliders[i].on_changed(sliders_on_changed)
    for i in range(len(i_sliders)):
        i_sliders[i].on_changed(sliders_on_changed)
    for i in range(len(t_sliders)):
        t_sliders[i].on_changed(sliders_on_changed)

    # Add a button for resetting the parameters
    reset_button_ax = fig.add_axes([0.8, 0.005, 0.15, 0.045])
    reset_button = Button(reset_button_ax, 'Reset', color=axis_color, hovercolor='0.975')
    def reset_button_on_clicked(mouse_event):
        for i in range(len(c_sliders)):
            c_sliders[i].reset()
        for i in range(len(i_sliders)):
            i_sliders[i].reset()
        for i in range(len(t_sliders)):
            t_sliders[i].reset()
    reset_button.on_clicked(reset_button_on_clicked)

    # Add a button for saving the parameters
    save_button_ax = fig.add_axes([0.1, 0.005, 0.3, 0.045])
    save_button = Button(save_button_ax, 'Save Params', color=axis_color, hovercolor='0.975')
    def save_params_on_clicked(mouse_event):
        with open("./fitconfig.json", "w") as write_fit_settings:
            write_fit_settings.write(json.dumps(fit_settings, indent=4, sort_keys=True))
            write_fit_settings.close()
            print("saving parameters:")
            print(json.dumps(fit_settings, indent=4, sort_keys=True))
        
    save_button.on_clicked(save_params_on_clicked)

    plt.show()