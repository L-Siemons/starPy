
'''
This is the main module containing the class that represents the star file
'''

import numpy as np 
import pandas as pd 
import copy
import random as r

class StarFile():
    
    def __init__(self, file):
        
        '''
        
        This class stores all the data in a star file as a dictionary in the following manner: 
        
        1) The star file is split up into 'data chunks' using the headers 'data_'.
           Each data chunk is stored in the dictionary 'self.data[chunk_id]'. 
           
        2) If the data chunk is simple and not tabular then this is represented as another
           dictionary. eg self.data['data_general']['_rlnmaskname'] = 'mask.mrc'
        
        3) If the data chunk contains a loop then the data is stored as a pandas array.
        
        Parameters:
        -----------
        file : str
            The name of the star file
        
        Attributes
        ----------
        file_name : str 
            the star file name 
        
        self.data : dict
            contains the data in the star file
            
        '''
        
        # open the attributes 
        self.file_name = file
        self.data = {}
        
        # read the file
        f = open(file)
        lines = f.readlines()
        f.close()
        
        # varrious things needed to store data and track states
        loop_data = {}
        loop_headers = {}
        line_state = 'default'
        loop_state = False
        
        # go through the lines 
        for l in lines: 
            
            s = l.split('#')[0].split()    
            if s != []:
                
                line_state = 'default'
                
                if 'data_' in l:
                    chunk_id = s[0]
                    loop_state = False
                    line_state = 'chunk_header'
                   
                # here we need to initialise all the things we want for
                # reading the loops 
                
                if 'loop_' in l:
                    loop_state = True
                    line_state = 'loop_header'
                    
                    headers = []
                    loop_data[chunk_id] = []
                    loop_headers[chunk_id] = []
                
                # if there are no loops then we justy read in the data as a simple dictionary 
                if line_state == 'default' and loop_state==False:
                    if chunk_id not in self.data:
                        self.data[chunk_id] = {}
                    
                    # convert the values to floats where possible
                    try:
                        value = float(s[1])
                    except ValueError:
                        value = s[1]
                        
                    self.data[chunk_id][s[0]] = value
                
                # if a loop structure is pressent we will read it in as a pandas 
                # data frame
                if loop_state and line_state == 'default':
                    
                    # this is the marker for the header 
                    # here we assume that after the first non-header line we will not see any more 
                    
                    if s[0][0] == '_':
                        loop_headers[chunk_id].append(s[0])
                    
                    else:
                        
                        float_line = []
                        for i in s:
                            try:
                                float_line.append(float(i))
                            except ValueError:
                                float_line.append(i)
                        loop_data[chunk_id].append(float_line)
                    
                    
        
        # now we just need to store the data in loop_data as pandas arrays
        for i in loop_data:
            array = np.array(loop_data[i])
            self.data[i] = pd.DataFrame(array, columns=loop_headers[i])

                
    def write_out(self, out_name, fields=False):

        '''
        A simple write out function

        Parameters: 
        -----------

        out_name : str
            The name of the file you would like to write out to

        fields : false or list
            If false all data_blocks will be written out. If a list 
            is passed then only the datablocks in the list will be written out
        '''

        
        def write_simple_block(dict_, file):

            '''
            Write a dictionary to the star file
            '''    

            for i in dict_:
                val = str(dict_[i])
                file.write('%s     %s\n'%(i, val))

        def write_tabular_data(dataframe, file):

            f.write('loop_\n')
            for i in dataframe.columns:
                f.write(i+'\n')

            lines = dataframe.to_csv(index=False, header=False)
            lines = lines.replace(',', '     ')
            file.write(lines)
        
        f = open(out_name, 'w')
        f.write('# This file was written by StarPy\n\n')

        if fields == False:

            for i in self.data:

                f.write(i+'\n\n')

                if type(self.data[i]) == dict:
                    write_simple_block(self.data[i], f)

                if type(self.data[i]) == pd.DataFrame:
                    write_tabular_data(self.data[i], f)

                f.write('\n\n')

        else:
            print('this option is not implimented yet ... Please remind me to do it!')

        f.close()

    def select_random_data(self, data_block, removal_percent):
        '''
        This function can be used to remove a random percentage of the 
        rows in tabular data

        Parameters: 
        -----------

        data_block : str
            Name of the data_block we want to reduce 

        removal_percent : float 
            float between 0 and 1 that is the percent we want to remove
        '''

        # check its a dataframe
        assert type(self.data[data_block]) == pd.DataFrame

        rows_number = int((self.data[data_block].shape[0])*(1 - removal_percent))
        self.data[data_block] = self.data[data_block].sample(n=rows_number)

    def write_out_chunks(self, chunk_length, data_block):
        '''
        This function takes a data block and writes star files with N lines 
        in that data block. Note that other information in the star file is not written out 

        Parameters: 
        -----------

        chunk_length : int
            How many lines in the data block 

        data_block : str
            Name of the data_block we want to reduce 
        '''

        original = copy.copy(self.data[data_block])

        lst = [self.data[data_block].iloc[i:i+chunk_length] for i in range(0,len(self.data[data_block])-chunk_length+1,chunk_length)]

        for indx, i in enumerate(lst):

            self.data[data_block] = i 
            self.write_out(self.file_name.split('.')[0]+'_%i.star'%(indx))

        self.data[data_block] = original

    def half_field(self, data_block, field, random=False):

        '''
        This function writes out two star files where a databloack has been split 
        into two halfs using a feature in the datablock/pandas array. 

        This could be useful for splitting tomograms. 

        The two halfs are written into star files ending in 'half1(2).star' and the total star 
        file is written out to a file with '_total.star' as the ending. Note this changes the _rlnRandomSubset
        flag accordingly.

        Parameters: 
        -----------

        data_block : str
            Name of the data_block we want to reduce 

        field : str 
            the pandas colomn you want to use to split the data. 

        random : boolean
            True means that the tomograms get shuffled before splitting
        '''
    
        original = copy.copy(self.data[data_block])
        headers = list(set(self.data[data_block][field]))

        if random == True:
            headers = r.shuffle(headers)

        list1 = []
        list2 = []

        for indx, item in enumerate(headers):
            if (indx %2) == 0:
                list1.append(item)
            else:
                list2.append(item)

        print('writing half 1')
        half1 = original[original[field].isin(list1)].assign(_rlnRandomSubset=1)
        self.data[data_block] = half1
        self.write_out(self.file_name.split('.')[0]+'_half1.star')

        print('writing half 2')
        half2 = original[original[field].isin(list2)].assign(_rlnRandomSubset=2)
        self.data[data_block] = half2
        self.write_out(self.file_name.split('.')[0]+'_half2.star')

        print('writing total')
        self.data[data_block] = pd.concat([half1,half2])
        self.write_out(self.file_name.split('.')[0]+'_total.star')        

            
            
            
            
            
            
            
            
            
            
            
            
            
        
            
            