import os
import subprocess
import pandas as pd
from tqdm import tqdm

class FileOrganizer:
    def __init__(self, csv_file, source_dir, symlink_dir, final_export_dir):
        """
        Initializes the FileOrganizer.
        
        :param csv_file: Path to the CSV containing file paths and new hierarchy columns.
        :param source_dir: Original directory where files are located.
        :param symlink_dir: Directory where symlinked structure will be created.
        :param final_export_dir: Directory where real files will be copied using rsync.
        """
        self.csv_file = csv_file
        self.source_dir = source_dir.rstrip("/")
        self.symlink_dir = symlink_dir.rstrip("/")
        self.final_export_dir = final_export_dir.rstrip("/")
        self.df = pd.read_csv(csv_file)
        self.total_files = len(self.df)

    def create_symlinks(self):
        """
        Creates a structured directory with symlinks based on CSV data.
        """
        print("\n📁 Creating symlink structure...\n")
        
        for _, row in tqdm(self.df.iterrows(), total=self.total_files, desc="🔗 Creating symlinks"):
            original_path = os.path.join(self.source_dir, row["filepath"])
            
            # Construct the new path based on hierarchy columns
            new_path = os.path.join(self.symlink_dir, row["col1"], row["col2"], row["col3"], os.path.basename(original_path))

            # Ensure the directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            # Create the symlink
            if not os.path.exists(new_path):  # Avoid duplicate symlinks
                try:
                    os.symlink(original_path, new_path)
                except Exception as e:
                    print(f"⚠️ Error creating symlink for {original_path}: {e}")

    def run_rsync(self):
        """
        Runs rsync to copy the real files from the symlink structure.
        """
        print("\n🚀 Running rsync to copy real files...\n")

        rsync_cmd = [
            "rsync", "-av", "--copy-links",
            f"{self.symlink_dir}/", f"{self.final_export_dir}/"
        ]

        # Run rsync as a subprocess and track progress
        process = subprocess.Popen(rsync_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Count total symlinks (files to copy)
        total_symlinks = sum([len(files) for _, _, files in os.walk(self.symlink_dir)])

        with tqdm(total=total_symlinks, desc="📂 Copying files with rsync") as pbar:
            for line in iter(process.stdout.readline, ''):
                pbar.update(1)  # Increment tqdm progress bar
                print(line.strip())  # Print rsync output in real-time
        process.wait()

    def execute(self):
        """
        Full pipeline execution: create symlinks and run rsync.
        """
        self.create_symlinks()
        input("\n🔴 Press Enter to proceed with final rsync (this will copy actual files)...")
        self.run_rsync()
        print("\n✅ All files copied successfully! New structure is in:", self.final_export_dir)

if __name__ == "__main__":
    # Example usage
    organizer = FileOrganizer(
        csv_file="file_structure.csv",
        source_dir="/original_messy_data",
        symlink_dir="/organized_symlink_view",
        final_export_dir="/final_export"
    )
    organizer.execute()

