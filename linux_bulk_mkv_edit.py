#!/usr/bin/python3
"""
Application:  linux_bulk_mkv_edit.py
Version:  1.2
Author:  BSFEMA
Started:  2022-05-14
Prerequisites:  You need to have MKVToolNix installed:  https://mkvtoolnix.download/downloads.html
                Try running "mkvmerge --version" in terminal
                If that works, then you are good to go, otherwise install MKVToolNix
Command Line Parameters:  There is just 1:
                          It is the folder path that will be used to start looking at the *.mkv files from.
                          If this value isn't provided, then the starting path will be where this application file is located.
                          The intention is that you can call this application from a context menu from a file browser (e.g. Nemo) and it would automatically load up that folder.
Purpose:  I couldn't find a good tool for bulk editing audio and subtitles in mkv files on Linux, so I decided to make my own.
          This currently only includes track languages that you choose or parts of the track names you choose.
          This will not perform the conversion, but will spit out the command lines necessary to do the conversions.
          Simply copy the command lines into a terminal and away it goes.
Resources:  https://mkvtoolnix.download/doc/mkvextract.html
"""


from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sys
import os
import subprocess
import json

root = Tk()
top_frame = Frame(root)
audio_frame = Frame(root)
subtitle_frame = Frame(root)
label_al = ""
label_sl = ""
label_al_text = "Audio Langs (list)"
label_sl_text = "Subtitle Langs (list)"
entry_al = ""
entry_an = ""
entry_sl = ""
entry_st = ""
entry_sn = ""
bottom_frame = Frame(root)
tree = ""
vsb = ""
default_folder_path = ""  # The path for this application to run against.
files = {}  # A list of files in the 'default_folder_path' to run against = The json data for the mkv object's information.
video_tracks = {}  # A list of the files and the video tracks
audio_tracks = {}  # A list of the files and the audio tracks
subtitle_tracks = {}  # A list of the files and the subtitle tracks
audio_langs = []  # A list of the unique landuages for the audio tracks
subtitle_langs = []  # A list of the unique landuages for the subtitle tracks
command_lines = {}  # The full list of command lines, or the output of this application


def populate_tree():
    global root
    global tree
    global files
    global video_tracks
    global audio_tracks
    global subtitle_tracks
    global audio_langs
    global subtitle_langs
    global label_al_text
    global label_sl_text
    global entry_al_text
    global entry_sl_text
    global lebal_al
    global label_sl
    global entry_al
    global entry_sl
    root.config(cursor="watch")  # Set the cursor to a 'watch' icon while everything is loading
    root.update()
    clear_tree()  # Start with fresh grid
    get_files()  # Re-build file list
    max_file = 0
    max_audio = 0
    max_subtitle = 0
    for file in files:
        audio = ""
        for track in audio_tracks[file]:
            name = str(audio_tracks[file][track]["track_name"])
            if name == "":
                if len(audio) > 0:
                    audio = audio + ",  " + str(track) + "-" + str(audio_tracks[file][track]["track_lang"]) + " (" + str(audio_tracks[file][track]["track_type"]) + ")"
                else:
                    audio = audio + str(track) + "-" + str(audio_tracks[file][track]["track_lang"]) + " (" + str(audio_tracks[file][track]["track_type"]) + ")"
            else:
                if len(audio) > 0:
                    audio = audio + ",  " + str(track) + "-" + str(audio_tracks[file][track]["track_lang"]) + " ('" + str(name) + "' " + str(audio_tracks[file][track]["track_type"]) + ")"
                else:
                    audio = audio + str(track) + "-" + str(audio_tracks[file][track]["track_lang"]) + " ('" + str(name) + "' " + str(audio_tracks[file][track]["track_type"]) + ")"
        subtitle = ""
        for track in subtitle_tracks[file]:
            name = str(subtitle_tracks[file][track]["track_name"])
            if name == "":
                if len(subtitle) > 0:
                    subtitle = subtitle + ",  " + str(track) + "-" + str(subtitle_tracks[file][track]["track_lang"]) + " (" + str(subtitle_tracks[file][track]["track_type"]) + ")"
                else:
                    subtitle = subtitle + str(track) + "-" + str(subtitle_tracks[file][track]["track_lang"]) + " (" + str(subtitle_tracks[file][track]["track_type"]) + ")"
            else:
                if len(subtitle) > 0:
                    subtitle = subtitle + ",  " + str(track) + "-" + str(subtitle_tracks[file][track]["track_lang"]) + " ('" + str(name) + "' " + str(subtitle_tracks[file][track]["track_type"]) + ")"
                else:
                    subtitle = subtitle + str(track) + "-" + str(subtitle_tracks[file][track]["track_lang"]) + " ('" + str(name) + "' " + str(subtitle_tracks[file][track]["track_type"]) + ")"
        if len(file) > max_file:
            max_file = len(file)
        if len(audio) > max_audio:
            max_audio = len(audio)
        if len(subtitle) > max_subtitle:
            max_subtitle = len(subtitle)
        tree.insert("", 'end', text="L1", values=(str(file), audio, subtitle))
    tree.column("1", width=max_file * 7)  # NOTE:  You may need to play adound with this integer such that the column widths are displaying the fill texts.  For me '7' is good.
    tree.column("2", width=max_audio * 7)  # NOTE:  You may need to play adound with this integer such that the column widths are displaying the fill texts.  For me '7' is good.
    tree.column("3", width=max_subtitle * 7)  # NOTE:  You may need to play adound with this integer such that the column widths are displaying the fill texts.  For me '7' is good.
    # Update the label and entrty fields
    temp = ""
    audio_langs.sort()
    for element in audio_langs:
        if len(temp) == 0:
            temp = element
        else:
            temp = temp + ", " + element
    label_al_text = "Audio Langs (" + temp + ")"
    label_al.configure(text=label_al_text)
    label_al.update()
    entry_al.insert(END, temp)
    entry_al.pack()
    temp = ""
    subtitle_langs.sort()
    for element in subtitle_langs:
        if len(temp) == 0:
            temp = element
        else:
            temp = temp + ", " + element
    label_sl_text = "Subtitle Langs (" + temp + ")"
    label_sl.configure(text=label_sl_text)
    label_sl.update()
    entry_sl.insert(END, temp)
    entry_sl.pack()
    root.config(cursor="")  # Set cursor back to nothing now that it is done loading
    root.update()


def clear_tree():
    global tree
    global entry_al
    global entry_an
    global entry_sl
    global entry_st
    global entry_sn
    for row in tree.get_children():
        tree.delete(row)
    entry_al.delete(0, 'end')
    entry_an.delete(0, 'end')
    entry_sl.delete(0, 'end')
    entry_st.delete(0, 'end')
    entry_sn.delete(0, 'end')



def process_files():
    global default_folder_path
    global files
    global video_tracks
    global audio_tracks
    global subtitle_tracks
    global entry_al
    global entry_an
    global entry_sl
    global entry_st
    global entry_sn
    global command_lines
    # print(str("entry_al=" + entry_al.get()))
    # print(str("entry_an=" + entry_an.get()))
    # print(str("entry_sl=" + entry_sl.get()))
    # print(str("entry_st=" + entry_st.get()))
    # print(str("entry_sn=" + entry_sn.get()))
    command_lines.clear()
    command_lines = {}
    # Audio Lang
    al = ""
    if len(entry_al.get()) != 0:
        if ',' in entry_al.get():
           al = entry_al.get().split(',')
           count = 0
           for lang in al:
               lang = lang.strip()
               if len(lang) == 0:
                   al.pop(count)
               count = count +1
        else:
            al = entry_al.get().strip()
    # print("al=" + str(al))
    # Audio Name
    an = ""
    if len(entry_an.get()) != 0:
        an = entry_an.get().strip()
    # print("an=" + str(an))    # Make the full paths for the new/old file names
    # Subtitle Lang
    sl = ""
    if len(entry_sl.get()) != 0:
        if ',' in entry_sl.get():
           sl = entry_sl.get().split(',')
           count = 0
           for lang in sl:
               lang = lang.strip()
               if len(lang) == 0:
                   sl.pop(count)
               count = count +1
        else:
            sl = entry_sl.get().strip()
    # print("sl=" + str(sl))
    # Subtitle Type
    st = ""
    if len(entry_st.get()) != 0:
        st = entry_st.get().strip()
    # print("st=" + str(st))
    # Subtitle Name
    sn = ""
    if len(entry_sn.get()) != 0:
        sn = entry_sn.get().strip()
    # print("sn=" + str(sn))
    # Build parameters
    for file in files:
        # Get full paths for the original and new filenames
        if default_folder_path == "":
            new_filename = file[0:-4] + " (1)" + file[-4:]
        else:
            filename_append = 1
            while True:  # check to make sure you are saving it to a new file that doesn't exist, increment the " (#)" counter
                if os.path.exists(default_folder_path + "/" + file[0:-4] + " (" + str(filename_append) + ")" + file[-4:]):
                    filename_append = filename_append + 1
                else:
                    break
            new_filename = default_folder_path + "/" + file[0:-4] + " (" +str(filename_append) + ")" + file[-4:]
            orig_filename = default_folder_path + "/" + file
        if "'" in orig_filename:
            orig_filename = orig_filename.replace("'","'\\''")
        if "'" in new_filename:
            new_filename = new_filename.replace("'","'\\''")
        # Make a temp copy of the file, then start removing the various tracks
        keep_audio = {}
        keep_subtitle = {}
        # Audio Lang
        temp_audio = {}
        for track in audio_tracks[file]:
            if audio_tracks[file][track]["track_lang"] in str(al):
                temp_audio[track] = audio_tracks[file][track]
        keep_audio = temp_audio
        # Audio Name
        if len(an) > 0:
            temp_audio = {}
            for track in keep_audio:
                if str(an).upper() in keep_audio[track]["track_name"].upper():
                    temp_audio[track] = keep_audio[track]
            keep_audio = temp_audio
        # Subtitle Lang
        temp_subtitle = {}
        for track in subtitle_tracks[file]:
            if subtitle_tracks[file][track]["track_lang"] in str(sl):
                temp_subtitle[track] = subtitle_tracks[file][track]
        keep_subtitle = temp_subtitle
        # Subtitle Type
        if len(st) > 0:
            temp_subtitle = {}
            for track in keep_subtitle:
                if str(st).upper() in keep_subtitle[track]["track_type"].upper():
                    temp_subtitle[track] = keep_subtitle[track]
            keep_subtitle = temp_subtitle
        # Subtitle Name
        if len(sn) > 0:
            temp_subtitle = {}
            for track in keep_subtitle:
                if str(sn).upper() in keep_subtitle[track]["track_name"].upper():
                    temp_subtitle[track] = keep_subtitle[track]
            keep_subtitle = temp_subtitle
        # Build the track options based on the remaining tracks
        """
        Example:
        /usr/bin/mkvmerge --ui-language en_US --output 'test (1).mkv'
        --audio-tracks 2
        --subtitle-tracks 4
        --language 0:und
        --display-dimensions 0:1280x720
        --language 1:en
        --track-name '1:Test .ac3 file'
        --language 2:ja
        --track-name 2:Something
        --language 3:und
        --track-name 3:OGG
        --sub-charset 4:UTF-8
        --language 4:ja
        --track-name '4:[Random_Name]'
        --sub-charset 5:UTF-8
        --language 5:en
        --track-name '5:A to the double S'
        '(' test.mkv ')'
         --title ""  # If you blank out the title, then it defaults to the filename
        --track-order 0:0,0:1,0:2,0:3,0:4,0:5
        """
        command = "/usr/bin/mkvmerge --ui-language en_US --output '" + str(new_filename) + "'"
        track_order = ""
        # Pre-Stuff
        audio_tracks_used = ""
        if len(keep_audio) != len(audio_tracks[file]):
            for track in keep_audio:
                if len(audio_tracks_used) == 0:
                    audio_tracks_used = "--audio-tracks " + str(track)
                else:
                    audio_tracks_used = audio_tracks_used + "," + str(track)
            command = command + " " + audio_tracks_used
        subtitle_tracks_used = ""
        if len(keep_subtitle) != len(subtitle_tracks[file]):
            for track in keep_subtitle:
                if len(subtitle_tracks_used) == 0:
                    subtitle_tracks_used = "--subtitle-tracks " + str(track)
                else:
                    subtitle_tracks_used = subtitle_tracks_used + "," + str(track)
            command = command + " " + subtitle_tracks_used
        # Vidio tracks
        for track in video_tracks[file]:
            if len(track_order) == 0:
                track_order = track_order + "0:" + str(track)
            else:
                track_order = track_order + ",0:" + str(track)
            command = command + " " + "--language " + str(track) + ":" + video_tracks[file][track]["track_lang"]
            command = command + " " + "--track-name '" + str(track) + ":" + video_tracks[file][track]["track_name"] + "'"
            command = command + " " + "--display-dimensions " + str(track) + ":" + video_tracks[file][track]["track_disdim"]
        # Audio tracks
        for track in keep_audio:
            if len(track_order) == 0:
                track_order = track_order + "0:" + str(track)
            else:
                track_order = track_order + ",0:" + str(track)
            command = command + " " + "--language " + str(track) + ":" + keep_audio[track]["track_lang"]
            command = command + " " + "--track-name '" + str(track) + ":" + keep_audio[track]["track_name"] + "'"
            if len(keep_sudio) == 1:  # If there is only 1 track, then set it as default
                command = command + " " + "--default-track-flag " + str(track) + ":yes"
        # Subtitle Tracks
        for track in keep_subtitle:
            if len(track_order) == 0:
                track_order = track_order + "0:" + str(track)
            else:
                track_order = track_order + ",0:" + str(track)
            command = command + " " + "--sub-charset " + str(track) + ":" + keep_subtitle[track]["track_encode"]
            command = command + " " + "--language " + str(track) + ":" + keep_subtitle[track]["track_lang"]
            command = command + " " + "--track-name '" + str(track) + ":" + keep_subtitle[track]["track_name"] + "'"
            if len(keep_subtitle) == 1:  # If there is only 1 track, then set it as default
                command = command + " " + "--default-track-flag " + str(track) + ":yes"
        command = command + " " + "'(' '" + orig_filename + "' ')' --title \"\" --track-order " + str(track_order)
        command_lines[file] = command
        # print(str(command))
    display_commands()


def display_commands():
    global command_lines
    # Populate output on screen
    output = ""
    max_command = 0
    command_count = 0
    lines = 0
    for command in command_lines:
        command_count = command_count + 1
        if len(command_lines[command]) > max_command:
            max_command = len(command_lines[command])
        if len(command_lines[command]) > 400:
            if len(command_lines[command]) > 1200:
                lines = lines + 3
            elif len(command_lines[command]) > 800:
                lines = lines + 2
            else:
                lines = lines + 1
        output = output + command_lines[command] + "\n"
    # Create GUI
    popup = Toplevel()
    popup.wm_title("Command Line Output")
    popup_top_frame = Frame(popup)
    popup_bottom_frame = Frame(popup)
    popup_top_frame.pack(side=TOP, fill="both", expand=True)
    popup_bottom_frame.pack(side=BOTTOM)
    if max_command > 400:
        t_output = Text(popup_top_frame, height=command_count + lines + 2, width=(400))
    else:
        t_output = Text(popup_top_frame, height=command_count + lines + 2, width=(max_command * 3))
    t_scroll = Scrollbar(popup_top_frame)
    t_output.pack(side=LEFT, expand=True, fill=BOTH)
    t_scroll.pack(side=RIGHT, fill=Y)
    t_scroll.config(command=t_output.yview)
    t_output.config(yscrollcommand=t_scroll.set)
    b_copy = Button(popup_bottom_frame, text="Copy Output to Clipboard", fg="blue", command=copy_to_clipboard)
    b_copy.pack(side=LEFT)
    b_close = Button(popup_bottom_frame, text="Close Output", fg="red", command=popup.destroy)
    b_close.pack(side=LEFT)
    t_output.configure(font=(None, 9))
    t_output.delete('1.0', END)
    t_output.insert(END, str(output))


def copy_to_clipboard():
    global command_lines
    output = ""
    for command in command_lines:
        output = output + command_lines[command] + "\n"
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(str(output))
    r.update()
    r.destroy()


def pre_process_files():  # Build easy list of properties for each file
    global files
    global video_tracks
    global audio_tracks
    global subtitle_tracks
    global audio_langs
    global subtitle_langs
    video_tracks.clear()
    audio_tracks.clear()
    subtitle_tracks.clear()
    audio_langs.clear()
    subtitle_langs.clear()
    for file in files:
        video_tracks[file] = {}
        audio_tracks[file] = {}
        subtitle_tracks[file] = {}
        json_data = files[file]
        if not (json_data.get("tracks") is None):
            command = ""
            for track in json_data["tracks"]:
                # track_type = track["properties"]["codec_id"]
                track_type = track["codec"]
                track_id = track["id"]
                if "language_ietf" in track["properties"]:  # "language_ietf" isn't always a property...
                    track_lang = track["properties"]["language_ietf"]
                elif "language" in track["properties"]:
                    track_lang = track["properties"]["language"]
                else:
                    track_lang = ""
                if not (track["properties"].get("track_name") is None):
                    track_name = track["properties"]["track_name"]
                else:
                    track_name = ""
                if track["type"] == "video":
                    if "display_dimensions" in track["properties"]:
                        track_disdim = track["properties"]["display_dimensions"]
                    else:
                        track_disdim = ""
                    video_tracks[file][track_id] = {"track_type": track_type, "track_lang": track_lang, "track_name": track_name, "track_disdim": track_disdim}
                elif track["type"] == "audio":
                    if track_lang not in audio_langs:
                        audio_langs.append(track_lang)
                    audio_tracks[file][track_id] = {"track_type": track_type, "track_lang": track_lang, "track_name": track_name}
                elif track["type"] == "subtitles":
                    if "encoding" in track["properties"]:
                        track_encode = track["properties"]["encoding"]
                    else:
                        track_encode = ""
                    if track_lang not in subtitle_langs:
                        subtitle_langs.append(track_lang)
                    subtitle_tracks[file][track_id] = {"track_type": track_type, "track_lang": track_lang, "track_name": track_name, "track_encode": track_encode}
                else:
                    print("Unknown track type = " + str(file))


def get_files():  # Get all .mkv files from the 'default_folder_path'
    global default_folder_path
    global files
    files.clear()
    files = {}
    file_list = []  # Temp list to be sorted
    file_list.clear()
    for filename in os.listdir(default_folder_path):
        if str(filename[-3:]).lower() == "mkv":
            file_list.append(str(filename))
    file_list.sort()  # Get a sorted list of the files
    for file in file_list:
        # Get information from mkv file in json format:
        if default_folder_path == "":
            cmd = ["mkvmerge --identify --identification-format json " + file]
        else:
            cmd = ["mkvmerge --identify --identification-format json \"" + default_folder_path + "/" + file + "\""]
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        json_data, err = proc.communicate()
        json_data = json_data.decode("utf-8")
        json_data = json.loads(json_data)  # json information of all objects in the mkv file
        files[file] = json_data
    pre_process_files()  # Build an easy list of the tracks


def change_folder():
    global default_folder_path
    global root
    folder_selected = filedialog.askdirectory(title='Please choose a folder', initialdir=default_folder_path, parent=root)
    if os.path.isdir(folder_selected):
        default_folder_path = folder_selected
    root.title("Linux_Bulk_MKV_Edit - (" + str(default_folder_path) + ")")
    populate_tree()


def main():
    global default_folder_path
    global files
    global tree
    global vsb
    global label_al
    global label_al_text
    global label_sl
    global label_sl_text
    global entry_al
    global entry_an
    global entry_sl
    global entry_st
    global entry_sn
    files.clear()
    # Check for command line arguments, and set the default_folder_path appropriately
    if len(sys.argv) > 1:  # If there is a command line argument, check if it is a folder
        if os.path.isdir(sys.argv[1]):  # Valid folder, so set the default_folder_path to it
            default_folder_path = sys.argv[1]
        elif os.path.isdir(os.path.dirname(os.path.abspath(sys.argv[1]))):  # If file path was sent, use folder path from it.
            default_folder_path = os.path.dirname(os.path.abspath(sys.argv[1]))
        else:  # Invalid folder, so set the default_folder_path to where the python file is
            default_folder_path = sys.path[0]
    else:  # No command line argument, so set the default_folder_path to where the python file is
        default_folder_path = sys.path[0]
    # Build GUI
    root.title("Linux_Bulk_MKV_Edit - (" + str(default_folder_path) + ")")
    root.minsize(1160, 360)
    top_frame.pack(side=TOP, fill="both", expand=True)
    tree = ttk.Treeview(top_frame, selectmode=BROWSE)
    tree.pack(side='left', fill="both", expand=True)
    vsb = ttk.Scrollbar(top_frame, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)
    tree["columns"] = ("1", "2", "3")
    tree['show'] = 'headings'
    style = ttk.Style()
    style.configure("Treeview", font=(None, 8))
    tree.column("1", anchor='w', minwidth=100, width=600, stretch=NO)
    tree.column("2", anchor='w', minwidth=100, width=600, stretch=NO)
    tree.column("3", anchor='w', minwidth=100, width=600, stretch=NO)
    tree.heading("1", text="File", anchor=CENTER)
    tree.heading("2", text="Audio", anchor=CENTER)
    tree.heading("3", text="Subtitles", anchor=CENTER)
    # Bottom Frame
    bottom_frame.pack(side=BOTTOM)
    button1 = Button(bottom_frame, text="Change Folder", fg="black", command=change_folder)
    button2 = Button(bottom_frame, text="Re-Scan", fg="green", command=populate_tree)
    button3 = Button(bottom_frame, text="Process Files", fg="blue", command=process_files)
    button4 = Button(bottom_frame, text="Exit", fg="red", command=root.destroy)
    button1.pack(side=LEFT)
    button2.pack(side=LEFT)
    button3.pack(side=LEFT)
    button4.pack(side=LEFT)
    # Subtitle Frame
    subtitle_frame.pack(side='bottom',anchor='w')
    label_sk = Label(subtitle_frame, text="Keep:  ")
    label_sk.pack(side=LEFT)
    label_sl = Label(subtitle_frame, text=label_sl_text)
    entry_sl = Entry(subtitle_frame)
    label_sl.pack(side=LEFT)
    entry_sl.pack(side=LEFT)
    label_sn = Label(subtitle_frame, text="  Subtitle Name (contains)")
    entry_sn = Entry(subtitle_frame)
    label_sn.pack(side=LEFT)
    entry_sn.pack(side=LEFT)
    label_st = Label(subtitle_frame, text="  Subtitle Type (contains)")
    entry_st = Entry(subtitle_frame)
    label_st.pack(side=LEFT)
    entry_st.pack(side=LEFT)
    # Audio Frame
    audio_frame.pack(side='bottom',anchor='w')
    label_ak = Label(audio_frame, text="Keep:  ")
    label_ak.pack(side=LEFT)
    label_al = Label(audio_frame, text=label_al_text)
    entry_al = Entry(audio_frame)
    label_al.pack(side=LEFT)
    entry_al.pack(side=LEFT)
    label_an = Label(audio_frame, text="  Audio Name (contains)")
    entry_an = Entry(audio_frame)
    label_an.pack(side=LEFT)
    entry_an.pack(side=LEFT)
    # Run GUI
    populate_tree()
    root.update()
    root.mainloop()


if __name__ == "__main__":
    main()
