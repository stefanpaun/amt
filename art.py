#%%
from PIL import Image, ImageDraw
import math
import random
from scipy import spatial


NEG_COLOR = 255
POS_COLOR = 0
CIRCLE_RADIUS = 3
CONVERGENCE_LIMIT = 5 * 10**-1
DEFAULT_RESOLUTION = 1
MAGNIFICATION = 8


folder_base="img/"
image_filename = "vince.jpg"
image = Image.open(folder_base + image_filename).convert('L')

#%%
width, height = image.size
pixels = image.load()
putpixel = image.putpixel
nodes = []

#%%

def draw_points_vor(points, putpixel):
  #
  for i in range(len(points)):
    pt = (int(points[i][0]), int(points[i][1]))
    if pt == (0,0): 
      # Skip pixels at origin - they'll break the TSP art
      continue
    putpixel(pt, POS_COLOR)

num_cells = int(math.hypot(width, height) * MAGNIFICATION)
centroids = [
    [random.randrange(width) for x in range(num_cells)],
    [random.randrange(height) for x in range(num_cells)]
  ]
rho = [[0] * width for y in range(height)]
draw_points_vor((centroids[0], centroids[1]), putpixel)

#%%
def compute_centroids(centroids, new_centroid_sums, image_size):
  centroidal_delta = 0
  for i in range(len(centroids[0])):
    if not new_centroid_sums[2][i]:
      # all pixels in region have rho = 0
        # send centroid somewhere else
      centroids[0][i] = random.randrange(image_size[0])
      centroids[1][i] = random.randrange(image_size[1])
    else:
      new_centroid_sums[0][i] /= new_centroid_sums[2][i]
      new_centroid_sums[1][i] /= new_centroid_sums[2][i]
      # print "centroidal_delta", centroidal_delta
      centroidal_delta += hypot_square( (new_centroid_sums[0][i]-centroids[0][i]), (new_centroid_sums[1][i]-centroids[1][i]) )
      centroids[0][i] = new_centroid_sums[0][i]
      centroids[1][i] = new_centroid_sums[1][i]


#
# create weighted voronoi diagram and add up for new centroids
#
def sum_regions(centroids, new_centroid_sums, rho, res_step, size):
  #
  #
  # construct 2-dimensional tree from generating points
  tree = spatial.KDTree(zip(centroids[0], centroids[1]))
  #
  imgx, imgy = size
  x_range = np.arange(res_step/2.0, imgx, res_step)
  y_range = np.arange(res_step/2.0, imgy, res_step)
  point_matrix = list(itertools.product(x_range, y_range))
  nearest_nbr_indices = tree.query(point_matrix)[1]
  for i in range(len(point_matrix)):
    point = point_matrix[i]
    x = point[0]
    y = point[1]
    r = rho[int(y)][int(x)]
    nearest_nbr_index = nearest_nbr_indices[i]
    new_centroid_sums[0][nearest_nbr_index] += r * x
    new_centroid_sums[1][nearest_nbr_index] += r * y
    new_centroid_sums[2][nearest_nbr_index] += r
    #
    if i % 10 == 0:
      #
      perc = float(i) / len(point_matrix)
      printr( "{:.2%}".format(perc) )

#%%
new_centroid_sums = [
    [0] * num_cells,  #   x component
    [0] * num_cells,  #   y component
    [0] * num_cells   #   density
]
# 
#
# Iterate to convergence
iteration = 1
resolution = DEFAULT_RESOLUTION
while True:
    # Zero all sums.
    temp_list = []
    temp_list2 = []
    for ls in new_centroid_sums:
        for x in range( len(ls) ):
            temp_list2.append(0)
            ls[x] = 0
    #     temp_list.append(temp_list2)
    #     temp_list2 = []

    # new_centroid_sums = temp_list.copy()
            
    # Shade regions and add up centroid totals.
    sum_regions(centroids, new_centroid_sums, rho, 1.0 / resolution, image.size)
    # Compute new centroids.
    centroidal_delta = compute_centroids(centroids, new_centroid_sums, image.size)
    # Print step difference.
    printr( str(iteration) + "     \tDifference: " + str(centroidal_delta) + ".\n" )
    # Save a snapshot of the current image.
    clear_image(image.size, putpixel)
    draw_points(zip_points(centroids), putpixel)
    image.save(folder_base + str(iteration) + ".png", "PNG")
    # If no pixels shifted, we have to increase resolution.
    if centroidal_delta == 0.0:
        resolution *= 2
    # Break if difference below convergence point.
    elif centroidal_delta < CONVERGENCE_LIMIT * resolution:
        break
    # Increase iteration count.
    iteration += 1






#%%
NEG_COLOR = pixels[0,0]
print ("Neg_color:", NEG_COLOR)
#
for i in range(width):
    for j in range(height):
        #
        if pixels[i,j] != NEG_COLOR:
            #
            if not POS_COLOR:
                POS_COLOR = pixels[i,j]
            #
            nodes.append( (i,j) )
            #
        #
    #
#%%
def draw_circle(image_draw, pt, radius):
    pt_1 = (pt[0]-radius,pt[1]-radius)
    pt_2 = (pt[0]+radius,pt[1]+radius)
    image_draw.ellipse([pt_1,pt_2], fill=0)

def clear_image(size, putpixel):
    imgx, imgy = size
    for y in range(imgy):
        for x in range(imgx):
            putpixel((x, y), NEG_COLOR)


def magnify_image(original_size, nodes, stretch_factor):
    magnified_size = (original_size[0] * stretch_factor, original_size[1] * stretch_factor)
    magnified_image = Image.new("L", magnified_size)
    putpixel = magnified_image.putpixel
    clear_image(magnified_size, putpixel)
    return magnified_image
# %%


image = magnify_image(image.size, nodes, CIRCLE_RADIUS)
nodes = [(x[0] * CIRCLE_RADIUS, x[1] * CIRCLE_RADIUS) for x in nodes]

#%%


for y in range(height):
    for x in range(width):
        image.putpixel((x, y), NEG_COLOR)


# draw dots
draw = ImageDraw.Draw(image)
for node in nodes:
    draw_circle(draw, node, CIRCLE_RADIUS)

image.show()

# %%
