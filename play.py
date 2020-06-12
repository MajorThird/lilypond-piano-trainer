import alsaseq

import pygame
import os
import os.path
import argparse
import configparser
import options_play

class SoundGame(object):
    """docstring forSoundGame."""

    def __init__(self, options):
        self.options = options
        self.perform_initializations()


    def print_newpage(self):
        newpage_string = '\x1bc'
        print(newpage_string)


    def load_files(self):
        self.images = []

        if self.options["presentation_mode"]:
            filename = self.options["song_folder_complete"] + "/presentation_mode_start.png"
            img = pygame.image.load(filename)
            self.images.append(img)


        folder = self.options["song_folder_complete"]
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        files = sorted(files)
        for f in files:
            extension = os.path.splitext(f)[1]
            if extension == ".png" and f != "presentation_mode_start.png":
                filename = os.path.join(folder, f)
                img = pygame.image.load(filename)
                self.images.append(img)
        no_of_steps = len(self.images)
        print(str(no_of_steps) + " images loaded.")


        self.midi_notes = []
        read_data_to_container(self.midi_notes, "midi_notes", self.options["song_folder_complete"], int)

        if self.options["presentation_mode"]:
            self.midi_notes.append([])

    def update_step(self, direction="forward"):
        if direction == "forward":
            self.current_step = (self.current_step + 1) % len(self.images)
        elif direction == "backward":
            self.current_step = (self.current_step - 1)
            if self.current_step == -1:
                self.current_step = len(self.images) - 1

        self.current_activations = []
        self.correct_notes = self.midi_notes[self.current_step]
        white = (255,255,255)
        self.display.fill(white)
        self.display.blit(self.images[self.current_step], (0,0))
        pygame.display.update()




    def perform_initializations(self):
        self.init_pygame()
        self.init_alsa()
        self.load_files()
        self.is_running = True
        self.interrupt = False


        self.current_step = -1
        self.update_step()




    def init_alsa(self):
        # prepare alsaseq
        device_no = self.options["midi_device_no"] # find out using aconnect or aconnectgui
        alsaseq.client('Recorder', 1, 0, True )
        alsaseq.connectfrom( 0, device_no, 0 )
        alsaseq.start()


    def init_pygame(self):
        # pygame mixer
        # mixer_buffer = 10
        # pygame.mixer.pre_init(44100, -16, 1, mixer_buffer)
        # pygame.mixer.init()

        # display
        full_screen = False
        full_screen = True
        if full_screen:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
            pygame.init()

            info = pygame.display.Info()

            self.display = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        else:
            self.display = pygame.display.set_mode((0,0))

        pygame.display.set_caption('Lilypond Piano Trainer')



    def reaction_note_on(self,event):
        if not self.interrupt:
            pitch = event[7][1]
            velocity = event[7][2]
            if velocity > 0:
                if pitch in self.correct_notes:
                    if not pitch in self.current_activations:
                        self.current_activations.append(pitch)
                        if len(self.current_activations) == len(self.correct_notes):
                            self.update_step()
                elif self.options["presentation_mode"] and self.current_step == len(self.images) - 1:
                    self.update_step()

    def reaction_note_off(self,event):
        pass


    def play(self):

        while self.is_running:
            # check for quit in pygame
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.interrupt = not self.interrupt
                        print("toggle interrupt")
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    if event.key == pygame.K_RIGHT:
                        self.update_step()
                    if event.key == pygame.K_LEFT:
                        self.update_step(direction="backward")
                elif event.type == pygame.QUIT:
                    self.is_running = False


            if alsaseq.inputpending():
                event = alsaseq.input()
                if event[0] == 6:   # note on event (zumindest bei kleinem midikeyboard)
                    self.reaction_note_on(event)
                elif event[0] == 7:
                    self.reaction_note_off(event)


def get_config(filename):
    """
    All settings are stored in an external text file.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def main():
    options = options_play.get_options()
    game = SoundGame(options)
    game.play()


def read_data_to_container(container, filename, song_folder, conversion_func, no_list=False):
    with open(song_folder + filename + ".txt") as infile:
        for line in infile.read().split("\n"):
            if line != "":
                data = [conversion_func(n) for n in line.split(" ")]
                if no_list:
                    data = data[0]
                container.append(data)


if __name__ == "__main__":
    main()
