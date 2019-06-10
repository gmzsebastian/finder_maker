import pathlib
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
from astropy.table import Table
from astropy.nddata import CCDData
import os
from astropy.nddata import Cutout2D
from reproject import reproject_interp
from collections import OrderedDict
import json
import warnings

def get_coords(ra_in, dec_in):
    '''
    Convert ra and dec to degrees, regardless
    of whether the input is in 00:00:00 or 0.00
    format
    '''
    try:
        ra_in = float(ra_in)
        dec_in = float(dec_in)
    except:
        pass

    if type(ra_in) == np.str:
        coord = SkyCoord(ra_in + ' ' + dec_in, unit=(u.hourangle, u.deg))
        ra  = coord.ra.deg
        dec = coord.dec.deg
    else:
        coord = SkyCoord(ra_in, dec_in, unit=(u.deg, u.deg))
        ra  = coord.ra.deg
        dec = coord.dec.deg

    return ra, dec

def create_finder(aperture_size_pix, image_radius_pix, arrow_size_wcs, image_upper_std, image_lower_std, ra_in, dec_in, target_name, target_color, instructions, interactive = True, wcs_data = '', image_data = '', offset_coords = ''):
    '''
    Create a finder chart from an image at the specified coordinates

    Parameters
    ---------------
    aperture_size_pix : Size of the aperture in pixels
    image_radius_pix  : Size of the image in pixels
    arrow_size_wcs    : Size of the compass in arcsec
    image_upper_std   : Upper sigma for plotting
    image_lower_std   : Lower sigma for plotting
    ra_in, dec_in     : RA and DEC input
    target_name       : Name of object
    target_color      : Filter color: 'g', 'r', 'i', 'z', or 'y'
    instructions      : Is the transient nuclear or there?
    wcs_data          : wcs variable with coordinate info
    image_data        : CCDData object with data

    Output
    ---------------
    Save the output finder chart
    '''

    target_RA, target_DEC = get_coords(ra_in, dec_in)

    # Create Target Aperture
    print(target_RA, target_DEC)
    coord           = SkyCoord(target_RA, target_DEC, unit=(u.deg, u.deg))
    coord_pix       = wcs_data.wcs_world2pix(coord.ra.deg, coord.dec.deg, 1)
    target_aperture = CircularAperture(coord_pix, r=aperture_size_pix)

    # Image Information, and calculate background counts
    xmin = int(coord_pix[0] - image_radius_pix)
    xmax = int(coord_pix[0] + image_radius_pix)
    ymin = int(coord_pix[1] - image_radius_pix)
    ymax = int(coord_pix[1] + image_radius_pix)
    cropped_data = image_data[ymin:ymax,xmin:xmax]

    python_version = sys.version_info[0]
    if python_version == 3:
        average_background, _, std_background = sigma_clipped_stats(cropped_data, sigma_lower=2.0, sigma_upper=1.0, maxiters=5)
    elif python_version == 2:
        average_background, _, std_background = sigma_clipped_stats(cropped_data, sigma_lower=2.0, sigma_upper=1.0, iters=5)

    # Create Compass
    origin_x_pix,  origin_y_pix  = xmax - (image_radius_pix / 9), ymin + (image_radius_pix / 6)
    origin_x_wcs,  origin_y_wcs  = wcs_data.wcs_pix2world(origin_x_pix, origin_y_pix, 1)
    east_x_shift,  east_y_shift  = wcs_data.wcs_world2pix(origin_x_wcs + arrow_size_wcs / 60, origin_y_wcs, 1)
    north_x_shift, north_y_shift = wcs_data.wcs_world2pix(origin_x_wcs, origin_y_wcs + arrow_size_wcs / 60, 1)

    # Get offset stars coordinates
    if offset_coords != '':
        if ',' in offset_coords:
            good_coords = offset_coords.replace(' ', '').split(',')
        else:
            good_coords = offset_coords.replace('  ', ' ').split(' ')
        # Generate Aperure
        offset_RA, offset_DEC = get_coords(good_coords[0], good_coords[1])
        coord_offset_pix      = wcs_data.wcs_world2pix(offset_RA, offset_DEC, 1)
        offset_aperture       = CircularAperture(coord_offset_pix, r=aperture_size_pix)

        # Plot Offset star 
        offset       = offset_aperture.plot(color='magenta', lw = 0.6)
        offset_label = plt.text(coord_offset_pix[0], coord_offset_pix[1]+(image_radius_pix / 12), 'guide', fontweight = 'bold', color = 'k', alpha = 0.8, fontsize = 9)
        offset_label.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])

    # Plot
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.imshow(image_data, vmin = average_background-image_upper_std*std_background, vmax = average_background+image_lower_std*std_background, cmap='Greys', origin='lower',interpolation='none')
    plt.tick_params(axis='both', left=False, top=False, right=False, bottom=False, labelleft=False, labeltop=False, labelright=False, labelbottom=False)

    # Target
    aperture = target_aperture.plot(color='yellow', lw = 1)
    label = plt.text(coord_pix[0], coord_pix[1]+(image_radius_pix / 12), target_name, fontweight = 'bold', color = 'k', alpha = 0.8)
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

def download_ps1_image(ra, dec, filt, save_template = False, plot_name = '', workdir = '.'):
    '''
    Download Image from PS1 and correct leptitudes back to a linear scale.

    Parameters
    ---------------
    ra, dec       : Coordinates in degrees
    filt          : Filter color 'g', 'r', 'i', 'z', or 'y'
    save_template : Save the template to file?
    plot_name     : Name of the template + .fits
    workdir       : Directory to save files to

    Output
    ---------------
    ccddata : CCDData format of data with WCS
    '''

    # Query a center RA and DEC from PS1 in a specified color
    res = requests.get('http://ps1images.stsci.edu/cgi-bin/ps1filenames.py',
                 params={'ra': ra, 'dec': dec, 'filters': filt})

    # Get the image and save it into hdulist
    t       = Table.read(res.text, format='ascii')
    res     = requests.get('http://ps1images.stsci.edu' + t['filename'][0])
    hdulist = fits.open(BytesIO(res.content))

    # Linearize from leptitudes
    boffset = hdulist[1].header['boffset']
    bsoften = hdulist[1].header['bsoften']
    linear  = boffset + bsoften * 2 * np.sinh(hdulist[1].data * np.log(10.) / 2.5)
    ccddata = CCDData(linear, wcs=wcs.WCS(hdulist[1].header), unit='adu')

    # Save the template to file
    if save_template:
        template_filename = os.path.join(workdir, plot_name + '.fits')
        ccddata.write(template_filename, overwrite=True)

    return ccddata

def check_corner(data, ra_mod, dec_mod):
    '''
    Check if the specified ra_mod and dec_mod exsist in the data
    file.
    '''

    # Convert RA and DEC to x and y pixels
    x_corner, y_corner = data.wcs.all_world2pix(ra_mod, dec_mod, 1.0)

    # Check if coordinates exist in image
    size = (1, 1) # size of cutout in pixels
    try:
        cutout = Cutout2D(data, (x_corner, y_corner), size)
    except:
        print('Corner (%s, %s) not in template'%(x_corner, y_corner))
        return False, ra_mod, dec_mod
    return True, ra_mod, dec_mod

def create_wcs_object(center_ra, center_dec, out_size = 1500, scale = 0.35):
    '''
    Create a WCS object that is 1500 x 1500 pixels and has a scale of
    0.35 arcsec per pixel
    '''

    # Create a new WCS object.
    w = wcs.WCS(naxis=2)
    w.wcs.crpix = [out_size / 2, out_size / 2]
    w.wcs.crval = [center_ra, center_dec]
    w.wcs.cd = [[-scale / 3600, 0],[0, scale / 3600]]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    w.array_shape = [out_size, out_size]

    return w

def get_tns(url,json_list, api_key):
    '''
    This function will pull the object in "json_list" from the
    Transient Name Survey. The request is not verified because
    otherwise it returns an error.

    The function also includes my api_key for the bot that pulls
    the information from the webpage.

    '''
    try:
        # url for get obj
        get_url=os.path.join(url, 'object')
        # change json_list to json format
        json_file=OrderedDict(json_list)
        # construct the list of (key,value) pairs
        get_data=[('api_key',(None, api_key)),
                     ('data',(None,json.dumps(json_file)))]
        # get obj using request module
        warnings.filterwarnings("ignore")
        response=requests.post(get_url, files=get_data, verify=False)
        # return response
        return response
    except Exception as e:
        return [None,'Error message : \n'+str(e)]

def querry_mars(object_name):
    '''
    Query the MARS database from a ZTF name and
    get its RA and DEC
    '''

    # request link
    mars_link    = 'https://mars.lco.global/?objectId=%s&format=json'%object_name
    try:
        mars_request = requests.get(mars_link).json()
    except:
        print('Trying again ...')
        time.sleep(3)
        mars_request = requests.get(mars_link).json()

    # Get RA and DEC
    candidate = mars_request['results']
    ra  = candidate[0]['candidate']['ra']
    dec = candidate[0]['candidate']['dec']

    return ra, dec

def query_TNS(object_name):
    '''
    Query the TNS to get the object's RA, DEC, and object type
    Just in case it's a TDE.
    '''
    # Query TNS objects to get image and name
    key_location = os.path.join(pathlib.Path.home(), 'key.txt')
    api_key      = str(np.genfromtxt(key_location, dtype = 'str'))
    name_break   = object_name.find('2')
    url_tns_api  = "https://wis-tns.weizmann.ac.il/api/get"
    get_obj      = [("objname",object_name[name_break:].replace(' ', '')), ("photometry","0"), ("spectra","0")]
    response     = get_tns(url_tns_api,get_obj,api_key)
    data         = response.json()['data']['reply']

    # Extract RA and DEC
    ra  = response.json()['data']['reply']['radeg']
    dec = response.json()['data']['reply']['decdeg']
    object_type = response.json()['data']['reply']['object_type']['name']

    return ra, dec, object_type

def generate_template(ra, dec, color, object_name, out_size = 1500, image_radius = 250):
    '''
    Download the template from PS1, but check the corners to make sure it's
    not close to the edge. If it is close to the edge, then download more 
    templates to combine.
    '''

    # Create Empty WCS object to project the images onto
    wcs_object = create_wcs_object(ra, dec, out_size)

    # Get the data from PS1
    print('Downloading Template...')
    refdata0 = download_ps1_image(ra, dec, color, False, 'output', '.')

    # Reproject to wcs_object
    refdata0_reprojected, _ = reproject_interp((refdata0.data, refdata0.wcs), wcs_object, (out_size,out_size))

    # Image Radius in arcsec

    # Check that each corner exists in the image
    hi_hi_corner, hi_hi_ra, hi_hi_dec = check_corner(refdata0, ra + image_radius / 3600, dec + image_radius / 3600)
    hi_lo_corner, hi_lo_ra, hi_lo_dec = check_corner(refdata0, ra + image_radius / 3600, dec - image_radius / 3600)
    lo_hi_corner, lo_hi_ra, lo_hi_dec = check_corner(refdata0, ra - image_radius / 3600, dec + image_radius / 3600)
    lo_lo_corner, lo_lo_ra, lo_lo_dec = check_corner(refdata0, ra - image_radius / 3600, dec - image_radius / 3600)

    nan_array = np.zeros_like(refdata0_reprojected)
    nan_array[np.where(nan_array == 0)] = 'nan'

    if hi_hi_corner == False:
        print('Downloading Extra Template 1...')
        refdata1 = download_ps1_image(hi_hi_ra, hi_hi_dec, color, False, 'output', '.')
        refdata1_reprojected, _ = reproject_interp((refdata1.data, refdata1.wcs), wcs_object, (out_size,out_size))
    else:
        refdata1_reprojected = np.copy(nan_array)

    if hi_lo_corner == False:
        print('Downloading Extra Template 2...')
        refdata2 = download_ps1_image(hi_lo_ra, hi_lo_dec, color, False, 'output', '.')
        refdata2_reprojected, _ = reproject_interp((refdata2.data, refdata2.wcs), wcs_object, (out_size,out_size))
    else:
        refdata2_reprojected = np.copy(nan_array)

    if lo_hi_corner == False:
        print('Downloading Extra Template 3...')
        refdata3 = download_ps1_image(lo_hi_ra, lo_hi_dec, color, False, 'output', '.')
        refdata3_reprojected, _ = reproject_interp((refdata3.data, refdata3.wcs), wcs_object, (out_size,out_size))
    else:
        refdata3_reprojected = np.copy(nan_array)

    if lo_lo_corner == False:
        print('Downloading Extra Template 4...')
        refdata4 = download_ps1_image(lo_lo_ra, lo_lo_dec, color, False, 'output', '.')
        refdata4_reprojected, _ = reproject_interp((refdata4.data, refdata4.wcs), wcs_object, (out_size,out_size))
    else:
        refdata4_reprojected = np.copy(nan_array)

    refdata_output = np.nanmean((refdata0_reprojected, refdata1_reprojected, refdata2_reprojected, refdata3_reprojected, refdata4_reprojected), axis = 0)
    template_name = object_name.replace(' ', '') + '_template.fits'
    refdata = CCDData(refdata_output, wcs=wcs_object, unit='adu')
    refdata.write(template_name, overwrite=True)

    fits.setval(template_name, 'RA'    , value = ra)
    fits.setval(template_name, 'DEC'   , value = dec)
    fits.setval(template_name, 'FILTER', value = color)
    fits.setval(template_name, 'OBJECT', value = object_name)

    return wcs_object, refdata
