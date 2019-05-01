## Finder Maker

There are two scripts to create finders from either A) an image you have, or B) an image of a TNS or ZTF transient that you don't have that you want to download from PS1.

You can run it like this:
```
python local_finder.py image_name.fits
```

```
python local_finder.py SN2016iet
```

```
python local_finder.py 2018hyz
```

```
python local_finder.py ZTF18ablvime
```

Or you can run without specifying the object name, you will be prompted as the first step.

The result will be an image like this:
<p align="center"><img src="AT_2018hti_finder.jpg" align="center" alt="2017gwm" width="900"/></p>
Additional instructions can be added to the xlabel

# Future updates
- Ability to mark offset stars.
