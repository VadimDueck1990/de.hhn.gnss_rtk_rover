import micropython
import gc

import gnss.gnssntripclient
print("imported pyubx2.ubxmessage")
gc.collect()
micropython.mem_info(1)
gc.mem_free()
gc.mem_alloc()

