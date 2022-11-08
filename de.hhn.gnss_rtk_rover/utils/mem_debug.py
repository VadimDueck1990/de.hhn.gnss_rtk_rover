import micropython
import gc


def debug_gc():
    print("================================================================")
    micropython.mem_info()
    gc.collect()
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
    micropython.mem_info()
    print("================================================================")
