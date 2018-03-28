import geopandas_osm.osm
import numpy as np

from shapely.geometry import MultiLineString, Polygon, MultiPoint, LineString
from shapely.ops import polygonize

def outline_to_mask(line, x, y):
    """Create mask from outline contour

    Parameters
    ----------
    line: array-like (N, 2)
    x, y: 1-D grid coordinates (input for meshgrid)

    Returns
    -------
    mask : 2-D boolean array (True inside)

    Examples
    --------
    >>> from shapely.geometry import Point
    >>> poly = Point(0,0).buffer(1)
    >>> x = np.linspace(-5,5,100)
    >>> y = np.linspace(-5,5,100)
    >>> mask = outline_to_mask(poly.boundary, x, y)
    """
    import matplotlib.path as mplp
    mpath = mplp.Path(line)
    X, Y = np.meshgrid(x, y)
    points = np.array((X.flatten(), Y.flatten())).T
    mask = mpath.contains_points(points).reshape(X.shape)
    return mask


def _grid_bbox(x, y):
    dx = dy = 0
    return x[0]-dx/2, x[-1]+dx/2, y[0]-dy/2, y[-1]+dy/2

def _bbox_to_rect(bbox):
    l, r, b, t = bbox
    return Polygon([(l, b), (r, b), (r, t), (l, t)])

def shp_mask(shp, x, y, m=None):
    """Use recursive sub-division of space and shapely contains method to create a raster mask on a regular grid.

    Parameters
    ----------
    shp : shapely's Polygon (or whatever with a "contains" method and intersects method)
    x, y : 1-D numpy arrays defining a regular grid
    m : mask to fill, optional (will be created otherwise)

    Returns
    -------
    m : boolean 2-D array, True inside shape.

    Examples
    --------
    >>> from shapely.geometry import Point
    >>> poly = Point(0,0).buffer(1)
    >>> x = np.linspace(-5,5,100)
    >>> y = np.linspace(-5,5,100)
    >>> mask = shp_mask(poly, x, y)
    """
    rect = _bbox_to_rect(_grid_bbox(x, y))
    
    if m is None:
        m = np.zeros((y.size, x.size), dtype=bool)
               
    if not shp.intersects(rect):
        m[:] = False
    
    elif shp.contains(rect):
        m[:] = True
    
    else:
        k, l = m.shape
        
        if k == 1 and l == 1:
            m[:] = shp.contains(Point(x[0], y[0]))
            
        elif k == 1:
            m[:, :l//2] = shp_mask(shp, x[:l//2], y, m[:, :l//2])
            m[:, l//2:] = shp_mask(shp, x[l//2:], y, m[:, l//2:])
            
        elif l == 1:
            m[:k//2] = shp_mask(shp, x, y[:k//2], m[:k//2])
            m[k//2:] = shp_mask(shp, x, y[k//2:], m[k//2:])
        
        else:
            m[:k//2, :l//2] = shp_mask(shp, x[:l//2], y[:k//2], m[:k//2, :l//2])
            m[:k//2, l//2:] = shp_mask(shp, x[l//2:], y[:k//2], m[:k//2, l//2:])
            m[k//2:, :l//2] = shp_mask(shp, x[:l//2], y[k//2:], m[k//2:, :l//2])
            m[k//2:, l//2:] = shp_mask(shp, x[l//2:], y[k//2:], m[k//2:, l//2:])
        
    return m

def get_polygon(typ, bbox, recurse, tags, height, width, make_plot=True):
    df = geopandas_osm.osm.query_osm(typ, bbox, recurse, tags)
    if make_plot:
        df[df.type == 'LineString'].plot(figsize=(15,15))
    
    lines = df[df.type == 'LineString']['geometry']
    area = polygonize(lines.tolist())
    
    output = dict(type='FeatureCollection', features=[])
    for (index, area) in enumerate(area):
        
        feature = dict(type='Feature', properties=dict(index=index))
        feature['geometry'] = area.__geo_interface__
        output['features'].append(feature)
        
    x = np.linspace(bbox[0],bbox[2],width)
    y = np.linspace(bbox[3],bbox[1],height)
    mask = shp_mask(area, x, y)
    
    return mask