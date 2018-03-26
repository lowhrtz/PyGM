#!/usr/bin/python3
import base64
import os
import xml.etree.ElementTree as etree


def load_qrc(filename):
    resource_xml = etree.parse(filename)
    return resource_xml


def get_image_paths(resource_xml):
    image_paths = []
    root = resource_xml.getroot()
    for image_path in root[0]:
        image_paths.append(image_path.text)
    return image_paths


def convert_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        data = base64.b64encode(image_file.read())
    return data.decode()


def compile_resource(input_filename, output_filename):
    resource = load_qrc(input_filename)
    images = get_image_paths(resource)
    code_string = ''
    for image in images:
        basename = os.path.basename(image)
        basename = basename.replace('.', '_')
        code_string += '''{} = '{}'


'''.format(basename, convert_to_base64(image))
    with open(output_filename, 'w') as out_file:
        out_file.write(code_string)


if __name__ == '__main__':
    compile_resource('resources.qrc', 'resources.py')
