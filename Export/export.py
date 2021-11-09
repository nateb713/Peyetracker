import pandas as pd
from ResultContainers.result_containers import create_result_paths


def export(result_dfs, user_input):

    result_paths = create_result_paths(user_input['output_directory_path'])
    behavior_data = pd.DataFrame()
    event_data = pd.DataFrame()
    movement_data = pd.DataFrame()
    test_tag = pd.DataFrame()

    if (behavior_cols := user_input['attach_behavior_cols']):
        behavior_data = check_columns(result_dfs['behavior_test'][behavior_cols])
    if (eye_movement_cols := user_input['attach_movement_cols']):
        movement_data = check_columns(result_dfs['eye_movements'][eye_movement_cols])
    if (event_cols := user_input['attach_event_cols']):
        event_data = check_columns(result_dfs['roi_event_map'][event_cols])
        event_data = event_data.reset_index()
    
    for tag, df in result_dfs.items():
        if (not df.empty) and (tag in result_paths.keys()):
            path = result_paths[tag]
            _export(df, path, movement_data, behavior_data,event_data, test_tag)

def _export(df, path, movement_data, behavior_data, event_data, test_tag):
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)

    df = check_columns(df)    
    if not movement_data.empty:
        if not any(x in str(path) for x in ['filtered_asc', 'fixation']):
            df = merge_dfs(df, movement_data)
    
    if not behavior_data.empty:
        if not 'behavior_test' in str(path):
            df = merge_dfs(df, behavior_data)
    
    if not test_tag.empty:
        if not 'test_tag' in str(path):
            df = merge_dfs(df, test_tag)
    if not event_data.empty:
        df = merge_dfs(df, event_data)
        
    try:
        df = df.applymap(str)
        
    except AttributeError:
        pass
    with open(path, 'w') as f:
        df.to_csv(f, header=True)


def check_columns(df):
    if 'level_0' in df.columns:
        df.drop(columns='level_0', inplace=True)
    return df

def merge_dfs(df1, df2): 
    try:
        df1.reset_index(inplace=True)
        df2.reset_index(inplace=True)
    except ValueError:
        pass
    common_cols = [df1_col for df1_col in df1.columns if any(
    df1_col == df2_col for df2_col in df2.columns)]
    
    merged = df1.merge(df2, on=common_cols, how='left')
    return merged