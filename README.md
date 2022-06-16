# Linux Bulk MKV Edit

## Purpose:
I couldn't find a good tool for bulk editing (e.g. removing) of audio and subtitle tracks in mkv files on **Linux**, so I decided to make my own.  This currently only includes tracks with languages that you choose or parts of the track names you choose.  This will not perform the conversion directly, but will spit out the command lines necessary to do the conversions.  Simply copy the command lines into a terminal and away it goes.

Currently, this uses TkInter for the GUI.   If there is any interest in this, I may convert it to a better looking GTK GUI, which would make it easier to add more features.

## Functionality:
* Point it at a folder and it will display for every .mkv file in that folder the following:
  * The file name
  * Audio track information
    * Track ID/Number
    * Track Language
    * Track Name
    * Track Type
  * Subtitle track information
    * Track ID/Number
    * Track Language
    * Track Name
    * Track Type
* Next, choose which tracks to **keep** based on the user selected criteria.
  * Audio Languages
    * Default:  A list each unique audio language that the combined MKV files have.
    * If you remove a track (Example:  Change "en, ja" to "ja"), then the resulting MKV files will not contain any audio track of the language type that you removed.
  * Audio Name
    * If you populate this, then the resulting MKV files will only contain the audio tracks that have a track name that contains the characters you entered.
    * Note:  This is a single string field, it does not currently support multiple values.
  * Subtitle Languages
    * Default:  A list each unique subtitle language that the combined MKV files have.
    * If you remove a track (Example:  Change "en, ja" to "ja"), then the resulting MKV files will not contain any subtitle track of the language type that you removed.
  * Subtitle Name
    * If you populate this, then the resulting MKV files will only contain the subtitle tracks that have a track name that contains the characters you entered.
    * Note:  This is a single string field, it does not currently support multiple values.
  * Subtitle Type
    * If you populate this, then the resulting MKV files will only contain the subtitle tracks that have a track 'type' that contains the characters you entered.
    * Note:  This is a single string field, it does not currently support multiple values.
  * Note:  If you don't modify the default selections, the resulting files will contain all the original audio and subtitle tracks.
* Next, click the Process Files button to get the command line output to perform the conversion.
  * Paste the output into a terminal and the files will be converted.
* Note:  This will always set the MKV title to blank, which is my preference as I prefer my video player to just display the filename.
* HINT:  I recommend my own [Linux File Rename Utility](https://github.com/BSFEMA/linux_file_rename_utility) for bulk renaming of files in Linux! 

## Author:
BSFEMA

## Started:
2022-05-14

## Prerequisites:
You need to have MKVToolNix installed:  https://mkvtoolnix.download/downloads.html  Try running "mkvmerge --version" in terminal.  If that works, then you are good to go, otherwise install MKVToolNix

## Command Line Parameters:
There is just 1.  It is the folder path that will be used to start looking at the *.mkv files from.  If this value isn't provided, then the starting path will be where this application file is located.  The intention is that you can call this application from a context menu from a file browser (e.g. Nemo) and it would automatically load up that folder.

## Nemo Action:

You can create a nemo action file so that you can right-click in a folder and launch the linux_bulk_mkv_edit.py application from there.

Example (filename = "linux_bulk_mkv_edit.nemo_action") 

    [Nemo Action]
    Name=Linux Bulk MKV Edit
    Quote=double
    Exec=python3 "[PATH_TO]/linux_bulk_mkv_edit.py" %F
    Selection=any
    Extensions=any
    Icon-Name=python3

Save the "linux_bulk_mkv_edit.nemo_action" file to "~/.local/share/nemo/actions".

Context menus might be possible for other file managers, but that will be up to you to figure out ;)

## Resources:
https://mkvtoolnix.download/doc/mkvextract.html