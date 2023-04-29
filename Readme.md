# Coastal Video Monitoring using Linux & Python

## Installation
Install ffmpeg in your linux OS
```
sudo apt update && sudo apt upgrade
sudo apt install ffmpeg
```

Use pyhton3 inside an anaconda/miniconda enviroment
e.g. installation of miniconda
```
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
export PATH=$PATH:/home/cyberithub/miniconda3/bin
```

restart shell and make sure your are inside the correct python env, e.g. the ```which python``` should return something similar to ```/home/tasos/anaconda3/bin/python```

You should have the following python libraries installed:
scipy, openCV >= 3 (not 2), numpy
```
conda install -c anaconda scipy
conda install -c conda-forge opencv
conda install -c anaconda numpy
```

Then make a tempFS to put temporary video frames in there and make sure you own this folder!:
NOTE: this should be done after every restart of your OS
```
sudo mount -t tmpfs -o size=1g tmpfs /mnt/tmp
sudo chown $USER:$USER /mnt/tmp
```

## What the codes contain:

### make_products_MAIN_v10_3.py

makes sigma timex etc of a specified folder, uses multithreading using N_threads = N_threads_of_current_CPU
uses the ```make_products_from_VIDEO_Files.py```


## Results
Using a laptop with i7-3612QM CPU @ 2.10GHz and 8GB RAM needs about
- 35sec to split 8 3gp videos to frames
- 12m:30s to make products (timex sigma immin immax snapshot sigmaColor) from frames



## Authors list
- Original (matlab) work by MV
- Debugging (matlab version) by VT
- This (python) version: Tasos


## LICENSE

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

**Free Software, Hell Yeah! Reference it if you use it, keep it open source if you use it**


LICENSE SYNOPSIS:



```markdown
1. Anyone can copy, modify and distribute this software.
2. You have to include the license and copyright notice with each and every distribution.
3. You can use this software privately.
4. You can use this software for commercial purposes.
5. If you dare build your business solely from this code, you risk open-sourcing the whole code base.
6. If you modify it, you have to indicate changes made to the code.
7. Any modifications of this code base MUST be distributed with the same license, GPLv3.
8. This software is provided without warranty.
9. The software author or license can not be held liable for any damages inflicted by the software.
```

