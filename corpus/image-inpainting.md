# Image inpainting

Inpainting fills a masked region of an image with plausible content.

## Diffusion methods

The simplest approach propagates the surrounding colours into the hole. A harmonic fill solves Laplace's equation inside the mask, so each pixel becomes the average of its neighbours; biharmonic filling also continues gradients smoothly. The Navier-Stokes method (Bertalmio et al. 2001) transports image intensity along isophotes, lines of constant intensity, and the fast-marching method of Telea (2004) fills the hole from the boundary inward with a weighted average of known pixels. These methods are fast and work for thin scratches and small holes but blur texture in large holes.

## Exemplar-based methods

Exemplar-based inpainting (Criminisi, Perez and Toyama 2004) copies whole patches from the known part of the image. The fill order matters: a priority of confidence times data term fills patches where strong edges run into the hole first, so linear structures are continued before texture is filled. PatchMatch (Barnes et al. 2009) made the patch search fast enough for interactive editing.

## Learned methods

LaMa (Suvorov et al. 2022) uses fast Fourier convolutions, which give a global receptive field, and is trained on large, irregular masks; it handles large holes and repetitive structure well. Diffusion-model inpainting (for example Stable Diffusion inpainting and BrushNet) can generate complex new content guided by a text prompt.

## Evaluation pitfalls

PSNR and SSIM computed over the whole image change little when the hole is small, so they should also be computed inside the mask. Perceptual metrics such as LPIPS and FID measure realism, not correctness. For scientific images, check the quantity that will be measured afterwards: a generative model can produce a convincing but wrong leaf outline, which changes leaf area and shape traits even though the image looks fine.
