from PIL import Image
import numpy as np
from collections import defaultdict
import networkx as nx
import seaborn as sns

class PageImage():
    def __init__(self, width, height, name, scale_factor=3):
        self.scale_factor = scale_factor
        self.page_width = int(np.floor(width*self.scale_factor))
        self.page_height = int(np.floor(height*self.scale_factor))

        self.image_data = np.zeros((self.page_height, self.page_width, 3), dtype=np.uint8)
        self.logic_data = np.zeros((self.page_height, self.page_width), dtype=np.uint16)
        self.image_data += 255
        self.block_counter = 1
        self.name = name
        self.color_counter = 0
        self.blocks = {}
        palettes = sns.color_palette('Accent') + sns.color_palette('Paired') + sns.color_palette('Greys') + sns.color_palette('hsv') # nipy_spectral
        self.colors = {i: [round(c*255) for c in p] for i,p in enumerate(palettes)}

    def add_pdf_layer(self, file):
        print(self.image_data.shape)
        self.image_data = np.array(Image.open(file).convert('RGB'))

    def add_box(self, x, y, w, h, color='random', mode='border', count=True):
        x = x * self.scale_factor
        y = y * self.scale_factor
        w = w * self.scale_factor
        h = h * self.scale_factor

        CENTER_SCALE = 1.022
        center = [(x + w/2) * CENTER_SCALE, -(y + h/2) * CENTER_SCALE]

        if color == 'random':
            color = self.get_random_color()

        if mode == 'block':
            for x_i in range(w-1):
                for y_i in range(h-1):
                    self.image_data[y+y_i, x+x_i] = color

        if mode == 'border':
            # set background:
            #for x_i in range(w-1):
            #    for y_i in range(h-1):
            #        self.image_data[y+y_i, x+x_i] = [250,250,250]

            # set border
            for x_i in range(w):
                self.image_data[y,x+x_i] = color
                self.image_data[y+h,x+x_i] = color
            for y_i in range(h):
                self.image_data[y+y_i,x] = color
                self.image_data[y+y_i,x+w] = color

        
        if count:
            for x_i in range(w-1):
                for y_i in range(h-1):
                    self.logic_data[y+y_i+1, x+x_i+1] = self.block_counter
            
            self.blocks[self.block_counter]=center
            self.block_counter += 1
        return self.block_counter -1

    def get_random_color(self):
        options = list(self.colors.keys())
        return self.colors[options[np.random.choice(len(options))]]

    def get_next_color(self):
        options = list(self.colors.keys())
        res = self.color_counter % len(options)
        self.color_counter += 1
        return self.colors[res]

    def draw(self, path):
        image = Image.fromarray(self.image_data)
        image.save(path)
        return path

    def get_image(self):
        return self.image_data

    def get_image_binary(self):
        print(self.get_image().shape)
        return (1 - np.mean(self.get_image(), 2) / 255).astype(bool)

    def get_logic_image(self):
        return self.logic_data

    def get_block_positions(self):
        return self.blocks
    
    def get_graph(self):
        logic_image = self.get_logic_image()
        edge_distances = {'x': defaultdict(lambda: defaultdict(
            lambda: 100000)), 'y': defaultdict(lambda: defaultdict(lambda: 100000))}

        for direction, img in zip(['x', 'y'], [logic_image, logic_image.T]):
            for row in img:
                last_seen = None
                distance = 0
                for number in row:
                    if number != 0:
                        if last_seen and last_seen != number:
                            a, b = sorted([last_seen, number])
                            edge_distances[direction][a][b] = min(
                                edge_distances[direction][a][b], distance)
                        last_seen = number
                        distance = 0
                    else:
                        distance += 1

        G = nx.Graph()
        for direction, edges_for_direction in edge_distances.items():
            for a, edge in edges_for_direction.items():
                for b, distance in edge.items():
                    # print(edge.values())
                    if distance == min(edge.values()):
                        x = direction == 'x'
                        if x:
                            distance = 1 - distance / self.page_width
                        else:
                            distance = 1 - distance / self.page_height
                        distance = distance ** 3
                        G.add_edge(a, b, distance=distance, x=x,
                                y=(not x))  # specify edge data

        return G



def white_to_transparent(image):
    # make all white pixels transparent
    datas = image.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    image.putdata(newData)
    return image

def everything_but_grayscales_to_transparent(image):
    # make all white pixels transparent
    datas = image.getdata()
    newData = []
    for item in datas:
        if item[0] == item[1] == item[2] and item[0] < 250:
            newData.append(item)
        else:
            newData.append((255, 255, 255, 0))

    image.putdata(newData)
    return image


