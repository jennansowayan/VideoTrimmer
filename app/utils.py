def is_valid_timestamp(text):
    import re
    pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    return pattern.match(text) is not None
