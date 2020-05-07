
'''
This is the main module containing the class that represents the star file
'''

import numpy as np 
import pandas as pd 

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

        f.close()

        
        
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
            
            