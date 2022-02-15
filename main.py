import obspython
import sounddevice as sd
import numpy as np

global interval
global threshold
global avatar_speaking
global avatar_mute
global previous_state

global activation
global activation_hold
global activation_clock

interval        = 100   #ms
threshold       = 25
avatar_speaking = ""
avatar_mute     = ""
previous_state  = True  # initial state is (volume_norm < threshold) == True

activation          = False
activation_hold     = 500
activation_clock    = 0

def update(indata, outdata, frames, time, status):
    global threshold
    global avatar_speaking
    global avatar_mute
    global activation
    global previous_state

    volume_norm = np.linalg.norm(indata)*10
    #print(int(volume_norm))    # active activation threshold logger

    # skip update if animating
    if activation:
        global activation_clock
        global activation_hold

        # increment activation clock
        activation_clock += interval

        if activation_clock >= activation_hold:
            activation = False
            activation_clock = 0

    # access sources only on state change
    elif previous_state != (volume_norm < threshold):
        previous_state = (volume_norm < threshold)

        if volume_norm < threshold:
            speaking_toggle, mute_toggle = False, True
        else:
            speaking_toggle, mute_toggle = True, False
            # activate animation hold
            activation = True

        scene_sources = obspython.obs_frontend_get_scenes()

        for scn_src in scene_sources:

            scn = obspython.obs_scene_from_source(scn_src)
            scn_items = obspython.obs_scene_enum_items(scn)

            for itm in scn_items:

                itm_src = obspython.obs_sceneitem_get_source(itm)

                if obspython.obs_source_get_name(itm_src) == avatar_speaking:
                    obspython.obs_sceneitem_set_visible(itm, speaking_toggle)

                elif obspython.obs_source_get_name(itm_src) == avatar_mute:
                    obspython.obs_sceneitem_set_visible(itm, mute_toggle)

            obspython.sceneitem_list_release(scn_items)

        obspython.source_list_release(scene_sources)

def audio_read():
    global interval

    # read from stream
    with sd.Stream(callback=update):
        sd.sleep(interval)

def refresh_pressed(props, prop):
    global activation
    global activation_clock
    global interval

    obspython.timer_remove(audio_read)

    activation          = False
    activation_clock    = 0

    obspython.timer_add(audio_read, interval)

def script_description():
	return "Monitors microphone audio input to display appropriate avatar GIFs.\n\nBy Cutwell"

def script_update(settings):
    global interval
    global threshold
    global avatar_speaking
    global avatar_mute
    global activation_hold

    obspython.timer_remove(audio_read)

    interval        = obspython.obs_data_get_int(settings, "interval")
    threshold       = obspython.obs_data_get_int(settings, "threshold")
    activation_hold = obspython.obs_data_get_int(settings, "activation_hold")
    avatar_speaking = obspython.obs_data_get_string(settings, "speaking_source_select_list")
    avatar_mute     = obspython.obs_data_get_string(settings, "mute_source_select_list")

    if interval != "" and threshold != "" and activation_hold != "" and avatar_speaking != "" and avatar_mute != "":
	    obspython.timer_add(audio_read, interval)

def script_defaults(settings):
    obspython.obs_data_set_default_int(settings, "interval", 100)
    obspython.obs_data_set_default_int(settings, "threshold", 25)
    obspython.obs_data_set_default_int(settings, "activation_hold", 2000)

def script_properties():
    props = obspython.obs_properties_create()
    
    obspython.obs_properties_add_int(props, "interval", "Animation hold interval", 5, 3600, 1)
    obspython.obs_properties_add_int(props, "threshold", "Activation threshold (normalised volume)", 5, 3600, 1)
    obspython.obs_properties_add_int(props, "activation_hold", "Activation hold (ms)", 5, 3600, 1)
    
    avatar_speaking_drop_list = obspython.obs_properties_add_list(props, "speaking_source_select_list", "Avatar speaking source", obspython.OBS_COMBO_TYPE_LIST, obspython.OBS_COMBO_FORMAT_STRING)
    avatar_mute_drop_list = obspython.obs_properties_add_list(props, "mute_source_select_list", "Avatar mute source", obspython.OBS_COMBO_TYPE_LIST, obspython.OBS_COMBO_FORMAT_STRING)
    
    obspython.obs_property_list_add_string(avatar_speaking_drop_list, "", "")
    obspython.obs_property_list_add_string(avatar_mute_drop_list, "", "")

    # append sources to drop lists
    sources = obspython.obs_enum_sources()
    for src in sources:
        obspython.obs_property_list_add_string(avatar_speaking_drop_list, obspython.obs_source_get_name(src), obspython.obs_source_get_name(src))
        obspython.obs_property_list_add_string(avatar_mute_drop_list, obspython.obs_source_get_name(src), obspython.obs_source_get_name(src))
    obspython.source_list_release(sources)
    
    obspython.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
	
    return props

def script_save(settings):
    obspython.obs_save_sources()

def script_unload():
    obspython.timer_remove(audio_read)