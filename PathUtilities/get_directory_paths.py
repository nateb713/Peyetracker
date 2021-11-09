import re
from collections import namedtuple, defaultdict
import os
from .general_path_functions import normalize_path

class GetPathsFromDirectory:
    
    
    def __init__(self
                ,path
                ,metadata_keys_raw=None
                ,valid_metadata_keys=None
                ,target_path_type=None
                ,filename_contains=None
            ):
        self._path = path
        self._metadata_keys_raw = metadata_keys_raw
        self._valid_metadata_keys = valid_metadata_keys
        self._target_path_type = target_path_type
        self._filename_contains = filename_contains
        self.result = self.dispatch()



    def dispatch(self):
        target_paths = []
        if os.path.isdir(self._path):
            directory_files = [os.path.join(root, file)
                                for root, _, files in os.walk(self._path)
                                    for file in files
            ]
            
            target_paths = self.filter_files(directory_files)
            
            if not target_paths:
                print(f"Could not find paths with {self._target_path_type}")
                return 
        else:
            target_paths.append(self._path)

        # Insert error handle to ensure target paths
        normalized_paths = [normalize_path(path) for path in target_paths]

        if self._metadata_keys_raw:
            labeled_paths = LabelPaths(normalized_paths
                                    ,self._metadata_keys_raw
                                    ,self._valid_metadata_keys
                                    ).result
            return labeled_paths            
        return normalized_paths


    def filter_files(self, file_paths ):
        target_paths = []
        for file in file_paths:
            if self._filename_contains:
                if self._filename_contains in file:
                    target_paths.append(file)
            
            elif self._target_path_type:
                if file.endswith(self._target_path_type):
                    target_paths.append(file)
            else:
                target_paths.append(file)
        
        return target_paths


class LabelPaths:


    def __init__(self
                ,paths
                ,metadata_keys_raw=None
                ,valid_metadata_keys=None
                ):
        self._paths = paths
        self._metadata_keys_raw = metadata_keys_raw
        self._valid_metadata_keys = valid_metadata_keys
        self.result = self.dispatch()
    
    def dispatch(self):
        metadata = self.extract_metadata()
        labeled_paths = self.make_subjects(metadata)
        filtered = LabelPaths.filter_metadata_duplicates(labeled_paths)
        return filtered

    def extract_metadata(self):
        file_metadata = []
        for path in self._paths:
            name = path.stem.strip()
            split_name_raw = re.split('[\-_]|(\d+)', name)
            split_name = list(filter(None,split_name_raw)) #filters out the empty strings
            file_metadata.append(LabelPaths.convert_dtypes(split_name))
        return file_metadata

    @staticmethod
    def convert_dtypes(arr):
        converted = []
        for x in arr:
            if x.isdigit():
                converted.append(int(x))
            else:
                try:
                    converted.append(x.lower())
                except AttributeError:
                    converted.append(x)
        return converted

    def make_subjects(self, file_metadata):
        path_keys = [*self._valid_metadata_keys[:,1], 'path']
        num_fields_in_filename = len(self._metadata_keys_raw)
        Subject = namedtuple('Subject', path_keys)
        invalid_metadata = defaultdict(list)
        labeled_paths = []
        
        for path, metadata in zip(self._paths, file_metadata):
            if (_len := len(metadata) == num_fields_in_filename):
                filtered_data = [metadata[int(i)] for i in self._valid_metadata_keys[:,0]]
                '''
                if not isinstance(filtered_data[1], int):
                    print('invalid path: ', filtered_data, path)
                else:
                '''
                labeled_paths.append(Subject._make([*filtered_data, path]))
            else:
                invalid_metadata[_len].append([metadata, path])
        ### add error handling if invalid metadata
        return labeled_paths
    
    @staticmethod
    def filter_metadata_duplicates(paths):
        metadata = [x[:-1] for x in paths]
        index_container = defaultdict(list)
        for i, key in enumerate(metadata):
            index_container[key].append(i)
        filtered = [paths[indexes[0]] for _, indexes in index_container.items()]
        return filtered




