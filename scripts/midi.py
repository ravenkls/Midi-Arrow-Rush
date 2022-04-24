import pretty_midi
import pygame.midi

pygame.midi.init()

PLAYER = pygame.midi.Output(0)


class MidiFile:
    def __init__(self, file, tempo=1):
        self.file = str(file)
        self.data = pretty_midi.PrettyMIDI(self.file)
        self.tempo = 1 / tempo

        self.channels = self.calculate_instrument_channels()

        self.notes = {
            instrument: [
                Note.from_midi_note(note, self.channels[instrument], tempo=self.tempo)
                for note in instrument.notes
            ]
            for instrument in self.data.instruments
        }

    def intro(self, seconds):
        for notes in self.notes.values():
            for note in notes:
                note.time += seconds * 60

    def get_instruments_by_index(self, *indexes):
        return [self.data.instruments[i] for i in indexes]

    def calculate_instrument_channels(self):
        channels = list(
            {
                instrument.program
                for instrument in self.data.instruments
                if not instrument.is_drum
            }
        )

        channels_by_instrument = {}
        drums = False
        for instrument in self.data.instruments:

            # Reserve channel 10 for drums
            if instrument.is_drum:
                channel = 9
                drums = True
            else:
                channel = channels.index(instrument.program)

            if channel >= 9 and not drums and not instrument.is_drum:
                channel += 1

            channels_by_instrument[instrument] = channel

        return channels_by_instrument

    def initialise_player(self):
        for instrument, channel in self.channels.items():
            PLAYER.set_instrument(instrument.program, channel)


class Note:
    def __init__(self, player, time, note, duration, velocity, channel):
        self.player = player
        self.time = time
        self.note = note
        self.duration = duration
        self.velocity = velocity
        self.end_time = -1
        self.played = False
        self.finished = False
        self.channel = channel

    def update(self, frame):
        if frame < self.time:
            self.played = False
        if frame > self.time and frame and not self.played:
            PLAYER.note_on(self.note, self.velocity, self.channel)
            self.end_time = self.time + self.duration
            self.played = True
        elif frame == self.end_time:
            PLAYER.note_off(self.note, self.velocity, self.channel)
            self.finished = True

    @classmethod
    def from_midi_note(cls, midi_note, channel, tempo=1):
        return cls(
            time=int(midi_note.start * 60 * tempo),
            note=midi_note.pitch,
            duration=int((midi_note.end - midi_note.start) * 60 * tempo),
            velocity=midi_note.velocity,
            player=PLAYER,
            channel=channel,
        )
