import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET

#trainingDirList = ['bikedata','cocodata1','cocodata2','kittiedata','sgdata','vocdata1','vocdata2','vocdata3','vocdata4']
#trainingDirList = ['test_data']
trainingDirList = ['kittiedata']
token = "ssd_labels"

def main():
    for dirIn in trainingDirList:

        trainingDir = dirIn + '/' + token

        print("processing " + dirIn + " dataset......")

        txt_list = []
        # Loop through the txt files in source folder to convert
        for filename_txt in os.listdir(trainingDir):
            input_fname = os.path.join(trainingDir,filename_txt)

            with open(input_fname) as f:
                 content = f.readlines()    

            for sentence in content:
                sentence[:-2]
                numline = [i for i in sentence.split()]


                if int(numline[2]) == 1:
                    class_name = "person"
                elif int(numline[2]) == 2:
                    class_name = "bike"
                else:
                    class_name = "vehicle"

                filename_img = filename_txt[:-4] + ".png"
                value = (filename_img, 
                         numline[0], 
                         numline[1], 
                         class_name, 
                         numline[3], 
                         numline[4], 
                         numline[5], 
                         numline[6]
                         )
                txt_list.append(value)

            print("processed: " + filename_txt)

        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        txt_df = pd.DataFrame(txt_list, columns=column_name)
        txt_df.to_csv(dirIn+'/'+dirIn+'.csv', index=None)
        print("successfully converted to csv for: " + dirIn)

main()
