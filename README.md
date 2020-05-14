# LilyPond-piano-trainer
This program lets you create piano lessons and practice with them. It displays the notes you have to play and follows your playing. The sheet music is created with LilyPond.
See the program in action in my [YouTube video](https://youtu.be/Rm6I6rxtIac).


## Requirements
* Python 2
* lilyond
* opencv, LilyPond for the creation of lessons (*creator.py*).
* alsaseq, pygame for the playing mode (*play.py*).

## Warnings
* The practice mode currently only works under Linux because it requires ALSA. I hope that the creation mode already works on other operating systems.
* This is still a prototype. Most of the advanced LilyPond commands do not work or produce odd results. The provided examples all work correctly.
* When you create new lessons, make sure that the LilyPond file has exactly the same structure as the provided examples. (Otherwise, the staffs won't be identified correctly.)
* Before creating new lessons, I recommend experimenting with the exemplary LilyPond files.  
* LilyPond's relative mode does not work. If you want to use an existing LilyPond File with
notation in relative mode, you must first convert it to absolute mode. You can use LilyPonds's
`\displayLilyMusic` command to accomplish that.

## Usage
### How to create lessons
* Run `python creator.py` to load all options from *options.cfg*.
* `python creator.py -s pineapple_rag -r 1 -l 1` creates the lesson for the song *pineapple_rag* for the left and right hand to be played simultaneously. (It still loads *options.cfg* but overwrites the given options.)
* `python creator.py -s pineapple_rag -r 1 -l 1 -p 1` does the same in presentation mode.

### How to play/practice
* Determine the number of your MIDI device with `aconnect --list`. Assign this number to the variable *midi_device_no* in the file *options.cfg*.
* Run `python play.py` to load all options from *options.cfg*.
* `python play.py -l 1 -r 1 -p 0 -s pineapple_rag` loads the lesson *pineapple_rag* for the left and right hand with presentation mode turned off. (It still loads *options.cfg* but overwrites the mentioned options.)
