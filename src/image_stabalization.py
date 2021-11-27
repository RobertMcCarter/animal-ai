# See: https://learnopencv.com/video-stabilization-using-point-feature-matching-in-opencv/

# Import numpy and OpenCV
import numpy as np
import cv2


# Pre-define transformation-store array
transforms = np.zeros((n_frames - 1, 3), np.float32)

for i in range(n_frames - 2):
    # Detect feature points in previous frame
    prev_pts = cv2.goodFeaturesToTrack(
        prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3
    )

    # Read next frame
    success, curr = cap.read()
    if not success:
        break

    # Convert to grayscale
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)

    # Calculate optical flow (i.e. track feature points)
    curr_pts, status, err = cv2.calcOpticalFlowPyrLK(
        prev_gray, curr_gray, prev_pts, None
    )

    # Sanity check
    assert prev_pts.shape == curr_pts.shape

    # Filter only valid points
    idx = np.where(status == 1)[0]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]

    # Find transformation matrix
    m = cv2.estimateRigidTransform(
        prev_pts, curr_pts, fullAffine=False
    )  # will only work with OpenCV-3 or less

    # Extract traslation
    dx = m[0, 2]
    dy = m[1, 2]

    # Extract rotation angle
    da = np.arctan2(m[1, 0], m[0, 0])

    # Store transformation
    transforms[i] = [dx, dy, da]

    # Move to next frame
    prev_gray = curr_gray

    print(
        "Frame: "
        + str(i)
        + "/"
        + str(n_frames)
        + " -  Tracked points : "
        + str(len(prev_pts))
    )
