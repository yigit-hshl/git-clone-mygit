import os

def init():
  # Create the base directory
  os.makedirs(".mygit/objects", exist_ok=True)
  os.makedirs(".mygit/refs/heads", exist_ok=True)
  
  # Initialize HEAD to point to the main branch
  with open("./mygit/HEAD", "w") as f:
    f.write("ref: refs/heads/main\n")
  
  print("Initialized empty MyGit repository in .mygit/")