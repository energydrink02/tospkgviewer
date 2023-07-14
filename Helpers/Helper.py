import math

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KiB", "MiB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return f"{s} {size_name[i]}"

def Padding(num, pad):
    return 0 if (num % pad) == 0 else pad - (num % pad)