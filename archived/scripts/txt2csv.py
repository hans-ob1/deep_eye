import os
import glob
import pandas as pd
from PIL import Image
import xml.etree.ElementTree as ET

rootfoldername = "processed"
subfoldername_data = ['imagedata_2014','imagedata_2017','imagedata_val']
subfoldername_anno = ['annodata_2014','annodata_2017','annodata_val']

def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def processInformation(img_path, anno_path):
    csv_list = []

    for root, dirs, files in os.walk(img_path):
        for fname_img in files:
            if fname_img.endswith(".jpg"):

                # Obtain image size (w,h) and filename
                fname_img_path = img_path + "/" + fname_img
                im = Image.open(fname_img_path)
                width, height = im.size


                # Obtain corresponding bbox
                fname_txt = fname_img[:-4] + ".txt"
                fname_txt_path = anno_path + "/" + fname_txt

    
                with open(fname_txt_path) as f:
                    content = f.readlines()
                    content = [x.strip() for x in content] 

                    for line in content:
                        class_idx, xmin, ymin, xmax, ymax = line.split()

                        # Pack value
                        value = (fname_img, str(width), str(height), class_idx, xmin, ymin, xmax, ymax)
                        csv_list.append(value)
    
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    csv_df = pd.DataFrame(csv_list, columns=column_name)

    return csv_df

def main():

    # Getting the image path
    nextPathImg = rootfoldername + "/" + subfoldername_data[2]
    image_path = nextPathImg

    # Getting the annotation path
    nextPathAnno = rootfoldername + "/" + subfoldername_anno[2]
    anno_path = nextPathAnno

    csv_df = processInformation(image_path,anno_path)
    csv_df.to_csv('val.csv', index=None)
    print('Successfully converted txt to csv.')

    '''
    xml_df = xml_to_csv(image_path)
    xml_df.to_csv('raccoon_labels.csv', index=None)
    
    '''

main()


