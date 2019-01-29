import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy import units as u
from photutils import CircularAperture
import matplotlib.patheffects as PathEffects
import sys
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# Run with not flag to ignore interactive mode
# python make_finder.py not
print(sys.argv)
if 'not' in sys.argv:
    do_interactive = False
else:
    do_interactive = True

if do_interactive:
    # Import Image Data
    image_name = input('\n> File name: ')
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

def create_finder(aperture_size_pix, image_radius_pix, arrow_size_wcs, image_upper_std, image_lower_std, target_RA, target_DEC, target_name, target_color, instructions, interactive = True, image_name = '', do_tde = 'n', do_detection = 'y'):
    # For wcs_data variable
    global wcs_data, image_data

    # If using as a standalone function
    if interactive == False:
        file       = fits.open(image_name)
        image_data = file[0].data
        image_head = file[0].header

        try:
            # Set the value of EPOCH to the value of EQUINOX
             image_head.set('EPOCH', image_head['EQUINOX'])
        except:
            pass
        # Read in WCS data
        wcs_data = wcs.WCS(image_head)

        if do_tde == 'y':
            instructions += 'Center on galaxy core'
        if do_detection == 'n':
            instructions += ' \t Transient not in image'

    else:
        # Is the object nuclear?
        do_tde = input("\n> Is the transient nuclear? y/[n] ")
        if not do_tde: do_tde='n'

        if do_tde == 'y':
            instructions += 'Center on galaxy core'

        # Is the object nuclear?
        do_detection = input("\n> Is the transient in the image? [y]/n ")
        if not do_detection: do_detection='y'

        if do_detection == 'n':
            instructions += ' \t Transient not in image'

    # Create Target Aperture
    coord           = SkyCoord(target_RA, target_DEC, unit=(u.hourangle, u.deg))
    coord_pix       = wcs_data.wcs_world2pix(coord.ra.deg, coord.dec.deg, 1)
    target_aperture = CircularAperture(coord_pix, r=aperture_size_pix)

    # Image Information, and calculate background counts
    xmin = int(coord_pix[0] - image_radius_pix)
    xmax = int(coord_pix[0] + image_radius_pix)
    ymin = int(coord_pix[1] - image_radius_pix)
    ymax = int(coord_pix[1] + image_radius_pix)
    cropped_data = image_data[ymin:ymax,xmin:xmax]
    average_background, _, std_background = sigma_clipped_stats(cropped_data, sigma_lower=2.0, sigma_upper=1.0, iters=5)

    # Create Compass
    origin_x_pix,  origin_y_pix  = xmax - (image_radius_pix / 9), ymin + (image_radius_pix / 6)
    origin_x_wcs,  origin_y_wcs  = wcs_data.wcs_pix2world(origin_x_pix, origin_y_pix, 1)
    east_x_shift,  east_y_shift  = wcs_data.wcs_world2pix(origin_x_wcs + arrow_size_wcs / 60, origin_y_wcs, 1)
    north_x_shift, north_y_shift = wcs_data.wcs_world2pix(origin_x_wcs, origin_y_wcs + arrow_size_wcs / 60, 1)

    # Plot
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.imshow(image_data, vmin = average_background-image_upper_std*std_background, vmax = average_background+image_lower_std*std_background, cmap='Greys', origin='lower',interpolation='none')
    plt.tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=False, labeltop=False, labelright=False, labelbottom=False)

    # Target
    aperture = target_aperture.plot(color='yellow', lw = 2)
    label = plt.text(coord_pix[0], coord_pix[1]+(image_radius_pix / 9), target_name, fontweight = 'bold', color = 'k', alpha = 0.8)
    # Band
    color = plt.text(xmin + (image_radius_pix / 9), ymax - (image_radius_pix / 9), target_color + ' band', fontweight = 'bold', color = 'k', alpha = 0.8)

    # Compass
    arrow1 = plt.arrow(origin_x_pix, origin_y_pix, east_x_shift - origin_x_pix, east_y_shift - origin_y_pix, head_width=10, head_length=10, fc='k', ec='k')
    arrow2 = plt.arrow(origin_x_pix, origin_y_pix, north_x_shift - origin_x_pix, north_y_shift - origin_y_pix, head_width=10, head_length=10, fc='k', ec='k')
    north = plt.text(north_x_shift-(image_radius_pix / 30), north_y_shift+(image_radius_pix / 10), 'N', fontweight='bold', color = 'k', alpha = 0.8)
    east  = plt.text(east_x_shift-(image_radius_pix / 10),  east_y_shift-(image_radius_pix / 30), 'E', fontweight='bold', color = 'k', alpha = 0.8)
    size  = plt.text(east_x_shift-0.5*(east_x_shift - origin_x_pix)-(image_radius_pix / 30),  east_y_shift-(image_radius_pix / 10), "1'", fontweight='bold', color = 'k', alpha = 0.8)

    # plot borders
    label.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])
    color.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])
    arrow1.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])
    arrow2.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])
    north.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])
    east.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])
    size.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])

    # Instructions
    plt.xlabel(instructions, fontproperties = 'serif')
    plt.savefig(target_name + '_finder.jpg', dpi = 200, bbox_inches = 'tight')
    plt.clf()

# Plot Parameters
aperture_size_pix = 15   # Size of target aperture
image_radius_pix  = 300  # Radius of image in pixels
arrow_size_wcs    = 1    # Size of arrows in compass in arcmin

image_upper_std   = 4.0  # Image upper std for plotting 
image_lower_std   = 10.0 # Image lower std for plotting

if do_interactive:
    create_finder(aperture_size_pix, image_radius_pix, arrow_size_wcs, image_upper_std, image_lower_std, target_RA, target_DEC, target_name, target_color, instructions)

# Example of non-interactive mode
# create_finder(aperture_size_pix, image_radius_pix, arrow_size_wcs, image_upper_std, image_lower_std, '11:50:58.0924', '10:23:35.5934', 'ZTF18adbyxua', 'g', instructions, interactive = False, image_name = 'ZTF18adbyxua.fits', do_tde = 'y', do_detection = 'y')



