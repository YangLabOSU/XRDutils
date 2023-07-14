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

## File Naming Conventions
This code assumes NTW data is in the native .xrdml file format. It can also process ECE (Bede) data, and NTW (Bruker) data with the .X01 and .txt file formats, respectively. 

When the plots or getdata script are run on a folder, these file formats are converted to a universal '.proc.xrd' file containing simple x,y data for position and counts. (So a folder that has been processed will contain the original data file in addition to a file with the same name, except for this .proc.xrd extension)

When plotting, 'rc' being in the filename will generate a rocking curve plot, 'xrr' will generate an xrr plot, and neither of these will generate a default 2theta-omega plot. It is not case-sensitive.

Default figures are generated per subfolder, and are saved as the subfolder name followed by xrd, xrr, or rc.