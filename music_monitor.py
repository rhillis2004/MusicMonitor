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
            parent_folder = os.path.dirname(event.src_path)
            self.import_with_beets(parent_folder)

    def import_with_beets(self, folder_path):
        # Use the last part of the folder path as music_source
        music_source = os.path.basename(folder_path)
        print(f"Importing {folder_path} with music_source={music_source}")
        # Call beets import with -A and set music_source
        # Assumes beets is configured to accept music_source as a flexible attribute
        try:
            subprocess.run([
                'beet', 'import', '-A', f'-c', f'music_source={music_source}', folder_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error importing {folder_path}: {e}")

def main():
    event_handler = MusicEventHandler()
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
