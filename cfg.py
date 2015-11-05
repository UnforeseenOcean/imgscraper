__author__ = 'rcktscnc'

import configparser

config = configparser.ConfigParser()
config.read('params.cfg')
additionalParam = config['PARAMETERS']['AdditionalParam']
resultsPerItem = config['PARAMETERS']['ResultsPerItem']
imgSize = config['PARAMETERS']['ImageSize']

if int(resultsPerItem) < 1:
    resultsPerItem = '1'

if imgSize is '1':
    imgSize = 'icon'
if imgSize is '2':
    imgSize = 'small|medium|large|xlarge'
if imgSize is '3':
    imgSize = 'xxlarge'
if imgSize is '4':
    imgSize = 'huge'
if imgSize not in {'1', '2', '3', '4'}:
    imgSize = 'xxlarge'
