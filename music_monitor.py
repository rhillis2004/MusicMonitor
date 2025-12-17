import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MONITOR_PATH = '/mnt/nas/Music/imports'

import subprocess

class MusicEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            print(f"New folder detected: {event.src_path}")
            self.import_with_beets(event.src_path)
        else:
            print(f"New file detected: {event.src_path}")
            # Find the immediate subfolder of MONITOR_PATH containing the file
            abs_monitor_path = os.path.abspath(MONITOR_PATH)
            abs_file_path = os.path.abspath(event.src_path)
            rel_path = os.path.relpath(abs_file_path, abs_monitor_path)
            # The first part of rel_path is the immediate subfolder
            first_part = rel_path.split(os.sep)[0]
            immediate_subfolder = os.path.join(abs_monitor_path, first_part)
            print(f"Importing immediate subfolder: {immediate_subfolder}")
            self.import_with_beets(immediate_subfolder)

    def import_with_beets(self, folder_path):
        # Use the last part of the folder path as music_source
        music_source = os.path.basename(folder_path)
        print(f"Importing {folder_path} with music_source={music_source}")
        # Call beets import with -A and set music_source
        # Assumes beets is configured to accept music_source as a flexible attribute
        try:
            subprocess.run([
                'beet', 'import', '-A', '--set', f'music_source={music_source}', folder_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error importing {folder_path}: {e}")

def main():
    event_handler = MusicEventHandler()
    # Scan for existing subfolders and import them
    print(f"Scanning for existing subfolders in {MONITOR_PATH}...")
    for entry in os.scandir(MONITOR_PATH):
        if entry.is_dir():
            print(f"Found existing folder: {entry.path}")
            event_handler.import_with_beets(entry.path)

    observer = Observer()
    observer.schedule(event_handler, MONITOR_PATH, recursive=True)
    observer.start()
    print(f"Monitoring {MONITOR_PATH} for new files and folders...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
