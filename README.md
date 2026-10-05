# desk-signaller

> ### Super Important: this project will only run on devices running MicroPython. It will not run on standard Python installations.

## Disclaimer
This project was hard fought with actual tears of frustration. This is not a vibe-coded project, that would defeat the point in creating something strange and obscure with your own hands.

I actually put off writing this README because I could not sufficiently communicate the work that went into this!

The documentation here is the bare minimum outline of the project. This was a brutal induction into the world of train signalling and there are lots of nuances. For those interested, I have tried to document in the docstrings the sheer madness behind this project.

## MicroStomp

I have written a fully functioning STOMP client for MicroPython, it is all contained in one file eponymously named ```microstomp.py```. 

## An Introduction
Have you ever wanted to have a train signal on your desk? Me too! For the detail oriented among you who spot that this README is being updated 9 months after the last code commit, well done. This project was originally intended to be a simple one that I could knock out over a weekend. How I was wrong. This was an adventure into learning the STOMP protocol, writing my own STOMP client, learning and understanding more about train signalling than I thought was possible and being plagued by the Little Endian and Big Endian order of bytes.

![Gif of it working](https://github.com/ryaninthecloud/desk-signaller/blob/main/.github/media/b2qmzt.gif?raw=true)

## The hardware
In my case, I kept it simple, a 'light-only' signal with a red and a green light. I had a casing for a traffic light that I appropriated into a train signal.

I used an ESP32 Dev Board (my board of choice for most things), as it has both Bluetooth Low Energy and WiFi capabilities. This makes it perfect for streaming data directly to the board.

I wired up two groups of LEDs, one set of red and one set of green, these can be seen in the photo below.

![Wiring Schematic](https://github.com/ryaninthecloud/desk-signaller/blob/main/.github/media/schematic.png?raw=true)

<img src="https://github.com/ryaninthecloud/desk-signaller/blob/main/.github/media/IMG_1776.jpeg?raw=true" alt="wiring actual photo" style="width:400px">

The project runs on MicroPython, something that I had not used before, so a bit of flashing of the ESP32 was also required. [Excellent guide here](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html).

## Get Started

### Get a Network Rail account
The wonderful people at Network Rail provide an excellent, free public data service. Much of the data offered is real-time, so if you're looking for interesting datasets to try thingds out on then it's a great resource.

The dataset we are interested in for this project is the TD data - the Train Positioning Data. This dataset represents the position of locomotives at signalling berths.


### Finding your favourite signal
To find the right information about your favourite signal, we need to do a bit of fumbling on OpenTrainTimes.com. This wonderful website provides signal state visualisations. This means that we can actually identify our signal of interest and then with a bit of 'inspect element' we can get the necessary data about it.

Hopefully, you already have a favourite signal. If not, this isn't the project for you, I promise. The code handles much of the data fetching, but you do need to do some digging.

For example, say you're interested in the [Leeds West area](https://www.opentraintimes.com/maps/signalling/y2_1#T_LEEDSWJ), you would visit the signal map and locate your signal of interest -- I can't help with this, you either have a favourite signal or you do not. Say, for example, your favourite signal is 5125 on platform 2 of Grindleford. Go to 'Inspect Element' on your browser of choice, select the 'Element Selector' tool and click on 5125, we can see that the element looks like this:

```<circle cx="1965" cy="104" r="5" id="Y2S3670" class="red"></circle>```

The ID attribute is of interest to us, we can see that it is ```Y2S3670``` in this case. This is the information we need for our configuration file. Keep hold of this.

Navigate to [this excellent repository of train signal map data](https://github.com/Shwam3/EASMData), find the JSON that most accurately reflects the area your signal will be in. You are now interested in the numbers at the end of the ID that we collected, in our case a ```3670```. Search for this in the JSON of your area's signals, there may be two matches, or more, but we are interested in the JSON block that contains the 'i' 't' 'r' keys, such as below:

```
{
        "x": 1894,
        "y": 110,
        "d": "L3670",
        "i": "Y25A:6",
        "t": "R",
        "r": [
            "Y21C:8",
            "Y21D:1",
            "Y21D:2"
        ]
    }
```
For those interested, the key/value pairs are (as I understand them!):

| Key | Description |
|-----|-------------|
|i    | dataId (the signal data identifier when receiving STOMP messages)|
|r    | the routes that converge into this signal |
|x   | the X axis position of the signal|
|y| the Y axis position of the signal|
|t| the type of signal represented -- I'm vague here because I am having to infer from code & context!|


The thing we are really interested in is the ```i``` or ```dataId```, this is what will help us to break down the incoming messages and filter out irrelevan ones.

### A quick induction into the world of train signals...
Each signal is represented by a "block". Each block contains up to 8 signal elements. The signal element is the individual signal that changes state, for example:

```Block A = [0,0,0,0,0,0,0,0]``` where all signals are 'off'.
```Block A = [0,0,0,0,0,0,0,1]``` where all signals but the last (7th (or 8th if you're not a computer)) is off.

So breaking down ```i``` we get:
```Y2``` - signal area code
```5A``` - signal block identifier
```:6``` - the individual signal position in the block.

```This is sort of an over simplification, because there is the 'issue' of the Big Endian/Little Endian byte ordering, but the code takes care of that. You can read more about it in the 'signal_block.py' file.```

### Creating a config file

For our example, our ```config.json``` file will look like this:

```
{
	"Y2":{
		"5A":
			[
				{
					"platform":2,
					"element_position":1,
					"green_pin":12,
					"red_pin":13
				}
			]
		
	}
}
```
In this instance, the ```green_pin``` and ```red_pin``` keys refer to the pins on your microcontroller that control the ```high``` and ```low``` signals.

### Deploy!

> ##### Remember to follow the guide linked in the hardware section to flash your board with the firmware to run MicroPython. You will also need to configure your ```boot.py``` file to use your local network.


The next thing we need to do is update our ```settings.py``` file with our credentials for the Network Rail Open Data Feed.

We are sort of contributing to the 'the S in IoT stands for security' thing here, for that, I am sorry.

Populate the settings file as below.

```
NETWORK_RAIL_STOMP_USERNAME = <YOUR USERNAME (EMAIL)>
NETWORK_RAIL_STOMP_PASSWORD = <YOUR PASSWORD>
NETWORK_RAIL_STOMP_HOST = 'publicdatafeeds.networkrail.co.uk'
NETWORK_RAIL_STOMP_PORT = 61618
NETWORK_RAIL_STOMP_CLIENT_ID = 'microPythonSTOMP_trafficLight_Control'
SIGNAL_AREA_CODE = <YOUR SIGNAL AREA CODE, i.e. Y2>
APPLIANCE_NAME = <WHATEVER YOU LIKE!>
```

Download and install Thonny, a Python IDE which supports uploading to devices running MicroPython. [This is an excellent tutorial on getting started uploading MicroPython to your board] (https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/)

Follow the tutorial above to upload the application files - and your modified config and settings file to the device. Once uploaded, Thonny should show you the output of the application in the 'Shell' window, it should look something like this:

```
(info): appliance IP address is ('10.0.5.23', '255.255.255.0', '10.0.5.1', '10.0.145.100')
(info): boot procedure completed
(info): setting network time
(info): time is now (2026, 10, 5, 11, 32, 37, 0, 278)
(info): enumerating area Y2
(info): enumerating block address 5A
(info): area container is now {'Y2': {'5A': <SignalBlock object at 3ffd4c00>}}
(info): beginning connection to server
(info): web server is bound to ('0.0.0.0', 80)
(info): server responded to connect with  CONNECTED
```
Enjoy!


[![Test and Integrate](https://github.com/ryaninthecloud/desk-signaller/actions/workflows/run-tests.yml/badge.svg)](https://github.com/ryaninthecloud/desk-signaller/actions/workflows/run-tests.yml)

