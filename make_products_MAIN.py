#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: tasos
"""
import os
from glob import glob
import numpy as np
from make_products_from_VIDEO_Files import sort_in_C_recordings,make_products_from_video_files, bgr2rgb
from make_products_from_VIDEO_Files import series_normalize,uint8_matlab_compatible,datetime2matlabdn
import cv2
from scipy.io import savemat
from datetime import datetime,timedelta
import time
import scipy.io as spio


# %% FUNCTIONS HERE 
class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name,)
        print('Elapsed time:'+str(timedelta(seconds=int((time.time() - self.tstart)))))



def process_my_videos_N_save_results(video_fnames_of_this_hour,day,hour,camIP,out_path,station_parameters):
    make_sigmac1 = True
    timex,immin,immax,snap,sigmaa,sigmac = make_products_from_video_files(video_fnames_of_this_hour,day,hour,station_parameters,make_sigmac=make_sigmac1)
    day = day.replace("-", "_")
    # save JPEGs
    for ii in ['timex','immin','immax','snap','sigma']:
        if ii != 'sigma':
            fname2save = out_path+camIP+'/'+'figures'+'/'+ii+'/'
            fname2save += ii+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.jpg'
            eval("cv2.imwrite(fname2save,"+ii+")")
        else:
            sigma2jpeg = series_normalize(sigmaa,vmin = 0, vmax = 255)
            sigma2jpeg =  uint8_matlab_compatible(sigma2jpeg)
            fname2save = out_path+camIP+'/'+'figures'+'/'+ii+'/'
            fname2save += ii+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.jpg'
            cv2.imwrite(fname2save,sigma2jpeg)
    # save MATs
    format_date = '%Y_%m_%d_%H_%M_%S'
    
    datetime_object = datetime.strptime(day+'_'+str(int(hour)).zfill(2)+'_00_00',format_date)
    sdate = datetime2matlabdn(datetime_object)

    mat_dict={'im':bgr2rgb(immin),'date':day,'time':str(int(hour)).zfill(2)+'_00_00','sdate':sdate}
    new_dict = {'immin':mat_dict}
    fname2saveMAT = out_path+camIP+'/'+'data'+'/'+'immin'+'/'
    fname2saveMAT += 'immin'+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.mat'
    savemat(fname2saveMAT,new_dict,do_compression=True)
    
    mat_dict={'im':bgr2rgb(immax),'date':day,'time':str(int(hour)).zfill(2)+'_00_00','sdate':sdate}
    new_dict = {'immax':mat_dict}
    fname2saveMAT = out_path+camIP+'/'+'data'+'/'+'immax'+'/'
    fname2saveMAT += 'immax'+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.mat'
    savemat(fname2saveMAT,new_dict,do_compression=True)
    
    mat_dict={'im':bgr2rgb(timex),'date':day,'time':str(int(hour)).zfill(2)+'_00_00','sdate':sdate}
    new_dict = {'timex':mat_dict}
    fname2saveMAT = out_path+camIP+'/'+'data'+'/'+'timex'+'/'
    fname2saveMAT += 'timex'+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.mat'
    savemat(fname2saveMAT,new_dict,do_compression=True)  
    
    mat_dict={'im':bgr2rgb(snap),'date':day,'time':str(int(hour)).zfill(2)+'_00_00','sdate':sdate}
    new_dict = {'snap':mat_dict}
    fname2saveMAT = out_path+camIP+'/'+'data'+'/'+'snap'+'/'
    fname2saveMAT += 'snap'+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.mat'
    savemat(fname2saveMAT,new_dict,do_compression=True)
    
    
    mat_dict={'im':sigmaa,'imcol':bgr2rgb(sigmac),'sdate':sdate, 'date':day,'time':str(int(hour)).zfill(2)+'_00_00'}
    new_dict = {'sigmaa':mat_dict}
    fname2saveMAT = out_path+camIP+'/'+'data'+'/'+'sigma'+'/'
    fname2saveMAT += 'sigma'+'_'+day+'_'+str(int(hour)).zfill(2)+'_00_00.mat'
    savemat(fname2saveMAT,new_dict,do_compression=True)

def get_station_parameters(main_options_fname):
    station_parameters = spio.loadmat(main_options_fname, simplify_cells=True)
    station_parameters  =station_parameters['mainopts']
    if station_parameters['cname'] == 'Peyia1':
        station_parameters['pcam'] = '5-CORAL_BAY_CAM' 
        # kapoios MALAKAS ton epaikse edw
    return(station_parameters)

def make_repository_processed_paths(cam_IPs,out_path):
    paths1 = ['data','figures']
    paths2 = ['immin','immax','sigma','snap','stack','timex']
    for ip in cam_IPs:
        for p1 in paths1:
            for p2 in paths2:
                path = out_path+ip+'/'+p1+'/'+p2
                isExist = os.path.exists(path)
                if not isExist:
                    os.makedirs(path)

def get_hours_of_videos(all_Videos_fnames):
    hours_of_videos = np.empty(len(all_Videos_fnames))
    hours_of_videos[:] = np.nan
    for ii in range(len(all_Videos_fnames)):
        tmp  = os.path.basename(os.path.normpath(all_Videos_fnames[ii]))
        tmp = tmp[:-4] #remove extenstion
        tmp = tmp.split('_')
        tmp=tmp[-1]
        tmp=tmp[0:2]
        hours_of_videos[ii] = int(tmp) 
    return(hours_of_videos)

  
def process_current_hour(recordings_path,constant_subpath_recordings,out_path,camIP,day,hour,station_parameters):
    all_Videos_fnames = sorted(glob(recordings_path+day+'/'+constant_subpath_recordings+'/'+"*.3gp"))
    hours_of_videos = get_hours_of_videos(all_Videos_fnames)
    
    video_list_needed_indexes = np.where(hours_of_videos==hour2process)[0]
    video_list_needed_indexes = video_list_needed_indexes.astype(int)
    video_fnames_of_this_hour=[all_Videos_fnames[x] for x in video_list_needed_indexes]
    video_fnames_of_this_hour = sort_in_C_recordings(video_fnames_of_this_hour)
    

    print("Day:"+day+ ' hour:'+str(hour2process)+' starting processing')
    process_my_videos_N_save_results(video_fnames_of_this_hour,day,hour,camIP,out_path,station_parameters)
# %% MAIN
if __name__ == "__main__":
    DEMO_mode = True
    
    # %% PARAMETERS HERE 
    main_options_fname = 'main_options_Peyia.mat'
    
    
    station_parameters = get_station_parameters(main_options_fname)
    cam_IPs = [ station_parameters['ips'] ] # it must me be a list, e.g. cam_IPs = ['10_10_10_111']
    # TO DO: fix above line to work using multiple cameras
    constant_subpath_recordings = station_parameters['pcam'] #e.g. constant_subpath_recordings = '5-CORAL_BAY_CAM'
    
    
    # C:\Recordinds Equivaent
    recordings_path ='/media/tasos/9CD49202D491DF38/Users/Tasos/Desktop/examples/C_Recording' 
    #D:\Repository processed equivalent path
    out_path = '/media/tasos/9CD49202D491DF38/Users/Tasos/Desktop/examples/d_repository_processed_tmpFS'
    TEMP_FS_PATH = '/mnt/tmp'
    
    if recordings_path[-1] != '/':
        recordings_path +='/'
    if out_path[-1] != '/':
        out_path +='/'
        
        
    make_repository_processed_paths(cam_IPs,out_path)    


    if DEMO_mode:
        day = '2022-12-11'
        hour2process = int(10)
    else: #run data of current hour
        hour2process = int(time.strftime("%H")) #current hour
        day  = time.strftime("%Y-%m-%d")  
    for camIP in cam_IPs:
        with Timer('only break frames'):
            process_current_hour(recordings_path,constant_subpath_recordings,out_path,camIP,day,hour2process,station_parameters)


