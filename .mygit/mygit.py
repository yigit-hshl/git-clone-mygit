import os # used in init(), write_tree() and cat_file()
import hashlib # used in hash_object()
import zlib # used in hash_object()
import time # used in commit()

# ========================================
# ===== Initialize a database (init) =====
# ========================================
def init():
  # Create the base directory
  os.makedirs(".mygit/objects", exist_ok=True) # Create the objects directory
  os.makedirs(".mygit/refs/heads", exist_ok=True) # Create the refs/heads directory
  
  # Initialize HEAD to point to the main branch
  with open(".mygit/HEAD", "w") as f: # Open the HEAD file
    f.write("ref: refs/heads/main\n") # Write the main branch to the HEAD file
  
  print("Initialized empty MyGit repository in .mygit/")
  
# ================================================
# ===== Snapshot file contents (hash_object) =====
# ================================================
def hash_object(data, type="blob", write=True):
  # 1. Build the header
  header = f"{type} {len(data)}".encode() # Build the header
  full_data = header + b"\0" + data # Add the null byte
  
  # 2. Calculate the SHA-1 hash
  sha1 = hashlib.sha1(full_data).hexdigest() # Calculate the SHA-1 hash
  
  if write:
    # 3. Determine the path (e.g., objects/a1/b2c3d4...)
    # Why the sha1[:2]? > If you put 10,000 files in one folder, 
    # your operating system gets slow. Git splits them 
    # into 256 folders (00 through ff) based on the first two characters of 
    # the hash to keep things fast.
    path = os.path.join(".mygit/objects", sha1[:2], sha1[2:])
    os.makedirs(os.path.dirname(path), exist_ok=True) # Create the directory
    
    # 4. Compress and write
    with open(path, "wb") as f:
      f.write(zlib.compress(full_data)) # Compress and write
    
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
  
# ===================================================
# ===== Map file names to contents (write_tree) =====
# ===================================================
# This function scans your current directory and 
# creates a Tree object in your .mygit/objects folder.
def write_tree(directory="."): # Default to current directory
  entries = [] # List of entries
  
  # Walk through files in the current directory
  for entry in sorted(os.listdir(directory)):
    if entry == ".mygit": # Skip .mygit directory
      continue
    
    full_path = os.path.join(directory, entry) 
    
    if os.path.isfile(full_path):
      with open(full_path, "rb") as f: 
        sha1 = hash_object(f.read(), type="blob") # Hash the file
      # Format: mode, type, sha, name
      entries.append(f"100644 blob {sha1}\t{entry}") # Add the file to the tree
    elif os.path.isdir(full_path):
      # Recursion! A directory becomes a sub-tree
      sha1 = write_tree(full_path)
      entries.append(f"040000 tree {sha1}\t{entry}") # Add the directory to the tree
      
  # Join entries and hash the tree itself
  tree_content = "\n".join(entries).encode() # Join entries and encode
  return hash_object(tree_content, type="tree") # Hash the tree

# ==========================================================
# ===== Link snapshots together with metadata (commit) =====
# ==========================================================
def commit(message, author="User"): # Default to current user
    # 1. Get the current state of the directory as a Tree
    tree_sha = write_tree() # Get the tree SHA

    # 2. Get the parent SHA (from HEAD)
    parent_sha = None 
    head_path = ".mygit/HEAD"
    # (Simplified logic: in real Git, HEAD points to a branch file)

    # 3. Build the commit content
    commit_lines = [f"tree {tree_sha}"] 
    if parent_sha: 
      commit_lines.append(f"parent {parent_sha}") 
    
    commit_lines.append(f"author {author} <{author}@example.com> {int(time.time())} +0000") 
    commit_lines.append("")
    commit_lines.append(message)

    commit_content = "\n".join(commit_lines).encode() 

    # 4. Hash and save the commit
    commit_sha = hash_object(commit_content, type="commit")

    # 5. Update the branch pointer (e.g., main) to this new commit
    # For now, we'll just print it
    print(f"Created commit: {commit_sha}")
    return commit_sha