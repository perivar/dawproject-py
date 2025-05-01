from classes.application import Application
from classes.arrangement import Arrangement
from classes.clip import Clip
from classes.clips import Clips
from classes.contentType import ContentType
from classes.dawProject import DawProject
from classes.device import Device
from classes.deviceRole import DeviceRole
from classes.fileReference import FileReference
from classes.interpolation import Interpolation
from classes.lanes import Lanes
from classes.marker import Marker
from classes.markers import Markers
from classes.mixerRole import MixerRole
from classes.note import Note
from classes.notes import Notes
from classes.points import Points
from classes.project import Project
from classes.realParameter import RealParameter
from classes.realPoint import RealPoint
from classes.referenceable import Referenceable
from classes.timeUnit import TimeUnit
from classes.transport import Transport
from classes.unit import Unit
from classes.utility import Utility


def create_empty_project():
    Referenceable.reset_id()
    project = Project()
    project.application = Application(name="Test", version="1.0")
    return project


SIMPLE_FEATURES = {"CLIPS", "NOTES", "AUDIO"}
ALL_FEATURES = {"CUE_MARKERS", "CLIPS", "AUDIO", "NOTES", "AUTOMATION", "ALIAS_CLIPS", "PLUGINS"}


def create_dummy_project(num_tracks=3, features=SIMPLE_FEATURES, advanced=False):
    if advanced:
        features = ALL_FEATURES

    if features is None:
        features = SIMPLE_FEATURES

    project = create_empty_project()
    project.transport = Transport()
    project.transport.tempo = RealParameter()
    project.transport.tempo.unit = Unit.BPM
    project.transport.tempo.value = 120.0

    master_track = Utility.create_track("Master", content_types=set(), mixer_role=MixerRole.MASTER, pan=0.5, volume=1.0)
    project.structure.append(master_track)

    if "PLUGINS" in features:
        device = Device()
        device.device_name = "Limiter"
        device.device_role = DeviceRole.AUDIO_FX
        device.state = FileReference("plugin-states/12323545.vstpreset")

        if master_track.channel.devices is None:
            master_track.channel.devices = []

        master_track.channel.devices.append(device)

    project.arrangement = Arrangement()
    arrangement_lanes = Lanes()
    arrangement_lanes.time_unit = TimeUnit.BEATS
    project.arrangement.lanes = arrangement_lanes

    if "CUE_MARKERS" in features:
        cue_markers = Markers()
        project.arrangement.markers = cue_markers
        cue_markers.markers.append(create_marker(0, "Verse"))
        cue_markers.markers.append(create_marker(24, "Chorus"))

    for i in range(num_tracks):
        track = Utility.create_track(
            f"Track {i + 1}", content_types={ContentType.NOTES}, mixer_role=MixerRole.REGULAR, pan=0.5, volume=1.0
        )
        project.structure.append(track)
        track.color = f"#{i:x}{i:x}{i:x}{i:x}{i:x}{i:x}"
        track.channel.destination = master_track.channel

        track_lanes = Lanes()
        track_lanes.track = track
        arrangement_lanes.lanes.append(track_lanes)

        if "CLIPS" in features:
            clips = Clips()
            track_lanes.lanes.append(clips)

            clip = Clip(time=8 * i)
            clip.name = f"Clip {i}"
            clip.duration = 4.0
            clips.clips.append(clip)

            notes = Notes()
            clip.content = notes

            for j in range(8):
                note = Note(time=0.5 * j, duration=0.5, key=36 + 12 * (j % (1 + i)))
                note.velocity = 0.8
                note.release_velocity = 0.5
                note.time = 0.5 * j
                note.duration = 0.5
                notes.notes.append(note)

            if "ALIAS_CLIPS" in features:
                clip2 = Clip(time=32 + 8 * i)
                clip2.name = f"Alias Clip {i}"
                clip2.duration = 4.0
                clips.clips.append(clip2)
                clip2.reference = notes

            if i == 0 and "AUTOMATION" in features:
                points = Points()
                points.target.parameter = track.channel.volume
                track_lanes.lanes.append(points)

                # fade-in over 8 quarter notes
                points.points.append(create_point(0.0, 0.0, Interpolation.LINEAR))
                points.points.append(create_point(8.0, 1.0, Interpolation.LINEAR))

    return project


def create_point(time, value, interpolation):
    point = RealPoint(time=time, value=value, interpolation=interpolation)
    return point


def create_marker(time, name):
    marker_event = Marker(time=time, name=name)
    return marker_event


def save_project(project, name):
    DawProject.save_xml(project, f"{name}.xml")
    print(f"Saved project to {name}.xml")


if __name__ == "__main__":
    import sys

    advanced = "-advanced" in sys.argv
    project = create_dummy_project(features=SIMPLE_FEATURES, advanced=advanced)
    filename = "example_advanced" if advanced else "example_simple"
    save_project(project, filename)
