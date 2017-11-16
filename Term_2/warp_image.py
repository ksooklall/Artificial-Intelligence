import cv2
import numpy as np
import matplotlib.pyplot as plt

# Read image
image = cv2.imread()

# Convert image
img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Make a copy
cp_img = img

def warp(image):
	source_points = np.float32([[400, 820], [350, 1050], [610, 1100], [650, 875]])
	target_point = np.float32([[500, 800], [500, 1100], [800, 1100], [800, 800]])
	
	# Compute perspective transform, M
	M = cv2.getPerspectiveTransform(source_points, target_points)
	
	# Inver if needed 
	M_inv = cv2.getPeerspectiveTransform(target_point, source_points)

	# Image shape
	image_shape = (image.shape[1], image,shape[0])

	# Compute and return warped image
	warped = cv2.warpPerspective(image, M, image_shape, flags=cv2.INTER_LINEAR)

	return warp

# Warping time
warped_image = warp(cp_img)


# Display original and warp image
f, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
ax1.title('Original image')
ax1.imshow(cp_img)

ax2.set_title('Warped Image')
ax2.imshow(warped_image)
