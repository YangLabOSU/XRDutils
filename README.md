# XRDutilis_getdata and XRDutils_plots
Utilities for XRD processing/ plotting in Yang Lab at OSU.

## Usage
There are two command-line interfaces you can use to convert XRD data and plot it.

first change the "root_dir" variable in plotconfig.JSON to your XRD data location (this can be a directory containing subdirectories for each sample with the xrd data). 

Then run
~~~
python XRDutils_getdata.py -sf
~~~
To convert all data in the root directory and generate/ save plots for each subfolder. 

You can run
~~~
python XRDutils_getdata.py -h
~~~
for a list of other options.

To compare specific files/folders containing data, you can run
~~~
python XRDutils_plots.py <file/folder1> <file/folder2> ... -rst
~~~


Here, including the rst flag rewrites over the file list in the plotconfig.JSON file. Alternatively, you can enter the folders/files you want to plot in that JSON file and then simply run 
~~~
python XRDutils_plots.py
~~~
to generate plots comparing them.

The filtering system supports some simple Boolean operations. For example, if you want to plot files in the root folder with 
* subdirectories containing 
    * "Fe2O3(30)" AND "Al2O3" 
    * OR "NiO"
* and only filenames containing
    * "XRD" AND "00012"
    * OR "RC"

You can use the following command:
~~~
python .\XRDutils_plots.py -rst -ff "Fe2O3(30),Al2O3" "NiO" -f "XRD,00012" "RC"
~~~

Note that here the -rst flag sets the file or folder list to be empty. This causes the program to search for data in the root folder and its subdirectories.

## File Naming Conventions
This code assumes NSL data is in the native .xrdml file format. It can also process ECE (Bede) data, and NTW (Bruker) data with the .X01 and .txt file formats, respectively. 

When the plots or getdata script are run on a folder, these file formats are converted to a universal '.proc.xrd' file containing simple x,y data for position and counts. (So a folder that has been processed will contain the original data file in addition to a file with the same name, except for this .proc.xrd extension)

When plotting, 'rc' being in the filename will generate a rocking curve plot, 'xrr' will generate an xrr plot, and neither of these will generate a default 2theta-omega plot. It is not case-sensitive.

Default figures are generated per subfolder, and are saved as the subfolder name followed by xrd, xrr, or rc.

If you give the program specific files to plot with extensions, it requires the processed files (with extension .proc.xrd). If you just give it folders it will automatically search for these files.

# XRDutils_fits

Utilities for "fitting" and visualizing laue oscillations in 2theta-omega scans.

## Usage

As of now this program cannot automatically fit data, but rather shows an easily adjustable simulation of thin film effects such as laue oscillations in 2theta-omega scans. This is particularly useful when there are mutliple interfering layers, which makes simple eyeball analysis difficult. Practically, you could use this program to get a reasonably accurate measurement of lattice parameter and thickness from a 2theta-omega scan of a thin film or stack of thin films. No XRR support yet.

Similar to XRDutils_plots.py, there is a JSON file which holds the settings for the thin film/ substrate stack you want to simulate (fitconfig.json). This can be easily modified on the fly with command line arguments when running the python file, or manually adjusted by changing the json file and running the python file with no arguments. There is also a material database JSON file which stores the lattice parameters for each material (material_database.json).

### Example usage:

The first time you run this, you will need to change the root directory to the one containing your XRD data. Put a back or forward slash at the end:
~~~
python XRDutils_fits.py -r "C:\Users\justi\Research\Data\XRD\" 
~~~

Then it can be used as follows:

~~~
python XRDutils_fits.py "XF139_NiO(30min)_MgO(001)D_3p5in_500C_45W_6%O2/MgO(001)_iCore_TA_FAST_XF139.proc.xrd" -f "NiO 20" -s "MgO"
~~~

This will plot the data file (must be a processed file in x,y format) with a simulation of a 20nm NiO layer on an MgO substrate modelled by a Lorentzian. Then sliders can be used to adjust the fit parameters to match the data. The parameters can then be stored with a button in the GUI (running the python file with parameters will overwrite the previously stored ones though, so watch out). The hkl of the film or substrate can also be specified (normally it is chosen from a default stored in the materials databse file) with parenthesis:

~~~
python XRDutils_fits.py -f "NiO(0 0 2) 20" -s "MgO(0 0 4)"
~~~

When running the python file from the command line, all arguments are optional. The fitconfig file can be manually adjusted to change some options which cannot be changed in the CLI or GUI, such as the substrate fwhm or intensity.