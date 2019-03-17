    
from PIL import Image
import binascii
import optparse
import cv2
import numpy as np
import os
from moviepy.editor import *
from natsort import natsorted
import glob



replacable_bits = ('0','1', '2', '3', '4', '5', '6','7','8','9','a','b','c','d','e','f')
speicial_char = '10000101000000001000110010010000100101010111100010011000101010001010000010100101011111'
current_dir = os.getcwd()


def rgb2hex(r, g, b):
	return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def hex2rgb(hexcode): 
        return tuple(map(ord, hexcode[1:].decode('hex')))

def str2bin(message):
	binary = bin(int(binascii.hexlify(message), 16))
	return binary[2:]

def bin2str(binary):
	message = binascii.unhexlify('%x' % (int('0b'+binary,2)))
	return message

def encode(hexcode, digit):
        r,g,b = hexcode[0:3], hexcode[3:5], hexcode[5:]
        
        if g[-1] in replacable_bits:
                g = g[:-1] + digit
                hexcode = r + g + b
                return hexcode
        else:
                return None

def detect_encode(hexcode, digit):
        r,g,b = hexcode[0:3], hexcode[3:5], hexcode[5:]

        if g[-1] in replacable_bits:
                return hexcode, True
        else:
                return None, False

def decode(hexcode):
        r,g,b = hexcode[0:3], hexcode[3:5], hexcode[5:]
        if g[-1] in ('0', '1'):
                return g[-1]
        else:
                return None

def hide(datas, message):

        binary = (message) + speicial_char
        not_common = 0
        newData = []
        digit = 0
        temp = ''
        for item in datas:
            if (digit < len(binary)):
                    newpix = encode(rgb2hex(item[0],item[1],item[2]),binary[digit])
                    if newpix == None:
                            newData.append(item)
                            not_common += 1
                    else:
                            r, g, b = hex2rgb(newpix)
                            newData.append((r,g,b))
                            digit += 1
            else:
                    newData.append(item)
        return newData 
                

def detect(datas, message):

        PRINT = False
        binary = (message) + speicial_char

        if PRINT: print "Your data is %d bits" %len(binary)
        if PRINT: print "Your image saving capacity is %d bits" %( len(datas))
        not_common = 0
        newData = []
        digit = 0
        temp = ''
        for item in datas:
            newpix, status = detect_encode(rgb2hex(item[0],item[1],item[2]),'a')
            if status == False:
                not_common += 1
            else:
                #r, g, b = hex2rgb(newpix)
                #newData.append((r,g,b,255))
                digit += 1

        if PRINT: print "Your image can store %d bits" % (digit) 
        storage_capacity = (digit)
        data_length = len(binary)
        total_storage_capacity = len(datas)
        return storage_capacity, data_length, total_storage_capacity
                

def isFeasible(datas, message):

        storage_capacity, data_length, total_storage_capacity = detect(datas, message)
        #print "Storage Capacity: %d \t Data Length: %d" %(storage_capacity , data_length)
        if storage_capacity >= data_length:
                return True

        else : return False
                       
def retr(datas):
        binary = ''
        for item in datas:
                digit = decode(rgb2hex(item[0],item[1],item[2]))
                if digit == None:
                        pass
                else:
                        binary = binary + digit
                        if (binary[-86:] == speicial_char):
                                #print "Success"
                                return (binary[:-86])
                        
        return ('')


def ENCODE(input_video_filename, input_text_filename, print_output):
        if print_output == '1':
                PRINT = True
        else:
                PRINT = False
                
        input_filename = current_dir + str(input_video_filename)

        input_text_file = current_dir + str(input_text_filename)

        long_message = open(input_text_file, 'r').read()
        long_message_binary = str2bin(long_message)


        filesize = os.stat(input_filename).st_size
        if PRINT: print "Input video file size is: %d filesize" %filesize

        cap = cv2.VideoCapture(input_filename)
        total_frame_counts = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if PRINT: print "Total number of frames in input video: %d"  %total_frame_counts

        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fps = cap.get(cv2.CAP_PROP_FPS)

        framecount = 0
        img_count = 0

        total_storage_in_video = 0

        while framecount < total_frame_counts :
                framecount += 1        
                ret, frame = cap.read()

                if total_storage_in_video < len(long_message)*8:

                        pil_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_frame = Image.fromarray(pil_frame)
                        pil_data = pil_frame.getdata()

                        store_cap_in_frame, data_length , tot_cap_in_frame =  detect(pil_data, "abc")
                        store_cap_in_frame = store_cap_in_frame -  86
                        encode_this_much = long_message_binary[(total_storage_in_video): total_storage_in_video + store_cap_in_frame]
                        canEncode = isFeasible(pil_data, encode_this_much)
                        total_storage_in_video = total_storage_in_video + store_cap_in_frame
                        #print framecount , canEncode, total_storage_in_video, len(long_message_binary)
                        percent_completed = float(float(total_storage_in_video)/float(len(long_message_binary))*100)
                        if percent_completed > 100: percent_completed = 100
                        if PRINT : print "%d percent data has been encoded in %d frames" % (int(percent_completed), framecount)
                        
                        if canEncode:
                                encoded_data = hide(pil_data, encode_this_much)
                                pil_frame.putdata(encoded_data)
                                frame = cv2.cvtColor(np.asarray(pil_frame), cv2.COLOR_RGB2BGR)
                                cv2.imwrite(current_dir + "/newpics/cv_frame_" + str(img_count) + ".png" , frame)
                        else :
                                cv2.imwrite(current_dir + "/newpics/cv_frame_" + str(img_count) + ".png" , frame)
                else:
                        cv2.imwrite(current_dir + "/newpics/cv_frame_" + str(img_count) + ".png" , frame)

                img_count +=1
                
        if PRINT : print "Converting frames to video"
        os.system('ffmpeg -framerate 25 -y -i ' + str(current_dir) + '/newpics/cv_frame_%d.png -codec copy ' + str(current_dir) + '/videos/output_video_encoded.mkv')
        
        cap.release()
        if PRINT : print "Removing Frames"
        for i in range(framecount):
                name = "cv_frame_" + str(i) + ".png"
##                if os.path.exists('./newpics' + name):
                if PRINT : print "Removing %s file" %name
                os.remove(current_dir + "/newpics/cv_frame_" + str(i) + ".png")

        if PRINT : print ("Encoding Completed")

def DETECT(input_video_filename, input_text_filename, print_output):
        if print_output == '1':
                PRINT = True
        else:
                PRINT = False
                
        input_filename = current_dir + str(input_video_filename)
        input_text_file = current_dir + str(input_text_filename)

        long_message = open(input_text_file, 'r').read()
        long_message_binary = str2bin(long_message)

        filesize = os.stat(input_filename).st_size
        if PRINT: print "Input video file size is: %d filesize" %filesize

        cap = cv2.VideoCapture(input_filename)
        total_frame_counts = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if PRINT: print "Total number of frames in input video: %d"  %total_frame_counts

        framecount = 0
        img_count = 0

        total_storage_in_video = 0
        final_storage_in_video = 0
        final_storage_of_text = 0
        if PRINT: print ("Space Calculation Started")
        while framecount < total_frame_counts :
                framecount += 1        
                ret, frame = cap.read()

                if total_storage_in_video < len(long_message)*8:

                        pil_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_frame = Image.fromarray(pil_frame)
                        pil_data = pil_frame.getdata()

                        store_cap_in_frame, data_length , tot_cap_in_frame =  detect(pil_data, "abc")
                        final_storage_in_video = final_storage_in_video + store_cap_in_frame
                        
                        store_cap_in_frame = store_cap_in_frame -  86
                        encode_this_much = long_message_binary[(total_storage_in_video): total_storage_in_video + store_cap_in_frame]
                        canEncode = isFeasible(pil_data, encode_this_much)
                        total_storage_in_video = total_storage_in_video + store_cap_in_frame

                        if canEncode :
                                final_storage_of_text = final_storage_of_text + len(encode_this_much)
                        
                        percent_completed = float(float(total_storage_in_video)/float(len(long_message_binary))*100)
                        if percent_completed > 100: percent_completed = 100
                        if PRINT : print "%d percent data has been read in %d frames" % (int(percent_completed), framecount)
                        

        if final_storage_in_video >  final_storage_of_text:
                if PRINT : print "Store Capacity of input video is: %d bits" %final_storage_in_video
                if PRINT : print "Space Required of input text is: %d bits" % final_storage_of_text
                if PRINT : print "Input file can be stored in the given input video"
        else:
                if PRINT : print "Store Capacity of input video is: %d bits" %final_storage_in_video
                if PRINT : print "Space Required of input text is: %d bits" % final_storage_of_text
                if PRINT : print "Input file can NOT be stored in given input video"
        cap.release()
        if PRINT: print ("Space Calculation Completed")
        
def retrieve_from_image():
        
        text = ''
        for i in range(20):
                img = cv2.imread(current_dir + "/newpics/cv_frame_" + str(i) + ".png")
                pil_frame = img#cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(pil_frame)
                pil_data = pil_frame.getdata()
                text =  text + retr(pil_data)
                print i
        print  len((text))
        filewrite = open(current_dir + "/data/hello7.txt", 'w')
        filewrite.write(bin2str(text))
        filewrite.close()

        
def RETRIEVE(input_video_filename, output_text_filename, print_output):
        if print_output == '1':
                PRINT = True
        else:
                PRINT = False

        input_filename = current_dir +  str(input_video_filename)
        input_text_file = current_dir +  str(output_text_filename)

        long_message_output = open(input_text_file, 'w')

        filesize = os.stat(input_filename).st_size
        if PRINT: print "Input video file size is: %d filesize" %filesize

        cap = cv2.VideoCapture(input_filename)
        total_frame_counts = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if PRINT: print "Total number of frames in input video: %d"  %total_frame_counts

        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        framecount  = 0
        total_text = ''
        if PRINT : print "Start Decoding"
        while framecount < total_frame_counts :     
                ret, frame = cap.read()
                if ret :
                        if PRINT : print "Successfully read %d frame" %framecount
                        framecount +=1
                        pil_frame = frame
                        pil_frame = Image.fromarray(pil_frame)
                        pil_data = pil_frame.getdata()                        
                        total_text =   total_text + retr(pil_data)
                        
        
        try:
                total_text = bin2str(total_text)
                if PRINT: print "Decoding Completed"
        except:
                total_text = ''
                if PRINT : print "Can not find any hidden data in input video file"
                pass
        long_message_output.write(total_text)
        long_message_output.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':

        parser = optparse.OptionParser('usage %prog'+\
		'-e/-d/-w <target file>')
	
	parser.add_option('-e', dest='ENCODE', type='string', \
		help='Retrieve the text from video')
	parser.add_option('-d', dest='RETRIEVE', type='string', \
		help='Encode the text in video')
	parser.add_option('-w', dest='DETECT', type='string', \
		help='Calculate the space in video according to input file for hiding')
	
	(options, args) = parser.parse_args()
	print options, args
	

	if (options.ENCODE != None):
                print options.ENCODE, args[0] , args[1]
		ENCODE(options.ENCODE, args[0], args[1])
	elif (options.RETRIEVE != None):
                print options.RETRIEVE, args[0] , args[1]
                RETRIEVE(options.RETRIEVE, args[0], args[1])
        elif (options.DETECT != None):
                print options.DETECT, args[0] , args[1]
                DETECT(options.DETECT, args[0], args[1])
	else:
		print parser.usage
		exit(0)

        
	#ENCODE(input_video_filename='videos/video_ani.mp4', input_text_filename='/data/data.txt', print_output=1)
        #RETRIEVE(input_video_filename, output_text_filename, print_output)
       
