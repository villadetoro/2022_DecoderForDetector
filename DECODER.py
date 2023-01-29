#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code that reads .dat (binary) files from a folder and (by decoding
 them to hexadecimal data first) converts them to 'useful' data

@author: s1867522@ed.ac.uk 
"""

import sys
#import math
#import numpy as np
import matplotlib.pyplot as plt

def read_binary(file_dat, file_hex):
    
    """
    Reads binary data from a .dat file and decodes it to hexadecimal into
    a .txt file of strings
                
    :param file_dat: binary .dat file (from detector)
        
    :return file_hex: hexadecimal data file in string form (.txt)
    """

    with open(file_dat, "rb") as f:      # "rb" to read binary 
        out_hex = open(file_hex + ".txt", "w")

        #iterate with i - just to debug the code without going through all the data  
        #i =100
        #while i :
        
        word = f.read(4)    #word -- 4 byte
       
        #to stop the loop when there are no more words in the file
        while True :
        
            #"little" because the most significant byte is at the end of the byte array
            hexa = hex(int.from_bytes(word, byteorder='little'))
            
            #to stop the loop when there are no more words in the file
            if hexa == '0x0' :              
                break


            #write hexadecimal data into output file 
            out_hex.write(hexa)
            out_hex.write("\n")
        
            #iterate with i 
            #i = i - 1
            
            word = f.read(4)
                 
    f.close()
    out_hex.close()

    return file_hex

    


def read_hex(file_hex):
    
    """
    Reads hexadecimal (strings) data from .txt into decimal data, following
    detector data structure (from detector documentation). Stores the decimal
    data in a python-lists 
                
    :param file_hex: hexadecimal data file in string form (.txt)
        
    :return decimal_data: decimal data in python-lists
    """ 
    
    #DATA BLOCK STRUCTURE - FIXED PARAMETERS
    #structure following documentation
    header_1 = str("0xffff80eb")
    header_2 = str("0xff008022")
    header_3 = str("0xff00")
    subheader_A = str("0xfa0") #SLOT U
    subheader_B = str("0xfb0") #SLOT D
    leading = str("0xc0")
    common_stop = str("0xa0")
    
    decimal_data_leading = []   #empty list to store final decimal data (leading edge)
    decimal_data_common = []   #empty list to store final decimal data (common stop)
    decimal_data_trailing = []  ##empty list to store final decimal data (trailing)
    #decimal_data = []   #empty list to store final decimal data (leading + trailling + common edge)
    
    scale = 16 #hexadecimal (for hexadecimal translations)
    
    
    with open(file_hex, "r") as file:
        
        #adding an index just for the tag in header_3_b
        #index = 0 
    
        for line in file:
            
            #beginning of several if statements to check that the data block has started
            if line.startswith(header_1):
                possible_header2 = next(file) #next word in the file
                
                if possible_header2.startswith(header_2):
                    total_words_dec = int(possible_header2[-4:], 16)  # 3 spaces gives me only last 2 digist: why 4??? blank spaces???       
                    possible_header3 = next(file)
                    
                    if possible_header3.startswith(header_3):
                        possible_sh_A = next(file)
                    
                    
                        #START OF SUBHEADERS:
                        
                        
                        if possible_sh_A.startswith(subheader_A):
                            
                            possible_sh_B = next(file)
                            
                            a_hex = possible_sh_A[-4:]
                            #n_words_A = int(possible_sh_A[-4:], 16)
                            
                            if possible_sh_B.startswith(subheader_B):
                                
                                b_hex = possible_sh_B[-4:]
                                b_words_dec = int(b_hex, 16)
                                
                                # -2 because subheader A and B are substracted (1 word each)
                                words_check = total_words_dec - 2 #sanity check
    
                                
                                #START OF DATA BODY reading
                                
                                
                                if words_check == b_words_dec:
                                #no data words in U slot
                                #32 CHANNELS
                                    
                                    for i in range(b_words_dec):
                                        
                                        #data body 
                                        data = str(next(file,i))
                                        
                                        if data.startswith(leading):
                                            
                                            data_2_leading = data[-7:]
    
                                            dec_data_leading = int(data_2_leading, 16)
                                        #print(dec_data)
                                        
                                            decimal_data_leading.append(dec_data_leading)
                                        
                                        if data.startswith(common_stop):
                                            
                                            data_2_common = data[-7:]
    
                                            dec_data_common = int(data_2_common, 16)
                                        #print(dec_data)
                                        
                                            decimal_data_common.append(dec_data_common)                                            
                                         
                                        channel = 1
                                        histograms(decimal_data_leading, decimal_data_common, decimal_data_trailing, channel)
                                
                                else: 
                                    #31 CHANNELS (SUB A AND SUB B)
                                    
                                    words_hex = b_hex + a_hex
                                    words_hex2 = str(words_hex)
                                    words_dec = int(words_hex2, 16)
                                    for i in range(words_dec):
                                        #data body 
                                        
                                        data = str(next(file,i))
                                        data_2 = data[-7:]
                                        dec_data = int(data_2, 16)
                                        
                                        decimal_data.append(dec_data)
    
                                                                                                      
        #print(decimal_data) 
        #print(decimal_data_trailing)                          
        file.close()     
    
    #return [decimal_data_leading, decimal_data_common, decimal_data_trailing]

def histograms(decimal_data_leading, decimal_data_common, decimal_data_trailing, channel):
    
    decimal_data = decimal_data_leading + decimal_data_common + decimal_data_trailing
    
    
    xaxes = ['frequency']
    yaxes = ['bins']
    titles = ['leading','common','trailing','total'] 
    data = [decimal_data_leading, decimal_data_common, decimal_data_trailing, decimal_data]
    
    f,a = plt.subplots(2,2)
    a = a.ravel()  #returns contiguous flattened array
    for idx,ax in enumerate(a):
        ax.hist(data[idx])
        ax.set_title(titles[idx])
        ax.set_xlabel(xaxes)
        ax.set_ylabel(yaxes)
    plt.tight_layout()
    plt.savefig("ch" + str(channel) + "histograms.png")

def main():
 
    """
    TO RUN THE CODE FROM TERMINAL:
        in the same directory where the code and data is run:
            python3 [NameOfCode] [DataFile] [NameHexadecimalsFile] 
    """ 
    
    if len(sys.argv)!=3:
        print("Wrong number of arguments.")
        print("Usage: " + sys.argv[0] + " <output file>")
        quit()
    else:
        file_dat_name = sys.argv[1]  #binary .dat file (from detector)
        file_hex_name = sys.argv[2]  #hexadecimal data file in string form (.txt)
        
        
        file_hex = read_binary(file_dat_name, file_hex_name)
        read_hex(file_hex)
    

    
# Execute main method, but only when directly invoked
if __name__ == "__main__":
    main()
