def str_time_to_seconds(time_str):
    '''
    Converts time in str '1m5.583s' or '7.66s' to seconds as a float.
    '''
    minutes = 0
    seconds = 0
    
    if 'm' in time_str:
        minutes_part, time_str = time_str.split('m')
        minutes = int(minutes_part)
    
    if 's' in time_str:
        seconds = float(time_str.replace('s', ''))
    
    return minutes * 60 + seconds