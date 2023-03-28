from enum import Flag, auto

class Disposition(Flag):
    NONE        = 0
    FLAT_1KK    = auto() # 1kk
    FLAT_1      = auto() # 1+1
    FLAT_2KK    = auto() # 2kk
    FLAT_2      = auto() # 2+1
    FLAT_3KK    = auto() # 3kk
    FLAT_3      = auto() # 3+1
    FLAT_4KK    = auto() # 4kk
    FLAT_4      = auto() # 4+1
    FLAT_5_UP   = auto() # 5+
    FLAT_OTHERS = auto() # others
