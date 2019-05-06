## Finder Maker

There are two scripts to create finders from either A) an image you have, or B) an image of a TNS or ZTF transient that you don't have that you want to download from PS1.

You can run it like this:
```
python make_finder.py image_name.fits
```

```
python get_finder.py SN2016iet
```

```
python get_finder.py 2018hyz
```

```
python get_finder.py ZTF18ablvime
```

Or you can run without specifying the object name, you will be prompted as the first step. If you want to run this from any directory you can reference the script in your `bash_profile` with something like:

`alias getfinder='ipython /Users/path_to_script/get_finder.py'`

`alias makefinder='ipython /Users/path_to_script/make_finder.py`

then run from the terminal with something like `gefinder AT2016iet`.

The result will be an image like this:
<p align="center"><img src="AT_2018hti_finder.jpg" align="center" alt="2017gwm" width="900"/></p>
Additional instructions can be added to the xlabel

You will be prompted if you want to change the target Name, RA, DEC, filter band, image size, and if you want to add an offset/guide star.
