REQUIRES MODULE pillow (PIL)

bg36.pyw
A program to select 2 random images from a (weighted) random folder in the background directory path (specified in sysinfo.ini), and stitch them together to create a wallpaper
that will work on a dual monitor setup. Also sets the background to this newly created image (only works on Windows with the the 'tile' wallpaper configuration selected).

sleepy.pyw
A program that will run bg36.pyw every 10 minutes (by default, can be changed in sysinfo.ini).

ranks.ini
Contains weightings for the different folders in the background directory path. Entries for newly found folders are automatically added when bg36.pyw is run, and entries for
folders that no longer exist are removed. Folders with a higher weighting will have a higher chance of being selected.

sysinfo.ini
Contains settings.