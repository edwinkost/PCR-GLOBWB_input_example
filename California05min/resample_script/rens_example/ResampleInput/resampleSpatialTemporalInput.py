################################################################################
#
#!/usr/bin/env python
#
# module:				resampleSpatialTemporalInput.py
#
# purpose:			processes files and resamples maps
#
################################################################################
  
  
import os, sys
import ConfigParser
import pcraster as pcr
from spatialDataSet2PCR import *

def getSelectedFilesFromCofigFile(cfgFileName, selectedFileExtensions= ['.nc','.map']):
	#-reads a config file and returns a list of files meeting the extensions specified
	#-initialize list of selected files
	selectedFileNames= []
	#-process config file
	config = ConfigParser.ConfigParser()
	config.optionxform = str
	config.read(cfgFileName)
	#-get default path
	defaultPath= ''
	try:
		for key, value in config.items('globalOptions'):
			if key == 'inputDir':
				defaultPath= value
	except:
		pass
	#-get info from sections
	for section in config.sections():
		for key, value in config.items(section):
			if os.path.splitext(value)[1] in selectedFileExtensions:
				fileName= value
				if not os.path.isabs(fileName):
					fileName= os.path.join(defaultPath,value)
				if os.path.isfile(fileName):
					selectedFileNames.append(fileName)
				else:
					print '- not found!: %s' % fileName
	#-return list
	return selectedFileNames, defaultPath

def getCDOLatLonProjectionFile(gdalAttributes, cdoTxtFileName,rowOrderIncreasing= True):
	#-converts the spatial attributes of a geographic dataset of the gdalinfo
	# into a text file specifying the lat-lon grid description to resample netCDF
	# files using CDO. input:
	# gdalAttributes: spatialAttrbiutes class object holding gdal attributes
	# cdoTxtFileName: name of the text file holding the CDO latlon projection
	# rowOrderIncreasing: boolean variable, default True for PCRaster maps,
	#		that defines the sign of the yIncrement
	#-defining CDO projection
	if rowOrderIncreasing:
		conversion= -1.
	else:
		conversion= 1.
	#-dictionary with attributes
	cdoProjection= {}
	cdoProjection['gridtype']= 'lonlat'
	cdoProjection['gridsize']= '%d' % (gdalAttributes.numberRows*gdalAttributes.numberCols)
	cdoProjection['xname']= 'longitude'
	cdoProjection['xlongname']= 'longitude'
	cdoProjection['xunits']= 'degrees_east'
	cdoProjection['yname']= 'latitude'
	cdoProjection['ylongname']= 'latitude'
	cdoProjection['yunits']= 'degrees_north'
	cdoProjection['xsize']= '%d' %  gdalAttributes.numberCols
	cdoProjection['ysize']= '%d' % gdalAttributes.numberRows
	cdoProjection['xfirst']= '%f' % (gdalAttributes.xLL+0.5*gdalAttributes.xResolution)
	cdoProjection['xinc']= '%f' % gdalAttributes.xResolution
	cdoProjection['yfirst']= '%f' % (gdalAttributes.yUR+0.5*conversion*gdalAttributes.yResolution)
	cdoProjection['yinc']= '%f' %(conversion*gdalAttributes.yResolution)
	#-open file, write attributes and close
	cdoTxtFile= open(cdoTxtFileName,'w')
	for key, value in cdoProjection.iteritems():
		cdoTxtFile.write('%-32s= %s\n' % (key, value))
	cdoTxtFile.close()
	#-all
	return 0

def resampleFromList(selectedFileNames,inputPath,outputPath,\
		cloneMapFileName,cdoProjectionTxtFileName):
	#-iterates over the list and creates new output structure and files
	fCnt= 0
	if outputPath[-1] != '/': outputPath+= '/'
	for iFile in selectedFileNames:
		fileExt= os.path.splitext(iFile)[1]
		if iFile[:len(inputPath)] == inputPath:
			oFile= iFile.replace(inputPath,outputPath)
		else:
			oFile= os.path.join(outputPath,iFile)
		oPath= os.path.split(oFile)[0]
		if not os.path.exists(oPath):
			os.makedirs(oPath)
		print ' - %3d: processing %s' % (fCnt,os.path.split(iFile)[1]),
		#-netCDF:
		if fileExt == '.nc':
			command= 'cdo -remapnn,%s %s %s' %\
				(cdoProjectionTxtFileName,iFile,oFile)
			os.system(command)
			print 'netCDF converted'
		elif fileExt == '.map':
			command= 'resample --clone %s %s %s' %\
				(cloneMapFileName,iFile,oFile)
			os.system(command)
			print 'map converted'
		fCnt+= 1
	#-all processed
	return 0
	
def main():
	#-arguments
	#-initialization: clone map with the extent input has to be resampled to
	cloneMapFileName= '/home/beek0120/PCRGLOBWB/CloneNiger/clone_niger_05min_2.map'
	cdoProjectionTxtFileName= 'temp_cdoproj.txt'
	#-config file
	cfgFileName= 'setup_5min.ini'
	#-output path
	outputPath= '/scratch/rens/niger'
	
	#-start: set clone and get attributes
	pcr.setclone(cloneMapFileName)
	cloneAttributes= spatialAttributes(cloneMapFileName)
	#-obtain projection
	getCDOLatLonProjectionFile(cloneAttributes,cdoProjectionTxtFileName)
	#-get list of file names
	selectedFileNames, inputPath= getSelectedFilesFromCofigFile(cfgFileName)
	#-resample maps & nc
	resampleFromList(selectedFileNames,inputPath,outputPath,cloneMapFileName,cdoProjectionTxtFileName)

	#-initialization: clone map with the extent input has to be resampled to
	cloneMapFileName= '/home/beek0120/PCRGLOBWB/CloneNiger//clone_niger_30min.map'
	cdoProjectionTxtFileName= 'temp_cdoproj.txt'
	#-config file
	cfgFileName= 'setup_meteo.ini'
	#-output path
	outputPath= '/scratch/rens/niger'
	
	#-start: set clone and get attributes
	pcr.setclone(cloneMapFileName)
	cloneAttributes= spatialAttributes(cloneMapFileName)
	#-obtain projection
	getCDOLatLonProjectionFile(cloneAttributes,cdoProjectionTxtFileName)
	#-get list of file names
	selectedFileNames, inputPath= getSelectedFilesFromCofigFile(cfgFileName)
	#-resample maps & nc
	resampleFromList(selectedFileNames,inputPath,outputPath,cloneMapFileName,cdoProjectionTxtFileName)		

if __name__ == '__main__':
	main()

