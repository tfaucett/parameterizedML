'''
author Taylor Faucett <tfaucett@uci.edu>
'''

import ROOT
import numpy as np
import pickle
import os
import glob
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import scipy.interpolate
import shutil
import gzip
from mpl_toolkits.mplot3d import Axes3D
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib
from sknn.mlp import Regressor, Layer

'''
The standard set of matplotlib colors plus some extras from the HTML/CSS standard
are used in multiple functions so they are defined globally here.
'''
colors  = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'brown', 'orange']

# Used to reconstruct the colormap in viscm
parameters = {'xp': [22.674387857633945, 11.221508276482126, -14.356589454756971, -47.18817758739222, -34.59001004812521, -6.0516291196352654],
              'yp': [-20.102530541012214, -33.08246073298429, -42.24476439790574, -5.595549738219887, 42.5065445026178, 40.13395157135497],
              'min_JK': 18.8671875,
              'max_JK': 92.5}

cm_data = [[ 0.26700401,  0.00487433,  0.32941519],
       [ 0.26851048,  0.00960483,  0.33542652],
       [ 0.26994384,  0.01462494,  0.34137895],
       [ 0.27130489,  0.01994186,  0.34726862],
       [ 0.27259384,  0.02556309,  0.35309303],
       [ 0.27380934,  0.03149748,  0.35885256],
       [ 0.27495242,  0.03775181,  0.36454323],
       [ 0.27602238,  0.04416723,  0.37016418],
       [ 0.2770184 ,  0.05034437,  0.37571452],
       [ 0.27794143,  0.05632444,  0.38119074],
       [ 0.27879067,  0.06214536,  0.38659204],
       [ 0.2795655 ,  0.06783587,  0.39191723],
       [ 0.28026658,  0.07341724,  0.39716349],
       [ 0.28089358,  0.07890703,  0.40232944],
       [ 0.28144581,  0.0843197 ,  0.40741404],
       [ 0.28192358,  0.08966622,  0.41241521],
       [ 0.28232739,  0.09495545,  0.41733086],
       [ 0.28265633,  0.10019576,  0.42216032],
       [ 0.28291049,  0.10539345,  0.42690202],
       [ 0.28309095,  0.11055307,  0.43155375],
       [ 0.28319704,  0.11567966,  0.43611482],
       [ 0.28322882,  0.12077701,  0.44058404],
       [ 0.28318684,  0.12584799,  0.44496   ],
       [ 0.283072  ,  0.13089477,  0.44924127],
       [ 0.28288389,  0.13592005,  0.45342734],
       [ 0.28262297,  0.14092556,  0.45751726],
       [ 0.28229037,  0.14591233,  0.46150995],
       [ 0.28188676,  0.15088147,  0.46540474],
       [ 0.28141228,  0.15583425,  0.46920128],
       [ 0.28086773,  0.16077132,  0.47289909],
       [ 0.28025468,  0.16569272,  0.47649762],
       [ 0.27957399,  0.17059884,  0.47999675],
       [ 0.27882618,  0.1754902 ,  0.48339654],
       [ 0.27801236,  0.18036684,  0.48669702],
       [ 0.27713437,  0.18522836,  0.48989831],
       [ 0.27619376,  0.19007447,  0.49300074],
       [ 0.27519116,  0.1949054 ,  0.49600488],
       [ 0.27412802,  0.19972086,  0.49891131],
       [ 0.27300596,  0.20452049,  0.50172076],
       [ 0.27182812,  0.20930306,  0.50443413],
       [ 0.27059473,  0.21406899,  0.50705243],
       [ 0.26930756,  0.21881782,  0.50957678],
       [ 0.26796846,  0.22354911,  0.5120084 ],
       [ 0.26657984,  0.2282621 ,  0.5143487 ],
       [ 0.2651445 ,  0.23295593,  0.5165993 ],
       [ 0.2636632 ,  0.23763078,  0.51876163],
       [ 0.26213801,  0.24228619,  0.52083736],
       [ 0.26057103,  0.2469217 ,  0.52282822],
       [ 0.25896451,  0.25153685,  0.52473609],
       [ 0.25732244,  0.2561304 ,  0.52656332],
       [ 0.25564519,  0.26070284,  0.52831152],
       [ 0.25393498,  0.26525384,  0.52998273],
       [ 0.25219404,  0.26978306,  0.53157905],
       [ 0.25042462,  0.27429024,  0.53310261],
       [ 0.24862899,  0.27877509,  0.53455561],
       [ 0.2468114 ,  0.28323662,  0.53594093],
       [ 0.24497208,  0.28767547,  0.53726018],
       [ 0.24311324,  0.29209154,  0.53851561],
       [ 0.24123708,  0.29648471,  0.53970946],
       [ 0.23934575,  0.30085494,  0.54084398],
       [ 0.23744138,  0.30520222,  0.5419214 ],
       [ 0.23552606,  0.30952657,  0.54294396],
       [ 0.23360277,  0.31382773,  0.54391424],
       [ 0.2316735 ,  0.3181058 ,  0.54483444],
       [ 0.22973926,  0.32236127,  0.54570633],
       [ 0.22780192,  0.32659432,  0.546532  ],
       [ 0.2258633 ,  0.33080515,  0.54731353],
       [ 0.22392515,  0.334994  ,  0.54805291],
       [ 0.22198915,  0.33916114,  0.54875211],
       [ 0.22005691,  0.34330688,  0.54941304],
       [ 0.21812995,  0.34743154,  0.55003755],
       [ 0.21620971,  0.35153548,  0.55062743],
       [ 0.21429757,  0.35561907,  0.5511844 ],
       [ 0.21239477,  0.35968273,  0.55171011],
       [ 0.2105031 ,  0.36372671,  0.55220646],
       [ 0.20862342,  0.36775151,  0.55267486],
       [ 0.20675628,  0.37175775,  0.55311653],
       [ 0.20490257,  0.37574589,  0.55353282],
       [ 0.20306309,  0.37971644,  0.55392505],
       [ 0.20123854,  0.38366989,  0.55429441],
       [ 0.1994295 ,  0.38760678,  0.55464205],
       [ 0.1976365 ,  0.39152762,  0.55496905],
       [ 0.19585993,  0.39543297,  0.55527637],
       [ 0.19410009,  0.39932336,  0.55556494],
       [ 0.19235719,  0.40319934,  0.55583559],
       [ 0.19063135,  0.40706148,  0.55608907],
       [ 0.18892259,  0.41091033,  0.55632606],
       [ 0.18723083,  0.41474645,  0.55654717],
       [ 0.18555593,  0.4185704 ,  0.55675292],
       [ 0.18389763,  0.42238275,  0.55694377],
       [ 0.18225561,  0.42618405,  0.5571201 ],
       [ 0.18062949,  0.42997486,  0.55728221],
       [ 0.17901879,  0.43375572,  0.55743035],
       [ 0.17742298,  0.4375272 ,  0.55756466],
       [ 0.17584148,  0.44128981,  0.55768526],
       [ 0.17427363,  0.4450441 ,  0.55779216],
       [ 0.17271876,  0.4487906 ,  0.55788532],
       [ 0.17117615,  0.4525298 ,  0.55796464],
       [ 0.16964573,  0.45626209,  0.55803034],
       [ 0.16812641,  0.45998802,  0.55808199],
       [ 0.1666171 ,  0.46370813,  0.55811913],
       [ 0.16511703,  0.4674229 ,  0.55814141],
       [ 0.16362543,  0.47113278,  0.55814842],
       [ 0.16214155,  0.47483821,  0.55813967],
       [ 0.16066467,  0.47853961,  0.55811466],
       [ 0.15919413,  0.4822374 ,  0.5580728 ],
       [ 0.15772933,  0.48593197,  0.55801347],
       [ 0.15626973,  0.4896237 ,  0.557936  ],
       [ 0.15481488,  0.49331293,  0.55783967],
       [ 0.15336445,  0.49700003,  0.55772371],
       [ 0.1519182 ,  0.50068529,  0.55758733],
       [ 0.15047605,  0.50436904,  0.55742968],
       [ 0.14903918,  0.50805136,  0.5572505 ],
       [ 0.14760731,  0.51173263,  0.55704861],
       [ 0.14618026,  0.51541316,  0.55682271],
       [ 0.14475863,  0.51909319,  0.55657181],
       [ 0.14334327,  0.52277292,  0.55629491],
       [ 0.14193527,  0.52645254,  0.55599097],
       [ 0.14053599,  0.53013219,  0.55565893],
       [ 0.13914708,  0.53381201,  0.55529773],
       [ 0.13777048,  0.53749213,  0.55490625],
       [ 0.1364085 ,  0.54117264,  0.55448339],
       [ 0.13506561,  0.54485335,  0.55402906],
       [ 0.13374299,  0.54853458,  0.55354108],
       [ 0.13244401,  0.55221637,  0.55301828],
       [ 0.13117249,  0.55589872,  0.55245948],
       [ 0.1299327 ,  0.55958162,  0.55186354],
       [ 0.12872938,  0.56326503,  0.55122927],
       [ 0.12756771,  0.56694891,  0.55055551],
       [ 0.12645338,  0.57063316,  0.5498411 ],
       [ 0.12539383,  0.57431754,  0.54908564],
       [ 0.12439474,  0.57800205,  0.5482874 ],
       [ 0.12346281,  0.58168661,  0.54744498],
       [ 0.12260562,  0.58537105,  0.54655722],
       [ 0.12183122,  0.58905521,  0.54562298],
       [ 0.12114807,  0.59273889,  0.54464114],
       [ 0.12056501,  0.59642187,  0.54361058],
       [ 0.12009154,  0.60010387,  0.54253043],
       [ 0.11973756,  0.60378459,  0.54139999],
       [ 0.11951163,  0.60746388,  0.54021751],
       [ 0.11942341,  0.61114146,  0.53898192],
       [ 0.11948255,  0.61481702,  0.53769219],
       [ 0.11969858,  0.61849025,  0.53634733],
       [ 0.12008079,  0.62216081,  0.53494633],
       [ 0.12063824,  0.62582833,  0.53348834],
       [ 0.12137972,  0.62949242,  0.53197275],
       [ 0.12231244,  0.63315277,  0.53039808],
       [ 0.12344358,  0.63680899,  0.52876343],
       [ 0.12477953,  0.64046069,  0.52706792],
       [ 0.12632581,  0.64410744,  0.52531069],
       [ 0.12808703,  0.64774881,  0.52349092],
       [ 0.13006688,  0.65138436,  0.52160791],
       [ 0.13226797,  0.65501363,  0.51966086],
       [ 0.13469183,  0.65863619,  0.5176488 ],
       [ 0.13733921,  0.66225157,  0.51557101],
       [ 0.14020991,  0.66585927,  0.5134268 ],
       [ 0.14330291,  0.66945881,  0.51121549],
       [ 0.1466164 ,  0.67304968,  0.50893644],
       [ 0.15014782,  0.67663139,  0.5065889 ],
       [ 0.15389405,  0.68020343,  0.50417217],
       [ 0.15785146,  0.68376525,  0.50168574],
       [ 0.16201598,  0.68731632,  0.49912906],
       [ 0.1663832 ,  0.69085611,  0.49650163],
       [ 0.1709484 ,  0.69438405,  0.49380294],
       [ 0.17570671,  0.6978996 ,  0.49103252],
       [ 0.18065314,  0.70140222,  0.48818938],
       [ 0.18578266,  0.70489133,  0.48527326],
       [ 0.19109018,  0.70836635,  0.48228395],
       [ 0.19657063,  0.71182668,  0.47922108],
       [ 0.20221902,  0.71527175,  0.47608431],
       [ 0.20803045,  0.71870095,  0.4728733 ],
       [ 0.21400015,  0.72211371,  0.46958774],
       [ 0.22012381,  0.72550945,  0.46622638],
       [ 0.2263969 ,  0.72888753,  0.46278934],
       [ 0.23281498,  0.73224735,  0.45927675],
       [ 0.2393739 ,  0.73558828,  0.45568838],
       [ 0.24606968,  0.73890972,  0.45202405],
       [ 0.25289851,  0.74221104,  0.44828355],
       [ 0.25985676,  0.74549162,  0.44446673],
       [ 0.26694127,  0.74875084,  0.44057284],
       [ 0.27414922,  0.75198807,  0.4366009 ],
       [ 0.28147681,  0.75520266,  0.43255207],
       [ 0.28892102,  0.75839399,  0.42842626],
       [ 0.29647899,  0.76156142,  0.42422341],
       [ 0.30414796,  0.76470433,  0.41994346],
       [ 0.31192534,  0.76782207,  0.41558638],
       [ 0.3198086 ,  0.77091403,  0.41115215],
       [ 0.3277958 ,  0.77397953,  0.40664011],
       [ 0.33588539,  0.7770179 ,  0.40204917],
       [ 0.34407411,  0.78002855,  0.39738103],
       [ 0.35235985,  0.78301086,  0.39263579],
       [ 0.36074053,  0.78596419,  0.38781353],
       [ 0.3692142 ,  0.78888793,  0.38291438],
       [ 0.37777892,  0.79178146,  0.3779385 ],
       [ 0.38643282,  0.79464415,  0.37288606],
       [ 0.39517408,  0.79747541,  0.36775726],
       [ 0.40400101,  0.80027461,  0.36255223],
       [ 0.4129135 ,  0.80304099,  0.35726893],
       [ 0.42190813,  0.80577412,  0.35191009],
       [ 0.43098317,  0.80847343,  0.34647607],
       [ 0.44013691,  0.81113836,  0.3409673 ],
       [ 0.44936763,  0.81376835,  0.33538426],
       [ 0.45867362,  0.81636288,  0.32972749],
       [ 0.46805314,  0.81892143,  0.32399761],
       [ 0.47750446,  0.82144351,  0.31819529],
       [ 0.4870258 ,  0.82392862,  0.31232133],
       [ 0.49661536,  0.82637633,  0.30637661],
       [ 0.5062713 ,  0.82878621,  0.30036211],
       [ 0.51599182,  0.83115784,  0.29427888],
       [ 0.52577622,  0.83349064,  0.2881265 ],
       [ 0.5356211 ,  0.83578452,  0.28190832],
       [ 0.5455244 ,  0.83803918,  0.27562602],
       [ 0.55548397,  0.84025437,  0.26928147],
       [ 0.5654976 ,  0.8424299 ,  0.26287683],
       [ 0.57556297,  0.84456561,  0.25641457],
       [ 0.58567772,  0.84666139,  0.24989748],
       [ 0.59583934,  0.84871722,  0.24332878],
       [ 0.60604528,  0.8507331 ,  0.23671214],
       [ 0.61629283,  0.85270912,  0.23005179],
       [ 0.62657923,  0.85464543,  0.22335258],
       [ 0.63690157,  0.85654226,  0.21662012],
       [ 0.64725685,  0.85839991,  0.20986086],
       [ 0.65764197,  0.86021878,  0.20308229],
       [ 0.66805369,  0.86199932,  0.19629307],
       [ 0.67848868,  0.86374211,  0.18950326],
       [ 0.68894351,  0.86544779,  0.18272455],
       [ 0.69941463,  0.86711711,  0.17597055],
       [ 0.70989842,  0.86875092,  0.16925712],
       [ 0.72039115,  0.87035015,  0.16260273],
       [ 0.73088902,  0.87191584,  0.15602894],
       [ 0.74138803,  0.87344918,  0.14956101],
       [ 0.75188414,  0.87495143,  0.14322828],
       [ 0.76237342,  0.87642392,  0.13706449],
       [ 0.77285183,  0.87786808,  0.13110864],
       [ 0.78331535,  0.87928545,  0.12540538],
       [ 0.79375994,  0.88067763,  0.12000532],
       [ 0.80418159,  0.88204632,  0.11496505],
       [ 0.81457634,  0.88339329,  0.11034678],
       [ 0.82494028,  0.88472036,  0.10621724],
       [ 0.83526959,  0.88602943,  0.1026459 ],
       [ 0.84556056,  0.88732243,  0.09970219],
       [ 0.8558096 ,  0.88860134,  0.09745186],
       [ 0.86601325,  0.88986815,  0.09595277],
       [ 0.87616824,  0.89112487,  0.09525046],
       [ 0.88627146,  0.89237353,  0.09537439],
       [ 0.89632002,  0.89361614,  0.09633538],
       [ 0.90631121,  0.89485467,  0.09812496],
       [ 0.91624212,  0.89609127,  0.1007168 ],
       [ 0.92610579,  0.89732977,  0.10407067],
       [ 0.93590444,  0.8985704 ,  0.10813094],
       [ 0.94563626,  0.899815  ,  0.11283773],
       [ 0.95529972,  0.90106534,  0.11812832],
       [ 0.96489353,  0.90232311,  0.12394051],
       [ 0.97441665,  0.90358991,  0.13021494],
       [ 0.98386829,  0.90486726,  0.13689671],
       [ 0.99324789,  0.90615657,  0.1439362 ]]

cm_data_bin = [[ 0.26700401,  0.00487433,  0.32941519],
       [1.0, 1.0, 1.0],
       [ 0.99324789,  0.90615657,  0.1439362 ]]

test_cm = LinearSegmentedColormap.from_list(__file__, cm_data)
test_cm_bin = LinearSegmentedColormap.from_list(__file__, cm_data_bin)


def file_runner(directory):
	print 'Entering file_runner'
	files = glob.iglob(directory+'*.root')
	for data in files:
		file_generate(data)


def file_generate(root_file):
	print 'Entering file_generate'
	print 'Generating data using values from: %s' %root_file
	mwwbb = root_export(root_file,'xtt','mwwbb')
	mx = root_export(root_file,'xtt','mx')
	mjj = root_export(root_file, 'xtt', 'mjj')
	target = root_export(root_file,'xtt','target')
	jes = root_export(root_file, 'xtt', 'jes')
	size = len(mwwbb)
	data = np.zeros((size, 5))
	if target[0] == 0.000000:
		label = 'bkg'
	elif target[0] == 1.000000:
		label = 'sig'
	for i in range(size):
		data[i, 0] = mwwbb[i]
		data[i, 1] = mjj[i]
		data[i, 2] = jes[i]
		data[i, 3] = target[i]
		data[i, 4] = mx[i]
	np.savetxt('data/root_export/%s_mx_%0.0f_jes_%0.3f.dat' %(label, mx[0], jes[0]), data, fmt='%f')

def root_export(root_file, tree, leaf):
	'''
	root_export uses pyROOT to scan invidual values from a selected TTree and TLeaf.
	The function returns an array of all values.

	Note: GetEntriesFast() is preferred over GetEntires() as it correctly returns a
	floating point number in case of a value of 0.0 rather than, in the case of GetEntries(),
	returning a NULL.
	'''

	print 'Entering root_export'
	print 'Extracting data from file: %s' %root_file
	print 'Extracting data from TTree: %s' %tree
	print 'Extracting data from TLeaf: %s' %leaf
	f = ROOT.TFile(root_file)
	t = f.Get(tree)
	l = t.GetLeaf(leaf)
	size = t.GetEntriesFast()
	entries = []
	for n in range(size):
		t.Scan(leaf,'','',1,n)
		val = l.GetValue(0)
		entries.append(val)
	return entries

def file_concatenater():
	'''
	file_concatenater pulls in the seperate signal and background .dat files and
	combines them prior to analysis. The concatenated are output into the directory
	of the same name.
	'''

	print 'Entering file_concatenater'
	sig_dat = glob.iglob('data/root_export/sig_mx_*.dat')
	bkg_dat = glob.iglob('data/root_export/bkg_mx_*.dat')
	for signal, background in zip(sig_dat, bkg_dat):
		sig = np.loadtxt(signal)
		bkg = np.loadtxt(background)
		data_complete = np.concatenate((sig, bkg), axis=0)
		np.savetxt('data/concatenated/ttbar_mx_%0.3f.dat' %sig[0,2], data_complete, fmt='%f')


'''
Fixed Training and Plots
'''

def fixed_training():
	'''
	fixed_training takes concatenated data and splits the data set into training_data
	(i.e. [mwwbb_value, mjj_value, jes], e.g. [[532.1, 84.3, 0.750], [728.4, 121.3, 0.750]]) and target_data (i.e. [1, 1, ... 0, 0]).
	The input undergoes pre-processing via SKLearns pipeline and then a NN is trained using the
	SKLearnNN wrapper which processes the data using Theano/PyLearn2. NN learning parameters
	(e.g. learning_rate, n_iter, etc) are selected before hand. target_data from the inputs
	are then used along with predictions to calculate the Receiver Operating Characteristic (ROC) curve
	and Area Under the Curve (AUC).
	'''

	print 'Entering fixed_training'

	nn = Pipeline([('min/max scaler', MinMaxScaler(feature_range=(0.0, 1.0))),
					('neural network',
						Regressor(
							layers =[Layer("Sigmoid", units=3),Layer("Sigmoid")],
							learning_rate=0.1,
							n_iter=25,
							#n_stable=1,
							#f_stable=0.001,
							#learning_momentum=0.1,
							batch_size=1,
							#learning_rule="nesterov",
							#valid_size=0.05,
							verbose=True,
							#debug=True
							))])

	jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]

	for idx, jes in enumerate(jes_list):
		input_data = np.loadtxt('data/concatenated/ttbar_mx_%0.3f.dat' %jes)
		data1 = np.loadtxt('data/concatenated/ttbar_mx_1.000.dat')
		training_data = input_data[:,0:2]
		jes_data = input_data[:,2]
		target_data = input_data[:,3]
		target_data1 = data1[:,3]
		jes = jes_data[0]

		print 'Processing fixed training on mu=%0.3f' %jes
		nn.fit(training_data, target_data)

		fit_score = nn.score(training_data, target_data)
		print 'score = %s' %fit_score

		outputs = nn.predict(training_data)
		outputs = outputs.reshape((1,len(outputs)))

		output_data = np.vstack((training_data[:,0],
								training_data[:,1],
								jes_data,
								target_data,
								outputs)).T
		np.savetxt('data/plot_data/fixed_%0.3f.dat' %jes, output_data, fmt='%f')

		actual = target_data1
		predictions = outputs[0]
		fpr, tpr, thresholds = roc_curve(actual, predictions)
		ROC_plot = np.vstack((fpr, tpr)).T
		ROC_AUC = [auc(fpr, tpr)]
		np.savetxt('data/plot_data/ROC/fixed_ROC_%0.3f.dat' %jes, ROC_plot, fmt='%f')
		np.savetxt('data/plot_data/AUC/fixed_ROC_AUC_%0.3f.dat' %jes, ROC_AUC)
		pickle.dump(nn, open('data/pickle/fixed_%0.3f.pkl' %jes, 'wb'))

def fixed_training_plot():
	'''
	fixed_training_plot is no longer necessary and has been replaced by
	parameterized_vs_fixed_output_plot. Initially this took prediction data
	from fixed_training and plotted the values. However, it is more convenient to pickle
	the NN training from fixed training and then run predictions separately rather than
	generate prediction outputs during training. This is left here because I'm a hoarder.
	'''

	print 'Entering fixed_training_plot'
	jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]
	for idx, jes in enumerate(jes_list):
		data = np.loadtxt('data/plot_data/fixed_%0.3f.dat' %jes)
		plt.plot(data[:,0], data[:,4],
					'.',
					color=colors[idx],
					#alpha=1,
					markevery = 100,
					#markersize = 1,
					label='jes$_f$=%0.3f' %jes,
					rasterized=True)
	plt.ylabel('NN output')
	plt.xlabel('$m_{WWbb}$')
	plt.xlim([0,3000])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/fixed_training_mwwbb_plot.pdf', dpi=400)
	plt.savefig('plots/images/fixed_training_mwwbb_plot.png')
	plt.clf()

	for idx, jes in enumerate(jes_list):
		data = np.loadtxt('data/plot_data/fixed_%0.3f.dat' %jes)
		plt.plot(data[:,1], data[:,4],
					'.',
					color=colors[idx],
					#alpha=1,
					markevery = 100,
					#markersize = 1,
					label='jes$_f$=%0.3f' %jes,
					rasterized=True)
	plt.ylabel('NN output')
	plt.xlabel('$m_{jj}$')
	plt.xlim([0,250])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/fixed_training_mjj_plot.pdf', dpi=400)
	plt.savefig('plots/images/fixed_training_mjj_plot.png')
	plt.clf()

def fixed_ROC_plot():
	'''
	fixed_ROC_plot takes in ROC and AUC values processed during training in fixed_training
	and plots the ROC curve. This will be deprecated in the future, for the same reason as
	fixed_training_plot, so that AUC and ROC values will be calculated and plotted separately
	from the training time.
	'''

	print "Entering fixed_ROC_plot"
	jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]
	#jes_list = [0.900, 1.000, 1.100]
	for idx, jes in enumerate(jes_list):
		data = np.loadtxt('data/plot_data/ROC/fixed_ROC_%0.3f.dat' %jes)
		AUC  = np.loadtxt('data/plot_data/AUC/fixed_ROC_AUC_%0.3f.dat' %jes)
		plt.plot(data[:,0], data[:,1],
					'-',
					color=colors[idx],
					label='jes$_{f_{1.000}}$=%0.3f (AUC=%0.3f)' %(jes, AUC),
					rasterized=True)
	plt.plot([0,1],[0,1], 'r--')
	plt.title('Receiver Operating Characteristic')
	plt.ylabel('1/Background efficiency')
	plt.xlabel('Signal efficiency')
	plt.xlim([0,1])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/fixed_ROC_plot.pdf', dpi=400)
	plt.savefig('plots/images/fixed_ROC_plot.png')
	plt.clf()



'''
Parameterized Training and Plots
'''

def parameterized_training():
	'''
	parameterized_training Trains a NN with multiple signals. In each case, one signal is
	excluded (e.g. mwwbb_complete750 trains for all signals excluding the one at jes=0.750).
	A seperate NN is trained for each of these scenarios and then pickled in an appropriately
	labeled file (e.g. Training excluding jes=0.750 is pickled as param_750.pkl)
	'''

	print 'Entering parameterized_training'

	mwwbb = np.concatenate((np.loadtxt('data/concatenated/ttbar_mx_0.750.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_0.900.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_0.950.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_0.975.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_1.000.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_1.025.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_1.050.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_1.100.dat'),
							np.loadtxt('data/concatenated/ttbar_mx_1.250.dat'),),
							axis=0)

	training_data = mwwbb[:,0:3]
	target_data = mwwbb[:,3]

	nn = Pipeline([('min/max scaler', MinMaxScaler(feature_range=(0.0, 1.0))),
					('neural network',
						Regressor(
								layers =[Layer("Sigmoid", units=3),Layer("Sigmoid")],
								learning_rate=0.01,
								n_iter=50,
								#n_stable=1,
								#f_stable=0.001,
								#learning_momentum=0.1,
								batch_size=10,
								learning_rule="nesterov",
								#valid_size=0.05,
								#verbose=True,
								#debug=True
								))])

	nn.fit(training_data, target_data)

	fit_score = nn.score(training_data, target_data)
	print 'score = %s' %fit_score

	#outputs = nn.predict(training_data)
	#outputs = outputs.reshape((1, len(outputs)))
	#param_plot = np.vstack((training_data[:,0], outputs)).T
	#np.savetxt('data/plot_data/param_%s.dat' %mx[idx], param_plot, fmt='%f')

	pickle.dump(nn, open('data/pickle/param_complete.pkl', 'wb'))

def parameterized_function(mwwbb, mjj, alpha, nn):
	'''
	parameterized_function acts as the function with an additional parameter alpha.
	This is used in parameterized_function_runner as the function which interpolates
	signals at alpha values. For example, a NN trained at mu=500, 750, 1250 and 1500
	can use the parameterized_function with a specificied value of alpha=1000 to
	interpolate the curve, ROC and AUC values at mu=1000 despite not having been trained
	for that location.
	'''

	training_data = np.array((mwwbb, mjj, alpha), ndmin=2)
	outputs   = nn.predict(training_data)
	return outputs[[0]]

def parameterized_function_runner():
	'''
	parameterized_function_runner takes the NN training from parameterized_training and
	calculates the outputs, and ROC/AUC from sample inputs. In each case of mu=500, 750,
	1000, 1250, 1500 the prediction of alpha is made using the NN which excluded that signal.
	For example, when a prediction is made with the parameter alpha=500, the prediction is made
	using the NN trained only at mu=750, 1000, 1250, 1500. Similarly, a prediction with the
	parameter alpha=750 is made with the NN trained at mu=500, 1000, 1250, 1500.
	'''

	print 'Entering parameterized_function_runner'
	alpha_list = [0.750,
					0.900,
					0.950,
					0.975,
					1.000,
					1.025,
					1.050,
					1.100,
					1.250]

	for idx, alpha in enumerate(alpha_list):
		data = np.loadtxt('data/concatenated/ttbar_mx_%0.3f.dat' %alpha)
		size = len(data[:,0])
		#print 'processing using: data/pickle/param_%0.3f.pkl on jes=%0.3f' %alpha
		#nn = pickle.load(open('data/pickle/param_%0.3f.pkl' %alpha, 'rb'))
		nn = pickle.load(open('data/pickle/param_complete.pkl', 'rb'))
		inputs = data[:,0:2]
		actuals = data[:,3]
		mwwbb = inputs[:,0]
		mjj = inputs[:,1]
		predictions = []
		for x in range(0,size):
			outputs = parameterized_function(mwwbb[x]/1., mjj[x]/1., alpha, nn)
			predictions.append(outputs[0][0])
			#print '(%s, %s, %s)' %(mwwbb[x], mjj[x], predictions[x])
		data = np.vstack((mwwbb, mjj, predictions, actuals)).T
		np.savetxt('data/plot_data/param_%0.3f.dat' %alpha, data, fmt='%f')
		fpr, tpr, thresholds = roc_curve(actuals, predictions)
		roc_auc = [auc(fpr, tpr)]

		roc_data = np.vstack((fpr, tpr)).T
		np.savetxt('data/plot_data/ROC/param_ROC_%0.3f.dat' %alpha, roc_data, fmt='%f')
		np.savetxt('data/plot_data/AUC/param_ROC_AUC_%0.3f.dat' %alpha, roc_auc)

def parameterized_training_plot():
	'''
	parameterized_training_plot plots the output values generated during
	parameterized_function_runner.
	'''

	print 'Entering parameterized_training_plot'

	#jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]
	jes_list = [0.900, 1.000, 1.100]
	for idx, jes in enumerate(jes_list):
		data = np.loadtxt('data/plot_data/param_%0.3f.dat' %jes)
		plt.plot(data[:,0], data[:,2],
					'o',
					color=colors[idx],
					alpha=0.3,
					markevery = 10000,
					#markersize = 1,
					label='jes$_p$=%0.3f' %jes,
					rasterized=True)
	plt.ylabel('NN output')
	plt.xlabel('$m_{WWbb}$')
	plt.xlim([0,3000])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/parameterized_training_mwwbb_plot.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_training_mwwbb_plot.png')
	plt.clf()

	for idx, jes in enumerate(jes_list):
		data = np.loadtxt('data/plot_data/param_%0.3f.dat' %jes)
		plt.plot(data[:,1], data[:,2],
					'o',
					color=colors[idx],
					linewidth = 1,
					alpha=0.3,
					markevery = 10000,
					#markersize = 1,
					label='jes$_p$=%0.3f' %jes,
					rasterized=True)
	plt.ylabel('NN output')
	plt.xlabel('$m_{jj}$')
	plt.xlim([0,250])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/parameterized_training_mjj_plot.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_training_mjj_plot.png')
	plt.clf()


def parameterized_ROC_plot():
	'''
	parameterized_ROC_plot plots the ROC and AUC values generated during
	parameterized_function_runner
	'''

	print 'Entering parameterized_ROC_plot'

	#jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]
	jes_list = [0.900, 1.000, 1.100]
	for idx, jes in enumerate(jes_list):
		ROC = np.loadtxt('data/plot_data/ROC/param_ROC_%0.3f.dat' %jes)
		AUC = np.loadtxt('data/plot_data/AUC/param_ROC_AUC_%0.3f.dat' %jes)
		plt.plot(ROC[:,0], ROC[:,1],
					'o',
					markerfacecolor=colors[idx],
					alpha=0.5,
					markevery=1000,
					label='jes$_p$=%0.3f (AUC=%0.3f)' %(jes, AUC),
					rasterized=True)
	plt.plot([0,1], [0,1], 'r--')
	plt.title('Receiver Operating Characteristic')
	plt.ylabel('1/Background efficiency')
	plt.xlabel('Signal efficiency')
	plt.xlim([0,1])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/parameterized_ROC_plot.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_ROC_plot.png')
	plt.clf()



'''
Comparison Training and Plots
'''

def parameterized_vs_fixed_output_plot():
	'''
	parameterized_vs_fixed_output_plot generates an array of points between 0-3000
	which are used to make predictions using the fixed and parameterized NN training
	in fixed_*.pkl and param_*.pkl
	'''

	print 'Entering parameterized_vs_fixed_output_plot'
	#jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]
	jes_list = [0.900, 1.000, 1.100]
	for idx, jes in enumerate(jes_list):
		print 'Plotting mass mwwbb, jes=%0.3f' %jes
		fixed = np.loadtxt('data/plot_data/fixed_%0.3f.dat' %jes)
		param = np.loadtxt('data/plot_data/param_%0.3f.dat' %jes)
		plt.plot(fixed[:,0], fixed[:,4],
					'.',
					color=colors[idx],
					markevery=1000,
					label='jes$_f$=%0.3f' %jes,
					rasterized=True
					)
		plt.plot(param[:,0], param[:,2],
					'o',
					color=colors[idx],
					markevery=2000,
					alpha=0.3,
					label='jes$_p$=%0.3f' %jes,
					rasterized=True
					)
	plt.legend(loc='lower right', fontsize=10)
	plt.grid(True)
	plt.xlim([0,3000])
	plt.ylim([0,1])
	plt.xlabel('$m_{WWbb}$')
	plt.ylabel('NN output')
	plt.savefig('plots/parameterized_vs_fixed_output_plot_mwwbb.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_vs_fixed_output_plot_mwwbb.png')
	plt.clf()

	for idx, jes in enumerate(jes_list):
		print 'Plotting mass mjj, jes=%0.3f' %jes
		fixed = np.loadtxt('data/plot_data/fixed_%0.3f.dat' %jes)
		param = np.loadtxt('data/plot_data/param_%0.3f.dat' %jes)
		plt.plot(fixed[:,1], fixed[:,4],
						'.',
						color=colors[idx],
						markevery=1000,
						label='jes$_f$=%0.3f' %jes,
						rasterized=True
						)
		plt.plot(param[:,1], param[:,2],
						'o',
						color=colors[idx],
						markevery=2000,
						alpha=0.3,
						label='jes$_p$=%0.3f' %jes,
						rasterized=True
						)
	plt.legend(loc='lower right', fontsize=10)
	plt.grid(True)
	plt.xlim([0,250])
	plt.ylim([0,1])
	plt.xlabel('$m_{jj}$')
	plt.ylabel('NN output')
	plt.savefig('plots/parameterized_vs_fixed_output_plot_mjj.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_vs_fixed_output_plot_mjj.png')
	plt.clf()

def parameterized_vs_fixed_ROC_plot():
	'''
	parameterized_vs_fixed_ROC_plot pulls the ROC/AUC data for both fixed
	and parameterized training to plot both on the same canvas.
	'''
	#jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]
	jes_list = [0.900, 1.000, 1.100]

	for idx, jes in enumerate(jes_list):
		print 'Plotting ROC for jes=%0.3f' %jes
		fixed_ROC = np.loadtxt('data/plot_data/ROC/fixed_ROC_%0.3f.dat' %jes)
		fixed_AUC = np.loadtxt('data/plot_data/AUC/fixed_ROC_AUC_%0.3f.dat' %jes)
		param_ROC = np.loadtxt('data/plot_data/ROC/param_ROC_%0.3f.dat' %jes)
		param_AUC = np.loadtxt('data/plot_data/AUC/param_ROC_AUC_%0.3f.dat' %jes)
		plt.plot(fixed_ROC[:,0], fixed_ROC[:,1],
					'.',
					color=colors[idx],
					markevery=1000,
					label='jes$_f$=%0.3f (AUC=%0.3f)' %(jes, fixed_AUC),
					rasterized=True
					)
		plt.plot(param_ROC[:,0], param_ROC[:,1],
					'o',
					color=colors[idx],
					markevery=10000,
					alpha=0.3,
					label='jes$_p$=%0.3f (AUC=%0.3f)' %(jes, param_AUC),
					rasterized=True
					)
	plt.legend(loc='lower right', fontsize=10)
	plt.grid(True)
	plt.plot([0,1],[0,1], 'r--')
	plt.title('Receiver Operating Characteristic')
	plt.ylabel('1/Background efficiency')
	plt.xlabel('Signal efficiency')
	plt.xlim([0,1])
	plt.ylim([0,1])
	plt.savefig('plots/parameterized_vs_fixed_ROC_plot.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_vs_fixed_ROC_plot.png')
	plt.clf()


def fixed_output_plot_heat_map():
	print 'Entering fixed_output_plot_heat_map'
	jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]

	for idx, jes in enumerate(jes_list):
		print 'Plotting jes=%0.3f' %jes
		data = np.loadtxt('data/plot_data/fixed_%0.3f.dat' %jes)
		size = 5000
		x = np.concatenate((data[:,0][:size], data[:,0][-size:]), axis=0)
		y = np.concatenate((data[:,1][:size], data[:,1][-size:]), axis=0)
		z = np.concatenate((data[:,4][:size], data[:,4][-size:]), axis=0)
		xmin = 0
		xmax = 3000
		ymin = 0
		ymax = 500
		zmin = 0
		zmax = 1
		#xmin = x.min()
		#xmax = x.max()
		#ymin = y.min()
		#ymax = y.max()
		#zmin = z.min()
		#zmax = z.max()

		# Set up a regular grid of interpolation points
		xi, yi = np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100)
		xi, yi = np.meshgrid(xi, yi)

		# Interpolate
		rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
		zi = rbf(xi, yi)
		plt.imshow(zi,
					vmin=zmin,
					vmax=zmax,
					origin='lower',
					extent=[xmin, xmax, ymin, ymax],
					aspect='auto',
					cmap=test_cm
					)
		plt.scatter(x, y, c=z,
					cmap=test_cm
					)
		plt.xlim([xmin, xmax])
		plt.ylim([ymin, ymax])
		plt.title('jes=%0.3f' %jes)
		plt.clim(0,1)
		plt.colorbar(label='NN output')
		plt.xlabel('$m_{WWbb}$')
		plt.ylabel('$m_{jj}$')
		plt.savefig('plots/output_heat_map/fixed/fixed_output_plot_heat_map_%0.3f.pdf' %jes, dpi=400)
		plt.savefig('plots/output_heat_map/images/fixed/fixed_output_plot_heat_map_%0.3f.png' %jes)
		plt.clf()

def parameterized_output_plot_heat_map():
	print 'Entering parameterized_output_plot_heat_map'
	jes_list = [0.750,
				0.900,
				0.950,
				0.975,
				1.000,
				1.025,
				1.050,
				1.100,
				1.250
				]

	for idx, jes in enumerate(jes_list):
		print 'Plotting jes=%0.3f' %jes
		data = np.loadtxt('data/plot_data/param_%0.3f.dat' %jes)
		size = 5000
		x = np.concatenate((data[:,0][:size], data[:,0][-size:]), axis=0)
		y = np.concatenate((data[:,1][:size], data[:,1][-size:]), axis=0)
		z = np.concatenate((data[:,2][:size], data[:,2][-size:]), axis=0)
		xmin = 0
		xmax = 3000
		ymin = 0
		ymax = 500
		zmin = 0
		zmax = 1
		color_map = 'CMRmap'
		#xmin = x.min()
		#xmax = x.max()
		#ymin = y.min()
		#ymax = y.max()
		#zmin = z.min()
		#zmax = z.max()

		# Set up a regular grid of interpolation points
		xi, yi = np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100)
		xi, yi = np.meshgrid(xi, yi)

		# Interpolate
		rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
		zi = rbf(xi, yi)
		plt.imshow(zi,
					vmin=zmin,
					vmax=zmax,
					origin='lower',
					extent=[xmin, xmax, ymin, ymax],
					aspect='auto',
					cmap=test_cm
					)
		plt.scatter(x, y, c=z,
					cmap=test_cm
					)
		plt.xlim([xmin, xmax])
		plt.ylim([ymin, ymax])
		plt.title('jes=%0.3f' %jes)
		plt.clim(0,1)
		plt.colorbar(label='NN output')
		plt.xlabel('$m_{WWbb}$')
		plt.ylabel('$m_{jj}$')
		plt.savefig('plots/output_heat_map/parameterized/parameterized_output_plot_heat_map_%0.3f.pdf' %jes, dpi=400)
		plt.savefig('plots/output_heat_map/images/parameterized/parameterized_output_plot_heat_map_%0.3f.png' %jes)
		plt.clf()


'''
Histograms
'''


def plot_histogram():
	'''
	plot_histogram plots a histogram of the signal and backgrounds pulled from
	the root files in the root_export directory
	'''

	print 'Entering plot_histogram'
	bin_size   = 50
	sig_dat = glob.iglob('data/root_export/sig_*.dat')
	bkg_dat = glob.iglob('data/root_export/bkg_*.dat')

	for idx, (signal, background) in enumerate(zip(sig_dat, bkg_dat)):
		sig = np.loadtxt(signal)
		bkg = np.loadtxt(background)
		print 'Plotting mWWbb at jes=%0.3f' %sig[0,2]
		n, bins, patches = plt.hist([sig[:,0], bkg[:,0]],
									bins=range(0,3000, bin_size), normed=True,
									histtype='step', alpha=0.75, linewidth=2,
									label=['Signal', 'Background'],
									rasterized=True)
		plt.setp(patches)
		plt.ylabel('Fraction of events$/%0.0f$ GeV' %bin_size)
		plt.xlabel('m$_{WWbb}$ [GeV]')
		plt.grid(True)
		plt.legend(loc='upper right', fontsize=10)
		plt.xlim([0, 3000])
		#plt.ylim([0, 35000])
		plt.title('jes=%0.3f' %sig[0,2])
		plt.savefig('plots/histograms/mWWbb_histogram_%0.3f.pdf' %sig[0,2], dpi=400)
		plt.savefig('plots/histograms/images/mWWbb_histogram_%0.3f.png' %sig[0,2])
		plt.clf()
	sig_dat = glob.iglob('data/root_export/sig_*.dat')
	bkg_dat = glob.iglob('data/root_export/bkg_*.dat')
	bin_size   = 15
	for idx, (signal, background) in enumerate(zip(sig_dat, bkg_dat)):
		sig = np.loadtxt(signal)
		bkg = np.loadtxt(background)
		print 'Plotting mjj at jes=%0.3f' %sig[0,2]
		n, bins, patches = plt.hist([sig[:,1], bkg[:,1]],
									bins=range(0,500, bin_size), normed=True,
									histtype='step', alpha=0.75, linewidth=2,
									label=['Signal', 'Background'],
									rasterized=True)
		plt.setp(patches)
		plt.ylabel('Fraction of events$/%0.0f$ GeV' %bin_size)
		plt.xlabel('m$_{jj}$ [GeV]')
		plt.grid(True)
		plt.title('jes=%0.3f' %sig[0,2])
		plt.legend(loc='upper right', fontsize=10)
		plt.xlim([0, 500])
		#plt.ylim([0, 35000])
		plt.savefig('plots/histograms/mjj_histogram_%0.3f.pdf' %sig[0,2], dpi=400)
		plt.savefig('plots/histograms/images/mjj_histogram_%0.3f.png' %sig[0,2])
		plt.clf()

def grid_heat_map(scatter_plot):
	print 'Entering fixed_output_plot_heat_map'

	jes_list = [0.750,
				0.900,
				0.950,
				0.975,
				1.000,
				1.025,
				1.050,
				1.100,
				1.250
				]
	grid_size = 60
	print 'Predictions on a %s x %s grid' %(grid_size, grid_size)
	for idx, jes in enumerate(jes_list):
		print 'Plotting jes=%0.3f' %jes
		grid = np.zeros((grid_size*grid_size,2))
		for x in range(grid_size):
			for y in range(grid_size):
				grid[y+(x*grid_size),0] = x*(3000/grid_size)
				grid[y+(x*grid_size),1] = y*(3000/grid_size)
		nn = pickle.load(open('data/pickle/fixed_%0.3f.pkl' %jes, 'rb'))
		output = nn.predict(grid)


		x = grid[:,0]
		y = grid[:,1]
		z = output
		fixed_output = output
		xmin = x.min()
		xmax = x.max()
		ymin = y.min()
		ymax = y.max()
		zmin = z.min()
		zmax = z.max()

		# Set up a regular grid of interpolation points
		xi, yi = np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100)
		xi, yi = np.meshgrid(xi, yi)

		# Interpolate
		rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
		zi = rbf(xi, yi)
		plt.imshow(zi,
					vmin=zmin,
					vmax=zmax,
					origin='lower',
					extent=[xmin, xmax, ymin, ymax],
					aspect='auto',
					cmap=test_cm
					)
		if scatter_plot=='yes':
			plt.scatter(x, y, c=z, cmap=test_cm)
		plt.xlim([xmin, xmax])
		plt.ylim([ymin, ymax])
		plt.title('jes=%0.3f' %jes)
		plt.clim(0,1)
		plt.colorbar(label='NN output')
		plt.xlabel('$m_{WWbb}$')
		plt.ylabel('$m_{jj}$')
		plt.savefig('plots/output_heat_map/grid_map/fixed_grid_heat_map_%0.3f.pdf' %jes, dpi=400)
		plt.savefig('plots/output_heat_map/images/fixed_grid/fixed_grid_heat_map_%0.3f.png' %jes)
		plt.clf()

		grid = np.zeros((grid_size*grid_size,3))
		for x in range(grid_size):
			for y in range(grid_size):
				grid[y+(x*grid_size),0] = x*(3000/grid_size)
				grid[y+(x*grid_size),1] = y*(3000/grid_size)
				grid[y+(x*grid_size),2] = jes
		nn = pickle.load(open('data/pickle/param_%0.3f.pkl' %jes, 'rb'))
		output = nn.predict(grid)

		x = grid[:,0]
		y = grid[:,1]
		z = output
		param_output = output
		fixed_param_dif = fixed_output - param_output
		xmin = x.min()
		xmax = x.max()
		ymin = y.min()
		ymax = y.max()
		zmin = z.min()
		zmax = z.max()

		# Set up a regular grid of interpolation points
		xi, yi = np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100)
		xi, yi = np.meshgrid(xi, yi)

		# Interpolate
		rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
		zi = rbf(xi, yi)
		plt.imshow(zi,
					vmin=zmin,
					vmax=zmax,
					origin='lower',
					extent=[xmin, xmax, ymin, ymax],
					aspect='auto',
					cmap=test_cm
					)
		if scatter_plot=='yes':
			plt.scatter(x, y, c=z, cmap=test_cm)
		plt.xlim([xmin, xmax])
		plt.ylim([ymin, ymax])
		plt.title('jes=%0.3f' %jes)
		plt.clim(0,1)
		plt.colorbar(label='NN output')
		plt.xlabel('$m_{WWbb}$')
		plt.ylabel('$m_{jj}$')
		plt.savefig('plots/output_heat_map/grid_map/parameterized_grid_heat_map_%0.3f.pdf' %jes, dpi=400)
		plt.savefig('plots/output_heat_map/images/parameterized_grid/parameterized_grid_heat_map_%0.3f.png' %jes)
		plt.clf()

		dif_matrix = np.column_stack((x, y, fixed_param_dif))
		color_map = 'seismic'
		x = dif_matrix[:,0]
		y = dif_matrix[:,1]
		z = dif_matrix[:,2]
		xmin = x.min()
		xmax = x.max()
		ymin = y.min()
		ymax = y.max()
		zmin = -1
		zmax = 1

		# Set up a regular grid of interpolation points
		xi, yi = np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100)
		xi, yi = np.meshgrid(xi, yi)

		# Interpolate
		rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
		zi = rbf(xi, yi)
		plt.imshow(zi,
					vmin=zmin,
					vmax=zmax,
					origin='lower',
					extent=[xmin, xmax, ymin, ymax],
					aspect='auto',
					cmap=test_cm_bin
					)
		if scatter_plot=='yes':
			plt.scatter(x, y, c=z, cmap=test_cm_bin)
		plt.xlim([xmin, xmax])
		plt.ylim([ymin, ymax])
		plt.clim(zmin,zmax)
		plt.title('jes=%0.3f' %jes)
		plt.colorbar(label='NN output difference (fixed - parameterized)')
		plt.xlabel('$m_{WWbb}$')
		plt.ylabel('$m_{jj}$')
		plt.savefig('plots/output_heat_map/dif_matrix/dif_matrix_%0.3f.pdf' %jes, dpi=400)
		plt.savefig('plots/output_heat_map/images/dif_matrix/dif_matrix_%0.3f.png' %jes)
		plt.clf()

def fixed_analysis_data_alt():
	print 'Entering fixed_analysis_data'
	files = glob.iglob('data/plot_data/fixed_*.dat')
	for idx, file in enumerate(files):
		print 'Outputing data for file: %s' %file
		fixed_data = np.loadtxt(file)
		fixed_output = np.vstack((fixed_data[:,3], #Label (i.e. 0 or 1)
									fixed_data[:,0], #mWWbb
									fixed_data[:,1], #mjj
									fixed_data[:,4], #NN_output
									fixed_data[:,2], #JES_gen
									fixed_data[:,2]  #JES_eval
									)).T
		np.savetxt('data/analysis_data/fixed_%0.3f.csv' %fixed_data[0,2], fixed_output, fmt='%f', delimiter=',')

def fixed_analysis_data():
	alpha_list = [0.750,
					0.900,
					0.950,
					0.975,
					1.000,
					1.025,
					1.050,
					1.100,
					1.250]

	for idx, alpha in enumerate(alpha_list):
		print 'processing alpha=%0.3f' %alpha
		data = np.loadtxt('data/concatenated/ttbar_mx_%0.3f.dat' %alpha)
		nn = pickle.load(open('data/pickle/fixed_1.000.pkl', 'rb'))
		inputs = data[:,0:2]
		actuals = data[:,3]
		mwwbb = inputs[:,0]
		mjj = inputs[:,1]
		outputs = nn.predict(inputs)
		predictions = outputs.reshape((1, len(mjj)))
		JES_gen = np.zeros([1, len(mjj)])
		JES_eval = np.zeros([1, len(mjj)])
		JES_gen.fill(alpha)
		JES_eval.fill(1.000000)
		data = np.vstack((actuals, mwwbb, mjj, predictions, JES_gen, JES_eval)).T
		np.savetxt('data/analysis_data/fixed_%0.3f.dat' %alpha, data, fmt='%f')

	output_data = np.concatenate((np.loadtxt('data/analysis_data/fixed_0.750.dat'),
									np.loadtxt('data/analysis_data/fixed_0.900.dat'),
									np.loadtxt('data/analysis_data/fixed_0.950.dat'),
									np.loadtxt('data/analysis_data/fixed_0.975.dat'),
									np.loadtxt('data/analysis_data/fixed_1.000.dat'),
									np.loadtxt('data/analysis_data/fixed_1.025.dat'),
									np.loadtxt('data/analysis_data/fixed_1.050.dat'),
									np.loadtxt('data/analysis_data/fixed_1.100.dat'),
									np.loadtxt('data/analysis_data/fixed_1.250.dat')),
									axis=0)
	np.savetxt('data/analysis_data/fixed.csv', output_data, fmt='%f', delimiter=',')

	files = glob.glob('data/analysis_data/fixed_*.dat')
	for idx, file in enumerate(files):
		os.remove(file)
	for idx, alpha in enumerate(alpha_list):
		print 'processing alpha=%0.3f' %alpha
		data = np.loadtxt('data/concatenated/ttbar_mx_%0.3f.dat' %alpha)
		nn = pickle.load(open('data/pickle/fixed_1.000.pkl', 'rb'))
		inputs = data[:,0:2]
		actuals = data[:,3]
		outputs = nn.predict(inputs)
		predictions = outputs[:,0]
		fpr, tpr, thresholds = roc_curve(actuals, predictions)
		roc_auc = [auc(fpr, tpr)]

		roc_data = np.vstack((fpr, tpr)).T
		np.savetxt('data/analysis_data/ROC/fixed_ROC_%0.3f.dat' %alpha, roc_data, fmt='%f')
		np.savetxt('data/analysis_data/AUC/fixed_ROC_AUC_%0.3f.dat' %alpha, roc_auc)

def parameterized_analysis_data():
	alpha_list = [0.750,
					0.900,
					0.950,
					0.975,
					1.000,
					1.025,
					1.050,
					1.100,
					1.250]

	jes_val_list = []
	label = []
	mWWbb = []
	mJJ = []
	NN_output = []
	JES_gen = []
	JES_eval = []
	for i in range(50, 170, 20):
		jes_val_list.append(i/100.)
	print jes_val_list
	for idx, alpha in enumerate(alpha_list):
		print 'processing alpha=%0.3f' %alpha
		data = np.loadtxt('data/concatenated/ttbar_mx_%0.3f.dat' %alpha)
		size = len(data[:,0])
		nn = pickle.load(open('data/pickle/param_complete.pkl', 'rb'))
		inputs = data[:,0:2]
		actuals = data[:,3]
		mwwbb = inputs[:,0]
		mjj = inputs[:,1]
		for x in range(0,size):
			for y in range(len(jes_val_list)):
				outputs = parameterized_function(mwwbb[x]/1., mjj[x]/1., jes_val_list[y], nn)
				label.append(actuals[x]/1.)
				mWWbb.append(mwwbb[x]/1.)
				mJJ.append(mjj[x]/1.)
				NN_output.append(outputs[0][0])
				JES_gen.append(alpha)
				JES_eval.append(jes_val_list[y])

	data = np.vstack((label, mWWbb, mJJ, NN_output, JES_gen, JES_eval)).T
	np.savetxt('data/analysis_data/parameterized.csv', data, fmt='%f', delimiter=',')

	'''
	for idx, alpha in enumerate(alpha_list):
		print 'processing alpha=%0.3f' %alpha
		data = np.loadtxt('data/concatenated/ttbar_mx_%0.3f.dat' %alpha)
		size = len(data[:,0])
		nn = pickle.load(open('data/pickle/param_complete.pkl', 'rb'))
		inputs = data[:,0:2]
		actuals = data[:,3]
		mwwbb = inputs[:,0]
		mjj = inputs[:,1]
		predictions = []
		label =[]
		for x in range(0,size):
			outputs = parameterized_function(mwwbb[x]/1., mjj[x]/1., alpha, nn)
			predictions.append(outputs[0][0])
		fpr, tpr, thresholds = roc_curve(actuals, predictions)
		roc_auc = [auc(fpr, tpr)]

		roc_data = np.vstack((fpr, tpr)).T
		np.savetxt('data/analysis_data/ROC/param_ROC_%0.3f.dat' %alpha, roc_data, fmt='%f')
		np.savetxt('data/analysis_data/AUC/param_ROC_AUC_%0.3f.dat' %alpha, roc_auc)
	'''

def fixed_analysis_ROC_plot():
	print 'Entering parameterized_analysis_ROC_plot'

	jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]

	for idx, jes in enumerate(jes_list):
		print 'Plotting jes=%0.3f' %jes
		ROC = np.loadtxt('data/analysis_data/ROC/fixed_ROC_%0.3f.dat' %jes)
		AUC = np.loadtxt('data/plot_data/AUC/fixed_ROC_AUC_%0.3f.dat' %jes)
		plt.plot(ROC[:,0], ROC[:,1],
					'.',
					markerfacecolor=colors[idx],
					alpha=0.5,
					markevery=1000,
					label='jes$_p$=%0.3f (AUC=%0.3f)' %(jes, AUC),
					rasterized=True)
	plt.plot([0,1], [0,1], 'r--')
	plt.title('Receiver Operating Characteristic')
	plt.ylabel('1/Background efficiency')
	plt.xlabel('Signal efficiency')
	plt.xlim([0,1])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/fixed_analysis_ROC_plot.pdf', dpi=400)
	plt.savefig('plots/images/fixed_analysis_ROC_plot.png')
	plt.clf()

def parameterized_analysis_ROC_plot():
	print 'Entering parameterized_analysis_ROC_plot'

	jes_list = [0.750, 0.900, 0.950, 0.975, 1.000, 1.025, 1.050, 1.100, 1.250]

	for idx, jes in enumerate(jes_list):
		print 'Plotting jes=%0.3f' %jes
		ROC = np.loadtxt('data/analysis_data/ROC/param_ROC_%0.3f.dat' %jes)
		AUC = np.loadtxt('data/plot_data/AUC/param_ROC_AUC_%0.3f.dat' %jes)
		plt.plot(ROC[:,0], ROC[:,1],
					'o',
					markerfacecolor=colors[idx],
					alpha=0.5,
					markevery=1000,
					label='jes$_p$=%0.3f (AUC=%0.3f)' %(jes, AUC),
					rasterized=True)
	plt.plot([0,1], [0,1], 'r--')
	plt.title('Receiver Operating Characteristic')
	plt.ylabel('1/Background efficiency')
	plt.xlabel('Signal efficiency')
	plt.xlim([0,1])
	plt.ylim([0,1])
	plt.legend(loc='lower right')
	plt.grid(True)
	plt.savefig('plots/parameterized_analysis_ROC_plot.pdf', dpi=400)
	plt.savefig('plots/images/parameterized_analysis_ROC_plot.png')
	plt.clf()

def CSV2ROOT(title):
	ntuple = ROOT.TNtuple(title, title, 'label:mwwbb:mjj:nn:jesTrue:jesParam')
	ntuple.ReadFile('data/analysis_data/%s.csv' %title)
	f = ROOT.TFile('data/analysis_data/%s.root' %title, "RECREATE")
	f.cd()
	ntuple.Write()
	f.Close()



if __name__ == '__main__':
	'''
	File Runners
	'''
	#file_runner()
	#flat_bkg(10000,0,5000)
	#file_concatenater()

	'''
	Fixed Training and Plots
	'''
	#fixed_training()
	#fixed_training_plot()
	#fixed_ROC_plot()
	#fixed_output_plot_heat_map()

	'''
	Parameterized Training and Plots
	'''
	#parameterized_training()
	#parameterized_function_runner()
	#parameterized_training_plot()
	#parameterized_ROC_plot()
	parameterized_output_plot_heat_map()

	'''
	Comparison Training and Plots
	'''
	#parameterized_vs_fixed_output_plot()
	#parameterized_vs_fixed_ROC_plot()
	#grid_heat_map('no')

	'''
	Output Histograms
	'''
	#plot_histogram()

	'''
	Outputing data
	'''
	#fixed_analysis_data()
	#fixed_analysis_ROC_plot()
	#parameterized_analysis_data()
	#parameterized_analysis_ROC_plot()
	#CSV2ROOT('fixed')
	#CSV2ROOT('parameterized')
