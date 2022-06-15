from collections import OrderedDict

DEFAULT_CHANNEL_SETTINGS = OrderedDict([    
    ('Visible', 1.0),
    ('Valid', 1.0),
    ('Line_R', 127.0),
    ('Line_G', 100.0),
    ('Line_B', 192.0),
    ('Back_R', 192.0),
    ('Back_G', 192.0),
    ('Back_B', 192.0),
    ('ActiveLAyer', 0.0),
    ('YRangeManual', 0.0),
    ('YRangeMin', -1.0),
    ('YRangeMax', 1.0),
    ('PanelHeight', 100.0),
])

# default datasets names
DATASET_DNAME = 'Data'
INFO_DNAME = 'Info'
CHANNEL_DNAME = 'ChannelSettings'
MARKS_DNAME = 'Marks'

# default datasets data types
DATASET_DTYPE = '<f4'
CHANNEL_DTYPES = [
    ('Channel', 'S256'),
    ('Visible', '<f4'),
    ('Valid', '<f4'),
    ('Line_R', '<f4'),
    ('Line_G', '<f4'),
    ('Line_B', '<f4'),
    ('Back_R', '<f4'),
    ('Back_G', '<f4'),
    ('Back_B', '<f4'),
    ('ActiveLAyer', '<f4'),
    ('YRangeManual', '<f4'),
    ('YRangeMin', '<f4'),
    ('YRangeMax', '<f4'),
    ('PanelHeight', '<f4')
]    
INFO_DTYPES = [
    ('ChannelName', 'S256'),
    ('DatacacheName', 'S256'),
    ('Units', 'S256')
]
MARKS_DTYPES = [
    ('SampleLeft', '<i4'),
    ('SampleRight', '<i4'),
    ('Group', 'S256'),
    ('Validity', '<f4'),
    ('Channel', 'S256'),
    ('Info', 'S256'),
]
ATTR_DTYPE = '<f4'