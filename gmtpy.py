
import subprocess
import cStringIO
import re
import os
import sys
import shutil
from itertools import izip
from os.path import join as pjoin
import tempfile
import random
import logging
import math

import numpy as num
golden_ratio   = 1.61803
point          = 1.0/72.0

# units in points
units = { 'i':72., 'c':72./2.54, 'm':72.*100./2.54, 'p':1. }

inch = units['i']
cm = units['c']

alphabet = 'abcdefghijklmnopqrstuvwxyz'

gmt_installations = {}
gmt_installations['4.2.1'] = { 'home': '/sw/etch-ia32/gmt-4.2.1',
                               'bin':  '/sw/etch-ia32/gmt-4.2.1/bin' }
gmt_installations['4.3.0'] = { 'home': '/sw/etch-ia32/gmt-4.3.0',
                               'bin':  '/sw/etch-ia32/gmt-4.3.0/bin' }
#gmt_installations['4.3.1'] = { 'home': '/sw/share/gmt',
#                               'bin': '/sw/bin' }

    
def cmp_version(a,b):
    ai = [ int(x) for x in a.split('.') ]
    bi = [ int(x) for x in b.split('.') ]
    return cmp(ai, bi)

newest_installed_gmt_version = sorted(gmt_installations.keys(), cmp=cmp_version)[-1]


# To have consistent defaults, they are hardcoded here and should not be changed.

gmt_defaults_by_version = {}
gmt_defaults_by_version['4.2.1'] = r'''
#
#       GMT-SYSTEM 4.2.1 Defaults file
#
#-------- Plot Media Parameters -------------
PAGE_COLOR              = 255/255/255
PAGE_ORIENTATION        = portrait
PAPER_MEDIA             = a4+
#-------- Basemap Annotation Parameters ------
ANNOT_MIN_ANGLE         = 20
ANNOT_MIN_SPACING       = 0
ANNOT_FONT_PRIMARY      = Helvetica
ANNOT_FONT_SIZE         = 12p
ANNOT_OFFSET_PRIMARY    = 0.075i
ANNOT_FONT_SECONDARY    = Helvetica
ANNOT_FONT_SIZE_SECONDARY       = 16p
ANNOT_OFFSET_SECONDARY  = 0.075i
DEGREE_SYMBOL           = ring
HEADER_FONT             = Helvetica
HEADER_FONT_SIZE        = 36p
HEADER_OFFSET           = 0.1875i
LABEL_FONT              = Helvetica
LABEL_FONT_SIZE         = 14p
LABEL_OFFSET            = 0.1125i
OBLIQUE_ANNOTATION      = 1
PLOT_CLOCK_FORMAT       = hh:mm:ss
PLOT_DATE_FORMAT        = yyyy-mm-dd
PLOT_DEGREE_FORMAT      = +ddd:mm:ss
Y_AXIS_TYPE             = hor_text
#-------- Basemap Layout Parameters ---------
BASEMAP_AXES            = WESN
BASEMAP_FRAME_RGB       = 0/0/0
BASEMAP_TYPE            = plain
FRAME_PEN               = 1.25p
FRAME_WIDTH             = 0.075i
GRID_CROSS_SIZE_PRIMARY = 0i
GRID_CROSS_SIZE_SECONDARY       = 0i
GRID_PEN_PRIMARY        = 0.25p
GRID_PEN_SECONDARY      = 0.5p
MAP_SCALE_HEIGHT        = 0.075i
TICK_LENGTH             = 0.075i
POLAR_CAP               = 85/90
TICK_PEN                = 0.5p
X_AXIS_LENGTH           = 9i
Y_AXIS_LENGTH           = 6i
X_ORIGIN                = 1i
Y_ORIGIN                = 1i
UNIX_TIME               = FALSE
UNIX_TIME_POS           = -0.75i/-0.75i
#-------- Color System Parameters -----------
COLOR_BACKGROUND        = 0/0/0
COLOR_FOREGROUND        = 255/255/255
COLOR_NAN               = 128/128/128
COLOR_IMAGE             = adobe
COLOR_MODEL             = rgb
HSV_MIN_SATURATION      = 1
HSV_MAX_SATURATION      = 0.1
HSV_MIN_VALUE           = 0.3
HSV_MAX_VALUE           = 1
#-------- PostScript Parameters -------------
CHAR_ENCODING           = ISOLatin1+
DOTS_PR_INCH            = 300
N_COPIES                = 1
PS_COLOR                = rgb
PS_IMAGE_COMPRESS       = none
PS_IMAGE_FORMAT         = ascii
PS_LINE_CAP             = round
PS_LINE_JOIN            = miter
PS_MITER_LIMIT          = 0
PS_VERBOSE                      = FALSE
GLOBAL_X_SCALE          = 1
GLOBAL_Y_SCALE          = 1
#-------- I/O Format Parameters -------------
D_FORMAT                = %lg
FIELD_DELIMITER         = tab
GRIDFILE_SHORTHAND      = FALSE
GRID_FORMAT             = nf
INPUT_CLOCK_FORMAT      = hh:mm:ss
INPUT_DATE_FORMAT       = yyyy-mm-dd
IO_HEADER               = FALSE
N_HEADER_RECS           = 1
OUTPUT_CLOCK_FORMAT     = hh:mm:ss
OUTPUT_DATE_FORMAT      = yyyy-mm-dd
OUTPUT_DEGREE_FORMAT    = +D
XY_TOGGLE               = FALSE
#-------- Projection Parameters -------------
ELLIPSOID               = WGS-84
MAP_SCALE_FACTOR        = default
MEASURE_UNIT            = inch
#-------- Calendar/Time Parameters ----------
TIME_FORMAT_PRIMARY     = full
TIME_FORMAT_SECONDARY   = full
TIME_EPOCH              = 2000-01-01T00:00:00
TIME_IS_INTERVAL        = OFF
TIME_INTERVAL_FRACTION  = 0.5
TIME_LANGUAGE           = us
TIME_SYSTEM             = other
TIME_UNIT               = d
TIME_WEEK_START         = Sunday
Y2K_OFFSET_YEAR         = 1950
#-------- Miscellaneous Parameters ----------
HISTORY                 = TRUE
INTERPOLANT             = akima
LINE_STEP               = 0.01i
VECTOR_SHAPE            = 0
VERBOSE                 = FALSE'''

gmt_defaults_by_version['4.3.0'] = r'''
#
#	GMT-SYSTEM 4.3.0 Defaults file
#
#-------- Plot Media Parameters -------------
PAGE_COLOR		= 255/255/255
PAGE_ORIENTATION	= portrait
PAPER_MEDIA		= a4+
#-------- Basemap Annotation Parameters ------
ANNOT_MIN_ANGLE		= 20
ANNOT_MIN_SPACING	= 0
ANNOT_FONT_PRIMARY	= Helvetica
ANNOT_FONT_SIZE_PRIMARY	= 12p
ANNOT_OFFSET_PRIMARY	= 0.075i
ANNOT_FONT_SECONDARY	= Helvetica
ANNOT_FONT_SIZE_SECONDARY	= 16p
ANNOT_OFFSET_SECONDARY	= 0.075i
DEGREE_SYMBOL		= ring
HEADER_FONT		= Helvetica
HEADER_FONT_SIZE	= 36p
HEADER_OFFSET		= 0.1875i
LABEL_FONT		= Helvetica
LABEL_FONT_SIZE		= 14p
LABEL_OFFSET		= 0.1125i
OBLIQUE_ANNOTATION	= 1
PLOT_CLOCK_FORMAT	= hh:mm:ss
PLOT_DATE_FORMAT	= yyyy-mm-dd
PLOT_DEGREE_FORMAT	= +ddd:mm:ss
Y_AXIS_TYPE		= hor_text
#-------- Basemap Layout Parameters ---------
BASEMAP_AXES		= WESN
BASEMAP_FRAME_RGB	= 0/0/0
BASEMAP_TYPE		= plain
FRAME_PEN		= 1.25p
FRAME_WIDTH		= 0.075i
GRID_CROSS_SIZE_PRIMARY	= 0i
GRID_PEN_PRIMARY	= 0.25p
GRID_CROSS_SIZE_SECONDARY	= 0i
GRID_PEN_SECONDARY	= 0.5p
MAP_SCALE_HEIGHT	= 0.075i
POLAR_CAP		= 85/90
TICK_LENGTH		= 0.075i
TICK_PEN		= 0.5p
X_AXIS_LENGTH		= 9i
Y_AXIS_LENGTH		= 6i
X_ORIGIN		= 1i
Y_ORIGIN		= 1i
UNIX_TIME		= FALSE
UNIX_TIME_POS		= BL/-0.75i/-0.75i
UNIX_TIME_FORMAT	= %Y %b %d %H:%M:%S
#-------- Color System Parameters -----------
COLOR_BACKGROUND	= 0/0/0
COLOR_FOREGROUND	= 255/255/255
COLOR_NAN		= 128/128/128
COLOR_IMAGE		= adobe
COLOR_MODEL		= rgb
HSV_MIN_SATURATION	= 1
HSV_MAX_SATURATION	= 0.1
HSV_MIN_VALUE		= 0.3
HSV_MAX_VALUE		= 1
#-------- PostScript Parameters -------------
CHAR_ENCODING		= ISOLatin1+
DOTS_PR_INCH		= 300
N_COPIES		= 1
PS_COLOR		= rgb
PS_IMAGE_COMPRESS	= none
PS_IMAGE_FORMAT		= ascii
PS_LINE_CAP		= round
PS_LINE_JOIN		= miter
PS_MITER_LIMIT		= 0
PS_VERBOSE		= FALSE
GLOBAL_X_SCALE		= 1
GLOBAL_Y_SCALE		= 1
#-------- I/O Format Parameters -------------
D_FORMAT		= %lg
FIELD_DELIMITER		= tab
GRIDFILE_SHORTHAND	= FALSE
GRID_FORMAT		= nf
INPUT_CLOCK_FORMAT	= hh:mm:ss
INPUT_DATE_FORMAT	= yyyy-mm-dd
IO_HEADER		= FALSE
N_HEADER_RECS		= 1
OUTPUT_CLOCK_FORMAT	= hh:mm:ss
OUTPUT_DATE_FORMAT	= yyyy-mm-dd
OUTPUT_DEGREE_FORMAT	= +D
XY_TOGGLE		= FALSE
#-------- Projection Parameters -------------
ELLIPSOID		= WGS-84
MAP_SCALE_FACTOR	= default
MEASURE_UNIT		= inch
#-------- Calendar/Time Parameters ----------
TIME_FORMAT_PRIMARY	= full
TIME_FORMAT_SECONDARY	= full
TIME_EPOCH		= 2000-01-01T00:00:00
TIME_IS_INTERVAL	= OFF
TIME_INTERVAL_FRACTION	= 0.5
TIME_LANGUAGE		= us
TIME_UNIT		= d
TIME_WEEK_START		= Sunday
Y2K_OFFSET_YEAR		= 1950
#-------- Miscellaneous Parameters ----------
HISTORY			= TRUE
INTERPOLANT		= akima
LINE_STEP		= 0.01i
VECTOR_SHAPE		= 0
VERBOSE			= FALSE'''


gmt_defaults_by_version['4.3.1'] = r'''
#
#	GMT-SYSTEM 4.3.1 Defaults file
#
#-------- Plot Media Parameters -------------
PAGE_COLOR		= 255/255/255
PAGE_ORIENTATION	= portrait
PAPER_MEDIA		= a4+
#-------- Basemap Annotation Parameters ------
ANNOT_MIN_ANGLE		= 20
ANNOT_MIN_SPACING	= 0
ANNOT_FONT_PRIMARY	= Helvetica
ANNOT_FONT_SIZE_PRIMARY	= 12p
ANNOT_OFFSET_PRIMARY	= 0.075i
ANNOT_FONT_SECONDARY	= Helvetica
ANNOT_FONT_SIZE_SECONDARY	= 16p
ANNOT_OFFSET_SECONDARY	= 0.075i
DEGREE_SYMBOL		= ring
HEADER_FONT		= Helvetica
HEADER_FONT_SIZE	= 36p
HEADER_OFFSET		= 0.1875i
LABEL_FONT		= Helvetica
LABEL_FONT_SIZE		= 14p
LABEL_OFFSET		= 0.1125i
OBLIQUE_ANNOTATION	= 1
PLOT_CLOCK_FORMAT	= hh:mm:ss
PLOT_DATE_FORMAT	= yyyy-mm-dd
PLOT_DEGREE_FORMAT	= +ddd:mm:ss
Y_AXIS_TYPE		= hor_text
#-------- Basemap Layout Parameters ---------
BASEMAP_AXES		= WESN
BASEMAP_FRAME_RGB	= 0/0/0
BASEMAP_TYPE		= plain
FRAME_PEN		= 1.25p
FRAME_WIDTH		= 0.075i
GRID_CROSS_SIZE_PRIMARY	= 0i
GRID_PEN_PRIMARY	= 0.25p
GRID_CROSS_SIZE_SECONDARY	= 0i
GRID_PEN_SECONDARY	= 0.5p
MAP_SCALE_HEIGHT	= 0.075i
POLAR_CAP		= 85/90
TICK_LENGTH		= 0.075i
TICK_PEN		= 0.5p
X_AXIS_LENGTH		= 9i
Y_AXIS_LENGTH		= 6i
X_ORIGIN		= 1i
Y_ORIGIN		= 1i
UNIX_TIME		= FALSE
UNIX_TIME_POS		= BL/-0.75i/-0.75i
UNIX_TIME_FORMAT	= %Y %b %d %H:%M:%S
#-------- Color System Parameters -----------
COLOR_BACKGROUND	= 0/0/0
COLOR_FOREGROUND	= 255/255/255
COLOR_NAN		= 128/128/128
COLOR_IMAGE		= adobe
COLOR_MODEL		= rgb
HSV_MIN_SATURATION	= 1
HSV_MAX_SATURATION	= 0.1
HSV_MIN_VALUE		= 0.3
HSV_MAX_VALUE		= 1
#-------- PostScript Parameters -------------
CHAR_ENCODING		= ISOLatin1+
DOTS_PR_INCH		= 300
N_COPIES		= 1
PS_COLOR		= rgb
PS_IMAGE_COMPRESS	= none
PS_IMAGE_FORMAT		= ascii
PS_LINE_CAP		= round
PS_LINE_JOIN		= miter
PS_MITER_LIMIT		= 0
PS_VERBOSE		= FALSE
GLOBAL_X_SCALE		= 1
GLOBAL_Y_SCALE		= 1
#-------- I/O Format Parameters -------------
D_FORMAT		= %lg
FIELD_DELIMITER		= tab
GRIDFILE_SHORTHAND	= FALSE
GRID_FORMAT		= nf
INPUT_CLOCK_FORMAT	= hh:mm:ss
INPUT_DATE_FORMAT	= yyyy-mm-dd
IO_HEADER		= FALSE
N_HEADER_RECS		= 1
OUTPUT_CLOCK_FORMAT	= hh:mm:ss
OUTPUT_DATE_FORMAT	= yyyy-mm-dd
OUTPUT_DEGREE_FORMAT	= +D
XY_TOGGLE		= FALSE
#-------- Projection Parameters -------------
ELLIPSOID		= WGS-84
MAP_SCALE_FACTOR	= default
MEASURE_UNIT		= inch
#-------- Calendar/Time Parameters ----------
TIME_FORMAT_PRIMARY	= full
TIME_FORMAT_SECONDARY	= full
TIME_EPOCH		= 2000-01-01T00:00:00
TIME_IS_INTERVAL	= OFF
TIME_INTERVAL_FRACTION	= 0.5
TIME_LANGUAGE		= us
TIME_UNIT		= d
TIME_WEEK_START		= Sunday
Y2K_OFFSET_YEAR		= 1950
#-------- Miscellaneous Parameters ----------
HISTORY			= TRUE
INTERPOLANT		= akima
LINE_STEP		= 0.01i
VECTOR_SHAPE		= 0
VERBOSE			= FALSE'''


def gmt_default_config(version):
    '''Get default GMT configuration dict for given version.'''
    
    if not version in gmt_defaults_by_version:
        raise Exception('No GMT defaults for version %s found' % version)
    
    gmt_defaults = gmt_defaults_by_version[version]
    
    d = {}
    for line in gmt_defaults.splitlines():
        sline = line.strip()
        if not sline or sline.startswith('#'): continue
        k,v = sline.split('=',1)
        d[k.strip()] = v.strip()
    
    return d

def diff_defaults(v1,v2):
    d1 = gmt_default_config(v1)
    d2 = gmt_default_config(v2)
    for k in d1:
        if k not in d2:
            print '%s not in %s' % (k, v2)
        else:
            if d1[k] != d2[k]:
                print '%s %s = %s' % (v1, k, d1[k])
                print '%s %s = %s' % (v2, k, d2[k])
        
    for k in d2:
        if k not in d1:
            print '%s not in %s' % (k, v1)
     
#diff_defaults('4.2.1', '4.3.1')

# store defaults as dicts into the gmt installations dicts
for version, installation in gmt_installations.iteritems():
    installation['defaults'] = gmt_default_config(version)
    installation['version'] = version

# alias for the newest installed gmt version
gmt_installations['newest'] = gmt_installations[newest_installed_gmt_version]

paper_sizes_a = '''A0 2380 3368
                      A1 1684 2380
                      A2 1190 1684
                      A3 842 1190
                      A4 595 842
                      A5 421 595
                      A6 297 421
                      A7 210 297
                      A8 148 210
                      A9 105 148
                      A10 74 105
                      B0 2836 4008
                      B1 2004 2836
                      B2 1418 2004
                      B3 1002 1418
                      B4 709 1002
                      B5 501 709
                      archA 648 864
                      archB 864 1296
                      archC 1296 1728
                      archD 1728 2592
                      archE 2592 3456
                      flsa 612 936
                      halfletter 396 612
                      note 540 720
                      letter 612 792
                      legal 612 1008
                      11x17 792 1224
                      ledger 1224 792'''
                      

paper_sizes = {}
for line in paper_sizes_a.splitlines():
    k, w, h = line.split()
    paper_sizes[k.lower()] = float(w), float(h)


def make_bbox( width, height, gmt_config, margins=(0.8,0.8,0.8,0.8)):
    
    leftmargin, topmargin, rightmargin, bottommargin = margins
    portrait = gmt_config['PAGE_ORIENTATION'].lower() == 'portrait'
    
    paper_size = paper_sizes[gmt_config['PAPER_MEDIA'].lower().rstrip('+')]
    if not portrait: paper_size = paper_size[1], paper_size[0]
            
    xoffset = (paper_size[0] - (width + leftmargin + rightmargin)) / 2.0 + leftmargin;
    yoffset = (paper_size[1] - (height + topmargin + bottommargin)) / 2.0 + bottommargin;
    
    if portrait:
        bb1 = int((xoffset - leftmargin));
        bb2 = int((yoffset - bottommargin));
        bb3 = bb1 + int((width+leftmargin+rightmargin));
        bb4 = bb2 + int((height+topmargin+bottommargin));
    else:
        bb1 = int((yoffset - topmargin));
        bb2 = int((xoffset - leftmargin));
        bb3 = bb1 + int((height+topmargin+bottommargin));
        bb4 = bb2 + int((width+leftmargin+rightmargin));
    
    return xoffset, yoffset, (bb1,bb2,bb3,bb4)


def check_gmt_installation( installation ):
    
    home_dir = installation['home']
    bin_dir = installation['bin']
    version = installation['version']
    
    for d in home_dir, bin_dir:
        if not os.path.exists(d):
            logging.error(('Directory does not exist: %s\n'+
                          'Check your GMT installation.') % d)
    
    gmtdefaults = pjoin(bin_dir, 'gmtdefaults')
    args = [ gmtdefaults ]
    
    environ = os.environ.copy()
    environ['GMTHOME'] = home_dir
    p = subprocess.Popen( args, stderr=subprocess.PIPE, env=environ )
    (stdout, stderr) = p.communicate()
    m = re.search(r'(\d+(\.\d+)*)', stderr)
    if not m:
        raise Exception("Can't extract version number from output of %s" % gmtdefaults)
    
    versionfound = m.group(1)
    
    if versionfound != version:
        raise Exception(('Expected GMT version %s but found version %s.\n'+
                         '(Looking at output of %s)') % (version, versionfound, gmtdefaults))
    
def get_gmt_installation(version):
        
    if version not in gmt_installations:
        logging.warn('GMT version %s not installed, taking version %s instead' % 
                                                      (version, newest_installed_gmt_version))
        version = 'newest'
        
    installation = dict(gmt_installations[version])
    
    check_gmt_installation( installation )
    
    return installation
    
def gmtdefaults_as_text(version='newest'):
    
    '''Get the built-in gmtdefaults.'''
    
    if version not in gmt_installations:
        logging.warn('GMT version %s not installed, taking version %s instead' % 
                                                      (version, newest_installed_gmt_version))
        version = 'newest'
        
    if version == 'newest':
        version = newest_installed_gmt_version
        
    return gmt_defaults_by_version[version]
    


class Guru:
    '''Abstract base class providing template interpolation, accessible as attributes.
    
    Classes deriving from this one, have to implement a get_params(), which is
    called to get a dict to do ordinary "%(key)x"-substitutions. The deriving class
    must also provide a dict with the templates.'''
        
    def fill(self, templates, **kwargs):
        params = self.get_params(**kwargs)
        strings = [ t % params for t in templates ]
        return strings
    
    # hand through templates dict
    def __getitem__(self, template_name):
        return self.templates[template_name]
    
    def __setitem__(self, template_name, template):
        self.templates[template_name] = template
    
    def __contains__(self, template_name):
        return template_name in self.templates
   
    def __iter__(self):
        return iter(self.templates)
    
    def __len__(self):
        return len(self.templates)
    
    def __delitem__(self, template_name):
        del(self.templates[template_name])
        
        
        
    def _simple_fill(self, template_names, **kwargs):
        templates = [ self.templates[n] for n in template_names ]
        return self.fill(templates, **kwargs)
        
    def __getattr__(self, template_names):
        def f(**kwargs):
            return self._simple_fill(template_names, **kwargs)
        return f

    
class AutoScaler:
    '''Tunable 1D autoscaling based on data range.
    
    Instances of this class may be used to determine nice minima, maxima and
    increments for ax annotations, as well as suitable common exponents for
    notation.

    The autoscaling process is guided by the following public attributes
    (default values are given in parantheses):

      approx_ticks (7.0):

        Approximate number of increment steps (tickmarks) to generate.

      mode ('auto'):

        Mode of operation: one of 'auto', 'min-max', '0-max', 'min-0',
        'symmetric' or 'off'.

          'auto':      Look at data range and choose one of the choices below.
          'min-max':   Output range is selected to include data range.
          '0-max':     Output range shall start at zero and end at data max.
          'min-0':     Output range shall start at data min and end at zero. 
          'symmetric': Output range shall by symmetric by zero.
          'off':       Similar to 'min-max', but snap and space are disabled, 
                       such that the output range always exactly matches the 
                       data range.
      
      exp (None):
      
        If defined, override automatically determined exponent for notation by
        the given value.
        
      snap (False):
      
        If set to True, snap output range to multiples of increment. This
        parameter has no effect, if mode is set to 'off'.
        
      inc (None):
      
        If defined, override automatically determined tick increment by the
        given value.
      
      space (0.0):
      
        Add some padding to the range. The value given, is the fraction by which
        the output range is increased on each side. If mode is '0-max' or 'min-0',
        the end at zero is kept fixed at zero. This parameter has no effect if 
        mode is set to 'off'.
      
      exp_factor (3):
        
        Exponent of notation is chosen to be a multiple of this value.
        
      no_exp_interval ((-3,5)):
      
        Range of exponent, for which no exponential notation is allowed.'''
            
    def __init__(self, approx_ticks=7.0, 
                       mode='auto',
                       exp=None,
                       snap=False,
                       inc=None,
                       space=0.0,
                       exp_factor=3,
                       no_exp_interval=(-3,5)):
        
        '''Create new AutoScaler instance.
        
        The parameters are described in the AutoScaler documentation.
        '''
                       
        self.approx_ticks = approx_ticks
        self.mode = mode
        self.exp = exp
        self.snap = snap
        self.inc = inc
        self.space = space
        self.exp_factor = exp_factor
        self.no_exp_interval = no_exp_interval
        
    def make_scale(self, data_range, override_mode=None):
        
        '''Get nice minimum, maximum and increment for given data range.
        
        Returns (minimum,maximum,increment) or (maximum,minimum,-increment),
        depending on whether data_range is (data_min, data_max) or (data_max,
        data_min). If override_mode is defined, the mode attribute is
        temporarily overridden by the given value.
        '''
        
        data_min = min(data_range)
        data_max = max(data_range)
        
        is_reverse = (data_range[0] > data_range[1])
        
        a = self.mode
        if self.mode == 'auto':
            a = self.guess_autoscale_mode( data_min, data_max )
        
        if override_mode is not None:
            a = override_mode
        
        mi, ma = 0, 0
        if a == 'off':
            mi, ma = data_min, data_max
        elif a == '0-max':
            mi = 0.0
            if data_max > 0.0:
                ma = data_max
            else:
                ma = 1.0
        elif a == 'min-0':
            ma = 0.0
            if data_min < 0.0:
                mi = data_min
            else:
                mi = -1.0
        elif a == 'min-max':
            mi, ma = data_min, data_max
        elif a == 'symmetric':
            m = max(abs(data_min),abs(data_max))
            mi = -m
            ma =  m
        
        nmi = mi
        if (mi != 0. or a == 'min-max') and a != 'off':
            nmi = mi - self.space*(ma-mi)
            
        nma = ma
        if (ma != 0. or a == 'min-max') and a != 'off':
            nma = ma + self.space*(ma-mi)
             
        mi, ma = nmi, nma
        
        if mi == ma and a != 'off':
            mi -= 1.0
            ma += 1.0
        
        # make nice tick increment
        if self.inc is not None:
            inc = self.inc
        else:
            inc = self.nice_value( (ma-mi)/self.approx_ticks )
        
        if inc == 0.0:
            inc = 1.0
            
        # snap min and max to ticks if this is wanted
        if self.snap and a != 'off':
            ma = inc * math.ceil(ma/inc)
            mi = inc * math.floor(mi/inc) 
        
        if is_reverse:
            return ma, mi, -inc
        else:
            return mi, ma, inc
        
    def make_exp(self, x):
        '''Get nice exponent for notation of x.
        
        For ax annotations, give tick increment as x.'''
        
        if self.exp is not None: return self.exp
        x = abs(x)
        if x == 0.0: return 0
        if 10**self.no_exp_interval[0] <= x <= 10**self.no_exp_interval[1]: return 0
        return math.floor(math.log10(x)/self.exp_factor)*self.exp_factor
    
    def guess_autoscale_mode(self, data_min, data_max):
        '''Guess mode of operation, based on data range.
        
        Used to map 'auto' mode to '0-max', 'min-0', 'min-max' or 'symmetric'.
        '''
        
        if data_min >= 0.0:
            if data_min < data_max/2.:
                a = '0-max'
            else: 
                a = 'min-max'
        if data_max <= 0.0:
            if data_max > data_min/2.:
                a = 'min-0'
            else:
                a = 'min-max'
        if data_min < 0.0 and data_max > 0.0:
            if abs((abs(data_max)-abs(data_min))/(abs(data_max)+abs(data_min))) < 0.5:
                a = 'symmetric'
            else:
                a = 'min-max'
        return a
            
            
    def nice_value(self, x):
        '''Round x to nice value.'''
        
        exp = 1.0
        sign = 1
        if x<0.0:
            x = -x
            sign = -1
        while x >= 1.0:
            x /= 10.0
            exp *= 10.0
        while x < 0.1:
            x *= 10.0
            exp /= 10.0
        
        if x >= 0.75:
            return sign * 1.0 * exp
        if x >= 0.375:
            return sign * 0.5 * exp
        if x >= 0.225:
            return sign * 0.25 * exp
        if x >= 0.15:
            return sign * 0.2 * exp
        
        return sign * 0.1 * exp

class Ax(AutoScaler):
    '''Ax description with autoscaling capabilities.
    
    The ax is described by the AutoScaler's public attributes, plus the following
    additional attributes (with default values given in paranthesis):
    
      label (''):
    
        Ax label (without unit).
      
      unit (''):
        
        Physical unit of the data attached to this ax.
      
      scaled_unit (''),
      scaled_unit_factor(1.):
      
        Scaled physical unit and factor between unit and scaled_unit such that
        
            unit = scaled_unit_factor x scaled_unit. 
        
        (E.g. if unit is 'm' and data is in the range of nanometers, you may
        want to set the scaled_unit to 'nm' and the scaled_unit_factor to 1e9.)
        
     limits (None):
     
        If defined, fix range of ax to limits=(min,max).'''
    
    def __init__(self, label='', unit='', scaled_unit_factor=1., scaled_unit='', limits=None, **kwargs):
        '''Create new Ax instance.'''
        
        AutoScaler.__init__(self, **kwargs )
        self.label = label
        self.unit = unit
        self.scaled_unit_factor = scaled_unit_factor
        self.scaled_unit = scaled_unit
        self.limits = limits
        
        
    def label_str(self, exp, unit):
        '''Get label string including the unit and multiplier.'''
        
        slabel, sunit, sexp = '', '', ''
        if self.label:
            slabel = self.label
            
        if unit or exp != 0:
            if exp != 0:
                sexp = '\\327 10@+%i@+' % exp
                sunit = '[ %s %s ]' % (sexp, unit)
            else:
                sunit = '[ %s ]' % unit
        
        p = []
        if slabel: p.append(slabel)
        if sunit: p.append(sunit)
        return ' '.join(p)
        
        
    def make_params(self, data_range, ax_projection=False, override_mode=None):
        '''Get min, max, increment and label string for ax display.'
        
        Returns minimum, maximum, increment and label string including unit and
        multiplier for given data range.
        
        If ax_projection is True, values suitable to be displayed on the ax are
        returned, e.g. min, max and inc are returned in scaled units. Otherwise
        the values are returned in the original units, without any scaling.
        '''
        
        sf = self.scaled_unit_factor
        
        dr_scaled = [ sf*x for x in data_range ]
        
        mi,ma,inc = self.make_scale( dr_scaled, override_mode=override_mode )
        
        if ax_projection:
            exp = self.make_exp( inc )
            if sf == 1.:
                unit = self.unit
            else:
                unit = self.scaled_unit
            label = self.label_str( exp, unit )
            return mi/10**exp, ma/10**exp, inc/10**exp, label
        else:
            label = self.label_str( 0, self.unit )
            return mi/sf, ma/sf, inc/sf, label

class ScaleGuru(Guru):
    
    '''2D/3D autoscaling and ax annotation facility.
    
    Instances of this class provide automatic determination of plot ranges, tick
    increments and scaled annotations, as well as label/unit handling. It can in
    particular be used to automatically generate the -R and -B option arguments,
    which are required for most GMT commands.

    It extends the functionality of the Ax and AutoScaler classes at the level,
    where it can not be handled anymore by looking at a single dimension of the
    dataset's data, e.g.:

       i) The ability to impose a fixed aspect ratio between two axes.

       ii) Recalculation of data range on non-limited axes, when there are
       limits imposed on other axes.

    '''
    
    def __init__(self, data_tuples=None, axes=None, aspect=None):
        
        self.templates = dict( 
            R='-R%(xmin)g/%(xmax)g/%(ymin)g/%(ymax)g',
            B='-B%(xinc)g:%(xlabel)s:/%(yinc)g:%(ylabel)s:WSen' )
        
        maxdim = 2
        if data_tuples:
            maxdim = max(maxdim,max( [ len(dt) for dt in data_tuples ] ))
        
        if axes is not None:
            self.axes = axes
        else:
            self.axes = [ Ax() for i in range(maxdim) ]
        
        self.data_tuples = data_tuples
        
        # sophisticated data-range calculation
        data_ranges = [None] * maxdim
        for dt in data_tuples:
            
            in_range = True
            for ax,x in zip(self.axes, dt):
                if ax.limits:
                    in_range = num.logical_and(in_range, num.logical_and(ax.limits[0]<=x, x<=ax.limits[1]))
            
            for i,ax,x in zip(range(maxdim),self.axes, dt):
                if not ax.limits:
                    if in_range is not True:
                        xmasked = num.where(in_range, x, num.NaN)
                        range_this = num.nanmin(xmasked), num.nanmax(xmasked)
                    else:
                        range_this = num.nanmin(x), num.nanmax(x)
                else:
                    range_this = ax.limits
                
                if data_ranges[i] is None and range_this[0] <= range_this[1]:
                    data_ranges[i] = range_this
                else:
                    data_ranges[i] = (min(data_ranges[i][0],range_this[0]),
                                      max(data_ranges[i][1],range_this[1]))
                
        for i in range(len(data_ranges)):
            if data_ranges[i] is None:
                data_ranges[i] = (0.,1.)
        
        self.data_ranges = data_ranges
        self.aspect = aspect
                
    def get_params(self, ax_projection=False):
        
        '''Get dict with output parameters.
        
        For each data dimension, ax minimum, maximum, increment and a label
        string (including unit and exponential factor) are determined. E.g. in
        for the first dimension the output dict will contain the keys 'xmin',
        'xmax', 'xinc', and 'xlabel'. 

        Normally, values corresponding to the scaling of the raw data are
        produced, but if ax_projection is True, values which are suitable to be
        printed on the axes are returned. This means that in the latter case,
        the 'scaled_unit' and 'scaled_unit_factor' attributes as set on the axes
        are respected and that a common 10^x factor is factored out and put to
        the label string.
        '''
        
        xmi, xma, xinc, xlabel = self.axes[0].make_params( self.data_ranges[0], ax_projection )
        ymi, yma, yinc, ylabel = self.axes[1].make_params( self.data_ranges[1], ax_projection )
        if len(self.axes) > 2:
            zmi, zma, zinc, zlabel = self.axes[2].make_params( self.data_ranges[2], ax_projcetion )
        
        # enforce certain aspect, if needed
        if self.aspect is not None:
            xwid = xma-xmi
            ywid = yma-ymi
            if ywid < xwid*self.aspect:
                ymi -= (xwid*self.aspect - ywid)*0.5
                yma += (xwid*self.aspect - ywid)*0.5
                ymi, yma, yinc, ylabel = self.axes[1].make_params( (ymi, yma), ax_projection, override_mode='off' )
            elif xwid < ywid/self.aspect:
                xmi -= (ywid/self.aspect - xwid)*0.5
                xma += (ywid/self.aspect - xwid)*0.5
                xmi, xma, xinc, xlabel = self.axes[0].make_params( (xmi, xma), ax_projection, override_mode='off' )
        
        params = dict(xmin=xmi, xmax=xma, xinc=xinc, xlabel=xlabel, 
                      ymin=ymi, ymax=yma, yinc=yinc, ylabel=ylabel)
        if len(self.axes) > 2:
            params.update( dict(zmin=zmi, zmax=zma, zinc=zinc, zlabel=zlabel) )
        
        return params

class GumSpring:
    
    '''Sizing policy implementing a minimal size, plus a desire to grow.'''
    
    def __init__(self, minimal=None, grow=None):
        self.minimal = minimal
        if grow is None:
            if minimal is None:
                self.grow = 1.0
            else:
                self.grow = 0.0
        else:
            self.grow = grow
        self.value = 1.0
        
    def get_minimal(self):
        if self.minimal is not None:
            return self.minimal
        else:
            return 0.0
        
    def get_grow(self):
        return self.grow
    
    def set_value(self, value):
        self.value = value
        
    def get_value(self):
        return self.value
        
def distribute(sizes, grows, space):
    sizes = list(sizes)
    gsum = sum(grows)
    if gsum > 0.0:
        for i in range(len(sizes)):
            sizes[i] += space*grows[i]/gsum
    return sizes

class Widget(Guru):
    
    '''Base class of the gmtpy layout system.
    
    The Widget class provides the basic functionality for the nesting and
    placing of elements on the output page, and maintains the sizing policies of
    each element. Each of the layouts defined in gmtpy is itself a Widget.
    
    Sizing of the widget is controlled by get_min_size() and get_grow() which
    should be overloaded in derived classes. The basic behaviour of a Widget
    instance is to have a vertical and a horizontal minimum size which default
    to zero, as well as a vertical and a horizontal desire to grow, represented
    by floats, which default to 1. Additionally an aspect ratio constraint may
    be imposed on the Widget.

    After layouting, the widget provides its width, height, x-offset and
    y-offset in various ways. Via the Guru interface (see Guru class), templates
    for the -X, -Y and -J option arguments used by GMT arguments are provided.
    The defaults are suitable for plotting of linear (-JX) plots. Other
    projections can be selected by giving an appropriate 'J' template, or by
    manual construction of the -J option, e.g. by utilizing the width() and
    height() methods. The bbox() method can be used to create a PostScript
    bounding box from the widgets border, e.g. for use in the save() method of
    GMT instances.

    The convention is, that all sizes are given in PostScript points. Conversion
    factors are provided as constants 'inch' and 'cm' in the gmtpy module.
    '''
    
    def __init__(self, horizontal=None, vertical=None, parent=None):
        
        '''Create new widget.'''
        
        self.templates = dict( 
            X='-Xa%(xoffset)gp',
            Y='-Ya%(yoffset)gp',
            J='-JX%(width)gp/%(height)gp' )

        if horizontal is None:
            self.horizontal = GumSpring()
        else:
            self.horizontal = horizontal
        
        if vertical is None:
            self.vertical = GumSpring()
        else:
            self.vertical = vertical
            
        self.aspect = None
        self.parent = parent
        self.dirty = True
    
    def set_parent(self, parent):        
        self.parent = parent
        self.dirtyfy()
        
    def get_parent(self):
        return self.parent
    
    def set_horizontal(self, minimal=None, grow=None):
        
        '''Set the horizontal sizing policy of the Widget.
        
           minimal: new minimal width of the widget
           grow:    new horizontal grow disire of the widget
        '''
        
        self.horizontal = GumSpring(minimal, grow)
        self.dirtyfy()
    
    def set_vertical(self, minimal=None, grow=None):
        
        '''Set the horizontal sizing policy of the Widget.
        
           minimal: new minimal height of the widget
           grow:    new vertical grow disire of the widget
        '''

        self.vertical = GumSpring(minimal, grow)
        self.dirtyfy()
    
    def set_aspect(self, aspect=None):
        
        '''Set aspect constraint on the widget.
        
        The aspect is given as height divided by width.
        '''
        
        self.aspect = aspect
        self.dirtyfy()
    
    def set_policy(self, minimal=(None,None), grow=(None,None), aspect=None):
        
        '''Shortcut to set sizing and aspect constraints in a single method call.'''
        
        self.set_horizontal(minimal[0], grow[0])
        self.set_vertical(minimal[1], grow[1])
        self.set_aspect(aspect)
        
    def legalize(self, size, offset):
        
        '''Get legal size for widget.
        
        Returns: (new_size, new_offset)
        
        Given a box as `size` and `offset`, return `new_size` and `new_offset`, such
        that the widget's sizing and aspect constraints are fullfilled.
        The returned box is centered on the given input box.
        '''
        
        sh, sv = size
        oh, ov = offset
        shs, svs = Widget.get_min_size(self)
        ghs, gvs = Widget.get_grow(self)
        
        if ghs == 0.0: 
            oh += (sh-shs)/2.
            sh = shs
            
        if gvs == 0.0:
            ov += (sv-svs)/2.
            sv = svs
        
        if self.aspect is not None:
            if sh > sv/self.aspect:
                oh += (sh-sv/self.aspect)/2.
                sh = sv/self.aspect
            if sv > sh*self.aspect:
                ov += (sv-sh*self.aspect)/2.
                sv = sh*self.aspect
        
        return (sh, sv), (oh,ov)
    
    def get_min_size(self):
        
        '''Get minimum size of widget.
        
        Used by the layout managers. Should be overloaded in derived classes.
        '''
        
        mh, mv = self.horizontal.get_minimal(), self.vertical.get_minimal()
        if self.aspect is not None:
            if mv == 0.0:
                return mh, mh*self.aspect
            elif mh == 0.0:
                return mv/self.aspect, mv
        return mh, mv
        
    def get_grow(self):
        
        '''Get widget's desire to grow.
        
        Used by the layout managers. Should be overloaded in derived classes.
        '''
        
        return self.horizontal.get_grow(), self.vertical.get_grow()
        
    def set_size(self, size, offset):
        
        '''Set the widget's current size.
        
        Should not be called directly. It is the layout manager's responsibility
        to call this.
        '''
        
        (sh,sv),inner_offset = self.legalize(size,offset)
        self.offset = inner_offset
        self.horizontal.set_value(sh)
        self.vertical.set_value(sv)
        self.dirty = False
        
    
    def __str__(self):
        
        def indent(ind,str):
            return ('\n'+ind).join(str.splitlines())
        size, offset = self.get_size()
        s = "%s (%g x %g) (%g, %g)\n" % ((self.__class__,) + size + offset)
        children = self.get_children()
        if children:
            s += '\n'.join([ '  '+ indent('  ', str(c)) for c in children ])
        return s
        
    def get_corners(self, descend=False):
        
        '''Get coordinates of the corners of the widget.
        
        Returns list with coordinate tuples.
        
        If `decend` is True, the returned list will contain corner coordinates
        of all sub-widgets.
        '''
        
        self.do_layout()
        (sh,sv), (oh,ov) = self.get_size()
        corners = [ (oh,ov), (oh+sh,ov), (oh+sh,ov+sv), (oh,ov+sv) ]
        if descend:
            for child in self.get_children():
                corners.extend( child.get_corners( descend=True ) )
        return corners
        
    def get_sizes(self):
        
        '''Get sizes of this widget and all it's children.
        
        Returns a list with size tuples.
        '''
        self.do_layout()
        sizes = [ self.get_size() ]
        for child in self.get_children():
            sizes.extend( child.get_sizes() )
        return sizes
        
    def do_layout(self):
        
        '''Triggers layouting of the widget hierarchy, if needed.'''
        
        if self.parent is not None:
            return self.parent.do_layout()
        
        if not self.dirty:
            return
            
        sh, sv = self.get_min_size()
        gh, gv = self.get_grow()
        if sh == 0.0 and gh != 0.0:
            sh = 15.*cm
        if sv == 0.0 and gv != 0.0:
            sv = 15.*cm*gv/gh *1./golden_ratio
        self.set_size((sh,sv),(0.,0.))
    
    def get_children(self):
        
        '''Get sub-widgets contained in this widget.
        
        Returns a list of widgets.
        '''
        
        return []
            
    def get_size(self):
        
        '''Get current size and position of the widget.
        
        Triggers layouting and returns (width, height), (xoffset, yoffset)
        '''
        
        self.do_layout()
        return (self.horizontal.get_value(), self.vertical.get_value()), self.offset

    def get_params(self):
        
        '''Get current size and position of the widget.
        
        Triggers layouting and returns dict with keys `xoffset`, `yoffset`,
        `width` and `height`.
        '''
        
        self.do_layout()
        (w, h), (xo, yo) = self.get_size()
        return dict( xoffset=xo, yoffset=yo, width=w, height=h )
   
    def width(self):
        
        '''Get current height of the widget.
        
        Triggers layouting and returns width.'''
        
        self.do_layout()
        return self.horizontal.get_value()
        
    def height(self):
        
        '''Get current width of the widget.
        
        Triggers layouting and return height.'''
        
        self.do_layout()
        return self.vertical.get_value()
        
    def bbox(self):
        
        '''Get PostScript bounding box for this widget.
        
        Triggers layouting and returns values suitable to create PS bounding
        box, representing the widgets current size and position.
        '''
        
        self.do_layout()
        return (self.offset[0], self.offset[1], self.offset[0]+self.width(), self.offset[1]+self.height() )
    
    def dirtyfy(self):
        
        '''Set dirty flag on top level widget in the hierarchy.
        
        Called by various methods, to indicate, that the widget hierarchy needs
        new layouting.
        '''
        
        if self.parent is not None:
            self.parent.dirtyfy()
        
        self.dirty = True
   
class CenterLayout(Widget):
    
    '''A layout manager which centers its single child widget.
    
    The child widget may be oversized.
    '''
    
    def __init__(self, horizontal=None, vertical=None):
        Widget.__init__(self, horizontal, vertical)
        self.content = Widget(horizontal=GumSpring(grow=1.), vertical=GumSpring(grow=1.), parent=self)
        
        
    def get_min_size(self):
        shs, svs = Widget.get_min_size(self)
        sh, sv = self.content.get_min_size()
        return max(shs,sh), max(svs,sv)
    
    def get_grow(self):
        ghs, gvs = Widget.get_grow(self)
        gh, gv = self.content.get_grow()
        return gh*ghs, gv*gvs
        
    def set_size(self, size, offset):
        (sh, sv), (oh, ov) = self.legalize(size, offset)
        
        shc, svc = self.content.get_min_size()
        ghc, gvc = self.content.get_grow()
        if ghc != 0.: shc = sh
        if gvc != 0.: svc = sv
        ohc = oh+(sh-shc)/2.
        ovc = ov+(sv-svc)/2.
        
        self.content.set_size((shc,svc), (ohc,ovc))
        Widget.set_size(self,(sh,sv), (oh,ov))
        
    def set_widget(self, widget=None):
        
        '''Set the child widget, which shall be centered.'''
        
        if widget is None:
            widget = Widget()
        
        self.content = widget

        widget.set_parent(self)

    def get_widget(self):
        return self.content
    
    def get_children(self):
        return [ self.content ]

class FrameLayout(Widget):
    
    '''A layout manager containing a center widget sorrounded by four margin
    widgets.
    
            +---------------------------+
            |             top           |
            +---------------------------+
            |      |            |       |
            | left |   center   | right |
            |      |            |       |
            +---------------------------+
            |           bottom          |
            +---------------------------+
    
    This layout manager does a little bit of extra effort to maintain the aspect
    constraint of the center widget, if this is set. It does so, by allowing for
    a bit more flexibility in the sizing of the margins. Two shortcut methods
    are provided to set the margin sizes in one shot: set_fixed_margins and
    set_min_margins. The first sets the margins to fixed sizes, while the second
    gives them a minimal size and a (neglectably) small desire to grow. Using
    the latter may be useful when setting an aspect constraint on the center
    widget, because this way the maximum size of the center widget may be
    controlled without creating empty spaces between the widgets.
    '''
    
    def __init__(self, horizontal=None, vertical=None):
        Widget.__init__(self, horizontal, vertical)
        mw = 3.*cm
        self.left = Widget(horizontal=GumSpring(grow=0.15, minimal=mw), parent=self)
        self.right = Widget(horizontal=GumSpring(grow=0.15, minimal=mw), parent=self)
        self.top = Widget(vertical=GumSpring(grow=0.15, minimal=mw/golden_ratio), parent=self)
        self.bottom = Widget(vertical=GumSpring(grow=0.15, minimal=mw/golden_ratio), parent=self)
        self.center = Widget(horizontal=GumSpring(grow=0.7), vertical=GumSpring(grow=0.7), parent=self)
        
    def set_fixed_margins(self, left, right, top, bottom):
        '''Give margins fixed size constraints.'''
        
        self.left.set_horizontal(left,0)
        self.right.set_horizontal(right,0)
        self.top.set_vertical(top,0)
        self.bottom.set_vertical(bottom,0)
        
    def set_min_margins(self, left, right, top, bottom):
        '''Give margins a minimal size and the possibility to grow.
        
        The desire to grow is set to a very small number.'''
        self.left.set_horizontal(left,0.0001)
        self.right.set_horizontal(right,0.0001)
        self.top.set_vertical(top,0.0001)
        self.bottom.set_vertical(bottom,0.0001)
        
    def get_min_size(self):
        shs, svs = Widget.get_min_size(self)
        
        sl, sr, st, sb, sc = [ x.get_min_size() for x in self.left, self.right, self.top, self.bottom, self.center ]
        gl, gr, gt, gb, gc = [ x.get_grow() for x in self.left, self.right, self.top, self.bottom, self.center ]

        shsum = sl[0]+sr[0]+sc[0]
        svsum = st[1]+sb[1]+sc[1]

        # prevent widgets from collapsing
        for s,g in ((sl,gl),(sr,gr),(sc,gc)):
            if s[0]==0.0 and g[0]!=0.0:
                shsum += 1.*cm
        
        for s,g in ((st,gt),(sb,gb),(sc,gc)):
            if s[1]==0.0 and g[1]!=0.0:
                svsum += 1.*cm
        
        sh = max(shs, shsum)
        sv = max(svs, svsum)
        
        return sh, sv
        
    def get_grow(self):
        ghs, gvs = Widget.get_grow(self)
        gh = (self.left.get_grow()[0]+self.right.get_grow()[0]+self.center.get_grow()[0])*ghs
        gv = (self.top.get_grow()[1]+self.bottom.get_grow()[1]+self.center.get_grow()[1])*gvs
        return gh, gv
    
    def set_size(self, size, offset):
        (sh, sv), (oh, ov) = self.legalize(size, offset)
        
        sl, sr, st, sb, sc = [ x.get_min_size() for x in self.left, self.right, self.top, self.bottom, self.center ]
        gl, gr, gt, gb, gc = [ x.get_grow() for x in self.left, self.right, self.top, self.bottom, self.center ]
        
        ah = sh - (sl[0]+sr[0]+sc[0])
        av = sv - (st[1]+sb[1]+sc[1])
        if ah < 0.0 or av < 0.0:
            raise Exception("Container too small for contents")
        slh, srh, sch = distribute( (sl[0], sr[0], sc[0]), (gl[0],gr[0],gc[0]), ah )
        stv, sbv, scv = distribute( (st[1], sb[1], sc[1]), (gt[1],gb[1],gc[1]), av )
        if self.center.aspect is not None:
            ahm = sh - (sl[0]+sr[0] + scv/self.center.aspect)
            avm = sv - (st[1]+sb[1] + sch*self.center.aspect)
            if 0.0 < ahm < ah:            
                slh, srh, sch = distribute( (sl[0], sr[0], scv/self.center.aspect), (gl[0],gr[0],0.0), ahm )
            
            elif 0.0 < avm < av:
                stv, sbv, scv = distribute( (st[1], sb[1], sch*self.center.aspect), (gt[1],gb[1],0.0), avm )
        
        ah = sh - (slh+srh+sch)
        av = sv - (stv+sbv+scv)
        
        oh += ah/2.
        ov += av/2.
        sh -= ah
        sv -= av
        
        self.left.set_size((slh,scv), (oh,ov+sbv))
        self.right.set_size((srh,scv), (oh+slh+sch,ov+sbv))
        self.top.set_size((sh,stv), (oh,ov+stv+scv))
        self.bottom.set_size((sh,sbv), (oh,ov))
        self.center.set_size((sch,scv), (oh+slh,ov+sbv))
        Widget.set_size(self,(sh,sv), (oh,ov))
        
    def set_widget(self, which='center', widget=None):
        
        '''Set one of the sub-widgets.
        
        `which` should be one of 'left', 'right', 'top', 'bottom' or 'center'.
        '''
        
        if widget is None:
            widget = Widget()
        
        if which in ('left', 'right', 'top', 'bottom', 'center'):
            self.__dict__[which] = widget
        else:
            raise Exception('No such sub-widget: %s' % which)

        widget.set_parent(self)
            
    def get_widget(self, which='center'):
        
        '''Get one of the sub-widgets.
        
        `which` should be one of 'left', 'right', 'top', 'bottom' or 'center'.
        '''
        
        if which in ('left', 'right', 'top', 'bottom', 'center'):
           return self.__dict__[which]
        else:
            raise Exception('No such sub-widget: %s' % which)
    
    def get_children(self):
        return [ self.left, self.right, self.top, self.bottom, self.center ]
    
class GridLayout(Widget):
    
    '''A layout manager which arranges its sub-widgets in a grid.
    
    The grid spacing is flexible and based on the sizing policies of the
    contained sub-widgets. If an equidistant grid is needed, the sizing policies
    of the sub-widgets have to be set equally.

    The height of each row and the width of each column is derived from the
    sizing policy of the largest sub-widget in the row or column in question.
    The algorithm is not very sophisticated, so conflicting sizing policies
    might not be resolved optimally.
    '''
    
    def __init__(self, nx=2, ny=2, horizontal=None, vertical=None):
        
        '''Create new grid layout with `nx` columns and `ny` rows.'''
        
        Widget.__init__(self, horizontal, vertical)
        self.grid = []
        for iy in range(ny):
            row = []
            for ix in range(nx):
                w = Widget(parent=self)
                row.append(w)
                
            self.grid.append(row)
    
    def sub_min_sizes_as_array(self):
        esh = num.array([ [ w.get_min_size()[0] for w in row ] for row in self.grid ], dtype=num.float)
        esv = num.array([ [ w.get_min_size()[1] for w in row ] for row in self.grid ], dtype=num.float)
        return esh, esv
    
    def sub_grows_as_array(self):
        egh = num.array([ [ w.get_grow()[0] for w in row ] for row in self.grid ], dtype=num.float)
        egv = num.array([ [ w.get_grow()[1] for w in row ] for row in self.grid ], dtype=num.float)
        return egh, egv
    
    def get_min_size(self):
        sh, sv = Widget.get_min_size(self)
        esh, esv = self.sub_min_sizes_as_array()
        sh = max(sh, num.sum(esh.max(0)))
        sv = max(sv, num.sum(esv.max(1)))
        return sh, sv
        
    def get_grow(self):
        ghs, gvs = Widget.get_grow(self)
        egh, egv = self.sub_grows_as_array()        
        gh = num.sum(egh.max(0))*ghs
        gv = num.sum(egv.max(1))*gvs
        return gh, gv
        
    def set_size(self, size, offset):
        (sh, sv), (oh, ov) = self.legalize(size, offset)
        esh, esv = self.sub_min_sizes_as_array()
        egh, egv = self.sub_grows_as_array()
        
        # available additional space
        ah = sh - num.sum(esh.max(0))
        av = sv - num.sum(esv.max(1))
        if ah < 0.0 or av < 0.0:
            raise Exception("Container too small for contents")
        
        nx, ny = esh.shape
        
        # distribute additional space on rows and columns
        # according to grow weights and minimal sizes
        gsh = egh.sum(1)[:,num.newaxis].repeat(ny,axis=1)
        nesh = esh.copy()
        nesh += num.where( gsh > 0.0, ah*egh/gsh, 0.0 )
        nsh = num.maximum(nesh.max(0),esh.max(0))
        
        gsv = egv.sum(0)[num.newaxis,:].repeat(nx,axis=0)
        nesv = esv.copy()
        nesv += num.where( gsv > 0.0, av*egv/gsv, 0.0 )
        nsv = num.maximum(nesv.max(1),esv.max(1))
        
        ah = sh - sum(nsh)
        av = sv - sum(nsv)
        
        oh += ah/2.
        ov += av/2.
        sh -= ah
        sv -= av

        # resize child widgets
        neov = ov + sum(nsv)
        for row, nesv in zip(self.grid, nsv):
            neov -= nesv
            neoh = oh
            for w, nesh in zip(row,nsh):
                w.set_size((nesh, nesv),(neoh,neov))
                neoh += nesh
        
        Widget.set_size(self, (sh,sv), (oh,ov))
        
    def set_widget(self, ix, iy, widget=None):
        
        '''Set one of the sub-widgets.
        
        Sets the sub-widget in column `ix` and row `iy`. The indices are counted
        from zero.
        '''
        
        if widget is None:
            widget = Widget()
        
        self.grid[iy][ix] = widget
        widget.set_parent(self)

    def get_widget(self, ix, iy):
        
        '''Get one of the sub-widgets.

        Gets the sub-widget from column `ix` and row `iy`. The indices are
        counted from zero.'''
        
        return self.grid[iy][ix]
    
    def get_children(self):
        children = []
        for row in self.grid:
            children.extend(row)
            
        return children
        
def aspect_for_projection(R,J):
    gmt = GMT()
    gmt.psbasemap( R, J, '-G0', finish=True )
    l, b, r, t = gmt.bbox()
    return (t-b)/(r-l)

        
class GMT:
    '''A thin wrapper to GMT command execution.
    
    Each instance of this class is used for the task of producing one PS or PDF
    output file.

    Output of a series of GMT commands is accumulated in memory and can then be
    saved as PS or PDF file using the save() method.

    GMT commands are accessed as method calls to instances of this class. See
    docstring of __getattr__() for details on how the method's arguments are
    translated into options and arguments for the GMT command.

    Associated with each instance of this class, a temporary directory is
    created, where temporary files may be created, and which is automatically
    deleted, when the object is destroyed. The tempfilename() method may be used
    to get a random filename in the instance's temporary directory.

    Any .gmtdefaults files are ignored. The GMT class uses a fixed set of
    defaults, which may be altered via an argument to the constructor. If
    possible, GMT is run in 'isolation mode', which was introduced with GMT
    version 4.2.2, by setting GMT_TMPDIR to the instance's  temporary directory.
    With earlier versions of GMT, problems may arise with parallel execution of
    more than one GMT instance.
    
    Each instance of the GMT class may pick a specific version of GMT which
    shall be used, so that, if multiple versions of GMT are installed on the
    system, different versions of GMT can be used simultaneously such that
    backward compatibility of the scripts can be maintained.
    '''
    

    def __init__(self, config=None, version='newest' ):
        
        '''Create a new GMT instance.
         
        A dict gmt_config may be given to override some of the default GMT
        parameters. The version argument may be used to select a specific GMT
        version, which should be used with this GMT instance. The selected
        version of GMT has to be installed on the system, must be supported by
        gmtpy and gmtpy must know where to find it.'''
        
        self.installation = get_gmt_installation(version)
        self.gmt_config = dict(self.installation['defaults'])
        
        if config:
            self.gmt_config.update(config)
        
        self.tempdir = tempfile.mkdtemp("","gmtpy-")
        self.gmt_config_filename = pjoin(self.tempdir, 'gmtdefaults')
        f = open(self.gmt_config_filename,'w')
        for k,v in self.gmt_config.iteritems():
            f.write( '%s = %s\n' % (k,v) )
        f.close()
        
        self.output = cStringIO.StringIO()
        self.needstart = True
        self.finished = False
                
        self.environ = os.environ.copy()
        self.environ['GMTHOME'] = self.installation['home']
        # GMT isolation mode: works only properly with GMT version >= 4.2.2
        self.environ['GMT_TMPDIR'] = self.tempdir
       
        self.layout = None
        self.command_log = []
       
    def __del__(self):
        import shutil
        shutil.rmtree(self.tempdir)
        
    def _gmtcommand(self, command, 
                          *addargs,
                          **kwargs):
        
        '''Execute arbitrary GMT command.
        
        See docstring in __getattr__ for details.
        '''
        
        in_stream       = kwargs.pop('in_stream',   None)
        in_filename     = kwargs.pop('in_filename', None)
        in_string       = kwargs.pop('in_string',   None)
        in_columns      = kwargs.pop('in_columns',  None)
        in_rows         = kwargs.pop('in_rows',     None)
        out_stream      = kwargs.pop('out_stream',  None)
        out_filename    = kwargs.pop('out_filename',None)
        out_string      = kwargs.pop('out_string',  None)
        finish          = kwargs.pop('finish',      False)
        
        assert(not self.finished)
        
        # check for mutual exclusiveness on input and output possibilities
        assert( 1 >= len([ x for x in [in_stream, in_filename, in_string, in_columns, in_rows] if x is not None ]) )
        assert( 1 >= len([ x for x in [out_stream, out_filename] if x is not None ]) )
     
        options = []
        
        out_mustclose = False
        if out_filename is not None:
            out_mustclose = True
            out_stream = open(out_filename, 'w')
        
        in_mustclose = False
        if in_filename is not None:
            in_mustclose = True
            in_stream = open(in_filename, 'r')
        
        # convert option arguments to strings
        for k,v in kwargs.items():
            if len(k) > 1:
                raise Exception('Found illegal keyword argument "%s" while preparing options for command "%s"' % (k, command))
                
            if type(v) is bool:
                if v:
                    options.append( '-%s' % k )
            elif type(v) is tuple or type(v) is list:
                options.append( '-%s' % k + '/'.join([ str(x) for x in v]) )
            else:
                options.append( '-%s%s' % (k,str(v)) )
       
        # if not redirecting to an external sink, handle -K -O
        if not out_stream:
            if not finish:
                options.append('-K')
            else:
                self.finished = True
            
            if not self.needstart:
                options.append('-O')
            else:
                self.needstart = False
    
        # run the command
        args = [ pjoin(self.installation['bin'],command) ]
        if not os.path.isfile( args[0] ):
            raise Exception('No such file: %s' % args[0] )
        args.extend( options )
        args.extend( addargs )
        args.append( '+'+self.gmt_config_filename )
        p = subprocess.Popen( args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=self.environ )
        toproc = p.stdin
        
        # feed data to gmt process
        if in_stream is not None:
            toproc.write( in_stream.read() )
        
        if in_string is not None:
            toproc.write( in_string )
        
        if in_columns is not None:
            for row in izip(*in_columns):
                toproc.write(' '.join([str(x) for x in row]))
                toproc.write('\n')
            
        if in_rows is not None:
            for row in in_rows:
                toproc.write(' '.join([str(x) for x in row]))
                toproc.write('\n')
            
        toproc.close()
        
        # gather output from gmt process
        if not out_stream:
            self.output.write( p.stdout.read() )
        else:
            out_stream.write( p.stdout.read() )
        
        # cleanup
        if in_mustclose:
            in_stream.close()
        
        if out_mustclose:
            out_stream.close()
 
        retcode = p.wait()
        if retcode != 0: 
            raise Exception('Command %s returned an error. While executing command:\n%s' % (command, str(args)) )
        
        self.command_log.append( args )
        
    
    def __getattr__(self, command):
        
        '''Maps to call self._gmtcommand(command, *addargs, **kwargs).
                        
        Execute arbitrary GMT command.
        
        Run a GMT command and by default append its postscript output to the
        output file maintained by the GMT instance on which this method is
        called.

        Except for a few keyword arguments listed below, any `kwargs` and
        `addargs` are converted into command line options and arguments and
        passed to the GMT command. Numbers in keyword arguments are converted
        into strings. E.g. S=10 is translated into '-S10'. Tuples of numbers or
        strings are converted into strings where the elements of the tuples are
        separated by slashes '/'. E.g. R=(10,10,20,20) is translated into
        '-R10/10/20/20'. Options with a boolean argument are only appended to
        the GMT command, if their values are True.
        
        If no output redirection is in effect, the -K and -O options are handled
        by pygmt and thus should not be specified.

        The standard input of the GMT process is fed by data selected with one 
        of the following in_* keyword arguments:
        
           in_stream:   Data is read from an open file like object.
           in_filename: Data is read from the given file.
           in_string:   String content is dumped to the process.
           in_columns:  A 2D nested iterable whose elements can be accessed as
                        in_columns[icolumn][irow] is converted into an ascii
                        table, which is fed to the process.
           in_rows:     A 2D nested iterable whos elements can be accessed as
                        in_rows[irow][icolumn] is converted into an ascii table,
                        which is fed to the process.

        The standard output of the GMT process may be redirected by one of the 
        following options:
        
           out_stream:   Data is fed to an open file like object.
           out_filename: Data is dumped to the given file.
        
        If the keyword argument `finish` is present, the postscript file, which
        is maintained by the GMT instance is finished, and no further plotting
        is allowed.'''
        
        def f(*args, **kwargs):
            return self._gmtcommand(command, *args, **kwargs)
        return f
         
    def tempfilename(self, name=None):
        '''Get filename for temporary file in the private temp directory.
           
           If no `name` argument is given, a random name is picked. If `name` is
           given, returns a path ending in that `name`.'''
        
        if not name: 
            name = ''.join( [ random.choice(alphabet) for i in range(10) ])
        
        fn = pjoin(self.tempdir, name)
        return fn
    
    def tempfile(self, name=None):
        '''Create and open a file in the private temp directory.'''
        
        fn = self.tempfilename(name)
        f = open(fn, 'w')
        return f, fn
    
    def save(self, filename=None, bbox=None):
        '''Finish and save figure as PDF or PS file.
           
           If filename ends in '.pdf' a PDF file is created by piping the 
           GMT output through epstopdf.
           
           The bounding box is set according to the margins and size specified
           in the constructor.'''
        
        if not self.finished:
            self.psxy(R=True, J=True, finish=True)
        
        if bbox:
            oldbb = re.compile(r'%%BoundingBox:((\s+\d+){4})')
            newbb = '%%%%BoundingBox: %s' % ' '.join([ str(int(x)) for x in bbox ])
        
        if filename:
            tempfn = pjoin(self.tempdir, 'incomplete')
            out = open(tempfn, 'w')
        else:
            out = sys.stdout
            
        if bbox:
            out.write(oldbb.sub(newbb,self.output.getvalue()))
        else:
            out.write(self.output.getvalue())
        
        out.close()
        
        if filename.endswith('.pdf'):
            subprocess.call([ 'epstopdf', '--outfile='+filename, tempfn])
        else:
            shutil.move(tempfn, filename)
    
    def bbox(self):
        find_bb = re.compile(r'%%BoundingBox:((\s+\d+){4})')
        m = find_bb.search(self.output.getvalue())
        if m:
            bb = [ float(x) for x in m.group(1).split() ]
            return bb
        else:
            raise Exception('Cannot find bbox')
    
    
    def get_command_log(self):
        '''Get the command log.'''
        
        return self.command_log
        
    def __str__(self):
        s = ''
        for com in self.command_log:
            s += com[0] + "\n  " + "\n  ".join(com[1:]) + "\n\n"
        return s
    
    def page_size_points(self):
        '''Try to get paper size of output postscript file in points.'''
        
        pm = self.gmt_config['PAPER_MEDIA'].lower()
        if pm.endswith('+') or pm.endswith('-'):
            pm = pm[:-1]
            
        orient = self.gmt_config['PAGE_ORIENTATION'].lower()
        if pm in paper_sizes:
           
            if orient == 'portrait':
                return paper_sizes[pm]
            else:
                return paper_sizes[pm][1], paper_sizes[pm][0]
        
        m = re.match(r'custom_([0-9.]+)([cimp]?)x([0-9.]+)([cimp]?)', pm)
        if m:
            w, uw, h, uh = m.groups()
            w, h = float(w), float(h)
            if uw: w *= units[uw]
            if uh: h *= units[uh]
            if orient == 'portrait':
                return w,h
            else:
                return h,w
        
        return None, None
    
    def default_layout(self):
        '''Get a default layout for the output page.
           
        One of three different layouts is choosen, depending on the PAPER_MEDIA
        settings in the GMT configuration dict.

        If PAPER_MEDIA ends with a "+" such that EPS output is selected, a
        FrameLayout is centered on the page, whose size is controlled by its
        center widget's size plus the margins of the FrameLayout.

        If PAPER_MEDIA indicates, that a custom page size is wanted by starting
        with "Custom_", a FrameLayout is used to fill the complete page. The
        center widget's size is then controlled by the page's size minus the
        margins of the FrameLayout.
        
        In any other case, two FrameLayouts are nested, such that the outer
        layout attaches a 1 cm (printer) margin around the complete page, and
        the inner FrameLayout's center widget takes up as much space as possible
        under the constraint, that an aspect ratio of 1/golden_ratio is
        preserved.
        
        In any case, a reference to the innermost FrameLayout instance is
        returned. The top-level layout can be accessed by calling get_parent() on
        the returned layout.
        '''
        
        if self.layout is None:
            w,h = self.page_size_points()
            
            if w is None or h is None:
                raise Exception("Can't determine page size for layout")
            
            pm = self.gmt_config['PAPER_MEDIA'].lower()
            
            if pm.endswith('+'):
                outer = CenterLayout()
                outer.set_policy( (w,h), (0.,0.) )
                inner = FrameLayout()
                outer.set_widget( inner )
                widget = inner.get_widget('center')
                widget.set_policy((w/golden_ratio, 0.), (0.,0.), aspect=1./golden_ratio )
                mw = 3.0*cm
                inner.set_fixed_margins(mw, mw, mw/golden_ratio, mw/golden_ratio)
                self.layout = inner
                
            elif pm.startswith('custom_'):
                layout = FrameLayout()
                layout.set_policy( (w,h), (0.,0.) )
                mw = 3.0*cm
                layout.set_min_margins(mw, mw, mw/golden_ratio, mw/golden_ratio)
                self.layout = layout
            else:
                outer = FrameLayout()
                outer.set_policy( (w,h), (0.,0.) )
                outer.set_fixed_margins(1.*cm, 1.*cm, 1.*cm, 1.*cm)
                
                inner = FrameLayout()
                outer.set_widget('center', inner)
                mw = 3.0*cm
                inner.set_min_margins(mw, mw, mw/golden_ratio, mw/golden_ratio)
                
                widget = inner.get_widget('center')
                widget.set_aspect(1./golden_ratio)
                
                self.layout = inner
            
        return self.layout
                    
    def draw_layout(self, layout):
        '''Use psxy to draw layout; for debugging'''
        
        corners = layout.get_corners(descend=True)
        rects = num.array(layout.get_sizes(),dtype=num.float)
        rects_wid = rects[:,0,0]
        rects_hei = rects[:,0,1]
        rects_center_x = rects[:,1,0] + rects_wid*0.5
        rects_center_y = rects[:,1,1] + rects_hei*0.5
        nrects = len(rects)
        prects = (rects_center_x, rects_center_y, num.arange(nrects), 
                                    num.zeros(nrects), rects_hei,rects_wid)
        
        points = num.array(corners,dtype=num.float)
        
        cptfile = self.tempfilename()
        self.makecpt( C = 'ocean',
                    T = '%g/%g/%g' % (-nrects,nrects,1),
                    Z = True, 
                    out_filename = cptfile)
                    
        bb = layout.bbox()
        self.psxy( in_columns = prects,
                C = cptfile,
                W = '1p',
                S = 'J',
                R = (bb[0],bb[2],bb[1],bb[3]),
                *layout.XYJ())

    

if __name__ == '__main__':
    
    examples_dir = 'gmtpy-examples'
    if os.path.exists(examples_dir):
        shutil.rmtree(examples_dir)
    os.mkdir(examples_dir)
    
    
    x = FrameLayout()    
    y = GridLayout(3,3)
    y.set_widget(1,1,x)
    
    corners = y.get_corners(descend=True)
    rects = num.array(y.get_sizes(),dtype=num.float)
    rects_wid = rects[:,0,0]
    rects_hei = rects[:,0,1]
    rects_center_x = rects[:,1,0] + rects_wid*0.5
    rects_center_y = rects[:,1,1] + rects_hei*0.5
    nrects = len(rects)
    prects = (rects_center_x, rects_center_y, num.arange(nrects), num.zeros(nrects), rects_hei,rects_wid,)
    
    points = num.array(corners,dtype=num.float)
    
    gmt = GMT(config={'PAPER_MEDIA':'Custom_%gx%g' % (5.*inch,3.*inch), 
                       'FRAME_PEN':'2p',})
    
    widget = gmt.default_widget()
    
    axx = Ax( mode='min-max', space=0.05 )
    ayy = Ax( mode='min-max', space=0.05 )
    plot = ScaleGuru( [ (points[:,0], points[:,1]) ], axes=(axx,ayy), aspect=widget.height()/widget.width() )
    
    cptfile = gmt.tempfilename()
    gmt.makecpt( C = 'ocean',
                  T = '%g/%g/%g' % (-nrects,nrects,1),
                  Z = True, 
                  out_filename = cptfile)
    
    gmt.psxy( in_columns = prects,
               C = cptfile,
               W = '2p/black', 
               S = 'J',
               *(widget.XYJ() + plot.RB()))
               
    gmt.save('test.pdf')
    
    ### Example 1
    
    gmt = GMT()
    gmt.pscoast( R='g', J='E32/30/8i', B='10g10', D='c', A=10000, S=(114,159,207), G=(233,185,110), W='thinnest')
    gmt.save(pjoin(examples_dir,'example1.pdf'))
    gmt.save(pjoin(examples_dir,'example1.ps'))
    
    
    ### Example 2
    
    gmt = GMT(config=dict(PAPER_MEDIA='Custom_%gx%g' % (7*inch, 7*inch)))
    gmt.pscoast( R='g', 
                 J='E%g/%g/%g/%gi' % (0., 0., 180., 6.),
                 B='0g0', 
                 D='c', 
                 A=10000, 
                 S=(114,159,207), 
                 G=(233,185,110), 
                 W='thinnest', 
                 X='c', 
                 Y='c')
                 
    rows = []
    for i in range(5):
        strike = random.random() * 360.
        dip = random.random() * 90.
        rake = random.random() * 360.-180.
        lat = random.random() * 180.-90.
        lon = random.random() * 360.-180.
        rows.append([ lon, lat, 0., strike, dip, rake, 4., 0.,0., 
                            '%.3g, %.3g, %.3g' % (strike, dip, rake) ])
    gmt.psmeca( R=True, 
                J=True, 
                S='a0.5',
                in_rows=rows )

    gmt.save(pjoin(examples_dir, 'example2.ps'))
    gmt.save(pjoin(examples_dir, 'example2.pdf'))
    
    
    ### Example 3
    
    conf = { 'PAGE_COLOR':'0/0/0',  
             'BASEMAP_FRAME_RGB': '255/255/255'}
    gmt = GMT( config=conf)
    widget = gmt.default_widget()
    gmt.psbasemap(  R=(-5,5,-5,5), 
                    J='X%gi/%gi' % (5,5), 
                    B='1:Time [s]:/1:Amplitude [m]:WSen', 
                    G='100/100/100' )
    rows = []
    for i in range(11):
        rows.append((i-5., random.random()*10.-5.))
    
    gmt.psxy( in_rows=rows, R=True, J=True)
    gmt.save(pjoin(examples_dir, 'example3.pdf'))
    
    
    ### Example 4
    
    x = num.linspace(0.,math.pi*6,1001)
    y1 = num.sin(x) * 1e-9
    y2 = 2.0 * num.cos(x) * 1e-9
    
    xax = Ax( label='Time', unit='s' )
    yax = Ax( label='Amplitude', unit='m', scaled_unit='nm', scaled_unit_factor=1e9, approx_ticks=5, space=0.05  )
    guru = ScaleGuru( [(x,y1),(x,y2)], axes=(xax,yax) )
    gmt = GMT(config={'PAPER_MEDIA':'Custom_%gx%g' % (8*inch,3*inch)})
    layout = gmt.default_layout()
    widget = gmt.default_widget()
    
    draw_layout(gmt,layout)
    
    gmt.psbasemap( *(widget.JXY() + guru.RB(ax_projection=True)) )
    gmt.psxy( in_columns=(x,y1), *(widget.JXY() + guru.R()) )
    gmt.psxy( in_columns=(x,y2), *(widget.JXY() + guru.R()) )
    gmt.save(pjoin(examples_dir, 'example4.pdf'), bbox=layout.bbox())
    gmt.save(pjoin(examples_dir, 'example4.ps'), bbox=layout.bbox())
    
   
    ### Example 5
    
    x = num.linspace(0.,1e9,1001)
    y = num.sin(x)
    
    axx = Ax( label='Time', unit='s')
    ayy = Ax( label='Amplitude', scaled_unit= 'cm', scaled_unit_factor=100., space=0.05, approx_ticks=5 )
    
    guru = ScaleGuru( [ (x,y) ], axes=(axx,ayy))
    
    gmt = GMT( config=conf)
    layout = gmt.default_layout()
    widget = gmt.default_widget()
    gmt.psbasemap( *(widget.JXY() + guru.RB(ax_projection=True)) )
    gmt.psxy( in_columns=(x,y), *(widget.JXY() + guru.R()) )
    gmt.save(pjoin(examples_dir, 'example5.pdf'), bbox=layout.bbox())
    
    
    ### Example 6
    
    gmt = GMT(config={ 'PAPER_MEDIA':'a3'} )
    nx, ny = 2,5
    grid = GridLayout(nx,ny)
    
    layout = gmt.default_layout()
    layout.set_widget('center', grid)
    
    widgets = []
    for iy in range(ny):
        for ix in range(nx):
            inner = FrameLayout()
            inner.set_fixed_margins( 1.*cm*golden_ratio, 1.*cm*golden_ratio, 1.*cm, 1.*cm )
            grid.set_widget(ix,iy, inner)
            inner.set_vertical( 0, (iy+1.) )
            widgets.append(inner.get_widget('center'))
        
    draw_layout(gmt, layout)
    for widget in widgets:
        x = num.linspace(0.,10.,5)
        y = num.random.rand(5)
        xax = Ax(approx_ticks=4, snap=True)
        yax = Ax(approx_ticks=4, snap=True)
        guru = ScaleGuru( [ (x,y) ], axes=(xax,yax) )
        gmt.psbasemap( *(widget.JXY() + guru.RB(ax_projection=True)) )
        gmt.psxy( in_columns=(x,y), *(widget.JXY() + guru.R()) )
        
    gmt.save(pjoin(examples_dir, 'example6.pdf'), bbox=layout.bbox())

