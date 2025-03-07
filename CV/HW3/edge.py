import numpy as np
from collections import deque
from scipy.signal import convolve2d

def conv(image, kernel):
    """ An implementation of convolution filter.

    This function uses element-wise multiplication and np.sum()
    to efficiently compute weighted sum of neighborhood at each
    pixel.

    Args:
        image: numpy array of shape (Hi, Wi)
        kernel: numpy array of shape (Hk, Wk)

    Returns:
        out: numpy array of shape (Hi, Wi)
    """
    Hi, Wi = image.shape
    Hk, Wk = kernel.shape
    out = np.zeros((Hi, Wi))

    # For this assignment, we will use edge values to pad the images.
    # Zero padding will make derivatives at the image boundary very big,
    # whereas we want to ignore the edges at the boundary.
    pad_width0 = Hk // 2
    pad_width1 = Wk // 2
    pad_width = ((pad_width0,pad_width0),(pad_width1,pad_width1))
    padded = np.pad(image, pad_width, mode='edge')

    ### YOUR CODE HERE
    kernel = np.flip(np.flip(kernel)) 
    for i in range(pad_width0,Hi + pad_width0):
        for j in range(pad_width1 , Wi + pad_width1):
            out[i-pad_width0,j-pad_width1] = np.sum(padded[i-pad_width0:i+pad_width0+1,j-pad_width1:j+pad_width1+1] * kernel)

    ### END YOUR CODE

    return out

def gaussian_kernel(size, sigma):
    """ Implementation of Gaussian Kernel.
    
    This function follows the gaussian kernel formula,
    and creates a kernel matrix.

    Hints:
    - Use np.pi and np.exp to compute pi and exp
    
    Args:
        size: int of the size of output matrix
        sigma: float of sigma to calculate kernel

    Returns:
        kernel: numpy array of shape (size, size)
    """  
    
    ### YOUR CODE HERE
    assert sigma != 0,"sigma could not be zero"
  
    # Calculate the center of the kernel
    k = size // 2
    kernel = np.zeros((size, size), dtype=np.float32)
    d = (np.arange(size) - size // 2) ** 2
    kernel = np.exp(-(d.reshape(size, 1) + d.reshape(1, size)) / (2 * sigma ** 2)) 
    kernel = kernel   / (2 * np.pi * sigma ** 2) 

    # for i in range(size):
    #     for j in range(size):
    #         x = i - k
    #         y = j - k
    #         kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    
    # kernel /= (2 * np.pi * sigma**2)
    # kernel /= kernel.sum()  # Normalize
    ### END YOUR CODE

    return kernel

def partial_x(img):
    """ Computes partial x-derivative of input img.

    Hints: 
        - You may use the conv function in defined in this file.

    Args:
        img: numpy array of shape (H, W)
    Returns:
        out: x-derivative image
    """

    ### YOUR CODE HERE
    kernel_x = np.array([[-0.5, 0,0.5]])
    
    out=conv(img,kernel_x)

    ### END YOUR CODE

    return out

def partial_y(img):
    """ Computes partial y-derivative of input img.

    Hints: 
        - You may use the conv function in defined in this file.

    Args:
        img: numpy array of shape (H, W)
    Returns:
        out: y-derivative image
    """

    ### YOUR CODE HERE
    kernel_y = np.array([[-0.5],
                         [0],
                         [0.5]])
    out=conv(img,kernel_y)

    ### END YOUR CODE

    return out

def gradient(img):
    """ Returns gradient magnitude and direction of input img.

    Args:
        img: Grayscale image. Numpy array of shape (H, W)

    Returns:
        G: Magnitude of gradient at each pixel in img.
            Numpy array of shape (H, W)
        theta: Direction(in degrees, 0 <= theta < 360) of gradient
            at each pixel in img. Numpy array of shape (H, W)
    """
    G = np.zeros(img.shape)
    theta = np.zeros(img.shape)

    ### YOUR CODE HERE
    dx = partial_x(img)

    dy = partial_y(img)
    
    G = np.sqrt(dx ** 2 + dy ** 2) 
    
    theta = (np.arctan2(dy, dx) * 180 / np.pi) % 360
    ### END YOUR CODE

    return G, theta


def non_maximum_suppression(G, theta):
    """ Performs non-maximum suppression

    This function performs non-maximum suppression along the direction
    of gradient (theta) on the gradient magnitude image (G).
    
    Args:
        G: gradient magnitude image with shape of (H, W)
        theta: direction of gradients with shape of (H, W)

    Returns:
        out: non-maxima suppressed image
    """
    H, W = G.shape
    out = np.zeros((H, W))

    # Round the gradient direction to the nearest 45 degrees
    theta = np.floor((theta + 22.5) / 45) * 45

    ### BEGIN YOUR CODE
    theta = theta%360
    direction = {
        0   : (0,1),
        315 : (-1,1),
        270 : (-1,0),
        225 : (-1,-1),
        180 : (0,-1),
        135 : (1,-1),
        90  : (1,0),
        45  : (1,1),
        360 : (0,1)
    }
    for i in range(H):
        for j in range(W):
            fd = direction[theta[i][j]]
            bd = direction[(theta[i][j] + 180) % 360]
            fd_p = (i + fd[0],j + fd[1])
            bd_p = (i + bd[0],j + bd[1])
            if 0 <= fd_p[0] < H and 0 <= fd_p[1] < W:
                if G[i][j] < G[fd_p[0]][fd_p[1]]:
                    continue
            if 0 <= bd_p[0] < H and 0 <= bd_p[1] < W:
                if G[i][j] < G[bd_p[0]][bd_p[1]]:
                    continue
            out[i][j] = G[i][j]

        ### END YOUR CODE

    return out

def double_thresholding(img, high, low):
    """
    Args:
        img: numpy array of shape (H, W) representing NMS edge response
        high: high threshold(float) for strong edges
        low: low threshold(float) for weak edges

    Returns:
        strong_edges: Boolean array representing strong edges.
            Strong edeges are the pixels with the values above
            the higher threshold.
        weak_edges: Boolean array representing weak edges.
            Weak edges are the pixels with the values below the
            higher threshould and above the lower threshold.
    """

    strong_edges = np.zeros(img.shape, dtype=bool)
    weak_edges = np.zeros(img.shape, dtype=bool)

    ### YOUR CODE HERE
    strong_edges = img >= high
    weak_edges = (img < high) & (img > low)

     ### END YOUR CODE

    return strong_edges, weak_edges


def get_neighbors(y, x, H, W):
    """ Return indices of valid neighbors of (y, x)

    Return indices of all the valid neighbors of (y, x) in an array of
    shape (H, W). An index (i, j) of a valid neighbor should satisfy
    the following:
        1. i >= 0 and i < H
        2. j >= 0 and j < W
        3. (i, j) != (y, x)

    Args:
        y, x: location of the pixel
        H, W: size of the image
    Returns:
        neighbors: list of indices of neighboring pixels [(i, j)]
    """
    neighbors = []

    for i in (y-1, y, y+1):
        for j in (x-1, x, x+1):
            if i >= 0 and i < H and j >= 0 and j < W:
                if (i == y and j == x):
                    continue
                neighbors.append((i, j))

    return neighbors

def link_edges(strong_edges, weak_edges):
    """ Find weak edges connected to strong edges and link them.

    Iterate over each pixel in strong_edges and perform breadth first
    search across the connected pixels in weak_edges to link them.
    Here we consider a pixel (a, b) is connected to a pixel (c, d)
    if (a, b) is one of the eight neighboring pixels of (c, d).

    Args:
        strong_edges: binary image of shape (H, W)
        weak_edges: binary image of shape (H, W)
    Returns:
        edges: numpy array of shape(H, W)
    """

    H, W = strong_edges.shape
    indices = np.stack(np.nonzero(strong_edges)).T

    ### YOUR CODE HERE
    edges = np.copy(strong_edges)
    # Perform BFS!
    q=[]
    visited_nodes = np.zeros_like(edges)

    q.append((0,0))
    # While our nodes queue is not empty
    while len(q) != 0:
            # Take the first element in the list
            curr_i, curr_j = q.pop(0)

            # If we already visited this node - just continue
            if visited_nodes[curr_i, curr_j] == 1:
                continue

            # Mark node as visited
            visited_nodes[curr_i, curr_j] = 1

            neighors = get_neighbors(curr_i, curr_j, H, W)

            # Add neighbors
            for x,y in neighors:
                q.append((x,y))

            # Check for adjacent edges
            adjacent_edges = False
            for x,y in neighors:
                adjacent_edges = edges[x, y] or adjacent_edges

            if weak_edges[curr_i,curr_j] and adjacent_edges:
                edges[curr_i,curr_j] = True
                
    ### END YOUR CODE

    return edges

def canny(img, kernel_size=5, sigma=1.4, high=20, low=15):
    """ Implement canny edge detector by calling functions above.

    Args:
        img: binary image of shape (H, W)
        kernel_size: int of size for kernel matrix
        sigma: float for calculating kernel
        high: high threshold for strong edges
        low: low threashold for weak edges
    Returns:
        edge: numpy array of shape(H, W)
    """
    ### YOUR CODE HERE
    kernel = gaussian_kernel(kernel_size, sigma)
    smoothed = conv(img, kernel)
    G, theta = gradient(smoothed)
    nms = non_maximum_suppression(G, theta)
    strong_edges, weak_edges = double_thresholding(nms, high, low)
    edge = link_edges(strong_edges, weak_edges)
    ### END YOUR CODE

    return edge


def hough_transform(img):
    """ Transform points in the input image into Hough space.

    Use the parameterization:
        rho = x * cos(theta) + y * sin(theta)
    to transform a point (x,y) to a sine-like function in Hough space.

    Args:
        img: binary image of shape (H, W)
        
    Returns:
        accumulator: numpy array of shape (m, n)
        rhos: numpy array of shape (m, )
        thetas: numpy array of shape (n, )
    """
    # Set rho and theta ranges
    W, H = img.shape
    diag_len = int(np.ceil(np.sqrt(W * W + H * H)))
    rhos = np.linspace(-diag_len, diag_len, diag_len * 2 + 1)
    thetas = np.deg2rad(np.arange(-90.0, 90.0))

    # Cache some reusable values
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    num_thetas = len(thetas)

    # Initialize accumulator in the Hough space
    accumulator = np.zeros((2 * diag_len + 1, num_thetas), dtype=np.uint64)
    ys, xs = np.nonzero(img)

    # Transform each point (x, y) in image
    # Find rho corresponding to values in thetas
    # and increment the accumulator in the corresponding coordiate.

    ### YOUR CODE HERE
    for y,x in zip(ys, xs):
        for t_idx, theta in enumerate(thetas):
            ro = x*cos_t[t_idx] + y * sin_t[t_idx]
            # Finding our idx in the linear space
            ro_idx = int(ro +diag_len)
            accumulator[ro_idx, t_idx]+=1
    
    ### END YOUR CODE

    return accumulator, rhos, thetas
