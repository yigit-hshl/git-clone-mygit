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
  
def hash_object(data, type="blob", write=True):
  # 1. Build the header
  header = f"{type} {len(data)}".encode()
  full_data = header + b"\0" + data
  
  # 2. Calculate the SHA-1 hash
  sha1 = hashlib.sha1(full_data).hexdigest()
  
  if write:
    # 3. Determine the path (e.g., objects/a1/b2c3d4...)
    path = os.path.join(".mygit/objects", sha1[:2], sha1[2:])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # 4. Compress and write
    with open(path, "wb") as f:
      f.write(zlib.compress(full_data))
    
    return sha1