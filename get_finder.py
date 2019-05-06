import numpy as np
import matplotlib.pyplot as plt
from astropy.nddata import CCDData
from astropy import wcs
from reproject import reproject_interp
import json
import sys
from functions import *

script = np.where(['_finder.py' in i for i in sys.argv])[0][0]
if len(sys.argv) > script + 1:
    object_name = sys.argv[script + 1]
else:
    # Set the target name
    object_name = input('\n> File name: ')

# Set the color to the default
color = 'g'

# Set the target name to the default, or specify your own?
if object_name != '':
    do_name = input('\n> Set target name to %s? [y]/n '%object_name)
    if not do_name: do_name='y'
else:
    do_name = 'n'

if do_name != 'y':
    object_name = input('\n> Specify target name: ')

# Set the target color to the default, or specify your own?
if color != '':
    do_color = input("\n> Set target band to '%s'? [y]/n "%color)
    if not do_color: do_color='y'
else:
    do_color = 'n'

if do_color != 'y':
    color = input('\n> Specify target band: ')

# Extract RA and DEC
if 'ZTF' in object_name:
    print('Querying ZTF...')
    ra, dec = querry_mars(object_name)
    object_type = ''
else:
    print('Querying TNS...')
    ra, dec, object_type = query_TNS(object_name)

# Add instructions
instructions = ''

# Is the object nuclear?
if object_type == 'TDE':
    do_tde = input("\n> Is the transient nuclear? [y]/n ")
    if not do_tde: do_tde='y'
else:
    do_tde = input("\n> Is the transient nuclear? y/[n] ")
    if not do_tde: do_tde='n'

if do_tde == 'y':
    instructions += 'Center on galaxy core'

# Is the object nuclear?
if do_tde == 'n':
    do_detection = input("\n> Is the transient in the image? y/[n] ")
    if not do_detection: do_detection='n'

    if do_detection == 'n':
        instructions += '      Transient not in image'

# Set the size of the image in pixels
out_size = 500

do_size = input("\n> Set image radius to %s pixels? [y]/n "%out_size)
if not do_size: do_size='y'

if do_size != 'y':
    out_size = input('\n> Specify image radius in pixels: ')

# Add a guide/offset star?
do_offset = input("\n> Do you wish to add a guide/offset star? y/[n] ")
if not do_offset: do_offset='n'

if do_offset != 'n':
    offset_coords = input('\n> Specify guide star RA and DEC: ')
else:
    offset_coords = ''

# Generate the Template
try:
    wcs_object, refdata = generate_template(ra, dec, color, object_name, int(out_size) * 3, image_radius = 250)
    continue_run = True
except:
    print('Object Probably not in 3PI')
    continue_run = False

# Plot Parameters
aperture_size_pix = 10   # Size of target aperture
arrow_size_wcs    = 1    # Size of arrows in compass in arcmin
image_upper_std   = 4.0  # Image upper std for plotting 
image_lower_std   = 10.0 # Image lower std for plotting
print(out_size)

if continue_run:
    create_finder(aperture_size_pix, int(out_size), arrow_size_wcs, image_upper_std, image_lower_std, ra, dec, object_name, color, instructions, wcs_data = wcs_object, image_data = refdata, offset_coords = offset_coords)
