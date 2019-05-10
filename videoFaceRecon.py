import os
import sys
import cv2
import numpy as np

def normalize(X, low, high, dtype=None):
    """Normalizes a given array in X to a value between low and high."""
    X = np.asarray(X)
    minX, maxX = np.min(X), np.max(X)
    # normalize to [0...1].
    X = X - float(minX)
    X = X / float((maxX - minX))
    # scale to [low...high].
    X = X * (high-low)
    X = X + low
    if dtype is None:
        return np.asarray(X)
    return np.asarray(X, dtype=dtype)


def read_images(path, sz=None):
    c = 0
    X,y = [], []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    if (filename == ".directory"):
                        continue
                    filepath = os.path.join(subject_path, filename)
                    im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                    if (im is None):
                        print ("image " + filepath + " is none")
                    else:
                        print (filepath)
                    # resize to given size (if given)
                    if (sz is not None):
                        im = cv2.resize(im, (200, 200))

                    X.append(np.asarray(im, dtype=np.uint8))
                    y.append(c)
                # except IOError, (errno, strerror):
                #     print ("I/O error({0}): {1}".format(errno, strerror))
                except:
                    print ("Unexpected error:", sys.exc_info()[0])
                    raise
            print (c)
            c = c+1
            
    print (y)
    return [X,y]

def face_rec():

    names = ['fanshengmei']
    if len(sys.argv) < 2:
        print ("USAGE: facerec_demo.py </path/to/images> [</path/to/store/images/at>]")
        sys.exit()

    [X,y] = read_images(sys.argv[1])
    y = np.asarray(y, dtype=np.int32)
    
    if len(sys.argv) == 3:
        out_dir = sys.argv[2]
    
    model = cv2.face.createEigenFaceRecognizer()
    model.train(np.asarray(X), np.asarray(y))
    camera = cv2.VideoCapture("2.mp4")

    face_cascade = cv2.CascadeClassifier('./cascades/haarcascade_frontalface_alt2.xml')
    while (True):
      read, img = camera.read()
      # faces = face_cascade.detectMultiScale(img, 1.3, 5)
      faces = face_cascade.detectMultiScale(img, 1.4, 5)
      for (x, y, w, h) in faces:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # print(gray)
        roi = gray[x:x+w, y:y+h]
        # print(roi)
        try:
            roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_LINEAR)
            print (roi.shape)
            params = model.predict(roi)
            print ("Label: %s, Confidence: %.2f" % (params[0], params[1]))
            cv2.putText(img, names[params[0]], (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
            if (params[0] == 0):
                cv2.imwrite('face_rec.jpg', img)
        except:
            continue
      cv2.imshow("camera", img)
      if cv2.waitKey(1000 // 12) & 0xff == ord("q"):
        break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    face_rec()

def original():
    out_dir = None
    names = ['Joe', 'Jane', 'Jack']

    if len(sys.argv) < 2:
        print ("USAGE: facerec_demo.py </path/to/images> [</path/to/store/images/at>]")
        sys.exit()

    [X,y] = read_images(sys.argv[1])
    y = np.asarray(y, dtype=np.int32)
    # If a out_dir is given, set it:
    if len(sys.argv) == 3:
        out_dir = sys.argv[2]
    model = cv2.face.createEigenFaceRecognizer()
    model.train(np.asarray(X), np.asarray(y))
    camera = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('./cascades/haarcascade_frontalface_default.xml')
    while (True):
      read, img = camera.read()
      faces = face_cascade.detectMultiScale(img, 1.3, 5)
      for (x, y, w, h) in faces:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        roi = gray[x:x+w, y:y+h]
        roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_LINEAR)
        print (roi.shape)
        params = model.predict(roi)
        print ("Label: %s, Confidence: %.2f" % (params[0], params[1]))
        cv2.putText(img, names[params[0]], (x,y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 3)
      cv2.imshow("camera", img)
      if cv2.waitKey(1000 / 12) & 0xff == ord("q"):
        break

    [p_label, p_confidence] = model.predict(np.asarray(X[0]))
    print ("Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence))
    print (model.getParams())
    mean = model.getMat("mean")
    eigenvectors = model.getMat("eigenvectors")
    mean_norm = normalize(mean, 0, 255, dtype=np.uint8)
    mean_resized = mean_norm.reshape(X[0].shape)
    if out_dir is None:
        cv2.imshow("mean", mean_resized)
    else:
        cv2.imwrite("%s/mean.png" % (out_dir), mean_resized)
    for i in range(min(len(X), 16)):
        eigenvector_i = eigenvectors[:,i].reshape(X[0].shape)
        eigenvector_i_norm = normalize(eigenvector_i, 0, 255, dtype=np.uint8)
        if out_dir is None:
            cv2.imshow("%s/eigenface_%d" % (out_dir,i), eigenvector_i_norm)
        else:
            cv2.imwrite("%s/eigenface_%d.png" % (out_dir,i), eigenvector_i_norm)
    if out_dir is None:
        cv2.waitKey(0)

    cv2.destroyAllWindows()
