# Plant phenotyping from images

## Separating plant from background

The excess green index, ExG = 2g - r - b computed on chromaticity coordinates (each channel divided by r + g + b), separates green plant tissue from soil, paper or bench (Woebbecke et al. 1995). Because it uses ratios, it is largely insensitive to overall brightness. Otsu's method (1979) picks the threshold that maximises the between-class variance of the two resulting groups of pixels.

## Disease severity

Disease severity is the percentage of leaf area covered by lesions. Lesions are not green, so in a vegetation-index mask they appear as holes; holes inside the leaf can be filled, but lesions on the leaf margin are open to the background and get lost, which makes severity too low. Colour spaces that separate lightness from colour help to classify lesion pixels: in CIELAB, healthy leaf tissue has a strongly negative a* (green), necrotic tissue a positive a* (brown), and chlorotic tissue a high b* (yellow).

## Shape traits

From the leaf mask, region properties give area, perimeter, length and width of the fitted ellipse, aspect ratio, solidity (area divided by convex hull area, lower for lobed or serrated leaves) and circularity (4 pi area / perimeter squared). Pixel measurements become millimetres with a size reference in the image.

## Classical or deep learning?

Thresholding is fast, needs no training data and is easy to check, but breaks when the background is green or brown or the lighting is uneven. Deep segmentation models (U-Net and successors) handle complex scenes such as field images but need annotated training data and should be validated on images from the same conditions.
