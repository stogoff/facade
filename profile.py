def calc_profile_length(height, st_len, weight=0):
    length = 6
    if weight > 500:
        length = height
    else:
        try:
            length = st_len / (st_len//height)
        except:
            pass
    return length
