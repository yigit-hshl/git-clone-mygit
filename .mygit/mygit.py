import os
import hashlib
import zlib

def init():
  # Create the base directory
  os.makedirs(".mygit/objects", exist_ok=True)
  os.makedirs(".mygit/refs/heads", exist_ok=True)
  
  # Initialize HEAD to point to the main branch
  with open("./mygit/HEAD", "w") as f:
    f.write("ref: refs/heads/main\n")
  
  print("Initialized empty MyGit repository in .mygit/")
  
# This function will take file data and return its unique "address."  
def hash_object(data, type="blob", write=True):
  # 1. Build the header
  header = f"{type} {len(data)}".encode()
  full_data = header + b"\0" + data
  
  # 2. Calculate the SHA-1 hash
  sha1 = hashlib.sha1(full_data).hexdigest()
  
  if write:
    # 3. Determine the path (e.g., objects/a1/b2c3d4...)
    # Why the sha1[:2]? > If you put 10,000 files in one folder, 
    # your operating system gets slow. Git splits them 
    # into 256 folders (00 through ff) based on the first two characters of 
    # the hash to keep things fast.
    path = os.path.join(".mygit/objects", sha1[:2], sha1[2:])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # 4. Compress and write
    with open(path, "wb") as f:
      f.write(zlib.compress(full_data))
    
    return sha1
  
# If we can write it, we must be able to read it. To "restore" a file, 
# we need to reverse the process: find the file, decompress it, 
# and strip the header.
def cat_file(sha1):
  path = os.path.join(".mygit/objects", sha1[:2], sha1[2:])
  with open(path, "rb") as f:
    # Decompress
    raw = zlib.decompress(f.read())
    
    # Split header and content at the null byte
    header, content = raw.split(b"\0", 1)
    return content.decode()