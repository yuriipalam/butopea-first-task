import xml.etree.ElementTree as ET
from db_api import Database
import config


def prettify(element, indent='  '):
    queue = [(0, element)]
    while queue:
        level, element = queue.pop(0)
        children = [(level + 1, child) for child in list(element)]
        if children:
            element.text = '\n' + indent * (level+1)
        if queue:
            element.tail = '\n' + indent * queue[0][0]
        else:
            element.tail = '\n' + indent * (level-1)
        queue[0:0] = children


if __name__ == '__main__':
    db = Database()
    data = db.select_products_feed()

    xml_doc = ET.Element("rss", attrib={'xmlns:g':
                                        'http://base.google.com/ns/1.0',
                                        'version': '2.0'})

    channel = ET.SubElement(xml_doc, 'channel')
    ET.SubElement(channel, 'title').text = config.title
    ET.SubElement(channel, 'link').text = config.link
    ET.SubElement(channel, 'description').text = config.description
    for element in data:
        item = ET.SubElement(channel, 'item')
        for key in element.keys():
            if key == 'additional_image_link':
                for additional_images_link in element[key].split(','):
                    ET.SubElement(
                        item, f'g:{key}').text = additional_images_link
            else:
                ET.SubElement(item, f'g:{key}').text = element[f'{key}']

    prettify(xml_doc)
    tree = ET.ElementTree(xml_doc)
    tree.write('feed.xml', encoding='UTF-8', xml_declaration=True)
