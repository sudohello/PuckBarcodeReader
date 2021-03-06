Using the Source Code - Windows
===============================
This application is written in Python (v3.5) and was developed under Windows but should be portable to other platforms.

The following steps will help you prepare an appropriate Python environment to run this program. These instructions assume that you will use the 32-bit version of Python 3.5.1, but the barcode scanner should also run correctly under other versions of Python (e.g. 2.7, 3.4, 64bit).

* Install the appropriate version of Python by downloading the Windows binary installer from <https://www.python.org/downloads/release/python-351/>
    * You want the one labelled 'Windows x86 MSI installer'
    * During installation, make sure you check ‘Add python.exe to system path’.
    
* The following packages are required:
    * pyperclip
    * enum [only if using Python v2.7]
    * numpy
    * scipy
    * OpenCV
    * PyQt4
    
* Some of these packages can be installed using `pip`. To do this:
    * Open cmd.exe (being sure to ‘Run as Administrator’)
    * Upgrade pip by typing `pip install –-upgrade pip`
    * Install pyperclip by typing `pip install pyperclip`
    * Install enum by typing `pip install enum` [only if using Python 2.7]
    
* The easiest way to install the other packages is to download the precompiled binaries from <http://www.lfd.uci.edu/~gohlke/pythonlibs/>. To install each one, open cmd.exe and type `pip install filename`. Download the most recent version of each for your version of Python (3.5, 32bit), e.g.:
    * numpy-1.11.0+mkl-cp35-cp35m-win32.whl
    * opencv_python-3.1.0-cp35-cp35m-win32.whl
    * scipy-0.17.1-cp35-cp35m-win32.whl
    * PyQt4-4.11.4-cp35-none-win32.whl

NOTE: there is a requirements.txt file that was created for use by the CI server Travis. It works in Travis but it wasn't tested locally. It contains all of the above dependencies except for enum and PyQt4.
    
* Download the source code for the Barcode scanner program from <https://github.com/DiamondLightSource/PuckBarcodeReader> - use the ‘Download ZIP’ link. Open the zip and extract the contents to a suitable folder.

* Open cmd.exe and navigate to the above folder. `cd` into the dls_barcode folder. Then type `python main.py` to run the program.

* To run the tests, you will need to install the nose and mock packages:
   * `pip install nose`
   * `pip install mock`

Running the System Tests
========================
For the paths in the system tests to work with nosetests, the working directory must be the top project folder (i.e. that's how the Travis CI server runs them - see below).

Unfortunately I can't get Pycharm to give me a Nosetests option when I right-click on the top Project directory in the Project tree. The way around this is to manually edit the working directory in the Pycharm Run configuration for "Nosetests in tests" (Run -> Edit Configurations, then look at the entries in the "Python tests" tree) to be the top Project directory, so when we right-click on the tests/ directory and select "Nosetests in tests" it's pointing at the right path! 

Alternatively, we can simply run "nosetests" from the command line, in the top Project directory.

Creating a Self-Contained Executable
====================================
A Python package called [PyInstaller](http://www.pyinstaller.org/) can be used to create a stand-alone windows executable (.exe) file.

Install PyInstaller with `pip install pyinstaller`. Make sure that the correct version of Python is referenced in your system path.

To create the executable file, run the `build.bat` file. This will create the file `bin\barcode.exe`. This will be fairly large (~40 MB). If everything has worked correctly, this single file will be all that is needed to run the barcode scanner application.

Troubles creating Executable

Whe the path to Python on Pyinstaller contains spaces there an error [failed to create process](https://stackoverflow.com/questions/31808180/installing-pyinstaller-via-pip-leads-to-failed-to-create-process/34546220#34546220) occures. 
To get around the porblem call script pyinstaller-script.py.
For example: "C:\Users\Urszula Neuman\AppData\Local\Programs\Python\Python35\python.exe" "C:\Users\Urszula Neuman\AppData\Local\Programs\Python\Python35\Scripts\pyinstaller-script.py" main.py
The result exec file is created in subdirectrory called dist.

NOTE: when creating the executable on a 64bit machine (using Python 3.5.1 32bit) you might get the error ‘No module named pywintypes’. To fix this, try `pip install pypiwin32`.

Continuous Integration
======================
[Travis CI](https://travis-ci.org/) was setup as the Continuous Integration server for this repository. You should be able to login with your GitHub credentials and see the repository there. The configuration file for Travis is .travis.yml in the root directory.

