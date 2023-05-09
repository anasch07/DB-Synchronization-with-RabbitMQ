def float2(value): 
    try: return float(value if value and len(value) != 0 else "0")
    except ValueError: return 0


def int2(value): 
    try: return int(value if value and len(value) != 0 else "0")
    except ValueError: return 0
