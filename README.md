# stenography
This python script hides (encode) large amount of text in video files and then decode them as well

As for learning stenography and encoding/decoding large text files in the video (as oppose to an image, which is very normal), I started writing this Python script.

The basic concept is similar to hiding text in an image and/or in sound. The image data is taken into its binary form and the last bit of each byte of any channel data (i.e. Red, Green, Blue) of image in the data is replaced by the data that is to be hidden in the image. For this, the data was also converted into its binary form. For not changing the 'look' of each image, we can decide to hide the data-bits into the image only if the last byte is less than certain value. Note that, a byte data is between (0x0 to 0xF in HEX). 

For retrieving the data back, a special set of characters are used. These characters were appended before and after the databytes before encoding the completed appended-data into the images. This makes decoding quite easy. 

Requirements include:
1 - OpenCV
2 - PIL
3 - moviepy
4 - natsort
5 - glob
6 - numpy 
7 - optparse

For simple demo, one can follow this youtube video to see how to make this script work with different system arguments 

Part I (Total Space For text required and text encoding)
https://www.youtube.com/watch?v=LqekSSrwqQo&t=194s    

Part II (Decoding text from video)
https://www.youtube.com/watch?v=e4WDdVpFY44&t=40s

NOTE: Please note that as video-encoders reduced the size by manipulating data, I did save the video in mkv format. This basically stacked up images with no video-encoding thus our hidden data in the image-data is preserved as it is. 
