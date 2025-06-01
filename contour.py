import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# load image
path = 'creature.jpg'
image = cv2.imread(path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# get contours
edges = cv2.Canny(gray, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
contours = sorted(contours, key=lambda c: len(c), reverse=True)
contours = contours[:100]
canvas = np.ones_like(image) * 255
colors = plt.cm.get_cmap('tab20', len(contours))
points = []

#
for i, contour in enumerate(contours):
    c = colors(i)
    color = (int(c[2]*255), int(c[1]*255), int(c[0]*255))
    cv2.drawContours(canvas, [contour], -1, color, 2)

    contour = contour.squeeze()
    if len(contour.shape) == 1:
        pts = np.repeat(contour[np.newaxis, :], 5, axis=0)
    else:
        indices = np.linspace(0, len(contour) - 1, 5, dtype=int)
        pts = contour[indices]
    points.append((pts, color))



# plot
plt.figure(figsize=(10,10))
plt.imshow(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
plt.title("densest 50 contours")
plt.axis('off')
plt.savefig('contours.png')

plt.figure(figsize=(10,10))
for pts, color in points:
    color_rgb = (color[2]/255, color[1]/255, color[0]/255)
    plt.plot(pts[:, 0], pts[:, 1], 'o', color=color_rgb, markersize=8)
plt.gca().invert_yaxis()
plt.title("plotted contours (5 points per contour)")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True)
plt.axis('equal')
plt.savefig('points.png')

points = [point[0] for point in points]
df = pd.DataFrame(points)
df.to_csv("creature_points.txt", index=False)
