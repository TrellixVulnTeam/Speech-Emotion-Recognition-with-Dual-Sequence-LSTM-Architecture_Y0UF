#!/bin/bash
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.4 -b 128 -lr 0.001 -e 150 -hd 200 -tc -bi
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.4 -b 128 -lr 0.001 -e 150 -hd 200 -tc 
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.4 -b 128 -lr 0.001 -e 150 -hd 250 -tc -bi
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.4 -b 128 -lr 0.001 -e 150 -hd 250 -tc 
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.4 -b 128 -lr 0.001 -e 150 -hd 300 -tc -bi
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.4 -b 128 -lr 0.001 -e 150 -hd 300 -tc 
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.8 -b 128 -lr 0.001 -e 150 -hd 200 -tc -bi
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.8 -b 128 -lr 0.001 -e 150 -hd 200 -tc 
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.8 -b 128 -lr 0.001 -e 150 -hd 250 -tc -bi
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.8 -b 128 -lr 0.001 -e 150 -hd 250 -tc 
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.8 -b 128 -lr 0.001 -e 150 -hd 300 -tc -bi
CUDA_VISIBLE_DEVICES="1" python full_train_and_test.py -m Mean_Pool_2 -dr 0.8 -b 128 -lr 0.001 -e 150 -hd 300 -tc 
