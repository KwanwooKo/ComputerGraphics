import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code  # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Color:
    def __init__(self, R, G, B):
        self.color = np.array([R, G, B]).astype(np.float)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1) * 255).astype(np.uint8)

class Sphere:
    def __init__ (self, name, radius, center, diffuseColor):
        self.name = name
        self.radius = radius
        self.center = center
        self.diffuseColor = diffuseColor

class Box:
    def __init__(self, name, minPt, maxPt, diffuseColor):
        self.name = name
        self.minPt = minPt
        self.maxPt = maxPt
        self.diffuseColor = diffuseColor
        self.center = (minPt + maxPt) / 2

class ShadingColor:
    def __init__ (self, productName, diffuseColor):
        self.productName = productName
        self.diffuseColor = diffuseColor

class Camera:
    def __init__(self, viewDir, viewUp):
        self.camW = -normalize(viewDir)
        self.camU = normalize(np.cross(viewUp, self.camW))
        self.camV = normalize(np.cross(self.camW, self.camU))

    def intersection(self, viewPoint, coeff_u, coeff_v, distance):
        s = viewPoint + coeff_u * self.camU + coeff_v * self.camV - distance * self.camW
        return s

def normalize(vec):
    return vec / np.sqrt(np.dot(vec, vec))

class Ray:
    # endPoint => s(plane)
    # starPoint => viewPoint(camera)
    def __init__(self, startPoint, endPoint):
        self.startPoint = startPoint
        self.endPoint = endPoint

    def distance(self):
        vec = self.startPoint - self.endPoint
        return np.sqrt(np.dot(vec, vec))

    def getVector(self):
        vec = self.startPoint - self.endPoint
        vec = normalize(vec)
        return vec

    def hitSphere(self, radius, center):
        ray_p = self.startPoint - center # viewPoint
        # ray_p = self.startPoint - center
        ray_d = normalize(self.endPoint - self.startPoint)
        a = np.dot(ray_d, ray_d)
        b = np.dot(ray_d, -(ray_p))
        c = np.dot(ray_p, ray_p) - (radius * radius)

        if (b ** 2 - a * c) >= 0:
            t = (b - np.sqrt(b ** 2 - a * c)) / a
            if t < 0:
                return None
            point = self.startPoint + ray_d * t
            return point
        else:
            return None

    def lambertian(self, lightPoint, point, center, diffuseColor, lightIntensity):
        lightRay = normalize(lightPoint - point)
        normal = normalize(point - center)
        reflectedLight = diffuseColor * lightIntensity * max(0, np.dot(lightRay, normal).astype(np.float))
        return reflectedLight

    def phong(self, lightPoint, point, center, specularColor, lightIntensity, exponent):
        lightRay = normalize(lightPoint - point)
        eyeRay = normalize(self.startPoint - point)
        normal = normalize(point - center)
        h = normalize(lightRay + eyeRay)
        SpecularShading = specularColor * lightIntensity * (max(0, np.dot(h, normal)) ** exponent)
        return SpecularShading

    def rayTrace(self, lambertian, Phong):
        color = Color(lambertian[0] * Phong[0], lambertian[1] * Phong[1], lambertian[2] * Phong[2])
        color.gammaCorrect(2.2)
        return color

    def hitBox(self, minPt, maxPt):
        ray_p = self.startPoint
        ray_d = normalize(self.endPoint - self.startPoint)

        txMin = (minPt[0] - ray_p[0]) / ray_d[0]
        txMax = (maxPt[0] - ray_p[0]) / ray_d[0]

        if txMin > txMax:
            tmp = txMax     # swap
            txMax = txMin
            txMin = tmp

        tyMin = (minPt[1] - ray_p[1]) / ray_d[1]
        tyMax = (maxPt[1] - ray_p[1]) / ray_d[1]

        if tyMin > tyMax:
            tmp = tyMax     # swap
            tyMax = tyMin
            tyMin = tmp

        if txMin > tyMax or tyMin > txMax:
            return None

        if tyMin > txMin:
            txMin = tyMin
        if tyMax < txMax:
            txMax = tyMax

        tzMin = (minPt[1] - ray_p[1]) / ray_d[1]
        tzMax = (maxPt[1] - ray_p[1]) / ray_d[1]

        if tzMin > tzMax:
            tmp = tzMin
            tzMin = tzMax
            tzMax = tmp

        if txMin > tzMax or tzMin > txMax:
            return None

        if tzMin >= txMin:
            txMin = tzMin
        if tzMax < txMax:
            txMax = tzMax

        if txMin <= 0:
            return None

        return txMin


def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir = np.array([0, 0, -1]).astype(np.float)
    viewUp = np.array([0, 1, 0]).astype(np.float)
    viewProjNormal = -1 * viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth = 1.0
    viewHeight = 1.0
    projDistance = 1.0
    intensity = np.array([1, 1, 1]).astype(np.float)  # how bright the light is.
    exponent = 1.0
    specularColor = np.array([0., 0., 0.])
    imgSize = np.array(root.findtext('image').split()).astype(np.int)
    productColorList = []
    sphereList = []
    boxColorList = []
    boxList = []
    minPt = [0., 0., 0.]
    maxPt = [0., 0., 0.]
    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float)
        viewDir = np.array(c.findtext('viewDir').split()).astype(np.float)
        viewUp = np.array(c.findtext('viewUp').split()).astype(np.float)
        width = np.array(c.findtext('viewWidth').split()).astype(np.float)
        height = np.array(c.findtext('viewHeight').split()).astype(np.float)
        projDistance = c.findtext('projDistance')
        if projDistance is not None:
            projDistance = float(c.findtext('projDistance'))
        else:
            projDistance = 1.

    for c in root.findall('shader'):
        # ProductName = c.get('name')     # shader ± name
        diffuseColor = np.array(c.findtext('diffuseColor').split()).astype(np.float)
        specularColor = c.findtext('specularColor')
        if specularColor is not None:
            specularColor = np.array(c.findtext('specularColor').split()).astype(np.float)
        else:
            specularColor = np.array([0., 0., 0.])
        exponent = c.findtext('exponent')
        if exponent is not None:
            exponent = float(c.findtext('exponent'))
        else:
            exponent = 1.
        sphereName = c.get('name')
        shadingColor = ShadingColor(sphereName, diffuseColor)
        productColorList.append(shadingColor)    # color  ޾ƿԾ


    for c in root.findall('light'):
        lightPoint = np.array(c.findtext('position').split()).astype(np.float)
        lightIntensity = np.array(c.findtext('intensity').split()).astype(np.float)

    for c in root.findall('surface'):
        productType = c.get('type')
        for d in c.findall('shader'):
            refName = d.get('ref')      # blue
        # print(refName)
        if productType == "Sphere":
            radius = np.array(c.findtext('radius').split()).astype(np.float)
            center = np.array(c.findtext('center').split()).astype(np.float)
            for element in productColorList:
                if element.productName == refName:
                    singleSphere = Sphere(refName, radius, center, element.diffuseColor)
                    sphereList.append(singleSphere)
        if productType == "Box":
            minPt = np.array(c.findtext('minPt').split()).astype(np.float)
            maxPt = np.array(c.findtext('maxPt').split()).astype(np.float)
            for element in productColorList:
                if element.productName == refName:
                    singleBox = Box(refName, minPt, maxPt, element.diffuseColor)
                    boxList.append(singleBox)

    for element in sphereList:
        print(element.name, element.center, element.radius)
    for element in boxList:
        print(element.name, element.minPt, element.maxPt, element.diffuseColor)

    # code.interact(local=dict(globals(), **locals()))

    # Create an empty image
    channels = 3

    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:, :] = 0

    left = -width / 2
    bottom = -height / 2
    camera = Camera(viewDir, viewUp)
    for i in np.arange(imgSize[1]):
        for j in np.arange(imgSize[0]):

            coeff_u = left + width * (j + 0.5) / imgSize[0]
            coeff_v = bottom + height * (i + 0.5) / imgSize[1]

            s = camera.intersection(viewPoint, coeff_u, coeff_v, projDistance)

            ray = Ray(viewPoint, s)
            minDistance = 2147483647
            minPoint = None
            minSphere = None
            point = None

            for k in sphereList:
                point = ray.hitSphere(k.radius, k.center)
                if point is None:
                    continue

                vec = point - viewPoint
                distance = np.sqrt(np.dot(vec, vec))

                if minDistance > distance:
                    minDistance = distance
                    minPoint = point
                    minSphere = k

            for k in boxList:
                point = ray.hitBox(minPt, maxPt)
                if point is None:
                    continue
                vec = point - viewPoint
                distance = np.sqrt(np.dot(vec, vec))

                if minDistance > distance:
                    minDistance = distance
                    minPoint = point
                    minBox = k

            shadowPoint = None
            if minPoint is not None:
                for other in sphereList:
                    if minSphere.name != other.name:
                        shadowRay = Ray(minPoint, lightPoint)
                        shadowPoint = shadowRay.hitSphere(other.radius, other.center)

                    if shadowPoint is None:
                        continue
                    else:
                        break
                for other in boxList:
                    if minBox.name != other.name:
                        shadowRay = Ray(minPoint, lightPoint)
                        shadowPoint = shadowRay.hitBox(other.minPt, other.maxPt)
                    if shadowPoint is None:
                        continue
                    else:
                        break

                if shadowPoint is None and not boxList:
                    lambertian = ray.lambertian(lightPoint, minPoint, minSphere.center, minSphere.diffuseColor, lightIntensity)
                    phong = ray.phong(lightPoint, minPoint, minSphere.center, specularColor, lightIntensity, exponent)
                    # print(lambertian)
                    color = Color(lambertian[0] + phong[0], lambertian[1] + phong[1], lambertian[2] + phong[2])
                    # print(minSphere.name)
                    color.gammaCorrect(2.2)
                    img[imgSize[1] - 1 - i][j] = color.toUINT8()
                elif shadowPoint is None and not sphereList:
                    lambertian = ray.lambertian(lightPoint, minPoint, minBox.center, minBox.diffuseColor, lightIntensity)
                    phong = ray.phong(lightPoint, minPoint, minSphere.center, specularColor, lightIntensity, exponent)
                    # print(lambertian)
                    color = Color(lambertian[0] + phong[0], lambertian[1] + phong[1], lambertian[2] + phong[2])
                    # print(minSphere.name)
                    color.gammaCorrect(2.2)
                    img[imgSize[1] - 1 - i][j] = color.toUINT8()
                else:
                    black = Color(0, 0, 0)
                    img[imgSize[1] - 1 - i][j] = black.toUINT8()

            elif minPoint is None:
                # print("point is None")
                black = Color(0, 0, 0)
                img[imgSize[1] - 1 - i][j] = black.toUINT8()

    rawimg = Image.fromarray(img, 'RGB')
    # rawimg.save('out.png')
    rawimg.save(sys.argv[1] + '.png')


if __name__ == "__main__":
    main()

