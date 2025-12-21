
import time
import os
import threading
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MONITOR_PATH = '/mnt/nas/Music/imports'

import subprocess


class MusicEventHandler(FileSystemEventHandler):
    def __init__(self, import_queue):
        super().__init__()
        self.import_queue = import_queue

    def on_created(self, event):
        if event.is_directory:
            print(f"New folder detected: {event.src_path}")
            self.import_queue.put(event.src_path)
        else:
            print(f"New file detected: {event.src_path}")
            abs_monitor_path = os.path.abspath(MONITOR_PATH)
            abs_file_path = os.path.abspath(event.src_path)
            rel_path = os.path.relpath(abs_file_path, abs_monitor_path)
            first_part = rel_path.split(os.sep)[0]
            immediate_subfolder = os.path.join(abs_monitor_path, first_part)
            print(f"Importing immediate subfolder: {immediate_subfolder}")
            self.import_queue.put(immediate_subfolder)

def import_worker(import_queue):
    while True:
        folder_path = import_queue.get()
        if folder_path is None:
            break
        music_source = os.path.basename(folder_path)
        print(f"Importing {folder_path} with music_source={music_source}")
        try:
            subprocess.run([
                'beet', 'import', '-A', '-y', '--set', f'music_source={music_source}', folder_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error importing {folder_path}: {e}")
        import_queue.task_done()


def main():
    import_queue = queue.Queue()
    worker_thread = threading.Thread(target=import_worker, args=(import_queue,), daemon=True)
    worker_thread.start()

    event_handler = MusicEventHandler(import_queue)
    print(f"Scanning for existing subfolders in {MONITOR_PATH}...")
    for entry in os.scandir(MONITOR_PATH):
        if entry.is_dir():
            print(f"Found existing folder: {entry.path}")
            import_queue.put(entry.path)

    observer = Observer()
    observer.schedule(event_handler, MONITOR_PATH, recursive=True)
    observer.start()
    print(f"Monitoring {MONITOR_PATH} for new files and folders...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        import_queue.put(None)
    observer.join()
    worker_thread.join()

if __name__ == "__main__":
    main()
