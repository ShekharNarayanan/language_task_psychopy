"""Choose an available output before PsychoPy creates any sounds."""

import sys


def _default_output_name(audio):
    # Ask the same backend that plays the experiment's sounds for its system
    # default. PsychoPy's literal 'default' preference selects the first device.
    # Open in shared mode without starting playback, then release the stream.
    stream = audio.Stream(mode=1, latency_class=0, freq=[], channels=[])
    try:
        index = stream.status['OutDeviceIndex']
        return audio.get_devices(device_index=index)[0]['DeviceName']
    finally:
        stream.close()


def configure_audio_device(hardware, preferred):
    """Prefer the requested name, then system default, then first output.

    Set PsychoPy's hardware preference to an explicit, available device name.
    Microphones and devices excluded by audioWASAPIOnly cannot be selected.
    """
    from psychtoolbox import audio

    device_type = 13 if sys.platform == 'win32' and hardware.get('audioWASAPIOnly', False) else None
    outputs = [
        device for device in audio.get_devices(device_type=device_type)
        if device['NrOutputChannels'] > 0
    ]
    if not outputs:
        raise RuntimeError(
            'No audio output device is available to PsychoPy. '
            'Connect or enable headphones/speakers and restart the experiment.'
        )

    names = {device['DeviceName'] for device in outputs}
    if preferred in names:
        selected = preferred
        reason = 'configured device'
    else:
        print(f"Audio: configured device {preferred!r} is unavailable.", flush=True)
        try:
            default_name = _default_output_name(audio)
        except Exception as error:
            # Default discovery is optional; enumerated outputs remain usable.
            print(f'Audio: could not determine the system default: {error}', flush=True)
            default_name = None
        if default_name in names:
            selected = default_name
            reason = 'system default fallback'
        else:
            selected = outputs[0]['DeviceName']
            reason = 'first available output fallback'

    hardware['audioDevice'] = selected
    print(f'Audio: using {selected!r} ({reason}).', flush=True)
    return selected
