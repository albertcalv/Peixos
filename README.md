# Peixos
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

Peixos is an animal video tracking software for behavioural analysis. The software allows tracking species on videos using logical rules to tag high confidence elements in the video and requesting expert knowledge for disambiguation. Our GUI enables a friendly and fast interaction with the system allowing correcting tracking mistakes in real-time. The software is built-in Python3.6 and OpenCV.

![alt text](
https://github.com/albertcalv/LYD-Peixos/blob/master/doc/main_peixos.png?raw=true)

## Usage

### Installation 
1 Clone repository from github: 
```bash
git clone https://github.com/albertcalv/LYD-Peixos
```

2 Create new Conda environment
````bash
cd LYD-Peixos
conda env create -f peixos-env.yml
````

3 Install Peixos dependencies from .yml file
````bash
conda activate peixos-env
pip install .  
pip install PyQt5
````

### Run Peixos using the GUI 
````bash
conda activate peixos-env
python peixos/main_gui.py
````

### Run Peixos in Console 
````bash
python peixos/main_console.py --path_to_video=../video --path_to_video_back=../video_background --num_of_elements=num_of_elements
````

### How it works 
Peixos allows automatic tracking, no human supervision and manual supervision, the software stops the execution in doubtful frames.  The usage of _Manual with UI Validation_ mode is recommended especially in low-quality videos. Check the following links with further information: 

-  [Automatic Mode](https://github.com/albertcalv/LYD-Peixos/wiki/Usage#how-it-works-automatic-tracking)  

-  [Manual with UI Validation](https://github.com/albertcalv/LYD-Peixos/wiki/Usage#how-it-works-ui-validation)


## Peixos Wiki

**Table of contents**
-  [Requirements and Installation](https://github.com/albertcalv/LYD-Peixos/wiki/requirements-and-Installation)  
  
-  [Usage of Peixos](https://github.com/albertcalv/LYD-Peixos/wiki/Usage)
  
-  [Output Files](https://github.com/albertcalv/LYD-Peixos/wiki/Output) 
  
-  [Configuration Parameters](https://github.com/albertcalv/LYD-Peixos/wiki/Configuration) 

-  [Algorithm Documentation](https://github.com/albertcalv/LYD-Peixos/wiki/Algorithm-Documentation) 
  
-  [FAQs](https://github.com/albertcalv/LYD-Peixos/wiki/FAQs)
  
-  [Contact](https://github.com/albertcalv/LYD-Peixos/wiki/Contact)
