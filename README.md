# gif-tuber
 Create an OBS avatar (for livestreaming, youtube) using GIFs

### OBS Studio setup
 - Create two `Image` sources, set to images (.gif, etc.), and layered on top of each other. One for `speaking` and one for `mute` animations / images.
 - Other sources can also be used, for instance `Image Slide Show`.

### OBS Script setup
 1. Download Python 3.6.x and set the `Python Install Path`.
 2. Pip install `numpy` and `sounddevice`.
 3. Upload `main.py` as a script.

### Script settings
 - Set the activation threshold (view the `Script Log` to view audio input).
 - Adjust the parameters to fit your audio levels and gif images.
 - Set the avatar `speaking` and `mute` sources to the source names defined earlier.

 _Note: Setting `audio frames read per interval` metric too high will result in significant FPS issues due to blocking._
 
 _Tip: Use the `audio levels log` checkbox to set `activation threshold` to an ideal level_

 ### License
 MIT License
