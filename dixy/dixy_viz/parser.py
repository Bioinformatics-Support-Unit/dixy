import urllib
import json
import tempfile
import os.path

def main(input_list, slug, data_out, metadata_out):
    all_data = []
    all_headers = []
    for f in input_list:
        #url_slug = 'http://research.ncl.ac.uk/colonyzer/QFAVis/GISDatasets/'
        if slug.startswith('http'):
            fh = urllib.urlopen(slug+f, 'rU')
        else:
            infile = os.path.join(slug, f)
            fh = open(infile, 'rU')
        data_lines = fh.read().splitlines()
        fh.close()
        all_data.append(parse_data(data_lines))
        header = parse_header(data_lines)
        header['file_name'] = f
        all_headers.append(header)
    unified_orf_names = get_orf_names(all_data)
    m = make_metadata(all_data, all_headers)
    j = make_json(all_data, all_headers, unified_orf_names)
    #tmp = tempfile.NamedTemporaryFile(suffix='.js', dir='/home/django/media/js/', delete=False)
    out = open(data_out, 'w')
    out.write('data = '+json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))
    out.close()
    md_out = open(metadata_out, 'w')
    md_out.write(m)
    md_out.close()
    return data_out

def get_orf_names(data):
    orfs_list = []
    for d in data:
        orfs_list.append(d[0].keys())
    #get union of a list of lists
    orf_set = set().union(*orfs_list)
    return list(orf_set)

def lin_fit(x, y):
    '''Fits a linear fit of the form mx+b to the data'''
    import numpy
    #from scipy import optimize
    import scipy.optimize
    fitfunc = lambda params, x: params[0] * x    #create fitting function of form mx
    errfunc = lambda p, x, y: fitfunc(p, x) - y  #create error function for least squares fit
    init_a = 0.5                            #find initial value for a (gradient)
    init_p = numpy.array((init_a))  #bundle initial values in initial parameters
    #calculate best fitting parameters (i.e. m and b) using the error function
    p1, success = scipy.optimize.leastsq(errfunc, init_p.copy(),
            args = (numpy.array(x), numpy.array(y)))
    f = fitfunc(p1, x)          #create a fit with those parameters
    return p1, f

def get_slope(coordinates):
    xpoints = []
    ypoints = []
    for key in coordinates.keys():
        xpoints.append(float(coordinates[key][0]))
        ypoints.append(float(coordinates[key][1]))
    #from scikits.statsmodels.api import OLS
    p, fit = lin_fit(xpoints, ypoints)
    #results = OLS(ypoints, xpoints).fit()
    #slope = results.params
    #print p, slope
    #print results.summary()
    return p[0]

def make_metadata(data, headers):
#    j = []
    metadata_str = "metadata = {"
    all_xs = []
    all_ys = []
    for d in data:
        all_xs.append(d[1])
        all_ys.append(d[2])
    for i in range(0,len(all_xs)):
        for j in range(0,len(all_xs)):
            try:
                control_background_i = headers[i]['x-axis background']
                control_background_j = headers[j]['x-axis background']
                query_background_i = headers[i]['y-axis background']
                query_background_j = headers[j]['y-axis background']
            except KeyError:
                control_background_i = headers[i]['x-axis screen name']
                control_background_j = headers[j]['x-axis screen name']
                query_background_i = headers[i]['y-axis screen name']
                query_background_j = headers[j]['y-axis screen name']

            xx_pair = get_coordinates(all_xs[i], all_xs[j])
            xy_pair = get_coordinates(all_xs[i], all_ys[j])
            yx_pair = get_coordinates(all_ys[i], all_xs[j])
            yy_pair = get_coordinates(all_ys[i], all_ys[j])
            xx_slope = get_slope(xx_pair)
            xy_slope = get_slope(xy_pair)
            yx_slope = get_slope(yx_pair)
            yy_slope = get_slope(yy_pair)
            metadata_str = metadata_str+"""
    "{0}.x_{1}.x.xlabel": "{2}",
    "{0}.x_{1}.x.ylabel": "{3}",
    "{0}.x_{1}.x.slope": {4},
    "{0}.x_{1}.x.blabel": "{2} {3}",""".format(headers[i]['file_name'],
        headers[j]['file_name'],
        control_background_i,
        control_background_j,
        xx_slope)
            metadata_str = metadata_str+"""
    "{0}.x_{1}.y.xlabel": "{2}",
    "{0}.x_{1}.y.ylabel": "{3}",
    "{0}.x_{1}.y.slope": {4},
    "{0}.x_{1}.y.blabel": "{2} {3}",""".format(headers[i]['file_name'],
        headers[j]['file_name'],
        control_background_i,
        query_background_j,
        xy_slope)
            metadata_str = metadata_str+"""
    "{0}.y_{1}.x.xlabel": "{2}",
    "{0}.y_{1}.x.ylabel": "{3}",
    "{0}.y_{1}.x.slope": {4},
    "{0}.y_{1}.x.blabel": "{2} {3}",""".format(headers[i]['file_name'],
        headers[j]['file_name'],
        query_background_i,
        control_background_j,
        yx_slope)
            metadata_str = metadata_str+"""
    "{0}.y_{1}.y.xlabel": "{2}",
    "{0}.y_{1}.y.ylabel": "{3}",
    "{0}.y_{1}.y.slope": {4},
    "{0}.y_{1}.y.blabel": "{2} {3}",""".format(headers[i]['file_name'],
        headers[j]['file_name'],
        query_background_i,
        query_background_j,
        yy_slope)
    metadata_str = metadata_str[:-1]
    metadata_str = metadata_str + """
};"""
    return metadata_str

def get_coordinates(x, y):
    coordinates = {}
    for key in x.keys():
        try:
            coordinate = (x[key], y[key])
        except KeyError:
            coordinate = (x[key], -20.0)
        coordinates[key] = coordinate
    for key in y.keys():
        if key not in coordinates.keys():
            coordinates[key] = (-20.0, y[key])
    return coordinates

def make_json(data, headers, orfs):
    j = []
    for orf in orfs:
        d = {}
        d['orf_name'] = orf
        try:
            d['gene_name'] = data[0][0][orf]
        except KeyError:
            try:
                d['gene_name'] = data[1][0][orf]
            except KeyError:
                d['gene_name'] = data[2][0][orf]
        for i in range(0, len(headers)):
            filename = headers[i]['file_name']
            try:
                d[filename+'.x'] = float(data[i][1][orf])
                d[filename+'.y'] = float(data[i][2][orf])
                d[filename+'.gis'] = float(data[i][3][orf])
                d[filename+'.q'] = float(data[i][4][orf])
            except KeyError:
                d[filename+'.x'] = float(-20)
                d[filename+'.y'] = float(-20)
                d[filename+'.gis'] = float(1)
                d[filename+'.q'] = float(1)
        j.append(d)
    return j

def parse_header(fc):
    """Parse out significant information from QFA file header"""
    metadata = {}
    for line in fc:
        if line.startswith('###'):
            #end of metadata header
            break
        tokens = line.rstrip().split(':')
        metadata[tokens[0]] = tokens[1].strip()
    return metadata

def parse_data(fc):
    """Parse data from QFA file, use col as column reference for values"""
    data = 0
    genes = {}
    x_points = {}
    y_points = {}
    gis_values = {}
    q_values = {}
    for line in fc:
        if data == 1:
            #process data
            if line.startswith('ORF'):
                #this is the column headers
                pass
            else:
                tokens = line.split('\t')
                orf_name = tokens[0]
                genes[orf_name] = tokens[1]
                x_points[orf_name] = tokens[6]
                y_points[orf_name] = tokens[5]
                gis_values[orf_name] = tokens[4]
                q_values[orf_name] = tokens[3]
        if line.startswith('###'):
            #end of metadata header
            data = 1
    return (genes, x_points, y_points, gis_values, q_values)

if __name__ == '__main__':
    import sys
    #sys.argv[1] = location of files (URL or filesystem)
    #sys.argv[2] = output data json
    #sys.argv[3] = output metadata json
    #input_list = ['YKU70_23GIS_NEW.txt',
    #        'CDC13-1_20GIS_NEW.txt',
    #        'CDC13-1_27GIS_NEW.txt',
    #        'CDC13-1_36GIS_NEW.txt',
    #        'YKU70_30GIS_NEW.txt',
    #        'YKU70_37.5GIS_NEW.txt',
    #        'YKU70_37GIS_NEW.txt',
    #    ]
    #input_list = ['DAL_cdc2-2_CONC_vs_CONT_CONC_30_SDM_rhlk_CTGNH_GIS.txt',
    #'DAL_pol1-1_CONC_vs_CONT_CONC_33_SDM_rhlk_CTGNH_GIS.txt',
    #'DAL_pol2-12_CONC_vs_cdc13-1_DIL_36_SDM_rhlk_CTGNH_GIS.txt',
    #'DAL_pol2-12_CONC_vs_cdc2-2_CONC_36_SDM_rhlk_CTGNH_GIS.txt',
    #'DAL_pol2-12_CONC_vs_CONT_CONC_36_SDM_rhlk_CTGNH_GISold.txt',
    #'DAL_pol2-12_CONC_vs_CONT_CONC_36_SDM_rhlk_CTGNH_GIS.txt',
    #'DAL_pol2-12_CONC_vs_pol1-1_CONC_36_SDM_rhlk_CTGNH_GIS.txt',
    #'EJA_G4Quad_Drugs_vs_G4Quad_Drugs_30_100mM_HU_CSM__GIS_RFC1.txt',
    #'EJA_G4Quad_Drugs_vs_G4Quad_Drugs_30_100mM_HU_CSM__GIS.txt',
    #'EJA_G4Quad_Drugs_vs_G4Quad_Drugs_30_CSM_Lydall_GIS.txt',
    #'EMH_cdc13-1_con_vs_stn1-13_30_SDM_rhlk_CTGNH_nAUC_GIS.txt',
    #'MJG_stn1-13_vs_CONT_CONC_33_SDM_rhlk_CTGNH_nAUC_GIS.txt',]
    #input_list = ['cdc13-1_DIL_vs_cdc2-2_CONC_28.txt',
    #'cdc13-1_DIL_vs_CONT_DIL_28.txt',
    #'cdc13-1_DIL_vs_pol1-1_CONC_28.txt',
    #'cdc2-2_CONC_vs_cdc13-1_CONC_30.txt',
    #'cdc2-2_CONC_vs_CONT_CONC_30.txt',
    #'pol1-1_CONC_vs_cdc13-1_CONC_33.txt',
    #'pol1-1_CONC_vs_cdc2-2_CONC_33.txt',
    #'pol1-1_CONC_vs_CONT_CONC_33.txt',
    #'pol2-12_CONC_vs_cdc13-1_DIL_36.txt',
    #'pol2-12_CONC_vs_cdc2-2_CONC_36.txt',
    #'pol2-12_CONC_vs_CONT_CONC_36.txt',
    #'pol2-12_CONC_vs_pol1-1_CONC_36.txt',
    #]
    input_list = ['cdc13-1.txt',
    'cdc2-2 (Pol delta).txt',
    'HU_100mM.txt',
    'pol1-4 (Pol alpha).txt',
    'pol2-12 (Pol epsilon).txt',
    ]
    main(input_list, sys.argv[1], sys.argv[2], sys.argv[3])
