'''
This is the main interface to the metahtml library.

NOTE:
all metainformation extracted with the parse function contains the library's version;
this makes it easy to compare multiple parses of the same html file and determine which is the most accurate
'''

# imports
from collections import defaultdict
import importlib
import lxml
import lxml.html
import lxml.etree
import time
from urllib.parse import urlparse
from types import SimpleNamespace

from . import adblock
from . import content
from .content import ExtractorConfig_recall, ExtractorConfig

# configure logging
import logging
logger = logging.getLogger('metahtml')

################################################################################
# set the __version__ variable
################################################################################

# is the project has been installed with pip,
# then we set __version__ to the version specified in setup.py
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version

# if the project is not installed,
# then we fallback to get_version_info()
except DistributionNotFound:
    import os
    __version__ = 'uninstalled.' + os.popen('TZ=utc git log -1 --date="format-local:%Y%m%d%H%M%S" --format=format:"%cd+%h"').read()

# log the version
logger.info("version="+str(__version__))

################################################################################
# parse functions
################################################################################

cxpath_ldjson = lxml.etree.XPath('//script[@type="application/ld+json"]')

            
def parse(html, url, property_filter=None, fast=False, extractor_config=ExtractorConfig()):
    '''
    return the dictionary of meta information for a given html/url combination
    '''

    start_time = time.process_time()

    # create the parser object
    parser = SimpleNamespace()
    parser.html = html
    parser.url = url
    parser.url_parsed = urlparse(url)
    parser.meta = defaultdict(lambda: None)
    parser.meta['version'] = __version__
    parser.meta['url'] = url

    # parse the raw html using lxml;
    try:
        parser.doc = lxml.html.fromstring(html)

    except ValueError:
        html_fixed = html[html.find('?>')+2:]
        parser.doc = lxml.html.fromstring(html_fixed)

    except lxml.etree.ParserError:
        parser.doc = lxml.html.fromstring('<html></html>')

    import ujson
    import simplejson
    json_libs = [ujson,simplejson]

    parser.ldjsons = []
    for element in cxpath_ldjson(parser.doc):
        for lib in json_libs:
            try:
                parser.ldjsons.append(lib.loads(element.text))
            except Exception as e:
                logger.warning('url='+url+' '+lib.__name__+': '+"e="+e.__repr__())

    hostnames_adblock_breaks = [
        'archive.thinkprogress.org',
        'resources.infosecinstitute.com',
        'cjr.org',
        'www.cjr.org',
        ]
    if not fast and parser.url_parsed.hostname not in hostnames_adblock_breaks:
        adblock.rm_ads(parser)

    def calculate_property(property, property_name=None):
        if property_name is None:
            property_name = property
        if property_filter is None or property_name in property_filter:
            module = importlib.import_module('metahtml.property.'+property)
            parser.meta[property_name] = module.Extractor.extract(parser)

    calculate_property('timestamp.published')
    calculate_property('type')
    calculate_property('links', 'links.all')

    if parser.meta['type']['best']['value'] == 'article':
        calculate_property('language')
        calculate_property('timestamp.modified')

        if not fast:
            calculate_property('urls.canonical')
            calculate_property('urls.altlang')
            calculate_property('author')
            calculate_property('title')
            calculate_property('description')

            if not property_filter or 'content' in property_filter:
                parser.meta['content'] = {
                    'best': content.extract_content(parser, config=extractor_config)
                }

            calculate_property('links', 'links.content')
    else:
        parser.meta['timestamp.published'] = None

    stop_time = time.process_time()
    parser.meta['process_time'] = stop_time - start_time

    return parser.meta


def parse_for_testing(html, url, fast=False, debug=False):
    property_filter = ['language', 'timestamp.modified', 'timestamp.published', 'type']
    meta = parse(html, url, property_filter, fast)
    if debug:
        return meta
    else:
        return simplify_meta(meta)


def simplify_meta(meta):
    '''
    removes the verbose/debug information from the meta dictionary
    '''
    import json
    ret = {}
    for k in meta:
        try:
            if meta[k]['best'] is not None:
                ret[k] = meta[k]['best']['value']
        except (TypeError,KeyError) as e:
            ret[k] = meta[k]

    del ret['version']
    del ret['process_time']

    # convert datetime objects into strings
    ret = json.loads(json.dumps(dict(ret), default=str))

    return ret
