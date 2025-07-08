#!/usr/bin/env python3
import os
import re
import subprocess
from datetime import datetime

def get_git_commit_date(file_path, version):
    """Get the date of the git commit that mentions the specified version for the given file."""
    try:
        # Use git log to find commits that mention updating the roadmap to the specified version
        # Try different patterns that might appear in commit messages
        patterns = [
            f"update.*roadmap.*version {version}",
            f"roadmap.*version {version}",
            f"version {version}",
            f"v{version}",
            f"update.*to.*{version}"
        ]

        for pattern in patterns:
            cmd = f"git log --follow --grep='{pattern}' -i -- {file_path} | grep 'Date:' | head -1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.stdout:
                # Extract the date from the git log output
                date_match = re.search(r'Date:\s+(.+)', result.stdout)
                if date_match:
                    date_str = date_match.group(1)
                    # Parse the git date format
                    date_obj = datetime.strptime(date_str.strip(), '%a %b %d %H:%M:%S %Y %z')
                    # Format the date as YYYY-MM-DD
                    return date_obj.strftime('%Y-%m-%d')

        # If no commit found with the patterns, try getting the most recent commit before the next version
        # This is a fallback approach
        file_basename = os.path.basename(file_path)
        match = re.search(r'roadmap_\w+_(\d+)\.md', file_basename)
        if match:
            current_version = int(match.group(1))
            if current_version > int(version):
                # If we're looking for an earlier version of the current file
                cmd = f"git log --follow -- {file_path} | grep 'Date:' | head -1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    date_match = re.search(r'Date:\s+(.+)', result.stdout)
                    if date_match:
                        date_str = date_match.group(1)
                        date_obj = datetime.strptime(date_str.strip(), '%a %b %d %H:%M:%S %Y %z')
                        return date_obj.strftime('%Y-%m-%d')

    except Exception as e:
        print(f"Error getting git commit date for {file_path} version {version}: {e}")

    return None

def update_roadmap_dates(file_path):
    """Update the dates in the roadmap file based on git commit dates."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract the version history section
        version_history_match = re.search(r'## Version History\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if not version_history_match:
            print(f"No version history section found in {file_path}")
            return False

        version_history = version_history_match.group(1)

        # Extract the version numbers and dates
        version_pattern = r'\| (\d+) \| (\d{4}-\d{2}-\d{2}) \| (.+?) \|'
        versions = re.findall(version_pattern, version_history)

        if not versions:
            print(f"No versions found in {file_path}")
            return False

        # Create a new version history with updated dates
        new_version_history = version_history
        updates_made = False

        # Special case for version 18 of roadmap_DesignUX_18.md
        file_basename = os.path.basename(file_path)
        is_roadmap_18 = file_basename == "roadmap_DesignUX_18.md"

        for version, old_date, changes in versions:
            # Special case for version 18 of roadmap_DesignUX_18.md
            if is_roadmap_18 and version == "18":
                # Get the date from the most recent commit
                cmd = f"git log --follow -- {file_path} | grep 'Date:' | head -1"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    date_match = re.search(r'Date:\s+(.+)', result.stdout)
                    if date_match:
                        date_str = date_match.group(1)
                        date_obj = datetime.strptime(date_str.strip(), '%a %b %d %H:%M:%S %Y %z')
                        git_date = date_obj.strftime('%Y-%m-%d')
                        if git_date != old_date:
                            new_version_history = new_version_history.replace(
                                f"| {version} | {old_date} |",
                                f"| {version} | {git_date} |"
                            )
                            print(f"Updated {file_path} version {version}: {old_date} -> {git_date}")
                            updates_made = True
                        continue

            # Get the git commit date for this version
            git_date = get_git_commit_date(file_path, version)

            if git_date and git_date != old_date:
                # Replace the old date with the git commit date
                new_version_history = new_version_history.replace(
                    f"| {version} | {old_date} |",
                    f"| {version} | {git_date} |"
                )
                print(f"Updated {file_path} version {version}: {old_date} -> {git_date}")
                updates_made = True

        if updates_made:
            # Replace the version history section in the content
            new_content = content.replace(version_history_match.group(0), f"## Version History\n{new_version_history}")

            # Write the updated content back to the file
            with open(file_path, 'w') as f:
                f.write(new_content)

            return True
        else:
            print(f"No updates needed for {file_path}")
            return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all roadmap files."""
    roadmap_dir = "docs/roadmaps/active"
    roadmap_files = [f for f in os.listdir(roadmap_dir) if f.startswith("roadmap_") and f.endswith(".md")]

    updated_files = 0
    for file_name in roadmap_files:
        file_path = os.path.join(roadmap_dir, file_name)
        print(f"Processing {file_path}...")
        if update_roadmap_dates(file_path):
            updated_files += 1

    print(f"Updated {updated_files} out of {len(roadmap_files)} roadmap files.")

if __name__ == "__main__":
    main()
