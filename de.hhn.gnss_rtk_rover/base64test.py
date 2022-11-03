import micropython
import gc
print("imported micropython, gc")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

# import employee_instance
# micropython.mem_info()
# gc.mem_free()
# gc.mem_alloc()
import gnss.uart_reader
print("imported uart_reader")
gc.collect()
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

