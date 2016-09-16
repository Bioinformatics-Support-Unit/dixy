from django.shortcuts import render_to_response
import datetime
import urllib
import urllib2
import os
from dixy_viz import qfa_parser
from django.template import RequestContext

def get_input_list(site='dixy'):
    if site == 'dixy':
        input_list = ['YKU70_23GIS_NEW.txt',
            'CDC13-1_20GIS_NEW.txt',
            'CDC13-1_27GIS_NEW.txt',
            'CDC13-1_36GIS_NEW.txt',
            'YKU70_30GIS_NEW.txt',
            'YKU70_37.5GIS_NEW.txt',
            'YKU70_37GIS_NEW.txt',
            ]
    if site == 'dixy-private':
        input_list = ['YKU70_23GIS_NEW.txt',
            'CDC13-1_20GIS_NEW.txt',
            'CDC13-1_27GIS_NEW.txt',
            'CDC13-1_36GIS_NEW.txt',
            'YKU70_30GIS_NEW.txt',
            'YKU70_37.5GIS_NEW.txt',
            'YKU70_37GIS_NEW.txt',
            ]
    if site == 'dixy-pol':
        input_list = ['cdc13-1.txt',
            'cdc2-2 (Pol delta).txt',
            'HU_100mM.txt',
            'pol1-4 (Pol alpha).txt',
            'pol2-12 (Pol epsilon).txt',
            ]
    if site == 'dixy-telo':
        input_list = ['APB_QFA0142_cdc13-1_rad9D_27_SDM_rhlk_CTGNH_vs_QFA0140_cdc13-1_27_SDM_rhlk_CTGH_MDRMDP_GIS.txt',
        'APB_QFA0142_cdc13-1_rad9D_UD_X1_SDM_rhlk_CTGNH_vs_QFA0140_cdc13-1_UD_X3_SDM_rhlk_CTGH_MDRMDP_GIS.txt',
        'DAL_QFA0051_cdc13-1_exo1D_30_SDM_rhlk_CTGNH_vs_QFA0140_cdc13-1_27_SDM_rhlk_CTGH_MDRMDP_GIS.txt',
        'DAL_QFA0136_stn1-13_33_SDM_rhlk_CTGNH_vs_QFA0018_lyp1_HLN_33_SDM_rhlk_CTGNH_MDRMDP_GIS.txt',
        'DAL_QFA0139_Yku70_37_5_SDM_rhk_CTGN_vs_QFA0141_ura3_37_SDM_rhk_CTGN_MDRMDP_GIS.txt',
        'DAL_QFA0140_cdc13-1_27_SDM_rhlk_CTGH_vs_QFA0141_ura3_27_SDM_rhk_CTGN_MDRMDP_GIS.txt',
        'DAL_QFA0140_cdc13-1_UD_X3_SDM_rhlk_CTGH_vs_QFA0141_ura3_UD_X3_SDM_rhk_CTGN_MDRMDP_GIS.txt',
        'MJG_QFA0131_rfa3-313_30_SDM_rhlk_CTGNH_vs_QFA0018_lyp1_HLN_30_SDM_rhlk_CTGNH_MDRMDP_GIS.txt',
        ]
    return input_list

def get_url_stem(path):
    if path.startswith('/dixy-telo'):
        return 'dixy-telo'
    if path.startswith('/dixy-private'):
        return 'dixy-private'
    if path.startswith('/dixy-pol'):
        return 'dixy-pol'
    else:
        return 'dixy'

def home(request):
    url_stem = get_url_stem(request.get_full_path())
    return render_to_response(url_stem+'/index.html', {'year':datetime.datetime.now().year,
                                            'context': 'home',
                                            'path_var': url_stem,})

def about(request):
    url_stem = get_url_stem(request.get_full_path())
    return render_to_response(url_stem+'/about.html', {'year':datetime.datetime.now().year,
                                            'context': 'about'})

def contact(request):
    url_stem = get_url_stem(request.get_full_path())
    return render_to_response(url_stem+'/contact.html', {'year':datetime.datetime.now().year,
                                            'context': 'contact'})

def test(request):
    url_stem = get_url_stem(request.get_full_path())
    chart_index = 0
    input_files = get_input_list(url_stem)
    i = 0
    x_files = []
    y_files = []
    metadata = []
    button_labels = {}
    for input_file in input_files:
        x_files.append(input_file+".x")
        y_files.append(input_file+".y")
        metadata.append(input_file+".x_"+input_file+".y")
        this_label = os.path.splitext(input_file)[0]
        button_labels[i] = this_label
        i += 1
    return render_to_response(url_stem+'/dviz2.html', {
            'data': url_stem+'-data.js',
            'metadata': url_stem+'-metadata.js',
            'x_files': x_files,
            'y_files': y_files,
            'metadata_labels': metadata,
            'inputs': button_labels,
            'context': 'viz',
            'year':datetime.datetime.now().year,
            },
            context_instance=RequestContext(request)
        )


def d3_viz(request, index=None):
    url_stem = get_url_stem(request.get_full_path())
    #set the required datasets
    if request.method != 'POST':
        #render the form to select datasets
        #parse input headers (to get individual axes & complete sets)
        headers = {}
        input_list = get_input_list(url_stem)
        for f in input_list:
            headers[f] = qfa_parser.get_header_only(f, url_stem)
        return render_to_response(url_stem+'/viz_form.html', {'context': 'viz',
                            'headers': headers,
                            'year':datetime.datetime.now().year,
                            },
                            context_instance=RequestContext(request))
    else:
        #data_file = p.main(input_list)
        #os.chmod(data_file, 420)
        #data_file_name = data_file.split('/')[-1]
        x_files = []
        y_files = []
        parsers = []
        metadata = []
        button_labels = {}
        chart_index = 0
        i = 0
        for thing in request.POST:
            if thing.endswith('.txt'):
                x_files.append(thing+".x")
                y_files.append(thing+".y")
                metadata.append(thing+".x_"+thing+".y")
                this_label = os.path.splitext(thing)[0]
                button_labels[i] = this_label
                i += 1
        is_custom = request.POST.get('custom1', False)
        if is_custom:
            button_labels[i] = 'Custom Set'
            x_file = request.POST['xdata1']
            y_file = request.POST['ydata1']
            x_files.append(x_file)
            y_files.append(y_file)
            metadata.append(x_file+"_"+y_file)
        #dc = d3charts.D3charts(x_files, y_files)
        return render_to_response(url_stem+'/dviz2.html', {#'charts':dc.javascript,
            #'data': data_file_name,
            'data': url_stem+'-data.js',
            'metadata': url_stem+'-metadata.js',
            'x_files': x_files,
            'y_files': y_files,
            'metadata_labels': metadata,
            'inputs': button_labels,
            'context': 'viz',
            'year':datetime.datetime.now().year,
            },
            context_instance=RequestContext(request)
        )

def get_interactions(start, gene_list):
    accesskey = "095db6c6e05853ca59a01352d80528d6"
    url = "http://webservice.thebiogrid.org/interactions/"
    params = urllib.urlencode({
        'searchIds': 'true',
        'geneList': gene_list,
        'taxId': '559292',
        'interSpeciesExcluded': 'true',
        'includeInteractorInteractions': 'true',
        'throughputTag': 'low',
        'start': start,
        'accesskey': accesskey,
    })
    fh = urllib2.urlopen(url, params)
    return fh.readlines()

def process_interactions(i, g, e, gene_array):
    for line in i:
        line = line.rstrip()
        tokens = line.split('\t')
        sys_name1 = tokens[5]
        sys_name2 = tokens[6]
        gene1 = tokens[7]
        gene2 = tokens[8]
        int_type = tokens[12]
        if sys_name1 in gene_array:
            g.append((gene1, True))
        else:
            g.append((gene1, False))
        if sys_name2 in gene_array:
            g.append((gene2, True))
        else:
            g.append((gene2, False))
        e.append((gene1, gene2, int_type))
    return g, e

def network(request, in_genes=None):
    url_stem = get_url_stem(request.get_full_path())
    if in_genes:
        gene_list = in_genes
        gene_array = gene_list.split('|')
    else:
        gene_array = ['YPL089C',]
        gene_list = '|'.join(gene_array)
    start = 0
    interactions = get_interactions(start, gene_list)
    genes = []
    edges = []
    while len(interactions) == 10000:
        genes, edges = process_interactions(interactions, genes, edges, gene_array)
        start += 10000
        interactions = get_interactions(start, gene_list)
    genes, edges = process_interactions(interactions, genes, edges, gene_array)
    genes = list(set(genes))
    edges = list(set(edges))
    json_genes = []
    json_edges = []
    i = 0
    for gene in genes:
        i += 1
        if gene[1]:
            favColor = '#C40233'
        else:
            favColor = '#888'
        if i == len(genes):
            s = "{ data: { id: '"+str(i)+"', name: '"+gene[0]+"', favColor: '"+favColor+"' } }"
        else:
            s = "{ data: { id: '"+str(i)+"', name: '"+gene[0]+"', favColor: '"+favColor+"' } },"
        json_genes.append(s)
    i = 0
    for edge in edges:
        i += 1
        source = str([x[0] for x in genes].index(edge[0]) + 1)
        target = str([x[0] for x in genes].index(edge[1]) + 1)
        if edge[2] == 'physical':
            favColor = "#6FB1FC"
        elif edge[2] == 'genetic':
            favColor = "#86B342"
        if i == len(edges):
            s = "{ data: { source: '"+source+"', target: '"+target+"', favColor: '"+favColor+"' } }"
        else:
            s = "{ data: { source: '"+source+"', target: '"+target+"', favColor: '"+favColor+"' } },"
        json_edges.append(s)
    return render_to_response(url_stem+'/network.html', {
                                        'request': in_genes,
                                        'genes':json_genes,
                                        'edges':json_edges,
                                        'start':start,
                                        'year':datetime.datetime.now().year,})

def get_data(f):
    url_slug = 'http://research.ncl.ac.uk/colonyzer/QFAVis/GISDatasets/'
    fh = urllib.urlopen(url_slug+f, 'r')
    data_lines = fh.read().splitlines()
    fh.close()
    return data_lines
