import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

from screens.utils.audio_device import configure_audio_device


def device(name, channels=2):
    return {'DeviceName': name, 'NrOutputChannels': channels}


class AudioDeviceTests(unittest.TestCase):
    def setUp(self):
        self.hardware = {'audioDevice': 'old setting'}
        self.outputs = [device('Microphone', 0), device('Speakers'), device('Headphones')]
        self.audio = Mock()
        self.audio.get_devices.side_effect = lambda **kwargs: (
            [device('Headphones')] if 'device_index' in kwargs else self.outputs
        )
        self.stream = self.audio.Stream.return_value
        self.stream.status = {'OutDeviceIndex': 42}
        modules = patch.dict('sys.modules', {'psychtoolbox': SimpleNamespace(audio=self.audio)})
        modules.start()
        self.addCleanup(modules.stop)
        self.output = io.StringIO()
        stdout = redirect_stdout(self.output)
        stdout.__enter__()
        self.addCleanup(stdout.__exit__, None, None, None)

    def test_available_preference_does_not_probe_default(self):
        self.assertEqual(configure_audio_device(self.hardware, 'Speakers'), 'Speakers')
        self.assertEqual(self.hardware['audioDevice'], 'Speakers')
        self.audio.Stream.assert_not_called()

    def test_missing_preference_uses_system_default_and_closes_probe(self):
        self.assertEqual(configure_audio_device(self.hardware, 'Missing'), 'Headphones')
        self.assertEqual(self.hardware['audioDevice'], 'Headphones')
        self.assertIn('system default fallback', self.output.getvalue())
        self.stream.close.assert_called_once()
        self.stream.start.assert_not_called()

    def test_unavailable_default_uses_first_output_not_microphone(self):
        self.outputs = [device('Microphone', 0), device('Speakers')]
        self.assertEqual(configure_audio_device(self.hardware, 'Missing'), 'Speakers')
        self.assertIn('first available output fallback', self.output.getvalue())

    def test_failed_default_probe_falls_back(self):
        self.audio.Stream.side_effect = RuntimeError('Default unavailable')
        self.assertEqual(configure_audio_device(self.hardware, 'Missing'), 'Speakers')
        self.assertIn('Default unavailable', self.output.getvalue())

    def test_failed_status_lookup_still_closes_probe(self):
        self.stream.status = {}
        self.assertEqual(configure_audio_device(self.hardware, 'Missing'), 'Speakers')
        self.stream.close.assert_called_once()

    def test_no_outputs_gives_actionable_error_without_changing_preference(self):
        self.outputs = [device('Microphone', 0)]
        with self.assertRaisesRegex(RuntimeError, 'Connect or enable headphones/speakers'):
            configure_audio_device(self.hardware, 'Missing')
        self.assertEqual(self.hardware['audioDevice'], 'old setting')
        self.audio.Stream.assert_not_called()

    def test_windows_wasapi_filter_is_respected(self):
        self.hardware['audioWASAPIOnly'] = True
        with patch('screens.utils.audio_device.sys.platform', 'win32'):
            configure_audio_device(self.hardware, 'Speakers')
        self.audio.get_devices.assert_called_once_with(device_type=13)


if __name__ == '__main__':
    unittest.main()
