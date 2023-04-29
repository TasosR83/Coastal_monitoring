#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 09:47:01 2023

READ
https://vuamitom.github.io/2019/12/13/fast-iterate-through-video-frames.html
https://stackoverflow.com/questions/58595510/loop-through-all-the-frames-in-the-video-python

VERSION:
    This is the version that splits video files into JPEGs into a temp-FS
@author: tasos
"""
import cv2
import numpy as np
import os
import subprocess
import shutil
from glob import glob
from datetime import datetime, timedelta
from scipy.io import savemat
from sys import exit
from numpy.core.records import fromarrays
# %%  FUNCTIONS HERE
def datetime2matlabdn(dt):
   mdn = dt + timedelta(days = 366)
   frac_seconds = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
   frac_microseconds = dt.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
   return mdn.toordinal() + frac_seconds + frac_microseconds

def bgr2gray(bgr):
    bgr = np.double(bgr)
    #return np.dot(bgr[...,:3], [0.2989, 0.5870, 0.1140])
    double_gray =  np.dot(bgr[...,:3], [0.1140, 0.5870, 0.2989])
    return(double_gray)
    #return uint8_matlab_compatible(double_gray)


def series_normalize_OLD(ser,vmin = 0, vmax = 1):
    # ORIGINAL by MV
    m1=np.nanmin(ser);
    m2=np.nanmax(ser-m1);
    
    nser=(ser-m1)/m2;

    nser2=vmin+nser*(vmax-vmin);
    
    nser2[nser2<vmin]=vmin;
    nser2[nser2>vmax]=vmax;
    return(nser2)

def series_normalize(x,vmin = 0, vmax = 1):
    # Rescaling (min-max normalization)
    tmp = (vmax-vmin)/(np.nanmax(x)-np.nanmin(x))
    X_new  = vmin+(x-np.nanmin(x))*tmp
    return(X_new)

def series_normalize_per_channel(x,vmin = 0, vmax = 1):
    tmp1 = np.shape(x)
    Nchanels = tmp1[2]
    output = np.zeros(tmp1)
    for ch in range(Nchanels):
        output[:,:,ch] = series_normalize(x[:,:,ch],vmin,vmax)
    return(output)

def bgr2rgb(bgr_img):
    rgb=np.zeros_like(bgr_img)
    rgb = rgb.astype(np.uint8)
    rgb[:,:,0] = bgr_img[:,:,2]
    rgb[:,:,1] = bgr_img[:,:,1]
    rgb[:,:,2] = bgr_img[:,:,0]
    return(rgb)

def uint8_matlab_compatible(data):
    out = np.uint8(np.clip(data+0.5,0,255))
    return(out)

def sort_in_C_recordings(filenames_list):
    
    # input as
    # 1_2023-01-15_070051.3gp
    # ...
    # 10_2023-01-15_080418.3gp
    # will by sorted according to the first number!!!
    # filenames_list = ['/media/tasos/9CD49202D491DF38/Users/Tasos/Desktop/examples/demo1dayVideos/2023-01-15/5-CORAL_BAY_CAM/10_2023-01-15_100728.3gp','/media/tasos/9CD49202D491DF38/Users/Tasos/Desktop/examples/demo1dayVideos/2023-01-15/5-CORAL_BAY_CAM/1_2023-01-15_100728.3gp','/media/tasos/9CD49202D491DF38/Users/Tasos/Desktop/examples/demo1dayVideos/2023-01-15/5-CORAL_BAY_CAM/2_2023-01-15_100728.3gp']
    index_by_first_number = np.zeros(len(filenames_list))
    for (ii,fullfname) in enumerate(filenames_list):
        basename = os.path.basename(fullfname)
        number = basename.split('_')[0]
        index_by_first_number[ii]=int(number)
    merged = dict(zip(index_by_first_number, filenames_list))
    tmp = sorted(merged.items())
    output = [];
    for ii in range(len(tmp)):
        output.append(tmp[ii][1])
    return(output)


def make_frames_from_videos(video_fnames_of_this_hour,day,hour,station_parameters,path_out = '/mnt/tmp',FnameContainsLeadingNumbering=True):
    # FnameContainsLeadingNumbering if TRUE means we have video filenames such as: 38_2022-12-12_120528.3gp
    my_dir = os.getcwdb()
    # make dir such as /mnt/tmp/192_168_1_201/2022_11_12/S_08
    path_out = path_out+'/'+station_parameters['ips']+'/'+day+'/'+'S_'+str(hour).zfill(2)+'/'
    if os.path.exists(path_out):
        print('the directory:')
        print(path_out)
        print('shouldnt exist!!!')
        print ('OVERWRITING FRAMES NOW !!!')
    else:
        os.makedirs(path_out)
    
    for videoFullFname in video_fnames_of_this_hour:
        if FnameContainsLeadingNumbering:
            video_basename = os.path.basename(videoFullFname)
            tmp1 = video_basename.split('_')[1:]
            basename_no_leading_number = '_'.join(tmp1)
            destination = path_out+'/'+basename_no_leading_number
            shutil.copyfile(videoFullFname, destination)
            video_basename_new = basename_no_leading_number
        else:
            video_basename = os.path.basename(videoFullFname)
            destination = path_out+'/'+video_basename
            shutil.copyfile(videoFullFname, destination)
            video_basename_new = video_basename
        video_basename_new_no_extens = os.path.splitext(video_basename_new)[0] # '2022-12-12_120528' instead of '2022-12-12_120528.3gp'
        os.chdir(path_out)
        command = 'ffmpeg -i '+video_basename_new+' ' +video_basename_new_no_extens+'_%05d.jpg '
        print('Splitting a video into frames')
        #subprocess.run(command, shell=True)
        # https://stackoverflow.com/questions/11269575/how-to-hide-output-of-subprocess
        subprocess.run(command, shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        
        # LETS RENAME JPEGs to contain "exact" (paparia, read better) timestamp including milisecond
        video = cv2.VideoCapture(video_basename_new)
        #  OpenCV >= 3 ONLY
        fps = video.get(cv2.CAP_PROP_FPS)
        totalNFrames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(fps)# floor NOT ROUND
        del video
        
        # LETS RENAME the frames as the orasis format
        video_starting_time_datetime_object = datetime.strptime(video_basename_new_no_extens, '%Y-%m-%d_%H%M%S')
        os.remove(video_basename_new) #remove file file from the tmpFS
        jpg_fnames_of_this_video = sorted(glob(path_out+'/'+video_basename_new_no_extens+'*.jpg'))
        if len(jpg_fnames_of_this_video) != totalNFrames:
            print('please de-bug me!!!')
            exit()
        for fullJPEGfname in jpg_fnames_of_this_video:
            _, file_extension = os.path.splitext(fullJPEGfname)
            fname_no_ext = os.path.basename(fullJPEGfname).split('.', 1)[0] #e.g. 2022-12-12_120528_00015
            dirname = os.path.dirname(fullJPEGfname)
            frame_index = int(fname_no_ext.split('_')[-1])
            thisFramesTime = video_starting_time_datetime_object + timedelta(seconds=(frame_index-1)*(1./float(fps)))
            new_fname = station_parameters['cname']+'_'+station_parameters['ips']+'_'+thisFramesTime.strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
            new_fname = dirname+'/'+new_fname+file_extension
            os.rename(fullJPEGfname, new_fname)
    ALL_fnames = sorted(glob(path_out+'/'+"*.jpg")) #full filenames of JPEGS of video frames
    print('Videos now are split to '+str(len(ALL_fnames))+' frames')
    make_metadata(ALL_fnames,path_out,video_fnames_of_this_hour[0],station_parameters)
    os.chdir(my_dir)
    return(ALL_fnames)



def make_metadata(ALL_fnames,path2save,AsourceVideoFullFname,station_parameters):
    #read at https://stackoverflow.com/questions/33212855/how-can-i-create-a-matlab-struct-array-from-scipy-io

    name0 = ALL_fnames[0]
    time0 = os.path.basename(name0).split('.', 1)[0]  
    time0 = time0.split('_')
    time0 = '_'.join(time0[-7:])
    time0 = datetime.strptime(time0, '%Y_%m_%d_%H_%M_%S_%f')
    
    N = len(ALL_fnames)
    camera = [station_parameters['cname'] for number in range(N)]
    test_name = [station_parameters['tname'] for number in range(N)]
    camIP = [station_parameters['ips'] for number in range(N)]
    
    path = os.path.dirname(os.path.dirname(name0))
    path  = [path for number in range(N)]
    
    pathroot = [os.path.dirname(AsourceVideoFullFname) for number in range(N)]
    
    a = os.path.basename(os.path.dirname(name0))
    set_name = [a for number in range(N)]
    
    sdate = []
    date = []
    my_time = []
    timestamp =[]
    filename = []
    for fullJPEGfname in ALL_fnames:
        basename_no_ext = os.path.basename(fullJPEGfname).split('.', 1)[0]  
        basename_splited = basename_no_ext.split('_')
        # e.g. basename_splited = 'Peyia1_10_10_10_111_2022_12_11_10_03_36_000'.split('_')
        tmp_date = '_'.join(basename_splited[-7:])
        frames_date = datetime.strptime(tmp_date, '%Y_%m_%d_%H_%M_%S_%f')
        sdate.append(datetime2matlabdn(frames_date))
        
        date.append('_'.join(basename_splited[-7:-4]))
        my_time.append(frames_date.strftime("%H:%M:%S.%f")[:-3])
        timestamp.append((frames_date-time0).total_seconds())
        filename.append(os.path.basename(fullJPEGfname))
    data2save = [camera,test_name,sdate,date,my_time,timestamp,camIP,path,pathroot,set_name,filename]
    myrec = fromarrays(data2save, names=['camera','test_name','sdate','date','time','timestamp','camIP','path','pathroot','set','filename'])
    savemat(path2save+'/'+'metadata.mat', {'meta': myrec},do_compression=True)


# MAKE PRODUCTS CODE
def make_products_from_video_files(video_fnames_of_this_hour,day,hour2show,station_parameters,make_sigmac=False):
    TMP_FS_path = '/mnt/tmp'
    frames_list_FullFnames = make_frames_from_videos(video_fnames_of_this_hour,day,hour2show,station_parameters,path_out = TMP_FS_path,FnameContainsLeadingNumbering=True)
    
    print('Start making products (timex sigma immin immax snapshot sigmaColor) from frames now')
    # get total number of frames
    totalNframes=len(frames_list_FullFnames)
    frame0 = cv2.imread(frames_list_FullFnames[0], cv2.IMREAD_COLOR)
    height = int(frame0.shape[0])
    width = int(frame0.shape[1])
    
    snap = frame0
    
    timex = np.zeros((height,width,3))
    timex = np.double(timex)
    timexmax = np.zeros((height,width,3))
    timexmin = 1000*totalNframes+np.zeros((height,width,3))
    sigmaa=np.zeros((height,width))
    N_unused = 0

    #framePrevious = np.nan
    #totalFrameII = 0
    for (frameII,frameFullFname) in enumerate(frames_list_FullFnames):
        frame = cv2.imread(frameFullFname, cv2.IMREAD_COLOR)

        gray = uint8_matlab_compatible(bgr2gray(frame))
        N_zeros = np.sum(gray==0) 
        frame = np.double(frame)
        
        # Make SIGMA
        if frameII != 0:
            diffPrevious=np.abs(np.double(grayPrevious)-np.double(gray))
            sigmaa += diffPrevious
        grayPrevious = gray
        
        #Make TIMEX IMMAX,IMMIN
        if N_zeros<0.5*width*height:
            timex += (frame)
            timexmax = np.maximum(frame, timexmax )
            timexmin = np.minimum(timexmin, frame)
        else:
            N_unused+=1
            print('Found a more than 50prcent black frame')                
 
    timex = timex/(totalNframes-N_unused)
    timex = uint8_matlab_compatible(timex)
    # for kk in range(s3):
    #     timex[:,:,kk] = matlab_uint8(timex[:,:,kk])
    # #timex = matlab_uint8(timex)
        
    immin=uint8_matlab_compatible(timexmin)
    immax=uint8_matlab_compatible(timexmax)
    
    # Make Sigma color
    if make_sigmac == True: #make sigma color
        timex_double = np.double(timex)
        sigmac = np.double(np.zeros((height,width,3)))
        for (frameII,frameFullFname) in enumerate(frames_list_FullFnames):
            frame = cv2.imread(frameFullFname, cv2.IMREAD_COLOR)
            sigmac += np.abs(np.double(frame)-timex_double);
    sigmac = series_normalize_per_channel(sigmac,1,255)
    sigmac = uint8_matlab_compatible(sigmac)
    for f in glob(TMP_FS_path+'/*.jpg'):
        os.remove(f)
    if make_sigmac == False:
        return(timex,immin,immax,snap,sigmaa)
    else:
        return(timex,immin,immax,snap,sigmaa,sigmac)

