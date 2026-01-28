import os # used in init(), write_tree() and cat_file()
import hashlib # used in hash_object()
import zlib # used in hash_object()
import time # used in commit()
import json # used in add()
import difflib # used in diff()

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
    ref_path = get_head_ref()
    parent_sha = None 
    if os.path.exists(ref_path):
      with open(ref_path, "r") as f:
        parent_sha = f.read().strip()

    # 3. Build the commit content
    commit_lines = [f"tree {tree_sha}"] 
    if parent_sha: 
      commit_lines.append(f"parent {parent_sha}") 
    
    commit_lines.append(f"author {author} <{author}@example.com> {int(time.time())} +0000") 
    commit_lines.append("")
    commit_lines.append(message)

    # 4. Hash and save the commit
    commit_sha = hash_object("\n".join(commit_lines).encode(), type="commit")

    # 5. Update the branch pointer (e.g., main) to this new commit
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, "w") as f:
      f.write(commit_sha)
    print(f"[{os.path.basename(ref_path)}] {commit_sha[:7]} - {message}")
    return commit_sha

"""
To make this a functional version control system, we need to stop just printing hashes and start storing them. 
This is where Refs (References) come in.

In Git, a branch is not a complex data structure; 
it is literally just a tiny text file that contains a 40-character SHA-1 hash. 
That’s it. When you make a new commit, you just overwrite that text file with the new hash.
"""
def get_head_ref():
  # Returns the path to the current branch file (e.g., .mygit/refs/heads/main)
  with open(".mygit/HEAD", "r") as f:
    content = f.read().strip() # Remove whitespace
  if content.startswith("ref: "): # Check if HEAD points to a branch
    return os.path.join(".mygit", content[5:]) # Return the branch file path
  return None # Return None if HEAD points to a commit

# =====================================
# ===== Show commit history (log) =====
# =====================================
def log():
  # Start at the current branch's latest commit
  ref_path = get_head_ref()
  if not os.path.exists(ref_path):
    print("No commits yet.")
    return 
  
  with open(ref_path, "r") as f:
    current_sha = f.read().strip()
  
  while current_sha:
    # Read the commit object
    content = cat_file(current_sha)
    print("-" * 20) 
    print(f"commit {current_sha}")

    # Parse the commit content to find the parent
    parent_sha = None # Initialize parent SHA
    lines = content.splitlines() # Split the commit content into lines
    for line in lines:
      if line.startswith("parent "): # Check if the line starts with "parent "
        parent_sha = line[7:] # Get the parent SHA
      if line == "": # End of header, start of message
        print(f"Message: {lines[lines.index(line) + 1:]}")
        break
    
    # Move to the previous commit
    current_sha = parent_sha

"""
Instead of committing everything, the add command copies files into the index. 
When you finally call commit, Git doesn't look at your folders; it only looks at the Index.
"""
# ========================================
# ===== Add files to the index (add) =====
# ========================================
def add(filename):
  # 1. Read the file and create a blob
  if not os.path.exists(filename):
    print(f"File {filename} not found.")
    return
  
  with open(filename, "rb") as f:
    sha1 = hash_object(f.read(), type="blob")
  
  # 2. Load the current index
  index = {}
  index_path = ".mygit/index"
  if os.path.exists(index_path):
    with open(index_path, "r") as f: 
      index = json.load(f) 
  
  # 3. Update the index with the filename and its blob hash
  index[filename] = sha1 # Add the file to the index

  # 4. Save the index back
  with open(index_path, "w") as f:
    json.dump(index, f) 
  
  print(f"Staged {filename}") 

def write_tree_from_index():
  index_path = ".mygit/index"
  if not os.path.exists(index_path):
    return None
  
  with open(index_path, "r") as f:
    index = json.load(f)

  entries = []
  for path, sha1 in sorted(index.items()):
    # For simplicity, we assume all staged files are blobs in the root
    entries.append(f"100644 blob {sha1}\t{path}")
  
  tree_content = "\n".join(entries).encode()
  return hash_object(tree_content, type="tree")

# ========================================
# ===== Checkout a commit (checkout) =====
# ========================================
def checkout(commit_sha):
  # 1. Read the commit to find its tree
  commit_content = cat_file(commit_sha)
  tree_sha = None
  for line in commit_content.splitlines():
    if line.startswith("tree "):
      tree_sha = line[5:]
      break
  
  # 2. Read the tree
  tree_content = cat_file(tree_sha)

  # 3. For each entry in the tree, overwrite the file on disk
  for line in tree_content.splitlines():
    # Format: mode type sha\tname
    parts = line.split()
    sha = parts[2]
    name = parts[3]

    blob_content = cat_file(sha)
    with open(name, "w") as f:
      f.write(blob_content)
    
    print(f"Checked out files from commit {commit_sha[:7]}")

# ================================
# ===== Show status (status) =====
# ================================
def status():
  # 1. Get staged files (Index)
  index = {}
  if os.path.exists(".mygit/index"):
    with open(".mygit/index", "r") as f:
      index = json.load(f)
  
  # 2. Get files in Working Directory
  working_files = [f for f in os.listdir('.') if os.path.isfile(f) and f != "mygit.py"]

  print(f"On branch: {get_head_ref().split('/')[-1]}")
  print("\nStaged files:")
  for f in index:
    print(f" (staged) {f}")
  
  print("\nUntracked files:")
  for f in working_files:
    if f not in index:
      print(f" (untracked) {f}")

# ========================================
# ===== Create a new branch (branch) =====
# ========================================
def create_branch(name):
  # 1. Get the current commit hash from the current branch
  current_ref = get_head_ref()
  with open(current_ref, "r") as f:
    current_sha = f.read().strip()
  
  # 2. Create a new ref file with that same hash
  new_ref_path = f".mygit/refs/heads/{name}"
  with open(new_ref_path, "w") as f:
    f.write(current_sha)
  
  print(f"Branch '{name}' created at {current_sha[:7]}")

# ============================
# ===== Show diff (diff) =====
# ============================
def diff(filename):
  # 1. Get the staged version from the index
  with open(".mygit/index", "r") as f:
    index = json.load(f)

  if filename not in index:
    print(f"{filename} is not staged.")
    return

  staged_sha = index[filename]
  staged_content = cat_file(staged_sha).splitlines()

  # 2. Get the current working directory version
  with open(filename, "r") as f:
    current_content = f.read().splitlines()

  # 3. Use Python's built-in difflib to show changes
  result = difflib.unified_diff(
    staged_content,
    current_content,
    fromfile="staged",
    tofile="working"
  )

  for line in result:
    print(line)

# =======================================
# ===== Remove file from index (rm) =====
# =======================================
def rm(filename):
  if os.path.exists(".mygit/index"):
    with open(".mygit/index", "r") as f:
      index = json.load(f)
    
    if filename in index:
      del index[filename]
      with open(".mygit/index", "w") as f:
        json.dump(index, f)
      print(f"Unstaged {filename} from index.")