# git-clone-mygit

A custom implementation of Git's core functionality written in Python. This project replicates the internal mechanics of a distributed version control system, focusing on object storage, content-addressable filesystems, and history tracking.

## Understanding Git

Git is a distributed version control system (DVCS) designed to handle everything from small to very large projects with speed and efficiency. Unlike older VCS, Git thinks of its data more like a series of snapshots of a miniature filesystem. Every time you commit, or save the state of your project in Git, it basically takes a picture of what all your files look like at that moment and stores a reference to that snapshot.

### Core Components
- **Blob**: Stores file data.
- **Tree**: Represents a directory listing (mapping names to blobs or other trees).
- **Commit**: Contains metadata (author, message) and a pointer to a root tree.
- **Index**: The staging area where changes are prepared before a commit.

## Getting Started with mygit.py

The `mygit.py` script serves as the command-line interface for this repository. It mimics standard Git commands to manage your local development workflow.

### Common Commands

#### Initialize a Repository
Create the necessary directory structure (`.mygit`) to start tracking a project.
```bash
python mygit.py init
```

#### Stage Changes
Add specific files to the staging area (the index) to be included in the next commit.
```bash
python mygit.py add <filename>
```

#### Commit Changes
Create a new snapshot of the staged changes with a descriptive message.
```bash
python mygit.py commit -m "Your descriptive message"
```

#### View History
Display a log of all commits made in the current branch, showing hashes, authors, and messages.
```bash
python mygit.py log
```

#### Check Status
See which files have been modified, which are staged for commit, and which are currently untracked.
```bash
python mygit.py status
```

#### Inspect Objects
To view the contents of a specific object in the `.mygit/objects` directory using its SHA-1 hash:
```bash
python mygit.py cat-file -p <object_hash>
```

## Project Structure

- `mygit.py`: The main executable script containing the CLI logic and command routing.
- `.mygit/`: The internal database directory (created after `init`) containing:
    - `objects/`: Content-addressable storage for blobs, trees, and commits.
    - `refs/`: Pointers to commit objects (branches and tags).
    - `HEAD`: A reference to the currently checked-out branch or commit.

