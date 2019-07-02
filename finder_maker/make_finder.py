#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy import wcs
import requests
from finder_maker import create_finder
import sys

script = np.where(['_finder.py' in i for i in sys.argv])[0][0]
if len(sys.argv) > script + 1:
    image_name = sys.argv[script + 1]
else:
    image_name = input('\n> File name: ')

# Import Image Data
file       = fits.open(image_name)
image_data = file[0].data
image_head = file[0].header

# FLWO needs to overwrite EPOCH label for WCS data
try:
    # Set the value of EPOCH to the value of EQUINOX
     image_head.set('EPOCH', image_head['EQUINOX'])
except:
    pass
# Read in WCS data
wcs_data = wcs.WCS(image_head)

# Try to read in target name information
try:
    target_name = image_head['OBJECT']
except:
    target_name = ''

# Set the target name to the default, or specify your own?
if target_name != '':
    do_name = input('\n> Set target name to %s? [y]/n '%target_name)
    if not do_name: do_name='y'
else:
    do_name = 'n'

if do_name != 'y':
    target_name = input('\n> Specify target name: ')

# Try to read in target coordinates
try:
    target_RA  = image_head['RA']
    target_DEC = image_head['DEC']
except:
    target_RA  = ''
    target_DEC = ''

# Set the target name to the default, or specify your own?
if target_RA != '':
    do_coords = input('\n> Set target coordinates to  %s  %s? [y]/n '%(target_RA, target_DEC))
    if not do_coords: do_coords='y'
else:
    do_coords = 'n'

if do_coords != 'y':
    target_RA  = input('\n> Specify target RA: ')
    target_DEC = input('\n> Specify target DEC: ')

# Try to read in target band
try:
    target_color = image_head['FILTER']
except:
    target_color = ''

# Set the target name to the default, or specify your own?
if target_color != '':
    do_color = input("\n> Set target band to '%s'? [y]/n "%target_color)
    if not do_color: do_color='y'
else:
    do_color = 'n'

if do_color != 'y':
    target_color = input('\n> Specify target band: ')

# Add instructions
instructions = ''
do_detection = 'y'

# Is the object nuclear?
do_tde = input("\n> Is the transient nuclear? y/[n] ")
if not do_tde: do_tde='n'

if do_tde == 'y':
    instructions += 'Center on galaxy core'

# Is the object in the image?
if do_tde == 'n':
    do_detection = input("\n> Is the transient in the image? [y]/n ")
    if not do_detection: do_detection='y'

    if do_detection == 'n':
        instructions += '      Transient not in image'

# Set the size of the image in pixels
image_radius_pix = 400

do_size = input("\n> Set image radius to %s pixels? [y]/n "%image_radius_pix)
if not do_size: do_size='y'

if do_size != 'y':
    image_radius_pix = input('\n> Specify image radius in pixels: ')

# Add a guide/offset star?
do_offset = input("\n> Do you wish to add a guide/offset star? y/[n] ")
if not do_offset: do_offset='n'

if do_offset != 'n':
    offset_coords = input('\n> Specify guide star RA and DEC: ')
else:
    offset_coords = ''

# Plot Parameters
aperture_size_pix = 10   # Size of target aperture
arrow_size_wcs    = 1    # Size of arrows in compass in arcmin
image_upper_std   = 4.0  # Image upper std for plotting 
image_lower_std   = 10.0 # Image lower std for plotting

create_finder(aperture_size_pix, int(image_radius_pix), arrow_size_wcs, image_upper_std, image_lower_std, target_RA, target_DEC, target_name, target_color, instructions, wcs_data = wcs_data, image_data = image_data, offset_coords = offset_coords)
