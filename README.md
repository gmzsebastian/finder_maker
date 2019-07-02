## Finder Maker

There are two scripts to create finders from either A) an image you have, or B) an image of a TNS or ZTF transient that you don't have that you want to download from PS1.

First install it with `python setup.py install`, and then you can run it like this:
```
make_finder.py image_name.fits
```

```
get_finder.py SN2016iet
```

```
get_finder.py 2018hyz
```

```
get_finder.py ZTF18ablvime
```

Or you can run without specifying the object name, you will be prompted as the first step.

The result will be an image like this:
<p align="center"><img src="AT_2018hti_finder.jpg" align="center" alt="2017gwm" width="900"/></p>
Additional instructions can be added to the xlabel.

You will be prompted if you want to change the target Name, RA, DEC, filter band, image size, and if you want to add an offset/guide star.

If you would rather use it as a package:

```from finder_maker import create_finder```
