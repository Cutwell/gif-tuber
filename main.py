import obspython
import sounddevice as sd
import numpy as np

global interval
global threshold
global avatar_speaking
global avatar_mute

global activation
global activation_hold
global activation_clock

interval        = 100   #ms
threshold       = 25
avatar_speaking = ""
avatar_mute     = ""

activation          = False
activation_hold     = 2000
activation_clock    = 0

def update(indata, outdata, frames, time, status):
    global threshold
    global avatar_speaking
    global avatar_mute
    global activation

    volume_norm = np.linalg.norm(indata)*10
    #print (int(volume_norm))

    # skip update if animating
    if activation:
        global activation_clock
        global activation_hold

        # increment activation clock
        activation_clock += interval

        if activation_clock >= activation_hold:
            activation = False
            activation_clock = 0

    else:
        current_scene   = obspython.obs_scene_from_source(obspython.obs_frontend_get_current_scene())
        speaking_source = obspython.obs_scene_find_source(current_scene, avatar_speaking)
        mute_source     = obspython.obs_scene_find_source(current_scene, avatar_mute)

        if current_scene and speaking_source and mute_source:

            if volume_norm < threshold:
                # show mute, hide speaking
                obspython.obs_sceneitem_set_visible(mute_source, True)
                obspython.obs_sceneitem_set_visible(speaking_source, False)
                
            else:
                # show speaking, hide mute
                obspython.obs_sceneitem_set_visible(speaking_source, True)
                obspython.obs_sceneitem_set_visible(mute_source, False)

                # activate animation hold
                activation = True

            # release sources after updating
            obspython.obs_scene_release(current_scene)
        
	
def audio_read():
    global interval

    # read from stream
    with sd.Stream(callback=update):
        sd.sleep(interval)

def refresh_pressed(props, prop):
    global activation
    global activation_clock

    activation          = False
    activation_clock    = 0

    audio_read()

def script_description():
	return "Monitors microphone audio input to display appropriate avatar GIFs.\n\nBy Cutwell"

def script_update(settings):
    global interval
    global threshold
    global avatar_speaking
    global avatar_mute
    global activation_hold

    threshold       = obspython.obs_data_get_int(settings, "threshold")
    activation_hold = obspython.obs_data_get_int(settings, "activation_hold")
    avatar_speaking = obspython.obs_data_get_string(settings, "avatar_speaking")
    avatar_mute     = obspython.obs_data_get_string(settings, "avatar_mute")

    obspython.timer_remove(audio_read)

    if threshold != "" and activation_hold != "" and avatar_speaking != "" and avatar_mute != "":
	    obspython.timer_add(audio_read, interval)

def script_defaults(settings):
    obspython.obs_data_set_default_int(settings, "threshold", 25)
    obspython.obs_data_set_default_int(settings, "activation_hold", 2000)

def script_properties():
    props = obspython.obs_properties_create()

    obspython.obs_properties_add_int(props, "threshold", "Activation threshold (normalised volume)", 5, 3600, 1)
    obspython.obs_properties_add_int(props, "activation_hold", "Activation hold (ms)", 5, 3600, 1)
    obspython.obs_properties_add_text(props, "avatar_speaking", "Avatar speaking Source", obspython.OBS_TEXT_DEFAULT)
    obspython.obs_properties_add_text(props, "avatar_mute", "Avatar mute Source", obspython.OBS_TEXT_DEFAULT)
    obspython.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
	
    return props
