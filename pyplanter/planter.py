#!/usr/bin/env python

import os
import shutil
import h5py as h
import numpy as np
from typing import Union

from .config.constants import *
from .config.config import *


class DatasetMixin():
    """_summary_

    Returns:
        _type_: _description_
    """

    def _remove_dataset(self, dname:Union[str,list]):
        """_summary_

        Args:
            dname (Union[str,list]): _description_
        """
        if isinstance(dname, str):
            dname = [dname]

        for dset in dname:
            if dset in self.f_obj:
                del self.f_obj[dset]


    def create_dataset(self, data_arr:np.ndarray, ch_names:list=None, datacache_name:str=None, unit_name:Union[str, list]=None):
        """_summary_

        Args:
            data_arr (_type_): _description_
        """

        # remove old dataset and all related structures
        if DATASET_DNAME in self.f_obj:
            self._remove_dataset(dname=[DATASET_DNAME, INFO_DNAME, CHANNEL_DNAME])

        # create new dataset
        self.f_obj.create_dataset(DATASET_DNAME, dtype=DATASET_DTYPE, data=data_arr, chunks=True, maxshape=(None, None))

        # generate channel parameters
        if ch_names is None:
            ch_names = list(map(str, range(data_arr.shape[0])))

        self._add_channel_params(ch_names, datacache_name, unit_name)


    def add_samples(self, data_arr:np.ndarray, dim:int=1):
        """_summary_

        Args:
            data_arr (_type_): ndarray of the same length as data.shape[1]

        Raises:
            ValueError: Incosistent shape of the input data.
        """

        DIM_MAPPING = {1: 0, 0: 1}

        # Check for existing dataset
        if not DATASET_DNAME in self.f_obj:
            self.create_dataset(self, data_arr)
            return

        # Check for data shape consistency
        if self.f_obj[DATASET_DNAME].shape[DIM_MAPPING[dim]] != data_arr.shape[DIM_MAPPING[dim]]:
            raise ValueError(
                f"""Inconsistent shape of the input data.
                Expected to be {self.f_obj[DATASET_DNAME].shape[DIM_MAPPING[dim]]}, 
                got {data_arr.shape[DIM_MAPPING[dim]]} instead."""
                )            

        self.f_obj[DATASET_DNAME].resize(
            self.f_obj[DATASET_DNAME].shape[dim] + data_arr.shape[dim],
            axis=dim,
            )
        
        if dim == 0:
            self.f_obj[DATASET_DNAME][-data_arr.shape[dim]:, :] = data_arr
        
        if dim == 1:
            self.f_obj[DATASET_DNAME][:, -data_arr.shape[dim]:] = data_arr
    

    def remove_samples(self, sample_range:tuple):
        """_summary_

        Args:
            range (tuple): _description_
        """
        if not DATASET_DNAME in self.f_obj:
            return

        content = self.f_obj[DATASET_DNAME][:]
        content = np.delete(content, np.s_[sample_range[0]:sample_range[1]], axis=1)
        
        del self.f_obj[DATASET_DNAME]

        self.f_obj.create_dataset(DATASET_DNAME, dtype=DATASET_DTYPE, data=content, chunks=True, maxshape=(None,None))


    def add_channels(self, data_arr:np.ndarray, ch_names:list=None, datacache_name:str=None, unit_name:Union[str, list]=None):
        """_summary_

        Args:
            data_arr (_type_): _description_
        """
        
        self.add_samples(data_arr, dim=0)
        
        # generate channel parameters
        if ch_names is None:
            nb_channels = self.f_obj[DATASET_DNAME].shape[0]
            ch_names = list(map(str, range(nb_channels, nb_channels+data_arr.shape[0])))

        self._add_channel_params(ch_names, datacache_name, unit_name)
        

    def _get_channels(self):
        """Retrieve channel names

        Args:
            self.f_obj (obj): file obj. handle

        Returns:
            (list): List of channel names.
        """
        
        if CHANNEL_DNAME in self.f_obj:
            return [item[0].decode('UTF-8') for item in self.f_obj[CHANNEL_DNAME][:]]        


    def _generate_channel_settings(self, ch_names:list):    
        """Generates channel settings for Signal Plant

        Args:
            self.f_obj (obj): file obj. handle
            ch_names (list): List of channel names

        Raises:
            TypeError: Check for strings in <ch_names> list

        Returns:
            self.f_obj (obj): file obj. handle
        """

        # Generate content
        content = list()

        for ch_name in ch_names:
            # Check channel name data type
            if not isinstance(ch_name, str):
                raise TypeError('List of channels names contains one or more non-string items.')

            # Generate single channel settings and append to content            
            temp = [ch_name.encode('UTF-8')]
            temp.extend(list(DEFAULT_CHANNEL_SETTINGS.values()))
            content.append(tuple(temp))

        content = np.array(
            content,
            dtype=CHANNEL_DTYPES,
            )

        # add/append dataset
        if CHANNEL_DNAME in self.f_obj:
            current_content = self.f_obj[CHANNEL_DNAME][:]
            content = np.append(current_content, content)

            del self.f_obj[CHANNEL_DNAME]
        
        self.f_obj.create_dataset(CHANNEL_DNAME, data=content)
        

    def _generate_channel_info(self, ch_names:list, datacache_name:str=None, unit_name:Union[str,list]=None):
        """Generates channel info for Signal Plant

        Args:
            self.f_obj (obj): file obj. handle
            ch_names (list): List of channel names
            datacache_names (list, optional): List of channel names. If None names are generated using default values.
            unit_names (list, optional): List of physical unit names. If None names are generated using default values.

        Returns:
            self.f_obj (obj): file obj. handle
        """

        # make a list of datacache names
        if datacache_name is None:
            datacache_name = DEFAULT_PARAMS['datacache_name']
        
        if isinstance(datacache_name, str):
            datacache_name = [datacache_name.encode('UTF-8') for _ in ch_names]

        # make a list of physical units
        if unit_name is None:
            unit_name = DEFAULT_PARAMS['data_units']
        
        if isinstance(unit_name, str):
            unit_name = [unit_name.encode('UTF-8') for _ in ch_names]

        # make a list of encoded channel names
        ch_names = [item.encode('UTF-8') for item in ch_names]

        # Generate content
        content = list(zip(ch_names, datacache_name, unit_name))

        content = np.array(
            content,
            dtype=INFO_DTYPES,
            )    

        # add/append dataset
        if INFO_DNAME in self.f_obj:
            current_content = self.f_obj[INFO_DNAME][:]
            content = np.append(current_content, content)

            del self.f_obj[INFO_DNAME]
        
        self.f_obj.create_dataset(INFO_DNAME, data=content)
    

    def _add_channel_params(self, ch_names:list, datacache_name:str=None, unit_name:Union[str,list]=None):
        """_summary_

        Args:
            ch_names (list): _description_
            datacache_name (str, optional): _description_. Defaults to None.
            unit_name (Union[str,list], optional): _description_. Defaults to None.
        """
        # generate channel settings
        self._generate_channel_settings(ch_names)

        # generate channel info
        self._generate_channel_info(ch_names, datacache_name, unit_name)


    def _remove_channel_params(self, channel_ids):
        """_summary_

        Args:
            channel_ids (_type_): _description_
        """
        for dname in (CHANNEL_DNAME, INFO_DNAME):
            content = self.f_obj[dname][:]
            content = np.delete(content, channel_ids, axis=0) # axis = 1 for columns
            
            del self.f_obj[dname]
            
            self.f_obj.create_dataset(dname, data=content)
    

    def remove_channel(self, field_txt:Union[str,list], field_name:str='channel') -> None:
        """_summary_

        Args:
            field_txt (Union[str,list]): _description_
            field_name (str, optional): _description_. Defaults to 'channel'.
        """

        if DATASET_DNAME not in self.f_obj:
            return

        field_mapping  = {'channel': 0, 'datacache': 1}
        
        assert field_name in field_mapping

        if isinstance(field_txt, str):
            field_txt = [field_txt]

        field_txt = set(field_txt)
        
        # get positions of searched key words in the dataset
        channel_ids = []
        for idx, item in enumerate(self.f_obj[INFO_DNAME][:]):
            if item[field_mapping[field_name]].decode('UTF-8') in field_txt:
                channel_ids.append(idx)
        
        if channel_ids:
            # remove entire datasets if number of matches corresponds to overall number of channels
            if len(channel_ids) == self.f_obj[INFO_DNAME].shape[0]:
                self._remove_dataset(dname=[DATASET_DNAME, INFO_DNAME, CHANNEL_DNAME])

            # remove channels from `Data` dataset
            content = self.f_obj[DATASET_DNAME][:]
            content = np.delete(content, channel_ids, axis=0) # axis = 1 for columns
            
            del self.f_obj[DATASET_DNAME]
            
            self.f_obj.create_dataset(DATASET_DNAME, data=content, chunks=True, maxshape=(None,None))

            # remove channel parameters from `Info` and `ChannelSettings`
            self._remove_channel_params(channel_ids)


    def remove_datacache(self, datacache_name:str):
        """_summary_

        Args:
            datacache_name (str): _description_
        """
        self.remove_channel(field_txt=datacache_name, field_name='datacache')
        

class MarksMixin():
    """_summary_

    Returns:
        _type_: _description_
    """

    def add_mark(
        self,
        start_sample:int=None,
        end_sample:int=None,
        group_id:str='',
        validity:float=0.0,
        channel_id:str='',
        info:str=''
        ) -> None:

        """_summary_

        Args:
            start_sample (_type_): _description_
            end_sample (_type_): _description_
            group_id (bytes, optional): _description_. Defaults to ''.
            validity (float, optional): _description_. Defaults to 0.0.
            channel_id (bytes, optional): _description_. Defaults to ''.
            info (bytes, optional): _description_. Defaults to b'a'.
        """
        
        # TODO: add mutiple marks at once

        # check sample validity
        if start_sample is None:
            return

        if end_sample is None:
            end_sample =  start_sample

        if end_sample - start_sample < 0:
            raise ValueError('Value of `end_sample` has to be equal or larger then `start_sample`')  

        # create NumPy array
        content = np.array(
            [(
                int(start_sample),
                int(end_sample),
                group_id.encode('UTF-8'),
                float(validity),
                channel_id.encode('UTF-8'),
                info.encode('UTF-8')
            )],
            dtype=MARKS_DTYPES,
        )

        if MARKS_DNAME in self.f_obj:           
            # read old marks and append new one
            current_content = self.f_obj[MARKS_DNAME][:]
            content = np.append(current_content, content)
        
            # remove old dataset and store the new one
            del self.f_obj[MARKS_DNAME]

        self.f_obj.create_dataset(MARKS_DNAME, data=content)
        
        
    def remove_marks(self, field_txt:str=None, field_name:str='group') -> None:
        """Remove marks from the file

        Args:
            group_id (str, optional): ID of group to remove. Defaults to None. If None, all marks will be deleted.
        """

        param_mapping = {'group': 2, 'channel': 4, 'info': 5,}

        #check for <marks> dataset existence
        if not MARKS_DNAME in self.f_obj:
            return                

        # delete all marks if group is not specified
        if field_txt is None:
            del self.f_obj[MARKS_DNAME]
            return
        
        else:
            if field_name not in param_mapping:
                raise ValueError(f'Field {field_name} does not exist. Use only valid field names: ' + ', '.join(list(param_mapping.keys())))

            field_idx = param_mapping[field_name]

            #filter out marks by field_txt
            valid_ids = [idx for idx, item in enumerate(self.f_obj[MARKS_DNAME]) if item[field_idx] != field_txt.encode('UTF-8')]
                
            valid_marks = self.f_obj[MARKS_DNAME][valid_ids] if valid_ids else None
            
            # remove old dataset and store the new one
            del self.f_obj[MARKS_DNAME]
            self.f_obj.create_dataset(MARKS_DNAME, data=valid_marks)                                                    
        
        
class AttributesMixin():
    """_summary_

    Returns:
        _type_: _description_
    """

    def attr_type (self, attr_name:str):
        """Returns attributes type

        Args:
            attr_name (str): Name of the attribute

        Returns:
            _type_: Attr data type
        """
                    
        return type(self.f_obj.attrs[attr_name])


    def get_attrs(self):
        return list(self.f_obj.attrs.keys())


    def add_attr(self, attr_dict):
        """_summary_

        Args:
            attr_dict (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        if not attr_dict or not isinstance(attr_dict, dict):
            return self.f_obj

        for attr_name, attr_value in attr_dict.items():
            # TODO: check if attr exits

            # Allow only ints and floats to be written as attributes.
            if isinstance(attr_value, (int, float)):        
                self.f_obj.attrs[attr_name] = np.array([attr_value], dtype=ATTR_DTYPE)


    def remove_attr(self, attr_name:Union[str, list, tuple]):
        """_summary_

        Args:
            attr_name (Union[str, list, tuple]): _description_
        """

        if isinstance(attr_name, str):
            attr_name = [attr_name]

        for item in attr_name:
            if item in self.f_obj.attrs.keys():
                del self.f_obj.attrs[item]        

        
    
class PlantedH5(MarksMixin, AttributesMixin, DatasetMixin):
    """_summary_

    Args:
        MarksMixin (_type_): _description_
        AttributesMixin (_type_): _description_
    """

    def __init__(self):
        self._f_obj = None
        

    @property
    def f_obj(self):
        return self._f_obj


    @f_obj.setter
    def f_obj(self, value):
        self._f_obj = value
    

    def create(self, f_path:str, sampl_freq:int=None):
        """Creates new h5 file.

        Args:
            f_path (_str_): Path to h5 file
            sampl_freq (int, optional): _description_. Defaults to 2000.

        Returns:
            _type_: _description_
        """    

        # Add suffix if doesn't exist
        if not f_path.lower().endswith('.h5'):
            f_path += '.h5'

        try:            
            self.f_obj = h.File(f_path, 'w')            
        except FileExistsError as e:
            pass
        except IOError as e:
            print(e)


        # Add sampling frequency into attributes
        self.f_obj.attrs['Fs'] = np.array([sampl_freq], dtype='<f4')    

        # # Add default parameters into attributes
        self.f_obj.attrs['GeneratedBy'] = DEFAULT_PARAMS['generated_by'].encode('UTF-8')
        self.f_obj.attrs['LeftI'] = DEFAULT_PARAMS['left_index']
        self.f_obj.attrs['RightI'] = DEFAULT_PARAMS['right_index']
        

    def open(self, f_path:str, mode:str='a'):
        """_summary_

        Args:
            f_path (_str_): Path to h5 file

        Returns:
            _handle_: File handle
        """

        #check if f_obj exists. If so, close old one first.
        if self.f_obj:
            self.close()

        try:
            self.f_obj = h.File(f_path, mode)
        
        except IOError as e:
            print(e)


    def merge(self, out_file:str, paths_list:list):        
        raise NotImplementedError


    def file_from_mark(self, group_id: str, info: str):        
        raise NotImplementedError


    def close(self):
        self.f_obj.close()   


    def flush(self):
        self.f_obj.flush()   


    def is_writable(self):
        return self.f_obj.mode in {'r+', 'a', 'w', 'w-', 'x'}



def main():
    """ Testing function
    """
    from datetime import datetime

    f_path = ''
    f_name = 'dummy_' + datetime.today().strftime('%Y-%m-%d_%H:%M:%S')

    # instantiate planter
    planter = PlantedH5()
    
    # basic operation with newly created h5 file
    # ---
    # ---
    dummy_array = np.ones((4, 200))

    # create new file with specified sampling frequency of time series
    planter.create(os.path.join(f_path, f_name), sampl_freq=2000)
    
    # create new dataset with custom settings
    channel_names = ['ch_1', 'ch_2', 'ch_3', 'ch_4']
    datacache_name = 'RAW'
    unit_name = ['mv', 'mv', 'Nm-1', 'Pa']

    planter.create_dataset(dummy_array, ch_names=channel_names, datacache_name=datacache_name, unit_name=unit_name)

    planter.flush()

    # append new time-series samples (to all current channels)
    planter.add_samples(dummy_array)

    # append new channel
    dummy_channel = np.ones((1, 400))
    planter.add_channels(dummy_channel, ch_names='ch_5', datacache_name='RAW', unit_name='mV')

    planter.flush()


    # basic operations with marks
    # ---
    # ---

    # add/remove marks
    # planter.remove_marks()
    
    # planter.add_mark(start_sample=5, end_sample=None, group_id='', validity=0.0, channel_id='', info='')

    
    # basic operations with attributes
    # ---
    # ---
    atrr_dict = {
        'attr_1': 500,
        'attr_2': 'content'
    }

    planter.add_attr(atrr_dict)
    
    planter.flush()   

    #close file
    planter.close()

    


if __name__ == '__main__':
    main()