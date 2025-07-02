import cv2


def canny_edge_detection(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)
    return edges


def blur_image(image):
    blurred_image = cv2.GaussianBlur(image, (15, 15), 0)
    return blurred_image


def invert_image(image):
    inverted_image = cv2.bitwise_not(image)
    return inverted_image


def apply_transformation(image, choice):
    if choice == "Canny Edge Detection":
        return canny_edge_detection(image)
    elif choice == "Blur":
        return blur_image(image)
    elif choice == "Invert":
        return invert_image(image)
