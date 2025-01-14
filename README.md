# XRDutilis
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
This code assumes NTW data is in the native .xrdml file format. It can also process ECE (Bede) data, and NTW (Bruker) data with the .X01 and .txt file formats, respectively. 

When the plots or getdata script are run on a folder, these file formats are converted to a universal '.proc.xrd' file containing simple x,y data for position and counts. (So a folder that has been processed will contain the original data file in addition to a file with the same name, except for this .proc.xrd extension)

When plotting, 'rc' being in the filename will generate a rocking curve plot, 'xrr' will generate an xrr plot, and neither of these will generate a default 2theta-omega plot. It is not case-sensitive.

Default figures are generated per subfolder, and are saved as the subfolder name followed by xrd, xrr, or rc.

If you give the program specific files to plot with extensions, it requires the processed files (with extension .proc.xrd). If you just give it folders it will automatically search for these files.