import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedStyle
import subprocess
import threading
import cv2
import os

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Converter")

        # Change theme to 'clam'
        style = ttk.Style()
        #style.theme_use('equilux')
        #root.resizable(1,1)
        root.resizable(0,0)
        style =ThemedStyle(root)
        style.set_theme('alt') 

        # Input Frame
        input_frame = ttk.Frame(root, padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  

        ttk.Label(input_frame, text="Input Video Files:").grid(row=0, column=0, sticky=tk.W)
        self.input_listbox = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, height=3)
        self.input_listbox.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Buttons for clearing the list and removing selected items
        ttk.Button(input_frame, text="Clear List", command=self.clear_list).grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(input_frame, text="Remove Selected", command=self.remove_selected).grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Button(input_frame, text="Add Videos", command=self.browse_input_files).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Rotate Video:").grid(row=2, column=0, sticky=tk.W)
        self.rotate_combobox = ttk.Combobox(input_frame, values=["0", "90 cw", "90 ccw", "180"], state="readonly")
        self.rotate_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.rotate_combobox.set("0")

        ttk.Label(input_frame, text="Codec:").grid(row=3, column=0, sticky=tk.W)
        self.codec_combobox = ttk.Combobox(input_frame, values=["h264", "hevc", "vp9"], state="readonly")
        self.codec_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
        self.codec_combobox.set("h264")

        ttk.Label(input_frame, text="Use GPU:").grid(row=4, column=0, sticky=tk.W)
        self.use_gpu_var = tk.BooleanVar()
        self.gpu_checkbox = ttk.Checkbutton(input_frame, variable=self.use_gpu_var, onvalue=True, offvalue=False)
        self.gpu_checkbox.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Trim Video (From - To hh:mm:ss):").grid(row=5, column=0, sticky=tk.W)
        self.trim_from_entry = ttk.Entry(input_frame, width=15)
        self.trim_from_entry.grid(row=5, column=1, padx=5, pady=5, sticky="nsew", columnspan=1)
        #self.trim_to_label = ttk.Label(input_frame, text="-")
        #self.trim_to_label.grid(row=5, column=3, padx=5, pady=5, sticky="nsew")
        self.trim_to_entry = ttk.Entry(input_frame, width=15)
        self.trim_to_entry.grid(row=5, column=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Bitrate (kb/s):").grid(row=6, column=0, sticky=tk.W)
        self.bitrate_entry = ttk.Entry(input_frame, width=15)
        self.bitrate_entry.grid(row=6, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Change Size:").grid(row=7, column=0, sticky=tk.W)
        self.size_combobox = ttk.Combobox(input_frame, values=["3840x2160", "1920x1080", "1280x720", "640x480"], state="readonly")
        self.size_combobox.grid(row=7, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Change Speed (e.g., 2 for 2x speed):").grid(row=8, column=0, sticky=tk.W)
        self.speed_entry = ttk.Entry(input_frame, width=15)
        self.speed_entry.grid(row=8, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Frame Rate:").grid(row=9, column=0, sticky=tk.W)
        self.frame_rate_entry = ttk.Entry(input_frame, width=15)
        self.frame_rate_entry.grid(row=9, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Frame Extraction Output Folder:").grid(row=10, column=0, sticky=tk.W)
        self.frame_extraction_entry = ttk.Entry(input_frame, width=30)
        self.frame_extraction_entry.grid(row=10, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Button(input_frame, text="Browse", command=self.browse_frame_extraction).grid(row=10, column=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Output Folder:").grid(row=11, column=0, sticky=tk.W)
        self.output_folder_entry = ttk.Entry(input_frame, width=30)
        self.output_folder_entry.grid(row=11, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Button(input_frame, text="Browse", command=self.browse_output_folder).grid(row=11, column=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(input_frame, text="Shutdown After Conversion:").grid(row=12, column=0, sticky=tk.W)
        self.shutdown_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, variable=self.shutdown_var, onvalue=True, offvalue=False).grid(row=12, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Button(input_frame, text="Convert Videos", command=self.convert_videos_threaded).grid(row=13, column=0, columnspan=2, pady=10, sticky="nsew")
        ttk.Button(input_frame, text="Combine All Files", command=self.combine_all_files).grid(row=13, column=2, pady=10, sticky="nsew")

        # Output Frame
        output_frame = ttk.Frame(root, padding="10")
        output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")  

        self.output_text = tk.Text(output_frame, height=10, width=50)
        self.output_text.grid(row=0, column=0, sticky="nsew")  

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        ttk.Label(output_frame, text="Progress:").grid(row=1, column=0, sticky=tk.W)
        ttk.Progressbar(output_frame, variable=self.progress_var, mode="determinate").grid(row=1, column=1, padx=5, pady=5, sticky="nsew")  

        # Set weight to make the columns and rows expandable
        for i in range(14):
            input_frame.columnconfigure(i, weight=1)
            input_frame.rowconfigure(i, weight=1)

        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

    def clear_list(self):
        self.input_listbox.delete(0, tk.END)

    def remove_selected(self):
        selected_indices = self.input_listbox.curselection()
        for index in reversed(selected_indices):
            self.input_listbox.delete(index)

    def browse_input_files(self):
        file_paths = filedialog.askopenfilenames(initialdir="/", title="Select Video Files", filetypes=[("Video files", "*.mp4;*.mkv;*.avi;*.webm;*.ts")])
        for file_path in file_paths:
            self.input_listbox.insert(tk.END, file_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(initialdir="/", title="Select Output Folder")
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, folder_path)

    def browse_frame_extraction(self):
        folder_path = filedialog.askdirectory(initialdir="/", title="Select Frame Extraction Output Folder")
        self.frame_extraction_entry.delete(0, tk.END)
        self.frame_extraction_entry.insert(0, folder_path)

    def convert_videos_threaded(self):
        # Start a new thread for video conversion
        threading.Thread(target=self.convert_videos).start()

    def convert_videos(self):
        input_files = self.input_listbox.get(0, tk.END)
        output_folder = self.output_folder_entry.get()
        codec = self.codec_combobox.get()
        use_gpu = self.use_gpu_var.get()
        trim_from = self.trim_from_entry.get()
        trim_to = self.trim_to_entry.get()
        bitrate = self.bitrate_entry.get()
        change_size = self.size_combobox.get()
        change_speed = self.speed_entry.get()
        rotate = self.rotate_combobox.get()
        frame_rate = self.frame_rate_entry.get()
        frame_extraction_folder = self.frame_extraction_entry.get()
        shutdown_after_conversion = self.shutdown_var.get()

        if not input_files or not output_folder:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please provide both input videos and output folder.")
            return

        # Wrap paths in double quotes to handle folder names with spaces
        output_folder = f'"{output_folder}"'
        frame_extraction_folder = f'"{frame_extraction_folder}"' if frame_extraction_folder else None

        # Reset progress bar
        self.progress_var.set(0)

        # Loop over input files and perform video conversion
        for i, input_file in enumerate(input_files):
            input_file = f'"{input_file}"'
            output_file_i = os.path.join(output_folder, os.path.basename(input_file))

            # Construct FFmpeg command
            ffmpeg_cmd_i = f"ffmpeg -i {input_file}"

            if use_gpu:
                ffmpeg_cmd_i += " -c:v h264_nvenc"  # Adjust based on the desired GPU codec

            if trim_from:
                ffmpeg_cmd_i += f" -ss {trim_from}"

            if trim_to:
                ffmpeg_cmd_i += f" -to {trim_to}"

            if bitrate:
                ffmpeg_cmd_i += f" -b:v {bitrate}k"

            if change_size:
                ffmpeg_cmd_i += f" -vf scale={change_size}"

            if change_speed:
                ffmpeg_cmd_i += f" -filter:v setpts={change_speed}*PTS"

            if rotate and rotate != "0":
                ffmpeg_cmd_i += f" -vf transpose={self.get_rotation_code(rotate)}"

            if frame_rate:
                ffmpeg_cmd_i += f" -r {frame_rate}"

            ffmpeg_cmd_i += f" -c:v {codec} {output_file_i}"

            # Execute the command using subprocess
            subprocess.run(ffmpeg_cmd_i, shell=True)

            # Update progress bar
            progress_percent = ((i + 1) / len(input_files)) * 100
            self.progress_var.set(progress_percent)

            # Extract frames if fps is provided and an output folder is selected
            if frame_extraction_folder:
                output_folder_i = os.path.join(frame_extraction_folder, f"video_{i}_frames")
                os.makedirs(output_folder_i, exist_ok=True)
                self.extract_frames(input_file, output_folder_i)

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Video conversion completed.")

        # Shutdown the PC if the option is selected
        if shutdown_after_conversion:
            subprocess.run(["shutdown", "/s", "/t", "1"])

    def get_rotation_code(self, rotate):
        if rotate == "90 cw":
            return "1"
        elif rotate == "90 ccw":
            return "2"
        elif rotate == "180":
            return "3"
        else:
            return "0"

    def extract_frames(self, input_path, output_folder):
        cap = cv2.VideoCapture(input_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = int(fps / 10)  # Extract 10 frames per second

        for i in range(0, frame_count, interval):
            ret, frame = cap.read()
            if not ret:
                break
            frame_path = os.path.join(output_folder, f"frame_{i}.jpg")
            cv2.imwrite(frame_path, frame)

        cap.release()

    def combine_all_files(self):
        # Combine all input files into a single output file
        input_files = self.input_listbox.get(0, tk.END)
        output_folder = self.output_folder_entry.get()

        if not input_files or not output_folder:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please provide both input videos and output folder.")
            return

        # Wrap paths in double quotes to handle folder names with spaces
        output_folder = f'"{output_folder}"'
        output_file = os.path.join(output_folder, "combined_output.mp4")

        # Construct FFmpeg command
        ffmpeg_cmd = f"ffmpeg -i \"concat:{'|'.join(input_files)}\" -c copy {output_file}"

        # Execute the command using subprocess
        subprocess.run(ffmpeg_cmd, shell=True)

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Video combination completed.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()
